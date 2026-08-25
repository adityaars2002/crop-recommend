# Smart Agriculture System - API Documentation

## Base URL
All API requests should be prefixed with:
`/api/v1/`

For example:
`http://127.0.0.1:8000/api/v1/crops/recommend/`

## Authentication
Currently, no authentication is required for these endpoints. This will change in future phases.

## Standard Response Format
All successful and failed responses follow a consistent wrapper format.

### Success Envelope
```json
{
    "success": true,
    "data": { ... } 
}
```
*Note: `data` can be an object or an array depending on the endpoint.*

### Error Envelope
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "One or more fields are invalid.",
        "fields": {
            "ph": ["Value for ph cannot be NaN or Infinity."]
        }
    }
}
```

---

## 1. Crop Recommendation Endpoint

Get a machine-learning powered recommendation for the top 3 crops suited for the provided environmental parameters.

- **Endpoint:** `POST /api/v1/crops/recommend/`
- **Content-Type:** `application/json`

### Request Body
All fields are required and must be numeric.

| Field | Description | Constraints |
|-------|-------------|-------------|
| `nitrogen` | Soil Nitrogen (N) | `>= 0` |
| `phosphorus` | Soil Phosphorus (P) | `>= 0` |
| `potassium` | Soil Potassium (K) | `>= 0` |
| `temperature` | Average Temperature (°C) | None |
| `humidity` | Relative Humidity (%) | `0 - 100` |
| `ph` | Soil pH value | `0 - 14` |
| `rainfall` | Rainfall (mm) | `>= 0` |

### cURL Example (Windows PowerShell)
```powershell
$body = '{"nitrogen":90, "phosphorus":42, "potassium":43, "temperature":25.5, "humidity":80.0, "ph":6.5, "rainfall":200.0}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/crops/recommend/' -Method Post -Body $body -ContentType 'application/json' | ConvertTo-Json -Depth 10
```

### Postman
Set method to `POST`. Enter URL: `http://127.0.0.1:8000/api/v1/crops/recommend/`. Under **Body**, select **raw** and **JSON**, then paste:
```json
{
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "temperature": 25.5,
    "humidity": 80,
    "ph": 6.5,
    "rainfall": 200
}
```

### Successful Response (HTTP 200 OK)
Returns the stored request ID, the original input, and the top 3 ranked recommendations with their `score`.

```json
{
    "success": true,
    "data": {
        "id": 1,
        "created_at": "2026-08-25T16:50:30.868484+05:30",
        "input": {
            "nitrogen": 90.0,
            "phosphorus": 42.0,
            "potassium": 43.0,
            "temperature": 25.5,
            "humidity": 80.0,
            "ph": 6.5,
            "rainfall": 200.0
        },
        "recommendations": [
            {
                "rank": 1,
                "crop": {
                    "id": 21,
                    "name": "rice",
                    "scientific_name": "Oryza sativa",
                    "description": "A staple cereal grain requiring submerged conditions.",
                    ...
                },
                "score": 0.504
            },
            {
                "rank": 2,
                "crop": {
                    "id": 9,
                    "name": "jute",
                    ...
                },
                "score": 0.4822
            },
            {
                "rank": 3,
                "crop": {
                    "id": 18,
                    "name": "papaya",
                    ...
                },
                "score": 0.0139
            }
        ]
    }
}
```

---

## 2. Crop List

Get a paginated list of all supported crops.

- **Endpoint:** `GET /api/v1/crops/`
- **Response:** HTTP 200 OK

```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "apple",
            "scientific_name": "Malus domestica",
            ...
        }
    ],
    "pagination": {
        "count": 22,
        "next": "http://127.0.0.1:8000/api/v1/crops/?page=2",
        "previous": null
    }
}
```

---

## 3. Crop Detail

Get details for a specific crop by ID.

- **Endpoint:** `GET /api/v1/crops/{id}/`
- **Response (Found):** HTTP 200 OK
- **Response (Not Found):** HTTP 404 Not Found

---

## 4. Recommendation History

Get a paginated list of all past recommendation requests.

- **Endpoint:** `GET /api/v1/crops/recommendations/history/`
- **Response:** HTTP 200 OK

---

## HTTP Status Codes
* **200 OK:** Request successful.
* **400 Bad Request:** Validation failed (e.g., missing fields, invalid ranges).
* **404 Not Found:** Resource does not exist.
* **503 Service Unavailable:** The ML model failed to load or crashed during inference.
* **500 Internal Server Error:** Unexpected backend exception.

---

## Android Integration Notes
The future Kotlin application (using Retrofit) should define its data classes to expect the wrapper object:
```kotlin
data class ApiResponse<T>(
    val success: Boolean,
    val data: T?,
    val error: ApiError?
)
```
The endpoint to hit for recommendations will be `POST /api/v1/crops/recommend/`. The response data will map perfectly to a `RecommendationHistory` object containing the `input` and a list of `RecommendationResult` objects.

**Limitation Disclaimer:** The `score` represents the Random Forest model's confidence probability. It is NOT a guarantee of agricultural success. Ensure the Android UI displays this nuance.
