from joblib import load
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Union

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

app = FastAPI(
    title='The Getaround API',
    description='This API allows users to predict rental prices based on car characteristics.',
)

@app.get('/', summary="Root Endpoint", description="Welcome message.")
async def root():
    message = '''If you are looking to estimate car prices from their features, you are in the right place.'''
    return message

@app.post('/predict', tags=["Predictions"], summary="Predict rental price", 
          description="""Use this endpoint to predict rental prices based on the car's characteristics. 
          Example request: \n
```
    {
        "model_key": "Renault",
        "mileage": 77334,
        "engine_power": 256,
        "fuel": "diesel",
        "paint_color": "black",
        "car_type": "coupe",
        "private_parking_available": true,
        "has_gps": false,
        "has_air_conditioning": true,
        "automatic_car": false,
        "has_getaround_connect": false,
        "has_speed_regulator": true,
        "winter_tires": false
    }
```\n

          This should return the predicted price.""")
async def predict(input_data: PredictionFeatures, request: Request):
    ''' Return predicted price according to car features'''

    body = await request.json()
    print(f"Received request body: {body}")

    print(f"Parsed input data (Pydantic): {input_data.dict()}")

    try:
        predictor = load('./model/model_reg.pkl')
        transformer = load('./model/transformer.pkl')
        user_data = pd.DataFrame([input_data.dict()])

        print(f"Data prepared for transformation: {user_data}")

        X = transformer.transform(user_data)
        print(f"Transformed data: {X}")

        X_pred = predictor.predict(X)
        print(f"Prediction: {X_pred}")

        return {f'The predicted price is: {X_pred[0]:.2f}$'}
    
    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
