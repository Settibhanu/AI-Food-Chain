import pandas as pd
import numpy as np
from pmdarima import auto_arima
from pmdarima.arima import ARIMA
import joblib 
import os
import matplotlib.pyplot as plt

# Field name mapping from new CSV format
FIELD_NAME_MAPPING = {
    'Fertilizerkgperha': 'Fertilizer_kg_per_ha',
    'SoilMoisture%': 'SoilMoisture_%',
    'TemperatureC': 'Temperature_C',
    'Rainfallmm': 'Rainfall_mm',
    'Yieldtonnesperha': 'Yield_tonnes_per_ha',
    'PestRiskScore': 'PestRiskScore',
    'HarvestRobotUptime%': 'HarvestRobotUptime_%',
    'StorageTemperatureC': 'StorageTemperature_C',
    'Humidity%': 'Humidity_%',
    'SpoilageRate%': 'SpoilageRate_%',
    'GradingScore': 'GradingScore',
    'PredictedShelfLifedays': 'PredictedShelfLife_days',
    'StorageDays': 'StorageDays',
    'ProcessType': 'ProcessType',
    'PackagingType': 'PackagingType',
    'PackagingSpeedunitspermin': 'PackagingSpeed_units_per_min',
    'DefectRate%': 'DefectRate_%',
    'MachineryUptime%': 'MachineryUptime_%',
    'TransportMode': 'TransportMode',
    'TransportDistancekm': 'TransportDistance_km',
    'FuelUsageLper100km': 'FuelUsage_L_per_100km',
    'DeliveryTimehr': 'DeliveryTime_hr',
    'DeliveryDelayFlag': 'DeliveryDelayFlag',
    'SpoilageInTransit%': 'SpoilageInTransit_%',
    'RetailInventoryunits': 'RetailInventory_units',
    'SalesVelocityunitsperday': 'SalesVelocity_units_per_day',
    'DynamicPricingIndex': 'DynamicPricingIndex',
    'WastePercentage%': 'WastePercentage_%',
    'HouseholdWastekg': 'HouseholdWaste_kg',
    'RecipeRecommendationAccuracy%': 'RecipeRecommendationAccuracy_%',
    'SatisfactionScore010': 'SatisfactionScore_0_10',
    'WasteType': 'WasteType',
    'SegregationAccuracy%': 'SegregationAccuracy_%',
    'UpcyclingRate%': 'UpcyclingRate_%',
    'BiogasOutputm3': 'BiogasOutput_m3',
    'minprice': 'minprice',
    'maxprice': 'maxprice',
    'modalprice': 'modalprice',
    'marketname': 'marketname',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'BatchID': 'BatchID',
    'CropType': 'CropType',
    'FarmLocation': 'FarmLocation',
    'HarvestDate': 'HarvestDate'
}

def normalize_column_names(df):
    """Rename columns from new CSV format to internal field names"""
    rename_dict = {}
    for old_name, new_name in FIELD_NAME_MAPPING.items():
        if old_name in df.columns:
            rename_dict[old_name] = new_name
    if rename_dict:
        df = df.rename(columns=rename_dict)
    return df

# --- 1. CSV Reader Function (Uses REAL modalprice) ---
def load_data_for_sarima_training(file_path: str, crop_type: str) -> pd.Series:
    """
    Loads data, filters by crop type, uses HarvestDate for the index, and prepares 
    the REAL 'modalprice' time series for SARIMA training.

    :param file_path: Path to the combined farm data CSV (e.g., 'farm_a_data.csv').
    :param crop_type: The specific crop to filter for (e.g., 'tomato').
    :return: A clean Pandas Series of modalprice data indexed by date, resampled monthly.
    """
    
    try:
        df = pd.read_csv(file_path)
        df = normalize_column_names(df)
    except FileNotFoundError:
        print(f"Error: Farm data file not found at {file_path}. Returning empty series.")
        return pd.Series()

    # 1. Filter by CropType
    df_crop = df[df['CropType'].str.lower() == crop_type.lower()].copy()

    if df_crop.empty:
        print(f"Error: No records found for crop '{crop_type}'.")
        return pd.Series()

    # 2. Create Time Series Index
    df_crop['HarvestDate'] = pd.to_datetime(df_crop['HarvestDate'])
    df_crop = df_crop.sort_values('HarvestDate').set_index('HarvestDate')

    # 3. Use REAL Modal Price Data
    if 'modalprice' not in df_crop.columns:
         print(f"Error: 'modalprice' column not found for {crop_type}. Cannot train model.")
         return pd.Series()
         
    price_series = df_crop['modalprice'].copy()
    price_series.name = f'{crop_type.capitalize()}_ModalPrice'

    # 4. Data Cleaning
    cleaned_prices = price_series.replace([np.inf, -np.inf], np.nan)
    cleaned_prices = cleaned_prices.ffill().bfill()
    
    # 5. Resample to Monthly Frequency ('MS') for m=12 seasonality
    # Use the mean price for that month to aggregate batch data.
    cleaned_prices_monthly = cleaned_prices.resample('MS').mean().ffill().dropna()

    return cleaned_prices_monthly

# --- 2. Model Training and Saving Function (Stabilized) ---
def train_and_save_sarima_model(crop_name: str, historical_prices: pd.Series):
    """
    Trains the best SARIMA model using auto_arima with fallbacks.
    If auto_arima fails, tries simpler models or returns a basic model.
    """
    
    print(f"\n--- Training SARIMA model for {crop_name} ---")
    
    if historical_prices.empty:
        print(f"Cannot train model for {crop_name}: Data is empty.")
        return None, None

    # Data validation checks
    if len(historical_prices) < 12:
        print(f"Warning: {crop_name} has only {len(historical_prices)} data points. Less than 12 months of data.")
    
    # Check for constant series (no variance)
    if historical_prices.std() == 0:
        print(f"Warning: {crop_name} has zero variance (all values are the same). Using mean model fallback.")
        from pmdarima.arima import ARIMA
        try:
            model = ARIMA(order=(0, 0, 0)).fit(historical_prices)
            print(f"Created simple mean model for {crop_name}")
            save_model(model, crop_name, historical_prices)
            return model, historical_prices
        except Exception as e:
            print(f"Error: Could not create model for {crop_name}: {e}")
            return None, None

    # Try auto_arima with full seasonality
    try:
        print("Attempting seasonal auto_arima fit...")
        stepwise_fit = auto_arima(
            historical_prices, 
            start_p=0, start_q=0,
            max_p=2, max_q=2,
            m=12,  # Monthly data seasonality
            start_P=0, seasonal=True, 
            d=1, D=1,
            with_intercept=False,
            method='powell',
            trace=True, 
            error_action='ignore',  
            suppress_warnings=True, 
            stepwise=True,
            scoring='bic',
            max_order=5
        )
        print(f"✓ Best SARIMAX order for {crop_name}: {stepwise_fit.order}, Seasonal: {stepwise_fit.seasonal_order}")
        save_model(stepwise_fit, crop_name, historical_prices)
        return stepwise_fit, historical_prices
        
    except ValueError as e:
        print(f"✗ Seasonal auto_arima failed: {e}")
        print("Attempting non-seasonal auto_arima fit...")
        
        # Fallback 1: Try non-seasonal ARIMA
        try:
            stepwise_fit = auto_arima(
                historical_prices, 
                start_p=0, start_q=0,
                max_p=2, max_q=2,
                m=1,  # Non-seasonal
                seasonal=False, 
                d=1,
                with_intercept=False,
                trace=True, 
                error_action='ignore',  
                suppress_warnings=True, 
                stepwise=True,
                scoring='bic',
                max_order=5
            )
            print(f"✓ Non-seasonal ARIMA fit successful. Order: {stepwise_fit.order}")
            save_model(stepwise_fit, crop_name, historical_prices)
            return stepwise_fit, historical_prices
            
        except ValueError as e2:
            print(f"✗ Non-seasonal auto_arima also failed: {e2}")
            print("Attempting fixed ARIMA(1,1,1) model...")
            
            # Fallback 2: Use fixed ARIMA order
            try:
                from pmdarima.arima import ARIMA
                stepwise_fit = ARIMA(order=(1, 1, 1)).fit(historical_prices)
                print(f"✓ Fixed ARIMA(1,1,1) model fit successful")
                save_model(stepwise_fit, crop_name, historical_prices)
                return stepwise_fit, historical_prices
                
            except Exception as e3:
                print(f"✗ ARIMA(1,1,1) failed: {e3}")
                print("Attempting simple differencing model ARIMA(0,1,0)...")
                
                # Fallback 3: Simplest differencing model
                try:
                    from pmdarima.arima import ARIMA
                    stepwise_fit = ARIMA(order=(0, 1, 0)).fit(historical_prices)
                    print(f"✓ Simple ARIMA(0,1,0) model fit successful")
                    save_model(stepwise_fit, crop_name, historical_prices)
                    return stepwise_fit, historical_prices
                    
                except Exception as e4:
                    print(f"✗ All model fitting attempts failed for {crop_name}: {e4}")
                    return None, None


def save_model(model, crop_name: str, historical_prices: pd.Series):
    """Helper function to save model to disk."""
    model_filename = f'sarima_{crop_name.lower().replace(" ", "_")}_model.pkl'
    save_path = os.path.join('models', model_filename)
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, save_path)
    print(f"Model successfully saved to {save_path}")


# --- 3. Execution Block ---
if __name__ == '__main__':
    
    # Define paths to updated farm data CSV files
    FARM_DATA_FILES = [
        'updated_farm_data/updated_farm_a_data.csv',
        'updated_farm_data/updated_farm_b_data.csv',
        'updated_farm_data/updated_farm_c_data.csv',
        'updated_farm_data/updated_farm_d_data.csv'
    ]
    
    # Define the crops you want to train models for
    # Ensure these crop types exist in your CSV file!
    CROPS_TO_TRAIN = ['tomato', 'corn', 'lettuce', 'wheat']
    
    fitted_models = {}

    # Iterate through all farm data files
    for farm_file in FARM_DATA_FILES:
        print(f"\n{'='*60}")
        print(f"Processing: {farm_file}")
        print(f"{'='*60}")
        
        for crop in CROPS_TO_TRAIN:
            # 1. Load data for the current crop
            price_series = load_data_for_sarima_training(
                file_path=farm_file, 
                crop_type=crop
            )

            # Check if enough data exists (at least 2 years/24 points for good seasonality analysis)
            if not price_series.empty and len(price_series) >= 12: 
                # 2. Train and Save the Model
                model_name = f'{crop.lower()}_price'
                fitted_model, cleaned_data = train_and_save_sarima_model(model_name, price_series)
                if fitted_model:
                    fitted_models[model_name] = (fitted_model, cleaned_data)
            else:
                print(f"\nSkipping training for {crop}: Insufficient data points (< 12) or data is empty.")

    print("\n" + "="*60)
    print("--- All required models training attempts complete. Check the 'models' directory. ---")
    print("="*60)
    
    # --- 4. Visualization Check (Example for the first successful model) ---
    if fitted_models:
        first_model_name = list(fitted_models.keys())[0]
        fitted_model, cleaned_data = fitted_models[first_model_name]
        
        n_periods = 6
        forecast_results = fitted_model.predict(n_periods=n_periods, return_conf_int=True, alpha=0.05)
        forecast_values = forecast_results[0]
        conf_int = forecast_results[1]
        
        last_date = cleaned_data.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=n_periods + 1, freq='MS')[1:]

        plt.figure(figsize=(10, 5))
        plt.plot(cleaned_data.index, cleaned_data.values, label=f'Historical Price ({first_model_name.capitalize()})', color='blue')
        plt.plot(forecast_index, forecast_values, label='Forecasted Price', color='red', linestyle='--')
        plt.fill_between(forecast_index, conf_int[:, 0], conf_int[:, 1], color='pink', alpha=0.3, label='95% CI')
        plt.title(f'{first_model_name.capitalize()} Price Forecast (Validation Plot)')
        plt.xlabel('Date')
        plt.ylabel('Price (₹/unit)')
        plt.legend()
        plt.grid(True, alpha=0.6)
        plt.savefig(f'{first_model_name}_forecast_plot.png')
        print(f"Saved visualization for {first_model_name} as {first_model_name}_forecast_plot.png")