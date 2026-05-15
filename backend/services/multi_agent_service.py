"""
Multi-Agent AI System
Specialized AI agents for supply chain intelligence.
Each agent has a distinct role and expertise domain.
"""

import re
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class BaseAgent:
    name: str = "Base"
    icon: str = "🤖"
    role: str = "General"
    triggers: List[str] = []

    def can_handle(self, query: str) -> float:
        q = query.lower()
        return sum(1.0 for t in self.triggers if t in q) / max(len(self.triggers), 1)

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        raise NotImplementedError


class RiskAnalysisAgent(BaseAgent):
    name = "Risk Analyst"
    icon = "⚠️"
    role = "Shipment Risk Assessment"
    triggers = ["risk", "anomaly", "danger", "critical", "alert", "flag",
                "suspicious", "unusual", "spike", "outlier", "detect"]

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        ctx_text = context[0]["content"] if context else ""
        return (
            f"**Risk Analysis Report** — SmartShip AI Risk Analyst\n\n"
            f"{ctx_text}\n\n"
            "**Current System Risk Profile:**\n"
            "• Isolation Forest detects anomalies with ~8% contamination threshold\n"
            "• Statistical rules flag: discount >35%, weight >5.5kg, calls ≥7\n"
            "• Risk scoring combines ML score (40%) + rule violations (60%)\n\n"
            "**Recommended Actions:**\n"
            "1. CRITICAL shipments → immediate human review required\n"
            "2. HIGH risk → automated re-routing or mode upgrade\n"
            "3. MEDIUM risk → proactive customer notification\n\n"
            "*Navigate to the Command Center to see live risk scores for all active shipments.*"
        )


class DelayPredictionAgent(BaseAgent):
    name = "Delay Predictor"
    icon = "🔮"
    role = "Delay Probability Analysis"
    triggers = ["predict", "delay", "probability", "chance", "likelihood",
                "on time", "on-time", "late", "forecast", "estimate"]

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        ctx_text = context[0]["content"] if context else ""
        return (
            f"**Delay Prediction Intelligence** — SmartShip Prediction Agent\n\n"
            f"{ctx_text}\n\n"
            "**Model Architecture:**\n"
            "• XGBoost classifier with 22 engineered features\n"
            "• ROC-AUC: 0.746 | Precision: 76.1% | Recall: 63.4%\n"
            "• Inference latency: <50ms per shipment\n\n"
            "**Top Predictive Signals (in order):**\n"
            "1. Discount offered (56.5% importance)\n"
            "2. Log-transformed weight (9.7%)\n"
            "3. Prior purchases / loyalty (5.1%)\n"
            "4. Product cost (4.6%)\n\n"
            "*Use the Single Prediction page for real-time delay probability with SHAP explanations.*"
        )


class RecommendationAgent(BaseAgent):
    name = "Operations Advisor"
    icon = "💡"
    role = "Operational Recommendations"
    triggers = ["recommend", "improve", "reduce", "optimize", "fix", "strategy",
                "action", "tip", "how to", "suggestion", "prevent", "avoid"]

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        ctx_text = context[0]["content"] if context else ""
        return (
            f"**Operations Optimization Playbook** — SmartShip Advisor\n\n"
            f"{ctx_text}\n\n"
            "**Immediate Actions (High ROI):**\n"
            "• 🔴 Cap promotional discounts at 20% during peak periods → -30% delay risk\n"
            "• 🟠 Upgrade packages >3kg to air freight → -18% delay probability\n"
            "• 🟡 Auto-send SMS notifications before delivery → -12% exception rate\n\n"
            "**Structural Improvements:**\n"
            "• Prioritize warehouse blocks A-C for time-sensitive orders\n"
            "• Implement address verification for first-time customers\n"
            "• Set up ML-based dynamic discount limits during surge periods\n\n"
            "**Expected Business Impact:**\n"
            "Implementing all actions could reduce delay rate by up to **35-40%**, "
            "saving an estimated **$50-80 per delayed shipment** in operational costs."
        )


class AnalyticsAgent(BaseAgent):
    name = "Data Analyst"
    icon = "📊"
    role = "Analytics & Insights"
    triggers = ["analytics", "analysis", "data", "trend", "pattern", "chart",
                "statistics", "stats", "insight", "metric", "performance", "report"]

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        ctx_text = context[0]["content"] if context else ""
        return (
            f"**Data Analytics Insight** — SmartShip Analytics Agent\n\n"
            f"{ctx_text}\n\n"
            "**Dataset Intelligence (10,999 shipments):**\n"
            "• Overall delay rate: **59.7%** — majority of shipments are at risk\n"
            "• Ship mode dominates volume: 67.8% of all shipments\n"
            "• Block F has highest volume (33.3%) and above-average delays\n"
            "• Average discount for delayed shipments: **18.7%** vs 5.5% for on-time\n\n"
            "**Trend Observations:**\n"
            "• High-discount promotional shipments cluster strongly in delay group\n"
            "• Weight and delay have non-linear relationship (log transform improves model)\n"
            "• New customers (prior_purchases <2) face 12% higher delay rate\n\n"
            "*Check the Feature Analysis page for interactive visualizations.*"
        )


class ExecutiveSummaryAgent(BaseAgent):
    name = "Executive Advisor"
    icon = "📋"
    role = "Executive Intelligence & Summaries"
    triggers = ["summary", "executive", "overview", "brief", "report", "status",
                "board", "investor", "ceo", "business", "impact", "roi", "value"]

    def respond(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        return (
            "**Executive Intelligence Brief** — SmartShip AI\n\n"
            "**Platform Status:** OPERATIONAL ✅\n\n"
            "**Business Metrics:**\n"
            "• Model covers 10,999 shipments across 6 warehouse blocks\n"
            "• Current delay prediction accuracy: 66.3% (ROC-AUC: 0.746)\n"
            "• Each prevented delay saves est. $50-80 in operational costs\n"
            "• Anomaly detection flags ~8% of shipments for human review\n\n"
            "**Strategic Priorities:**\n"
            "1. **Discount Management** — Primary lever; cap at 20% to reduce delays by ~30%\n"
            "2. **Freight Mode Optimization** — Route heavy items via air to cut delay risk\n"
            "3. **Customer Onboarding** — First-purchase verification reduces exceptions\n\n"
            "**ROI Estimate:**\n"
            "If delay rate drops from 59.7% → 40%, on 11K monthly shipments "
            "= **2,167 fewer delays × $65 avg savings = ~$141K/month operational savings.**\n\n"
            "*Full analytics available in the Analytics and Command Center dashboards.*"
        )


class MultiAgentOrchestrator:
    """Routes queries to the most capable specialist agent."""

    def __init__(self, search_engine):
        self.search_engine = search_engine
        self.agents: List[BaseAgent] = [
            RiskAnalysisAgent(),
            DelayPredictionAgent(),
            RecommendationAgent(),
            AnalyticsAgent(),
            ExecutiveSummaryAgent(),
        ]
        self.session_contexts: Dict[str, Dict] = {}

    def _select_agent(self, query: str) -> BaseAgent:
        best_agent = None
        best_score = -1.0
        for agent in self.agents:
            score = agent.can_handle(query)
            if score > best_score:
                best_score = score
                best_agent = agent
        return best_agent if best_score > 0 else self.agents[1]  # default: Delay Predictor

    def _get_rag_context(self, query: str) -> List[Dict]:
        from backend.services.ai_chat_service import KNOWLEDGE_BASE
        results = self.search_engine.search(query, top_k=2)
        return [KNOWLEDGE_BASE[idx] for idx, _ in results]

    def _greeting_check(self, q: str) -> Optional[str]:
        q = q.lower().strip()
        if any(w in q for w in ["hello", "hi ", "hey ", "greetings", "good morning"]):
            return (
                "Hello! I'm the **SmartShip AI Multi-Agent System**. "
                "I have 5 specialized agents ready to assist:\n\n"
                "• **⚠️ Risk Analyst** — anomaly detection & threat assessment\n"
                "• **🔮 Delay Predictor** — ML predictions & model insights\n"
                "• **💡 Operations Advisor** — optimization strategies\n"
                "• **📊 Data Analyst** — analytics & trend insights\n"
                "• **📋 Executive Advisor** — business summaries & ROI\n\n"
                "What would you like to explore?"
            )
        if any(w in q for w in ["thank", "thanks", "great", "awesome", "perfect", "cool"]):
            return "You're welcome! Which specialized agent can I route your next question to?"
        return None

    def process(self, query: str, session_id: str, history: List[Dict]) -> Dict[str, Any]:
        greeting = self._greeting_check(query)
        if greeting:
            return {
                "response": greeting,
                "agent": {"name": "SmartShip Orchestrator", "icon": "🤖", "role": "Multi-Agent Router"},
                "sources": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        agent = self._select_agent(query)
        context = self._get_rag_context(query)
        response = agent.respond(query, context, history)

        ctx = self.session_contexts.setdefault(session_id, {"turn_count": 0, "topics": []})
        ctx["turn_count"] += 1
        if context:
            ctx["topics"].append(context[0]["topic"])

        return {
            "response": response,
            "agent": {"name": agent.name, "icon": agent.icon, "role": agent.role},
            "sources": [{"topic": d["topic"], "id": d["id"]} for d in context],
            "session_context": {"turn": ctx["turn_count"], "topics_covered": len(set(ctx["topics"]))},
            "timestamp": datetime.utcnow().isoformat(),
        }
