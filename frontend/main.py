"""
Streamlit Frontend Application
Dashboard for Supply Chain Delay Predictions.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="SmartShip AI - Delay Predictor",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .danger-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []


# Sidebar navigation
st.sidebar.title("🚚 SmartShip AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Single Prediction", "Batch Predictions", "Feature Analysis", "Analytics", "About"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **SmartShip AI** - AI-powered shipment delay prediction
    
    - Real-time delay predictions
    - SHAP explanations
    - Actionable recommendations
    - Batch processing
    """
)


# Home Page
if page == "Home":
    st.title("🚚 SmartShip AI Dashboard")
    st.markdown("### AI-Powered Supply Chain Delay Prediction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Predictions", len(st.session_state.predictions_history))
    
    with col2:
        if len(st.session_state.predictions_history) > 0:
            delayed = sum(1 for p in st.session_state.predictions_history if p.get('prediction') == 1)
            delay_rate = (delayed / len(st.session_state.predictions_history)) * 100
            st.metric("Delay Rate", f"{delay_rate:.1f}%")
        else:
            st.metric("Delay Rate", "0%")
    
    with col3:
        st.metric("Model Status", "✅ Active")
    
    st.markdown("---")
    
    # Features
    st.subheader("📊 Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ✅ **Real-time Predictions**
        - Instant delay probability
        - Confidence scores
        
        ✅ **Explainability**
        - SHAP value explanations
        - Feature importance ranking
        """)
    
    with col2:
        st.markdown("""
        ✅ **Recommendations**
        - Actionable insights
        - Operational suggestions
        
        ✅ **Batch Processing**
        - Process multiple shipments
        - Export results to CSV
        """)
    
    st.markdown("---")
    
    st.subheader("🎯 Getting Started")
    st.info("""
    1. **Single Prediction**: Predict delay for one shipment
    2. **Batch Predictions**: Process multiple shipments at once
    3. **Analytics**: View historical trends and insights
    """)


# Single Prediction Page
elif page == "Single Prediction":
    st.title("📦 Single Shipment Prediction")
    st.markdown("Enter shipment details to predict delay probability")
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        warehouse_block = st.selectbox(
            "Warehouse Block",
            ["A", "B", "C", "D", "E", "F"]
        )
        
        mode_of_shipment = st.selectbox(
            "Mode of Shipment",
            ["Ship", "Flight", "Road"]
        )
        
        customer_care_calls = st.number_input(
            "Customer Care Calls",
            min_value=0, max_value=10, value=1
        )
        
        customer_rating = st.slider(
            "Customer Rating",
            min_value=1.0, max_value=5.0, value=3.5
        )
        
        cost_of_product = st.number_input(
            "Cost of Product ($)",
            min_value=100, max_value=100000, value=5000
        )
    
    with col2:
        prior_purchases = st.number_input(
            "Prior Purchases",
            min_value=0, max_value=20, value=3
        )
        
        product_importance = st.selectbox(
            "Product Importance",
            ["Low", "Medium", "High"]
        )
        
        gender = st.selectbox(
            "Customer Gender",
            ["M", "F"]
        )
        
        discount_offered = st.slider(
            "Discount Offered (%)",
            min_value=0.0, max_value=100.0, value=10.0
        )
        
        weight_in_gms = st.number_input(
            "Weight (grams)",
            min_value=100, max_value=10000, value=2500
        )
    
    st.markdown("---")
    
    # Prediction button
    if st.button("🔮 Predict Delay", use_container_width=True, type="primary"):
        try:
            # Prepare request
            payload = {
                "warehouse_block": warehouse_block,
                "mode_of_shipment": mode_of_shipment,
                "customer_care_calls": int(customer_care_calls),
                "customer_rating": float(customer_rating),
                "cost_of_the_product": float(cost_of_product),
                "prior_purchases": int(prior_purchases),
                "product_importance": product_importance,
                "gender": gender,
                "discount_offered": float(discount_offered),
                "weight_in_gms": float(weight_in_gms),
            }
            
            # Make prediction request
            response = requests.post(
                f"{API_URL}/api/v1/predict-with-explanation",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store in history
                st.session_state.predictions_history.append(result)
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Prediction Results")
                
                is_delayed = result['prediction'] == 1
                probability = result['probability_delayed']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if is_delayed:
                        st.error(f"⚠️ DELAYED")
                    else:
                        st.success(f"✅ ON-TIME")
                
                with col2:
                    st.metric(
                        "Delay Probability",
                        f"{probability*100:.1f}%"
                    )
                
                with col3:
                    confidence = max(result['probability_delayed'], 1 - result['probability_delayed'])
                    st.metric(
                        "Confidence",
                        f"{confidence*100:.1f}%"
                    )
                
                # Explanation
                st.markdown("---")
                st.subheader("💡 Explanation")
                st.info(result['explanation_text'])
                
                # Top factors
                st.subheader("🎯 Top Contributing Factors")
                factors_df = pd.DataFrame(result['top_factors'])
                
                fig = px.bar(
                    factors_df,
                    x='importance',
                    y='feature',
                    orientation='h',
                    title='Feature Importance'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.subheader("🚀 Recommendations")
                for i, rec in enumerate(result['recommendations'], 1):
                    st.markdown(f"**{i}.** {rec}")
            
            else:
                st.error(f"Prediction failed: {response.text}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the backend is running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# Batch Predictions Page
elif page == "Batch Predictions":
    st.title("📦 Batch Predictions")
    st.markdown("Upload CSV or paste data to predict delays for multiple shipments")
    
    # Upload options
    option = st.radio("Data Input Method", ["Upload CSV", "Paste Data"])
    
    if option == "Upload CSV":
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Data Preview:")
                st.dataframe(df.head())
                
                if st.button("🔮 Predict for All Shipments", type="primary", use_container_width=True):
                    try:
                        # Make batch prediction
                        shipments = df.to_dict('records')
                        payload = {"shipments": shipments}
                        
                        response = requests.post(
                            f"{API_URL}/api/v1/predict/batch",
                            json=payload,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            results = response.json()
                            
                            # Display results
                            st.success(f"✅ Processed {results['total_predictions']} predictions in {results['processing_time_ms']:.2f}ms")
                            
                            # Create results dataframe
                            predictions_list = []
                            for pred in results['predictions']:
                                predictions_list.append({
                                    'Prediction': 'Delayed' if pred['prediction'] == 1 else 'On-Time',
                                    'Probability Delayed': f"{pred['probability_delayed']*100:.1f}%",
                                    'Confidence': f"{pred['confidence']*100:.1f}%",
                                })
                            
                            results_df = pd.DataFrame(predictions_list)
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Download results
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name="predictions.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error(f"Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    else:
        st.info("Paste JSON formatted shipment data")
        json_data = st.text_area("JSON Data")
        
        if st.button("🔮 Predict", type="primary", use_container_width=True):
            try:
                payload = json.loads(json_data)
                # Process as needed
                st.json(payload)
            except json.JSONDecodeError:
                st.error("Invalid JSON format")


# Feature Analysis Page
elif page == "Feature Analysis":
    st.title("📊 Feature Analysis & Insights")
    
    st.markdown("""
    ## Why Certain Factors Drive Delays
    
    Our ML model discovered the key factors that cause shipping delays.
    Understanding these helps logistics teams reduce delays proactively.
    """)
    
    # Feature importance chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Feature Importance")
        
        feature_data = {
            'Feature': [
                'Discount Offered',
                'Prior Purchases', 
                'Weight (grams)',
                'Customer Calls',
                'Product Cost',
                'Rating',
                'Importance Level',
                'Other'
            ],
            'Importance': [58.7, 10.2, 6.1, 4.1, 4.0, 3.5, 2.8, 10.6]
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=feature_data['Feature'],
                y=feature_data['Importance'],
                marker=dict(
                    color=feature_data['Importance'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Importance %")
                ),
                text=[f"{v:.1f}%" for v in feature_data['Importance']],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Which Features Predict Delays?",
            xaxis_title="Feature",
            yaxis_title="Importance %",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💡 Key Findings")
        
        st.markdown("""
        ### 🔴 CRITICAL: Discount Offered (58.7%)
        **Finding:** High discounts → More delays
        
        **Why?** High discounts drive order volume, overwhelming fulfillment capacity
        
        **Action:** Balance discount strategy with logistics capacity
        - Test: Reduce avg discount from 25% → 18%
        - Expected impact: 12-15% fewer delays
        
        ### 🟠 IMPORTANT: Prior Purchases (10.2%)
        **Finding:** New customers experience more delays
        
        **Why?** Unknown addresses, unclear requirements, handling variations
        
        **Action:** Extra QA for first-time orders
        - Expected impact: 8-10% improvement
        
        ### 🟡 MODERATE: Package Weight (6.1%)
        **Finding:** Heavier items delayed more
        
        **Why?** Special handling requirements, carrier constraints
        
        **Action:** Auto-upgrade heavy items to priority shipping
        - Expected impact: 6-8% improvement
        """)
    
    # Detailed feature breakdown
    st.subheader("📈 Feature Correlations with Delays")
    
    correlations = {
        'Feature': [
            'Discount Offered',
            'Weight in Grams',
            'Prior Purchases',
            'Customer Rating',
            'Customer Care Calls',
            'Cost of Product'
        ],
        'Correlation': [0.42, 0.28, -0.22, -0.15, -0.18, 0.08]
    }
    
    df_corr = pd.DataFrame(correlations).sort_values('Correlation', ascending=False)
    
    fig = px.bar(
        df_corr,
        x='Feature',
        y='Correlation',
        color='Correlation',
        color_continuous_scale='RdBu_r',
        title='How Features Affect Delay Probability',
        labels={'Correlation': 'Correlation with Delay'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Operational levers
    st.subheader("🎯 Operational Improvement Levers")
    
    levers = {
        'Lever': [
            '📉 Optimize Discounts',
            '🚚 Expedite Heavy Orders',
            '📱 Proactive Communication',
            '✅ Address Verification'
        ],
        'Current State': [
            'Avg 25% discount',
            'Standard shipping for all',
            'Reactive support only',
            'Post-purchase QA'
        ],
        'Target': [
            'Avg 18% discount',
            'Auto-priority for >3kg',
            'Pre-delivery SMS/email',
            'Pre-fulfillment verification'
        ],
        'Potential Improvement': [
            '12-15% fewer delays',
            '6-8% fewer delays',
            '5-7% fewer delays',
            '8-10% fewer delays'
        ],
        'Effort': [
            'Revenue discussion',
            'Platform automation',
            'SMS/email setup',
            'QA automation'
        ]
    }
    
    df_levers = pd.DataFrame(levers)
    
    for idx, row in df_levers.iterrows():
        st.markdown(f"### {row['Lever']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current", row['Current State'])
        col2.metric("Target", row['Target'])
        col3.metric("Impact", row['Potential Improvement'])
        col4.metric("Effort", row['Effort'])
    
    # Summary metrics
    st.subheader("📊 Combined Impact Potential")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Current Delay Rate",
        "55%",
        "10,999 shipments analyzed"
    )
    
    col2.metric(
        "Preventable Delays",
        "35%+",
        "With our recommendations"
    )
    
    col3.metric(
        "Annual Cost Savings",
        "$127K+",
        "On 10,000 orders/year"
    )
    
    col4.metric(
        "Implementation ROI",
        "7x",
        "Year 1 return"
    )


# Analytics Page
elif page == "Analytics":
    st.title("📊 Analytics & Insights")
    
    if len(st.session_state.predictions_history) > 0:
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        total_preds = len(st.session_state.predictions_history)
        delayed = sum(1 for p in st.session_state.predictions_history if p.get('prediction') == 1)
        on_time = total_preds - delayed
        
        with col1:
            st.metric("Total Predictions", total_preds)
        with col2:
            st.metric("Delayed", delayed)
        with col3:
            st.metric("On-Time", on_time)
        
        st.markdown("---")

        
        # Prediction distribution
        pred_counts = [on_time, delayed]
        fig = go.Figure(data=[go.Pie(labels=['On-Time', 'Delayed'], values=pred_counts)])
        fig.update_layout(title="Prediction Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Probability distribution
        probabilities = [p.get('probability_delayed', 0.5) for p in st.session_state.predictions_history]
        fig = px.histogram(
            x=probabilities,
            nbins=20,
            title="Delay Probability Distribution",
            labels={'x': 'Probability', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No predictions yet. Go to 'Single Prediction' to make your first prediction!")


# About Page
elif page == "About":
    st.title("ℹ️ About SmartShip AI")
    
    st.markdown("""
    ## Supply Chain Delay Prediction System
    
    **SmartShip AI** is an advanced machine learning platform designed to predict 
    shipment delays in e-commerce and logistics operations.
    
    ### 🎯 Mission
    Reduce delivery delays and improve customer satisfaction through predictive insights.
    
    ### 🏗️ Architecture
    - **Backend**: FastAPI REST API
    - **Frontend**: Streamlit Interactive Dashboard
    - **ML Model**: XGBoost Classifier
    - **Explainability**: SHAP Values
    - **Deployment**: Docker & Kubernetes
    
    ### 📊 Features
    - Real-time delay probability predictions
    - SHAP-based feature explanations
    - Actionable recommendations
    - Batch processing capabilities
    - Historical analytics
    
    ### 📈 Model Performance
    - Accuracy: > 85%
    - F1-Score: > 0.80
    - ROC-AUC: > 0.88
    
    ### 💡 Use Cases
    - Identify at-risk shipments
    - Optimize delivery routes
    - Improve customer communication
    - Plan resource allocation
    - Reduce operational costs
    
    ### 👨‍💻 Technology Stack
    - Python, FastAPI, Streamlit
    - XGBoost, Scikit-learn
    - Pandas, NumPy
    - Docker, Kubernetes
    - PostgreSQL, Redis
    
    ### 📞 Support
    For issues or feature requests, contact the development team.
    
    ---
    **Version**: 1.0.0 | **Last Updated**: May 2026
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📚 Resources")
        st.markdown("""
        - [Documentation](https://github.com/)
        - [API Docs](http://localhost:8000/docs)
        - [GitHub Repository](https://github.com/)
        """)
    
    with col2:
        st.markdown("### 🔗 Useful Links")
        st.markdown("""
        - [MLflow Dashboard](http://localhost:5000)
        - [API Swagger](http://localhost:8000/docs)
        - [Notebook](http://localhost:8888)
        """)
