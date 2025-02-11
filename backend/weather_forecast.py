import os
import pickle
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_from_json  # not used here
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
router = APIRouter()

class WeatherForecastQuery(BaseModel):
    target_date: str  # Format: "YYYY-MM-DD HH:MM:SS"
    threshold: float = 25.0  # Temperature threshold

# Load the Prophet model from pickle.
MODEL_PATH = "backend/prophet_model.pkl"
if not os.path.exists(MODEL_PATH):
    logging.error("Prophet model file not found.")
    prophet_model = None
else:
    try:
        with open(MODEL_PATH, "rb") as f:
            prophet_model = pickle.load(f)
        logging.debug("Prophet model loaded successfully from pickle.")
    except Exception as e:
        logging.error("Error loading Prophet model: %s", e)
        prophet_model = None

def forecast_weather(target_date_str: str, threshold: float = 25.0) -> str:
    """
    Forecast weather from the current time up to the target date.
    Returns a forecast text indicating the predicted temperature and condition.
    """
    if prophet_model is None:
        raise Exception("Prophet model is not available.")
    
    target_date = pd.to_datetime(target_date_str)
    now = datetime.now()
    if target_date <= now:
        raise Exception("Target date must be in the future.")
    
    # Calculate hours from now to target date.
    hours_to_forecast = int((target_date - now).total_seconds() / 3600)
    
    # Create a future dataframe starting from now.
    future_df = prophet_model.make_future_dataframe(periods=hours_to_forecast, freq='H')
    forecast_df = prophet_model.predict(future_df)
    forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
    
    # Find the forecast row closest to target_date.
    closest_row = forecast_df.iloc[(forecast_df['ds'] - target_date).abs().argsort()[:1]]
    predicted_temp = closest_row['yhat'].values[0]
    
    condition = "Cloudy" if predicted_temp < threshold else "Clear"
    forecast_text = (f"On {target_date_str}, the forecasted temperature is {predicted_temp:.2f}°C. "
                     f"Expected condition: {condition}.")
    return forecast_text

@router.post("/forecast/")
def forecast_endpoint(query: WeatherForecastQuery):
    try:
        forecast_text = forecast_weather(query.target_date, query.threshold)
        return {"forecast": forecast_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
