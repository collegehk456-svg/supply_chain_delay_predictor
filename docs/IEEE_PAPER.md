# GenAI Logistics Intelligence Platform: Predictive Delay Analysis using Explainable ML and MLOps

## Abstract
In the modern e-commerce landscape, supply chain efficiency is critical to customer satisfaction and operational cost management. We propose *SmartShip AI*, an end-to-end MLOps platform that predicts shipment delays using Extreme Gradient Boosting (XGBoost). Beyond binary prediction, our architecture integrates SHapley Additive exPlanations (SHAP) and Large Language Models (LLMs) to provide Generative AI-driven natural language explanations and actionable operational recommendations. We implement a full MLOps lifecycle featuring automated drift detection, ensuring model robustness in production environments.

## 1. Objectives
1. **Predictive Accuracy:** Develop a robust ML pipeline to classify shipment delay risk with high precision.
2. **Explainability & Transparency:** Utilize SHAP to un-box model decisions and Gemini LLM to translate mathematical importance into human-readable logistics playbooks.
3. **Operational Impact:** Implement a Priority Scoring Engine that weighs delay probability against product cost and importance to compute net business risk.
4. **Production-Ready MLOps:** Ensure continuous learning through drift monitoring (Evidently AI) and experiment tracking (MLflow).

## 2. Methodology

### A. Data Processing & Feature Engineering
The model was trained on the Kaggle E-Commerce Shipping Dataset (10,999 records). We engineered 22 derived features, including log-transforms for heavy-tailed distributions (`Weight_in_gms`, `Cost_of_the_Product`) and interaction terms (e.g., `weight_cost_ratio`, `has_customer_calls`).

### B. Predictive Modeling
We utilized XGBoost for its superior performance on structured tabular data. Hyperparameters were tuned using cross-validation, achieving an ROC-AUC of 0.74, optimizing for precision to minimize false-positive escalations in logistics networks.

### C. Generative AI Explainability (GenAI)
To bridge the gap between data science and logistics management, we integrated the Google Gemini API. The system takes the XGBoost prediction, probability, and top 5 SHAP values as context prompts to generate dynamic, situation-specific operational recommendations.

### D. System Architecture
- **Frontend:** Streamlit with custom CSS (glassmorphism UI) for real-time executive monitoring.
- **Backend:** FastAPI for asynchronous, high-throughput model inference.
- **MLOps:** Containerized environments using Docker, DVC for dataset versioning, and Evidently AI for production data drift monitoring.

## 3. Results & Business Impact
Our analysis indicates that `Discount_offered` is the dominant feature driving delays (56.5% importance), revealing that high promotional periods cause significant warehouse bottlenecks. By identifying high-risk shipments prior to dispatch, companies can intelligently reroute packages (e.g., from Ship to Flight) or notify customers proactively, significantly improving SLA compliance and reducing support call overhead.

## 4. Future Scope
Future iterations will incorporate real-time external covariates, such as OpenWeather API integration and geopolitical risk scoring, to further enhance the anomaly detection engine. Furthermore, autonomous agentic frameworks will be developed to execute rerouting actions automatically via carrier APIs.

## 5. Conclusion
SmartShip AI demonstrates that the true value of machine learning in logistics is not merely prediction, but actionable explainability. By combining XGBoost, MLOps best practices, and Generative AI, we provide a scalable, production-ready blueprint for the future of intelligent supply chains.
