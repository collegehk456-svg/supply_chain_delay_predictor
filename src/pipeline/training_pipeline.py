
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

class TrainingPipeline:

    def run_pipeline(self):

        ingestion = DataIngestion()
        path = ingestion.ingest_data()

        transformation = DataTransformation()

        X_train, X_test, y_train, y_test, preprocessor = (
            transformation.transform_data(path)
        )

        trainer = ModelTrainer()

        trainer.train_model(
            X_train,
            X_test,
            y_train,
            y_test,
            preprocessor
        )
