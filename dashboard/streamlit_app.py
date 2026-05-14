
import streamlit as st
import pandas as pd
import joblib

st.title("🚚 SmartShip AI Dashboard")

model = joblib.load("models/model.pkl")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    st.write("Dataset Preview")
    st.dataframe(df.head())

    if st.button("Predict"):
        preds = model.predict(df)
        df["Prediction"] = preds
        st.success("Prediction Completed")
        st.dataframe(df.head())

        st.download_button(
            "Download Results",
            df.to_csv(index=False),
            file_name="predictions.csv"
        )
