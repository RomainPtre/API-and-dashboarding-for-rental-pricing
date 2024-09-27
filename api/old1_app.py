from joblib import load
import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, constr

class PredictionFeatures(BaseModel):
    # Using constr to enforce string constraints if needed
    input_data: list

app = FastAPI()

@app.get('/')
async def root():
    return "If you are looking to estimate car prices from their features, you are in the right place."

@app.post('/predict')
async def predict(input_data: PredictionFeatures):
    ''' Return predicted price according to car features'''
    
    # Load your models here
    predictor = load('./model/model_reg.pkl')
    transformer = load('./model/transformer.pkl')

    # Correctly extract the input data
    user_data_list = input_data.input_data[0]  # Extract the first element of input_data
    
    # Creating DataFrame with correct handling for special characters
    user_data = pd.DataFrame([user_data_list], columns=[
        'model_key', 
        'mileage', 
        'engine_power', 
        'fuel', 
        'paint_color',
        'car_type', 
        'private_parking_available', 
        'has_gps',
        'has_air_conditioning', 
        'automatic_car', 
        'has_getaround_connect',
        'has_speed_regulator', 
        'winter_tires'
    ])

    # Debugging: Print the user_data to check for special character handling
    print(f"User data: {user_data}")

    # Transform and predict
    X = transformer.transform(user_data)
    print(f"Transformed data: {X}")

    X_pred = predictor.predict(X)
    print(f"Prediction: {X_pred}")

    return {'The return predicted price is': X_pred[0]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
