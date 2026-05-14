
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

class DataTransformation:

    def transform_data(self, path):
        df = pd.read_csv(path)

        X = df.drop(columns=["Reached.on.Time_Y.N"])
        y = df["Reached.on.Time_Y.N"]

        categorical = [
            "Warehouse_block",
            "Mode_of_Shipment",
            "Product_importance",
            "Gender"
        ]

        numerical = [col for col in X.columns if col not in categorical]

        preprocessor = ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", StandardScaler(), numerical)
        ])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        return X_train, X_test, y_train, y_test, preprocessor
