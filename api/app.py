from joblib import load
import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel
from typing import Union

class Features(BaseModel):
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

app = FastAPI()

@app.get('/')
async def root():
    message = '''If you are looking to estimate car prices from their features, you are in the right place.'''
    return message

@app.post('/predict')
async def predict(input_data: Features, request: Request):
    ''' Return predicted price according to car features'''

    body = await request.json()
    print(f"Received request body: {body}")
    predictor = load('./model/model_reg.pkl')
    transformer = load('./model/transformer.pkl')
    user_data = pd.DataFrame([input_data.dict()])
    X = transformer.transform(user_data)
    X_pred = predictor.predict(X)
    return {'The return predicted price is': X_pred[0]}

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)