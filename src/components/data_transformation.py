import sys
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelEncoder

from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR, TEXT_COLUMN
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_object, read_yaml_file, save_csv_data


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise MyException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)

    def _rename_columns(self, df):
        logging.info("Renaming specific columns")
        df = df.rename(columns={
            "narrative": "complaint_text"
        })
        return df

    def _drop_index_column(self, df):
        logging.info("Dropping unwanted columns if present")
        drop_cols = self._schema_config.get("drop_columns", [])
        df = df.drop(columns=drop_cols, errors="ignore")
        return df
    
    def _dropna_columns(self, df):
        logging.info("Dropping rows with NA complaint_text")
        df = df.dropna(subset=["complaint_text"])
        return df


    def _preprocess_text(self, df):
        stop_words = set(stopwords.words("english"))
        df = df.copy()      
        df[TEXT_COLUMN] = df[TEXT_COLUMN].str.lower()
        # remove non alphabet characters
        df[TEXT_COLUMN] = df[TEXT_COLUMN].apply(
            lambda x: re.sub(r"[^a-zA-Z\s]", " ", x) )
        # remove extra spaces
        df[TEXT_COLUMN] = df[TEXT_COLUMN].apply(
           lambda x: re.sub(r"\s+", " ", x).strip())
        # remove stopwords
        df[TEXT_COLUMN] = df[TEXT_COLUMN].apply(
            lambda x: " ".join(word for word in x.split() if word not in stop_words))
        return df
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        Initiates the data transformation component for the pipeline.
        """
        try:
            logging.info("Data Transformation Started !!!")
            if not self.data_validation_artifact.validation_status:
                raise Exception(self.data_validation_artifact.message)

            # Load train and test data
            train_df = self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            logging.info("Train-Test data loaded")


            # Apply custom transformations in specified sequence
            train_df = self._rename_columns(train_df)
            train_df = self._drop_index_column(train_df)
            train_df = self._dropna_columns(train_df)
            train_df = self._preprocess_text(train_df)

            test_df = self._rename_columns(test_df)
            test_df = self._drop_index_column(test_df)
            test_df = self._dropna_columns(test_df)
            test_df = self._preprocess_text(test_df)
            logging.info("Custom transformations applied to train and test data")

            label_encoder = LabelEncoder()
            train_df["target"] = label_encoder.fit_transform(train_df["product"])
            test_df["target"] = label_encoder.transform(test_df["product"])

            save_object(self.data_transformation_config.label_encoder_file_path,label_encoder)
            save_csv_data(self.data_transformation_config.transformed_train_file_path, train_df)
            save_csv_data(self.data_transformation_config.transformed_test_file_path, test_df)
            logging.info("Saving transformation object and transformed files.")

            logging.info("Data transformation completed successfully")

            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.label_encoder_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

        except Exception as e:
            raise MyException(e, sys) from e