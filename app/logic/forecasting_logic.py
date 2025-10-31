# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ===== CORE BUSINESS LOGIC =====
def run_forecast(df: pd.DataFrame, target_columns: list):
    """
    Performs a linear regression forecast for each target column based on the 'year' column.
    
    Args:
        df (pd.DataFrame): DataFrame containing historical data. Must have a 'year' column.
        target_columns (list): A list of column names to forecast.

    Returns:
        dict: A dictionary where keys are target column names and values are dictionaries
              containing 'historical_values' and the 'forecasted_value'.
    """
    if df.empty or 'سال' not in df.columns:
        raise ValueError("DataFrame must contain a 'سال' column.")
    
    if len(df) < 2:
        raise ValueError("Forecasting requires at least 2 data points (years).")

    # Prepare the feature (X) and target (y) for regression
    # Reshape is needed because scikit-learn expects a 2D array for features
    X = df['سال'].values.reshape(-1, 1)
    next_year = np.array([[df['سال'].max() + 1]])

    forecast_results = {}

    for col in target_columns:
        if col not in df.columns:
            continue
            
        y = df[col].values
        
        # Create and train the linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict the value for the next year
        forecasted_value = model.predict(next_year)[0]
        
        # Store results
        forecast_results[col] = {
            'historical': df[['سال', col]].to_dict('records'),
            'forecast': forecasted_value
        }
        
    return forecast_results