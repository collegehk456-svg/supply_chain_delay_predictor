"""
AI Chat Service
RAG-based conversational assistant for SmartShip AI using TF-IDF semantic search.
No external API keys required — fully local and production-ready.
"""

import re
import math
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


KNOWLEDGE_BASE = [
    {
        "id": "discount_delay",
        "topic": "discount delay relationship",
        "content": "Discount offered is the single most powerful predictor of shipment delays, accounting for 56.5% of model importance. Shipments with discounts above 25% are significantly more likely to be delayed. This is because high discounts drive promotional surges that overwhelm fulfillment capacity. Recommendation: reduce discount to below 20% for time-critical shipments.",
        "tags": ["discount", "delay", "prediction", "feature importance"]
    },
    {
        "id": "weight_delay",
        "topic": "weight and delay",
        "content": "Weight in grams is the second most important factor (log_weight at 9.7% importance). Packages above 3,000 grams have a higher delay probability due to special handling requirements, freight restrictions, and sorting complexity. Expedited or priority shipping is recommended for heavy packages.",
        "tags": ["weight", "delay", "heavy", "grams"]
    },
    {
        "id": "shipment_modes",
        "topic": "shipment mode comparison",
        "content": "The three shipment modes are Ship (sea freight), Flight (air freight), and Road (ground transport). Ship is the slowest but cheapest. Flight is fastest but most expensive. Road is medium speed and cost. Air freight significantly reduces delay risk for time-sensitive shipments. Sea freight has the highest delay probability due to weather and port congestion.",
        "tags": ["ship", "flight", "road", "mode", "transport"]
    },
    {
        "id": "model_accuracy",
        "topic": "model performance metrics",
        "content": "The SmartShip AI XGBoost model achieves 66.3% accuracy, 76.1% precision, 63.4% recall, 69.2% F1-score, and 0.746 ROC-AUC on the test set. The model was trained on 10,999 shipments with 22 engineered features. High precision means when it predicts a delay, it is usually correct. The model is production-ready with proper preprocessing and feature engineering pipelines.",
        "tags": ["accuracy", "precision", "recall", "f1", "roc-auc", "performance", "metrics"]
    },
    {
        "id": "prior_purchases",
        "topic": "prior purchases customer loyalty",
        "content": "Prior purchases (customer loyalty) accounts for 5.1% of prediction importance. New customers with fewer prior purchases tend to have higher delay rates due to address verification issues, unfamiliarity with packaging requirements, and higher exception rates. Verifying addresses and providing extra onboarding communication reduces delay risk for new customers.",
        "tags": ["prior purchases", "customer", "loyalty", "new customer"]
    },
    {
        "id": "customer_care",
        "topic": "customer care calls and delay",
        "content": "Customer care calls are an important indicator — high call volume (above 4 calls) often signals existing problems with the shipment. Proactive communication via SMS or email before delivery reduces the need for reactive calls and improves on-time delivery rates. The model captures this as the 'has_customer_calls' engineered feature.",
        "tags": ["customer care", "calls", "communication", "proactive"]
    },
    {
        "id": "warehouse_blocks",
        "topic": "warehouse block locations",
        "content": "Warehouse blocks A through F represent different storage zones. Blocks D, E, and F are more remote warehouse sections associated with slightly higher delay rates, potentially due to longer internal transport times. Routing from blocks A, B, and C generally yields faster dispatch times.",
        "tags": ["warehouse", "block", "location", "storage"]
    },
    {
        "id": "product_importance",
        "topic": "product importance levels",
        "content": "Product importance is classified as Low, Medium, or High. High importance products represent high-value items requiring priority handling. Despite their classification, product importance itself has relatively low predictive power compared to discount and weight — suggesting that fulfillment operations do not strongly differentiate handling by declared importance.",
        "tags": ["product importance", "priority", "high value"]
    },
    {
        "id": "cost_product",
        "topic": "product cost and delay",
        "content": "Cost of the product accounts for 4.6% of prediction importance. Higher-cost items do not inherently face more delays, but they do require more careful handling and insurance processing, which can add processing time. Items above $10,000 benefit from priority tracking and handling protocols.",
        "tags": ["cost", "product cost", "high value", "expensive"]
    },
    {
        "id": "feature_engineering",
        "topic": "feature engineering pipeline",
        "content": "The SmartShip AI pipeline engineers 22 features from the original 10 inputs. Key engineered features include: log_weight (log transform of weight), log_cost (log transform of cost), has_discount (binary flag for any discount), has_customer_calls (binary flag for any calls), weight_cost_ratio (weight divided by cost), and interaction terms between key features. These transformations capture non-linear relationships that raw features miss.",
        "tags": ["feature engineering", "pipeline", "log transform", "interaction"]
    },
    {
        "id": "xgboost_model",
        "topic": "XGBoost model architecture",
        "content": "SmartShip uses XGBoost (Extreme Gradient Boosting) as its core prediction engine. The model uses 100 trees, max depth 5, learning rate 0.05, subsample 0.8, and scale_pos_weight 1.2 to handle class imbalance. Training uses early stopping with validation set monitoring. XGBoost was chosen for its superior performance on tabular data, interpretability via feature importance, and production inference speed.",
        "tags": ["xgboost", "model", "gradient boosting", "algorithm", "trees"]
    },
    {
        "id": "how_to_predict",
        "topic": "how to make a prediction",
        "content": "To predict shipment delay: 1) Go to 'Single Prediction' in the sidebar. 2) Fill in all shipment details: warehouse block, shipment mode, customer care calls, customer rating, product cost, prior purchases, product importance, gender, discount offered, and weight. 3) Click 'Predict Delay'. The system returns delay probability, confidence score, top contributing factors, and actionable recommendations.",
        "tags": ["prediction", "how to", "single prediction", "guide"]
    },
    {
        "id": "batch_prediction",
        "topic": "batch prediction CSV upload",
        "content": "Batch prediction allows processing multiple shipments at once. Upload a CSV file with columns: warehouse_block, mode_of_shipment, customer_care_calls, customer_rating, cost_of_the_product, prior_purchases, product_importance, gender, discount_offered, weight_in_gms. The system processes all rows and returns delay predictions with probabilities. Results can be downloaded as CSV.",
        "tags": ["batch", "CSV", "upload", "multiple shipments"]
    },
    {
        "id": "delay_rate",
        "topic": "overall delay statistics",
        "content": "Based on the training dataset of 10,999 shipments, approximately 60% of shipments are delayed (not reaching on time) while 40% arrive on time. This high base delay rate underscores the importance of proactive delay prediction and intervention. The model helps identify which specific shipments are most at risk so teams can prioritize intervention resources.",
        "tags": ["delay rate", "statistics", "dataset", "60%"]
    },
    {
        "id": "reduce_delays",
        "topic": "how to reduce delays",
        "content": "Top strategies to reduce shipment delays: 1) Keep discounts below 20% during peak periods to avoid fulfillment surges. 2) Use air freight for packages above 3kg. 3) Send proactive delivery notifications to reduce customer care call volume. 4) Verify new customer addresses before dispatch. 5) Route from warehouse blocks A-C when possible. 6) Use priority handling for products over $10,000.",
        "tags": ["reduce delay", "strategies", "optimization", "tips"]
    },
    {
        "id": "api_endpoints",
        "topic": "API endpoints available",
        "content": "SmartShip AI exposes these REST API endpoints: POST /api/v1/predict (basic prediction), POST /api/v1/predict-with-explanation (prediction + SHAP explanation + recommendations), POST /api/v1/predict/batch (batch predictions), POST /api/v1/predict/smart (full prediction with business impact), GET /api/v1/analytics/summary (analytics overview), GET /health (system health check), POST /api/v1/chat (AI chat assistant).",
        "tags": ["API", "endpoints", "REST", "integration"]
    },
    {
        "id": "shap_explanation",
        "topic": "SHAP feature explanations",
        "content": "SmartShip uses SHAP (SHapley Additive exPlanations) to explain each prediction. SHAP values show exactly how much each feature contributed to pushing the prediction toward delayed or on-time. Features with positive SHAP values increase delay probability; negative values decrease it. The top 5 most impactful features are displayed for each prediction, giving logistics teams clear, actionable insights.",
        "tags": ["SHAP", "explanation", "interpretability", "feature importance", "explainability"]
    },
    {
        "id": "mlops_pipeline",
        "topic": "MLOps pipeline architecture",
        "content": "SmartShip's MLOps pipeline follows these stages: Data Ingestion → Data Validation → Preprocessing (scaling, encoding) → Feature Engineering (22 features) → Model Training (XGBoost with cross-validation) → Evaluation (accuracy, precision, recall, F1, ROC-AUC) → Model Registry (joblib serialization) → API Serving (FastAPI) → Frontend (Streamlit) → Monitoring. The complete pipeline is saved as a single pkl file for reproducible inference.",
        "tags": ["MLOps", "pipeline", "architecture", "stages"]
    },
    {
        "id": "customer_rating",
        "topic": "customer rating impact",
        "content": "Customer rating (1-5 scale) captures historical satisfaction. Lower ratings (below 3) are weakly correlated with higher delay rates, possibly because unsatisfied customers are more likely to report delays or have had previous problematic shipments. However, rating has relatively low direct predictive power compared to operational features like discount and weight.",
        "tags": ["customer rating", "satisfaction", "rating scale"]
    },
    {
        "id": "gender_impact",
        "topic": "gender feature in predictions",
        "content": "Gender (M/F) is included as a feature in the dataset but has very low predictive importance. The model has learned that gender is not a strong predictor of shipment delays. This is expected — shipment delays are driven by operational factors (weight, discount, mode) rather than demographic features.",
        "tags": ["gender", "demographics", "feature importance"]
    },
    {
        "id": "dashboard_overview",
        "topic": "dashboard overview and navigation",
        "content": "The SmartShip AI dashboard has 6 main sections: Home (KPIs and overview), Single Prediction (predict one shipment with full explanation), Batch Predictions (upload CSV for bulk processing), Feature Analysis (understand what drives delays), Analytics (historical trends from your predictions), and AI Assistant (chat with the AI about shipments and delays). Navigate using the sidebar on the left.",
        "tags": ["dashboard", "navigation", "sections", "overview"]
    }
]


class TFIDFSearchEngine:
    """Lightweight TF-IDF search engine — no external dependencies."""
    
    def __init__(self):
        self.documents = []
        self.vocabulary = {}
        self.idf = {}
        self.tfidf_matrix = []
        self._built = False
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\b[a-z][a-z0-9]*\b', text)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'shall', 'can',
                     'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                     'it', 'its', 'this', 'that', 'these', 'those', 'as', 'or',
                     'and', 'but', 'if', 'not', 'than', 'more', 'also', 'which'}
        return [t for t in tokens if t not in stopwords and len(t) > 2]
    
    def build(self, documents: List[Dict]):
        self.documents = documents
        all_texts = []
        for doc in documents:
            text = doc['content'] + ' ' + doc['topic'] + ' ' + ' '.join(doc.get('tags', []))
            all_texts.append(self._tokenize(text))
        
        doc_count = len(all_texts)
        df = {}
        for tokens in all_texts:
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1
        
        vocab = sorted(df.keys())
        self.vocabulary = {w: i for i, w in enumerate(vocab)}
        self.idf = {w: math.log((doc_count + 1) / (df[w] + 1)) + 1 for w in vocab}
        
        self.tfidf_matrix = []
        for tokens in all_texts:
            tf = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            total = max(len(tokens), 1)
            vec = {}
            for token, count in tf.items():
                if token in self.idf:
                    vec[token] = (count / total) * self.idf[token]
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.tfidf_matrix.append({k: v / norm for k, v in vec.items()})
        
        self._built = True
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[int, float]]:
        if not self._built:
            return []
        
        tokens = self._tokenize(query)
        if not tokens:
            return []
        
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        total = max(len(tokens), 1)
        
        query_vec = {}
        for token, count in tf.items():
            if token in self.idf:
                query_vec[token] = (count / total) * self.idf[token]
        norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0
        query_vec = {k: v / norm for k, v in query_vec.items()}
        
        scores = []
        for idx, doc_vec in enumerate(self.tfidf_matrix):
            score = sum(query_vec.get(t, 0) * doc_vec.get(t, 0) for t in query_vec)
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(idx, score) for idx, score in scores[:top_k] if score > 0.01]


class AIChatService:
    """Production-grade AI chat service with RAG capabilities."""
    
    def __init__(self):
        self.search_engine = TFIDFSearchEngine()
        self.search_engine.build(KNOWLEDGE_BASE)
        self.conversation_history: Dict[str, List[Dict]] = {}
        logger.info("AI Chat Service initialized with RAG knowledge base (%d documents)", len(KNOWLEDGE_BASE))
    
    def _get_context(self, query: str) -> List[Dict]:
        results = self.search_engine.search(query, top_k=3)
        return [KNOWLEDGE_BASE[idx] for idx, score in results]
    
    def _build_response(self, query: str, context_docs: List[Dict], session_id: str) -> str:
        query_lower = query.lower()
        history = self.conversation_history.get(session_id, [])
        
        if any(w in query_lower for w in ['hello', 'hi ', 'hey', 'good morning', 'good afternoon']):
            return (
                "Hello! I'm SmartShip AI Assistant — your intelligent logistics advisor. "
                "I can help you understand shipment delay predictions, explain model decisions, "
                "give optimization tips, and answer questions about supply chain operations. "
                "What would you like to know?"
            )
        
        if any(w in query_lower for w in ['thank', 'thanks', 'great', 'awesome', 'perfect']):
            return "You're welcome! Is there anything else you'd like to know about shipment delay predictions or supply chain optimization?"
        
        if not context_docs:
            return (
                "I specialize in supply chain delay prediction for SmartShip AI. "
                "I can answer questions about: delay factors, model performance, prediction features, "
                "optimization strategies, API usage, and operational recommendations. "
                "Could you rephrase your question with more specific details?"
            )
        
        primary = context_docs[0]
        additional = context_docs[1:] if len(context_docs) > 1 else []
        
        intro_phrases = [
            "Based on SmartShip's data and ML insights,",
            "According to the SmartShip AI analysis,",
            "From SmartShip's predictive intelligence,",
            "The SmartShip AI system indicates that",
        ]
        
        query_words = query_lower.split()
        phrase_idx = sum(ord(c) for c in query_lower[:10]) % len(intro_phrases)
        intro = intro_phrases[phrase_idx]
        
        response = f"{intro} {primary['content']}"
        
        if additional and len(query.split()) > 5:
            supplement = additional[0]['content']
            sentences = supplement.split('. ')
            if sentences:
                response += f"\n\nAdditionally, {sentences[0].lower()}."
        
        if any(w in query_lower for w in ['how', 'reduce', 'improve', 'optimize', 'fix', 'prevent']):
            response += (
                "\n\n**Quick Action Tips:**\n"
                "• Keep discounts under 20% during peak periods\n"
                "• Use air freight for packages over 3kg\n"
                "• Send proactive delivery notifications\n"
                "• Verify new customer addresses before dispatch"
            )
        
        if any(w in query_lower for w in ['predict', 'try', 'test', 'make']):
            response += "\n\n*Try the Single Prediction page to see this in action with your own shipment data.*"
        
        return response
    
    def chat(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Try multi-agent orchestrator first
        agent_info = None
        try:
            from backend.services.multi_agent_service import MultiAgentOrchestrator
            if not hasattr(self, '_orchestrator'):
                self._orchestrator = MultiAgentOrchestrator(self.search_engine)
            result = self._orchestrator.process(message, session_id, self.conversation_history[session_id])
            response_text = result["response"]
            context_docs  = [{"topic": s["topic"], "id": s["id"]} for s in result.get("sources", [])]
            agent_info    = result.get("agent")
            session_ctx   = result.get("session_context", {})
        except Exception:
            context_docs = self._get_context(message)
            response_text = self._build_response(message, context_docs, session_id)
            session_ctx = {}

        self.conversation_history[session_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if len(self.conversation_history[session_id]) > 20:
            self.conversation_history[session_id] = self.conversation_history[session_id][-20:]
        
        if context_docs and isinstance(context_docs[0], dict):
            sources_out = context_docs
        elif context_docs:
            sources_out = [{"topic": d["topic"], "id": d["id"]} for d in context_docs]
        else:
            sources_out = []

        return {
            "response": response_text,
            "sources": sources_out,
            "agent": agent_info,
            "session_id": session_id,
            "session_context": session_ctx,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_suggestions(self) -> List[str]:
        return [
            "What is the #1 cause of shipment delays?",
            "Give me an executive summary of the platform",
            "How can I reduce my delay rate by 30%?",
            "What anomalies should I watch for?",
            "Analyze the discount and delay relationship",
            "What are the top recommendations for operations?",
        ]
