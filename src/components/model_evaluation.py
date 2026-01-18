from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact
from sklearn.metrics import f1_score
from src.exception import MyException
from src.constants import SCHEMA_FILE_PATH, TARGET_COLUMN, TEXT_COLUMN
from src.logger import logging
from src.utils.main_utils import load_object
import sys
import pandas as pd
from typing import Optional
from src.entity.s3_estimator import Proj1Estimator
from dataclasses import dataclass
from nltk.corpus import stopwords
import re
from src.utils.main_utils import save_object, read_yaml_file, save_csv_data
from sklearn.preprocessing import LabelEncoder
from src.entity.config_entity import DataTransformationConfig, ModelTrainerConfig

@dataclass
class EvaluateModelResponse:
    trained_model_f1_score: float
    best_model_f1_score: float
    is_model_accepted: bool
    difference: float


class ModelEvaluation:

    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            self.model_eval_config = model_eval_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise MyException(e, sys) from e

    def get_best_model(self) -> Optional[Proj1Estimator]:
        """
        Method Name :   get_best_model
        Description :   This function is used to get model from production stage.
        
        Output      :   Returns model object if available in s3 storage
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            bucket_name = self.model_eval_config.bucket_name
            model_path=self.model_eval_config.s3_model_key_path
            proj1_estimator = Proj1Estimator(bucket_name=bucket_name,
                                               model_path=model_path)

            if proj1_estimator.is_model_present(model_path=model_path):
                return proj1_estimator
            return None
        except Exception as e:
            raise  MyException(e,sys)
        
    def _rename_columns(self, df):
        logging.info("Renaming specific columns")
        df = df.rename(columns={
            "narrative": "complaint_text"
        })
        return df

    def _drop_index_column(self, df):
        self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
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
    

    def evaluate_model(self) -> EvaluateModelResponse:
        """
        Method Name :   evaluate_model
        Description :   This function is used to evaluate trained model 
                        with production model and choose best model 
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            # x = test_df.drop(TARGET_COLUMN, axis=1)
            # y = test_df[TARGET_COLUMN]

            logging.info("Test data loaded and now transforming it for prediction...")

            test_df = self._rename_columns(test_df)
            test_df = self._drop_index_column(test_df)
            test_df = self._dropna_columns(test_df)
            test_df = self._preprocess_text(test_df)

            label_encoder = load_object(file_path=DataTransformationConfig.transformed_object_file_path)
            test_df[TARGET_COLUMN] = label_encoder.transform(test_df[TARGET_COLUMN])
            
            trained_vectorizer = load_object(file_path=self.model_trainer_artifact.tfidf_vectorizer_path)
            # test_df[TEXT_COLUMN] = trained_vectorizer.transform(test_df[TEXT_COLUMN])
            
            # test_df = pd.DataFrame(X_test_vectorized.toarray(), columns=trained_vectorizer.get_feature_names_out())
            
            # y = test_df[TARGET_COLUMN]
            # x = test_df.drop(TARGET_COLUMN, axis=1)
            
            x = trained_vectorizer.transform(test_df[TEXT_COLUMN])
            y = test_df[TARGET_COLUMN]

            
            logging.info("Test data transformed.")
            
             # load trained model
            logging.info("Loading trained model for evaluation.")
            trained_model = load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
            logging.info("Trained model loaded/exists.")
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact["f1_score"]
            logging.info(f"F1_Score for this model: {trained_model_f1_score}")

            best_model_f1_score=None
            best_model = self.get_best_model()
            if best_model is not None:
                logging.info(f"Computing F1_Score for production model..")
                y_hat_best_model = best_model.predict(x)
                # convert string labels → numeric labels
                y_hat_best_model = label_encoder.transform(y_hat_best_model)
                best_model_f1_score = f1_score(y, y_hat_best_model)
                logging.info(f"F1_Score-Production Model: {best_model_f1_score}, F1_Score-New Trained Model: {trained_model_f1_score}")
            
            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score
            result = EvaluateModelResponse(trained_model_f1_score=trained_model_f1_score,
                                           best_model_f1_score=best_model_f1_score,
                                           is_model_accepted=trained_model_f1_score > tmp_best_model_score,
                                           difference=trained_model_f1_score - tmp_best_model_score
                                           )
            logging.info(f"Result: {result}")
            return result

        except Exception as e:
            raise MyException(e, sys)

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Method Name :   initiate_model_evaluation
        Description :   This function is used to initiate all steps of the model evaluation
        
        Output      :   Returns model evaluation artifact
        On Failure  :   Write an exception log and then raise an exception
        """  
        try:
            print("------------------------------------------------------------------------------------------------")
            logging.info("Initialized Model Evaluation Component.")
            evaluate_model_response = self.evaluate_model()
            s3_model_path = self.model_eval_config.s3_model_key_path

            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=evaluate_model_response.is_model_accepted,
                s3_model_path=s3_model_path,
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy=evaluate_model_response.difference)

            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact
        except Exception as e:
            raise MyException(e, sys) from e