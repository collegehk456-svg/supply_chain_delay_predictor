# SmartShip AI Platform Demo Script (3 Minutes)

**[0:00 - 0:30] Introduction & The Problem**
"Hello Judges! We are presenting SmartShip AI, a GenAI Logistics Intelligence Platform. In e-commerce, 60% of shipments face some form of delay, costing millions in SLA penalties. Current systems might flag a delay, but they don't tell warehouse managers *why* or *how to fix it*. Today, we're changing that."

**[0:30 - 1:15] Single Prediction & GenAI**
*(Navigate to Single Prediction tab)*
"Let's look at a live example. We have a high-value $5000 package weighing 3kg, currently routed via Sea Freight with a high promotional discount. I click 'Predict'.
Immediately, our FastAPI backend and XGBoost model process the data. But look at the output: Not only do we see an 82% delay probability, but our Generative AI engine (powered by Gemini) explains exactly why. It tells the manager: 'High discount suggests promotional volume, and sea freight is too slow for this weight class.' It then recommends: 'Upgrade to Air Freight to prevent an SLA breach.'"

**[1:15 - 2:00] Executive Dashboard & Analytics**
*(Navigate to Home / Executive Dashboard)*
"But managers need to see the big picture. Here on our Executive Dashboard, you see our Start-up level glassmorphism UI. We monitor real-time Anomaly Rates and Model Drift. Our system continuously calculates the Net Business Impact in USD, prioritizing queues not just by delay risk, but by the financial cost of failure."

**[2:00 - 2:45] AI Chat Assistant & MLOps**
*(Navigate to AI Assistant)*
"If a logistics planner has questions, they can use our built-in AI Assistant. It uses RAG to query our entire knowledge base of supply chain rules. Behind the scenes, this is a fully production-ready MLOps pipeline. We track experiments with MLflow, version data with DVC, and use Evidently AI to trigger automated retraining when data drift occurs."

**[2:45 - 3:00] Conclusion**
"In summary, SmartShip AI doesn't just predict the future; it uses Generative AI to change it, saving money and improving customer satisfaction. Thank you!"
