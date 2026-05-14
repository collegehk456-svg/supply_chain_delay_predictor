
import os
import joblib
import mlflow

from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

class ModelTrainer:

    def train_model(
        self,
        X_train,
        X_test,
        y_train,
        y_test,
        preprocessor
    ):

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", XGBClassifier())
        ])

        mlflow.set_experiment("smartship_ai")

        with mlflow.start_run():

            pipeline.fit(X_train, y_train)

            preds = pipeline.predict(X_test)

            accuracy = accuracy_score(y_test, preds)

            mlflow.log_metric("accuracy", accuracy)

            os.makedirs("models", exist_ok=True)

            joblib.dump(pipeline, "models/model.pkl")

            print(f"Accuracy: {accuracy}")
