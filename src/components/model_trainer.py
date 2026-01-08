# from sklearn.feature_extraction.text import TfidfVectorizer

# tfidf = TfidfVectorizer(
#     max_features=5000,
#     ngram_range=(1,2)
# )

# X_train_tfidf = tfidf.fit_transform(train_df["complaint_text"])
# X_test_tfidf = tfidf.transform(test_df["complaint_text"])


# from sklearn.svm import LinearSVC

# svm = LinearSVC(class_weight="balanced")

# svm.fit(X_train_tfidf, train_labels)
# svm_preds = svm.predict(X_test_tfidf)

# print("Linear SVM")
# print(classification_report(test_labels, svm_preds))


import sys
import os
import json
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_object, load_csv_data
from src.entity.config_entity import ModelTrainerConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
# from src.entity.estimator import MyModel


class ModelTrainer:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact,
                 model_trainer_config: ModelTrainerConfig):
        """
        :param data_transformation_artifact: Output reference of data transformation artifact stage
        :param model_trainer_config: Configuration for model training
        """
        self.data_transformation_artifact = data_transformation_artifact
        self.model_trainer_config = model_trainer_config

    def load_data(self):
        train_df = load_csv_data(self.data_transformation_artifact.transformed_train_file_path)
        test_df = load_csv_data(self.data_transformation_artifact.transformed_test_file_path)
        X_train = train_df["complaint_text"].values
        X_test = test_df["complaint_text"].values
        Y_train = train_df["product"].values
        Y_test = test_df["product"].values
        return X_train, X_test, Y_train, Y_test

    def vectorize_text(self, X_train, X_test):
        vectorizer = TfidfVectorizer(max_features=5000,ngram_range=(1, 2))
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        save_object(self.model_trainer_config.tfidf_vectorizer_path,vectorizer)
        return X_train_vec, X_test_vec
    
    def train_model(self, X_train_vec, Y_train):
        models={"LogisticRegression":LogisticRegression(max_iter=1000,class_weight="balanced"),
                "LinearSVC":LinearSVC(class_weight="balanced")}
        trained_models={}
        for name, model in models.items():
            logging.info(f"Training model: {name}")
            model.fit(X_train_vec,Y_train)
            trained_models[name]=model       
        return trained_models
    
    def evaluate_models(self, trained_models, X_test_vec, Y_test):
        best_model_name=None
        best_f1_score=0.0
        model_reports={}
        for name, model in trained_models.items():
            logging.info(f"Evaluating model: {name}")
            Y_pred = model.predict(X_test_vec)
            macro_f1 = f1_score(Y_test, Y_pred, average='macro')
            report = classification_report(Y_test, Y_pred, output_dict=True)
            model_reports[name] = {"f1_score": macro_f1, "report": report}
            if macro_f1 > best_f1_score:
                best_f1_score = macro_f1
                best_model_name = name  
        return model_reports, best_model_name, best_f1_score
    
    def initiate_model_trainer(self) -> ModelTrainerArtifact:   
        try:
            logging.info("Loading transformed data for model training")
            X_train, X_test, Y_train, Y_test = self.load_data()

            logging.info("Vectorizing text data")
            X_train_vec, X_test_vec = self.vectorize_text(X_train, X_test)

            logging.info("Training models")
            trained_models = self.train_model(X_train_vec, Y_train)

            logging.info("Evaluating models")
            model_reports, best_model_name, best_f1_score = self.evaluate_models(trained_models, X_test_vec, Y_test)

            logging.info(f"Best model: {best_model_name} with F1 score: {best_f1_score}")

            if best_f1_score < self.model_trainer_config.model_expected_score:
                raise Exception("No model met the expected performance criteria.")

            best_model = trained_models[best_model_name]
            save_object(self.model_trainer_config.trained_model_file_path, best_model)

            with open(self.model_trainer_config.metric_file_path, 'w') as f:
                json.dump(model_reports, f, indent=4)

            classification_metric_artifact = {
                "f1_score": model_reports[best_model_name]["f1_score"]
            }

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                tfidf_vectorizer_path=self.model_trainer_config.tfidf_vectorizer_path,
                metric_artifact=classification_metric_artifact
            )

            logging.info("Model training completed successfully")

            return model_trainer_artifact

        except Exception as e:
            logging.error("Error occurred in initiate_model_trainer", exc_info=True)
            raise MyException(e, sys) from e