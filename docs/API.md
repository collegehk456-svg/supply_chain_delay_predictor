# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API doesn't require authentication. In production, implement JWT tokens.

---

## Health Check Endpoints

### Health Status
**GET** `/health`

Returns detailed health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "timestamp": "2024-05-14T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

## Prediction Endpoints

### Single Prediction
**POST** `/predict`

Predict whether a single shipment will be delayed.

**Request Body:**
```json
{
  "warehouse_block": "A",
  "mode_of_shipment": "Flight",
  "customer_care_calls": 3,
  "customer_rating": 4.5,
  "cost_of_the_product": 5000,
  "prior_purchases": 2,
  "product_importance": "High",
  "gender": "M",
  "discount_offered": 15,
  "weight_in_gms": 2500
}
```

**Response:**
```json
{
  "prediction": 1,
  "probability_delayed": 0.78,
  "confidence": 0.95,
  "model_version": "v1.0"
}
```

**Status Codes:**
- `200` - Successful prediction
- `400` - Invalid input
- `500` - Internal server error
- `503` - Model not loaded

---

### Batch Predictions
**POST** `/predict/batch`

Predict delays for multiple shipments.

**Request Body:**
```json
{
  "shipments": [
    {
      "warehouse_block": "A",
      "mode_of_shipment": "Flight",
      "customer_care_calls": 3,
      "customer_rating": 4.5,
      "cost_of_the_product": 5000,
      "prior_purchases": 2,
      "product_importance": "High",
      "gender": "M",
      "discount_offered": 15,
      "weight_in_gms": 2500
    },
    {
      "warehouse_block": "B",
      "mode_of_shipment": "Ship",
      "customer_care_calls": 1,
      "customer_rating": 3.5,
      "cost_of_the_product": 2000,
      "prior_purchases": 0,
      "product_importance": "Low",
      "gender": "F",
      "discount_offered": 5,
      "weight_in_gms": 500
    }
  ]
}
```

**Response:**
```json
{
  "total_predictions": 2,
  "predictions": [
    {
      "prediction": 1,
      "probability_delayed": 0.78,
      "confidence": 0.95,
      "model_version": "v1.0"
    },
    {
      "prediction": 0,
      "probability_delayed": 0.25,
      "confidence": 0.88,
      "model_version": "v1.0"
    }
  ],
  "processing_time_ms": 45.23
}
```

---

### Prediction with Explanation
**POST** `/predict-with-explanation`

Predict with SHAP-based explanation and recommendations.

**Request Body:**
Same as single prediction endpoint.

**Response:**
```json
{
  "prediction": 1,
  "probability_delayed": 0.78,
  "top_factors": [
    {
      "feature": "Weight_in_gms",
      "importance": 0.25
    },
    {
      "feature": "Mode_of_Shipment",
      "importance": 0.20
    }
  ],
  "explanation_text": "This shipment is likely to be delayed due to high weight and ship mode.",
  "recommendations": [
    "Consider air transport for faster delivery",
    "Reduce product weight if possible"
  ],
  "model_version": "v1.0"
}
```

---

## Model Management Endpoints

### List Available Models
**GET** `/models`

Get list of available models.

**Response:**
```json
{
  "models": [
    {
      "name": "xgboost_v1.0",
      "status": "active",
      "type": "classification"
    }
  ]
}
```

---

### Get Active Model
**GET** `/models/active`

Get details of currently active model.

**Response:**
```json
{
  "name": "xgboost_v1.0",
  "status": "active",
  "version": "1.0.0",
  "created_at": "2024-05-14T10:30:00Z",
  "metrics": {
    "accuracy": 0.89,
    "precision": 0.85,
    "recall": 0.82,
    "f1_score": 0.83
  }
}
```

---

## Analytics Endpoints

### Summary Statistics
**GET** `/analytics/summary`

Get overall analytics summary.

**Response:**
```json
{
  "total_predictions": 1500,
  "api_status": "operational",
  "model_version": "v1.0",
  "timestamp": "2024-05-14T10:30:00.000Z"
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Descriptive error message"
}
```

### Common Errors

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Error | Server error |
| 503 | Unavailable | Model not loaded or service unavailable |

---

## Request/Response Examples

### Example 1: Simple Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "warehouse_block": "A",
    "mode_of_shipment": "Flight",
    "customer_care_calls": 3,
    "customer_rating": 4.5,
    "cost_of_the_product": 5000,
    "prior_purchases": 2,
    "product_importance": "High",
    "gender": "M",
    "discount_offered": 15,
    "weight_in_gms": 2500
  }'
```

### Example 2: Python Requests
```python
import requests

url = "http://localhost:8000/api/v1/predict"
data = {
    "warehouse_block": "A",
    "mode_of_shipment": "Flight",
    "customer_care_calls": 3,
    "customer_rating": 4.5,
    "cost_of_the_product": 5000,
    "prior_purchases": 2,
    "product_importance": "High",
    "gender": "M",
    "discount_offered": 15,
    "weight_in_gms": 2500
}

response = requests.post(url, json=data)
print(response.json())
```

### Example 3: JavaScript Fetch
```javascript
const url = "http://localhost:8000/api/v1/predict";
const data = {
    "warehouse_block": "A",
    "mode_of_shipment": "Flight",
    "customer_care_calls": 3,
    "customer_rating": 4.5,
    "cost_of_the_product": 5000,
    "prior_purchases": 2,
    "product_importance": "High",
    "gender": "M",
    "discount_offered": 15,
    "weight_in_gms": 2500
};

fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Input Validation

### Field Constraints

| Field | Type | Range/Values | Required |
|-------|------|--------------|----------|
| warehouse_block | string | A-F | Yes |
| mode_of_shipment | string | Ship, Flight, Road | Yes |
| customer_care_calls | integer | 0-10 | Yes |
| customer_rating | float | 1.0-5.0 | Yes |
| cost_of_the_product | float | > 0 | Yes |
| prior_purchases | integer | >= 0 | Yes |
| product_importance | string | Low, Medium, High | Yes |
| gender | string | M, F | Yes |
| discount_offered | float | 0-100 | Yes |
| weight_in_gms | float | > 0 | Yes |

---

## Rate Limiting

Currently not enforced. Will be added in production deployment.

---

## Swagger UI

Interactive API documentation available at:
```
http://localhost:8000/docs
```

---

## Version History

### v1.0.0 (Current)
- Initial release
- Single and batch predictions
- SHAP explanations
- Actionable recommendations
- Health check endpoints

---

## Support

For API issues or questions:
1. Check Swagger documentation: `http://localhost:8000/docs`
2. Review error messages
3. Check logs: `logs/app.log`
4. Open GitHub issue

---

Last Updated: May 2024
