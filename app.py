from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from datetime import datetime
import numpy as np
from datetime import timedelta
import requests
import re

app = Flask(__name__)

FARM_FILES = {
    'FarmA': 'farm_a_data.csv',
    'FarmB': 'farm_b_data.csv',
    'FarmC': 'farm_c_data.csv',
    'FarmD': 'farm_d_data.csv'
}

def load_farm_data(farm_name):
    """Load CSV data for a specific farm"""
    if farm_name in FARM_FILES and os.path.exists(FARM_FILES[farm_name]):
        df = pd.read_csv(FARM_FILES[farm_name])
        if 'HarvestDate' in df.columns:
            df['HarvestDate'] = pd.to_datetime(df['HarvestDate'])
        return df
    return pd.DataFrame()

def load_all_farms_data():
    """Load data from all farms for comparison"""
    all_data = {}
    for farm_name, file_path in FARM_FILES.items():
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if 'HarvestDate' in df.columns:
                df['HarvestDate'] = pd.to_datetime(df['HarvestDate'])
            all_data[farm_name] = df
    return all_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/farm/<farm_name>/kpis')
def get_farm_kpis(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    kpis = {
        'total_production': float(data['Yield_tonnes_per_ha'].mean()),
        'storage_spoilage': float(data['SpoilageRate_%'].mean()),
        'processing_defects': float(data['DefectRate_%'].mean()),
        'transport_delays': float((data['DeliveryDelayFlag'].sum() / len(data) * 100)),
        'retail_inventory': float(data['RetailInventory_units'].sum()),
        'waste_percentage': float(data['WastePercentage_%'].mean()),
        'satisfaction': float(data['SatisfactionScore_0_10'].mean()),
        'waste_segregation': float(data['SegregationAccuracy_%'].mean()),
        'total_records': len(data),
        'pest_risk': float(data['PestRiskScore'].mean()),
        'machinery_uptime': float(data['MachineryUptime_%'].mean()),
        'harvest_uptime': float(data['HarvestRobotUptime_%'].mean())
    }
    return jsonify(kpis)

@app.route('/api/farm/<farm_name>/production')
def get_farm_production_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    yield_by_crop = data.groupby('CropType')['Yield_tonnes_per_ha'].mean().to_dict()
    return jsonify({'crop_types': data['CropType'].unique().tolist(), 'yield_by_crop': yield_by_crop})

@app.route('/api/farm/<farm_name>/storage')
def get_farm_storage_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    return jsonify({
        'avg_temp': float(data['StorageTemperature_C'].mean()),
        'avg_humidity': float(data['Humidity_%'].mean()),
        'avg_spoilage': float(data['SpoilageRate_%'].mean()),
        'avg_shelf_life': float(data['PredictedShelfLife_days'].mean())
    })

@app.route('/api/farm/<farm_name>/processing')
def get_farm_processing_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    defect_by_process = data.groupby('ProcessType')['DefectRate_%'].mean().to_dict()
    return jsonify({
        'avg_defect_rate': float(data['DefectRate_%'].mean()),
        'avg_uptime': float(data['MachineryUptime_%'].mean()),
        'avg_packaging_speed': float(data['PackagingSpeed_units_per_min'].mean()),
        'defect_by_process': defect_by_process
    })

@app.route('/api/farm/<farm_name>/transportation')
def get_farm_transportation_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    return jsonify({
        'avg_distance': float(data['TransportDistance_km'].mean()),
        'avg_fuel': float(data['FuelUsage_L_per_100km'].mean()),
        'avg_delivery_time': float(data['DeliveryTime_hr'].mean()),
        'delay_percentage': float((data['DeliveryDelayFlag'].sum() / len(data) * 100))
    })

@app.route('/api/farm/<farm_name>/retail')
def get_farm_retail_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    return jsonify({
        'total_inventory': float(data['RetailInventory_units'].sum()),
        'avg_sales_velocity': float(data['SalesVelocity_units_per_day'].mean()),
        'avg_pricing_index': float(data['DynamicPricingIndex'].mean()),
        'avg_waste': float(data['WastePercentage_%'].mean())
    })

@app.route('/api/farm/<farm_name>/consumption')
def get_farm_consumption_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    return jsonify({
        'avg_household_waste': float(data['HouseholdWaste_kg'].mean()),
        'avg_recipe_accuracy': float(data['RecipeRecommendationAccuracy_%'].mean()),
        'avg_satisfaction': float(data['SatisfactionScore_0_10'].mean())
    })

@app.route('/api/farm/<farm_name>/waste')
def get_farm_waste_data(farm_name):
    data = load_farm_data(farm_name)
    if data.empty:
        return jsonify({'error': 'Farm not found'}), 404
    
    waste_dist = data['WasteType'].value_counts().to_dict()
    return jsonify({
        'avg_segregation': float(data['SegregationAccuracy_%'].mean()),
        'avg_upcycling': float(data['UpcyclingRate_%'].mean()),
        'avg_biogas': float(data['BiogasOutput_m3'].mean()),
        'waste_dist': waste_dist
    })

@app.route('/api/comparison/<section>')
def get_comparison_data(section):
    """Get comparison data for all farms for a specific section"""
    all_farms = load_all_farms_data()
    comparison = {}
    
    for farm_name, data in all_farms.items():
        if section == 'production':
            yield_by_crop = data.groupby('CropType')['Yield_tonnes_per_ha'].mean().to_dict()
            comparison[farm_name] = {
                'yield': float(data['Yield_tonnes_per_ha'].mean()),
                'pest_risk': float(data['PestRiskScore'].mean()),
                'harvest_uptime': float(data['HarvestRobotUptime_%'].mean()),
                'machinery_uptime': float(data['MachineryUptime_%'].mean()),
                'yield_by_crop': yield_by_crop
            }
        elif section == 'storage':
            comparison[farm_name] = {
                'avg_temp': float(data['StorageTemperature_C'].mean()),
                'avg_humidity': float(data['Humidity_%'].mean()),
                'avg_spoilage': float(data['SpoilageRate_%'].mean()),
                'avg_shelf_life': float(data['PredictedShelfLife_days'].mean())
            }
        elif section == 'processing':
            defect_by_process = data.groupby('ProcessType')['DefectRate_%'].mean().to_dict()
            comparison[farm_name] = {
                'avg_defect_rate': float(data['DefectRate_%'].mean()),
                'avg_uptime': float(data['MachineryUptime_%'].mean()),
                'avg_packaging_speed': float(data['PackagingSpeed_units_per_min'].mean()),
                'defect_by_process': defect_by_process
            }
        elif section == 'transportation':
            comparison[farm_name] = {
                'avg_distance': float(data['TransportDistance_km'].mean()),
                'avg_fuel': float(data['FuelUsage_L_per_100km'].mean()),
                'avg_delivery_time': float(data['DeliveryTime_hr'].mean()),
                'delay_percentage': float((data['DeliveryDelayFlag'].sum() / len(data) * 100))
            }
        elif section == 'retail':
            comparison[farm_name] = {
                'total_inventory': float(data['RetailInventory_units'].sum()),
                'avg_sales_velocity': float(data['SalesVelocity_units_per_day'].mean()),
                'avg_pricing_index': float(data['DynamicPricingIndex'].mean()),
                'avg_waste': float(data['WastePercentage_%'].mean())
            }
        elif section == 'consumption':
            comparison[farm_name] = {
                'avg_household_waste': float(data['HouseholdWaste_kg'].mean()),
                'avg_recipe_accuracy': float(data['RecipeRecommendationAccuracy_%'].mean()),
                'avg_satisfaction': float(data['SatisfactionScore_0_10'].mean())
            }
        elif section == 'waste':
            waste_dist = data['WasteType'].value_counts().to_dict()
            comparison[farm_name] = {
                'avg_segregation': float(data['SegregationAccuracy_%'].mean()),
                'avg_upcycling': float(data['UpcyclingRate_%'].mean()),
                'avg_biogas': float(data['BiogasOutput_m3'].mean()),
                'waste_dist': waste_dist
            }
    
    return jsonify(comparison)

@app.route('/api/overview')
def get_overview():
    """Get comparison data for all farms"""
    all_farms = load_all_farms_data()
    overview = {}
    
    for farm_name, data in all_farms.items():
        overview[farm_name] = {
            'yield': float(data['Yield_tonnes_per_ha'].mean()),
            'spoilage': float(data['SpoilageRate_%'].mean()),
            'defects': float(data['DefectRate_%'].mean()),
            'delays': float((data['DeliveryDelayFlag'].sum() / len(data) * 100)),
            'waste': float(data['WastePercentage_%'].mean()),
            'satisfaction': float(data['SatisfactionScore_0_10'].mean()),
            'pest_risk': float(data['PestRiskScore'].mean()),
            'machinery_uptime': float(data['MachineryUptime_%'].mean()),
            'total_records': len(data),
            'performance_score': 0  # Will calculate below
        }
    
    # Calculate performance scores (0-100)
    if overview:
        max_yield = max(f['yield'] for f in overview.values())
        min_spoilage = min(f['spoilage'] for f in overview.values())
        min_defects = min(f['defects'] for f in overview.values())
        min_delays = min(f['delays'] for f in overview.values())
        min_waste = min(f['waste'] for f in overview.values())
        max_satisfaction = max(f['satisfaction'] for f in overview.values())
        min_pest = min(f['pest_risk'] for f in overview.values())
        max_uptime = max(f['machinery_uptime'] for f in overview.values())
        
        for farm_name in overview:
            f = overview[farm_name]
            score = (
                (f['yield'] / max_yield * 20 if max_yield > 0 else 0) +
                ((1 - f['spoilage'] / 30) * 15 if f['spoilage'] < 30 else 0) +
                ((1 - f['defects'] / 15) * 15 if f['defects'] < 15 else 0) +
                ((1 - f['delays'] / 30) * 10 if f['delays'] < 30 else 0) +
                ((1 - f['waste'] / 25) * 10 if f['waste'] < 25 else 0) +
                (f['satisfaction'] / 10 * 15) +
                ((1 - f['pest_risk'] / 100) * 10 if f['pest_risk'] < 100 else 0) +
                (f['machinery_uptime'] / 100 * 5)
            )
            f['performance_score'] = round(score, 1)
    
    return jsonify(overview)

@app.route('/api/ai-insights/<farm_name>/<section>')
def get_ai_insights(farm_name, section):
    """Generate smart AI insights based on actual data analysis"""
    if farm_name == 'all':
        all_farms = load_all_farms_data()
        return generate_comparison_insights(all_farms, section)
    else:
        data = load_farm_data(farm_name)
        if data.empty:
            return jsonify({'error': 'Farm not found'}), 404
        return generate_farm_insights(farm_name, data, section)

def generate_comparison_insights(all_farms, section):
    """Generate concise insights comparing all farms"""
    insights = []
    recommendations = []
    farm_insights = {}  # One-line insights per farm
    
    # Calculate metrics for all farms
    farms_data = {}
    for farm_name, data in all_farms.items():
        farms_data[farm_name] = {
            'yield': float(data['Yield_tonnes_per_ha'].mean()),
            'spoilage': float(data['SpoilageRate_%'].mean()),
            'defects': float(data['DefectRate_%'].mean()),
            'delays': float((data['DeliveryDelayFlag'].sum() / len(data) * 100)),
            'waste': float(data['WastePercentage_%'].mean()),
            'satisfaction': float(data['SatisfactionScore_0_10'].mean()),
            'pest_risk': float(data['PestRiskScore'].mean()),
            'machinery_uptime': float(data['MachineryUptime_%'].mean()),
            'harvest_uptime': float(data['HarvestRobotUptime_%'].mean()),
            'storage_temp': float(data['StorageTemperature_C'].mean()),
            'humidity': float(data['Humidity_%'].mean()),
            'shelf_life': float(data['PredictedShelfLife_days'].mean()),
            'segregation': float(data['SegregationAccuracy_%'].mean()),
            'upcycling': float(data['UpcyclingRate_%'].mean()),
            'biogas': float(data['BiogasOutput_m3'].mean()),
        }
        farm_insights[farm_name] = []
    
    # Production insights
    if section == 'production':
        best_yield = max(farms_data.items(), key=lambda x: x[1]['yield'])
        worst_yield = min(farms_data.items(), key=lambda x: x[1]['yield'])
        worst_pest = max(farms_data.items(), key=lambda x: x[1]['pest_risk'])
        best_pest = min(farms_data.items(), key=lambda x: x[1]['pest_risk'])
        worst_uptime = min(farms_data.items(), key=lambda x: x[1]['harvest_uptime'])
        best_uptime = max(farms_data.items(), key=lambda x: x[1]['harvest_uptime'])
        
        insights.append(f"🏆 {best_yield[0]} leads with highest yield ({best_yield[1]['yield']:.1f}t/ha)")
        if worst_yield[1]['yield'] < 5:
            insights.append(f"⚠️ {worst_yield[0]} needs yield optimization ({worst_yield[1]['yield']:.1f}t/ha)")
            recommendations.append("Optimize soil nutrition and crop rotation")
            recommendations.append("Consider precision agriculture techniques")
        else:
            insights.append(f"📊 {worst_yield[0]} has lower yield ({worst_yield[1]['yield']:.1f}t/ha) - improvement opportunity")
            recommendations.append("Improve farming practices and soil quality")
        
        if worst_pest[1]['pest_risk'] > 50:
            insights.append(f"🐛 {worst_pest[0]} has high pest risk ({worst_pest[1]['pest_risk']:.0f}) - requires attention")
            recommendations.append("Implement integrated pest management (IPM)")
        if best_pest[1]['pest_risk'] < 20:
            insights.append(f"✅ {best_pest[0]} has excellent pest control (risk: {best_pest[1]['pest_risk']:.0f})")
        
        if worst_uptime[1]['harvest_uptime'] < 85:
            insights.append(f"⚙️ {worst_uptime[0]} has low harvest uptime ({worst_uptime[1]['harvest_uptime']:.0f}%) - maintenance needed")
            recommendations.append("Schedule preventive equipment maintenance")
        if best_uptime[1]['harvest_uptime'] > 95:
            insights.append(f"✅ {best_uptime[0]} has excellent machinery uptime ({best_uptime[1]['harvest_uptime']:.0f}%)")
        
        # Yield gap analysis
        yield_gap = best_yield[1]['yield'] - worst_yield[1]['yield']
        if yield_gap > 2:
            insights.append(f"📈 Yield gap of {yield_gap:.1f}t/ha between best and worst performers")
            recommendations.append("Share best practices across farms")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['yield'] == worst_yield[1]['yield'] and metrics['yield'] < 5:
                farm_insights[farm] = f"Low yield ({metrics['yield']:.1f}t/ha)"
            elif metrics['pest_risk'] == worst_pest[1]['pest_risk'] and metrics['pest_risk'] > 50:
                farm_insights[farm] = f"High pest risk ({metrics['pest_risk']:.0f})"
            elif metrics['harvest_uptime'] > 95:
                farm_insights[farm] = f"Excellent uptime ({metrics['harvest_uptime']:.0f}%)"
            else:
                farm_insights[farm] = f"Yield: {metrics['yield']:.1f}t/ha"
    
    # Storage insights
    elif section == 'storage':
        best_spoilage = min(farms_data.items(), key=lambda x: x[1]['spoilage'])
        worst_spoilage = max(farms_data.items(), key=lambda x: x[1]['spoilage'])
        best_temp = min(farms_data.items(), key=lambda x: abs(x[1]['storage_temp'] - 3.5))
        # Find worst temp (furthest from optimal range 2-5°C)
        worst_temp_candidates = [(f, m) for f, m in farms_data.items() if m['storage_temp'] < 2 or m['storage_temp'] > 5]
        if worst_temp_candidates:
            worst_temp = max(worst_temp_candidates, key=lambda x: abs(x[1]['storage_temp'] - 3.5))
        else:
            worst_temp = max(farms_data.items(), key=lambda x: abs(x[1]['storage_temp'] - 3.5))
        best_humidity = min(farms_data.items(), key=lambda x: abs(x[1]['humidity'] - 80))
        
        insights.append(f"✅ {best_spoilage[0]} has lowest spoilage ({best_spoilage[1]['spoilage']:.1f}%) - best practice")
        if worst_spoilage[1]['spoilage'] > 15:
            insights.append(f"❌ {worst_spoilage[0]} has critical spoilage ({worst_spoilage[1]['spoilage']:.1f}%) - immediate action needed")
            recommendations.append("Review cold chain integrity and storage protocols")
            recommendations.append("Implement real-time temperature monitoring")
        elif worst_spoilage[1]['spoilage'] > 10:
            insights.append(f"⚠️ {worst_spoilage[0]} needs spoilage reduction ({worst_spoilage[1]['spoilage']:.1f}%)")
            recommendations.append("Optimize storage conditions and temperature control")
        else:
            insights.append(f"📊 {worst_spoilage[0]} has spoilage at {worst_spoilage[1]['spoilage']:.1f}% - within range")
        
        # Temperature optimization
        if abs(best_temp[1]['storage_temp'] - 3.5) < 1:
            insights.append(f"🌡️ {best_temp[0]} maintains optimal temperature ({best_temp[1]['storage_temp']:.1f}°C)")
        
        worst_temp_val = worst_temp[1]['storage_temp']
        if worst_temp_val < 2 or worst_temp_val > 5:
            insights.append(f"🌡️ {worst_temp[0]} has temperature deviation ({worst_temp_val:.1f}°C) - calibration needed")
            recommendations.append("Calibrate refrigeration systems")
        elif abs(worst_temp_val - 3.5) > 1.5:
            insights.append(f"🌡️ {worst_temp[0]} temperature at {worst_temp_val:.1f}°C - can be optimized")
        
        # Humidity optimization
        if abs(best_humidity[1]['humidity'] - 80) < 5:
            insights.append(f"💧 {best_humidity[0]} maintains optimal humidity ({best_humidity[1]['humidity']:.0f}%)")
        
        # Shelf life comparison
        best_shelf = max(farms_data.items(), key=lambda x: x[1]['shelf_life'])
        insights.append(f"📅 {best_shelf[0]} achieves longest shelf life ({best_shelf[1]['shelf_life']:.1f} days)")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['spoilage'] == worst_spoilage[1]['spoilage'] and metrics['spoilage'] > 10:
                farm_insights[farm] = f"High spoilage ({metrics['spoilage']:.1f}%)"
            elif metrics['spoilage'] == best_spoilage[1]['spoilage']:
                farm_insights[farm] = f"Low spoilage ({metrics['spoilage']:.1f}%)"
            else:
                farm_insights[farm] = f"Spoilage: {metrics['spoilage']:.1f}%"
    
    # Processing insights
    elif section == 'processing':
        best_defects = min(farms_data.items(), key=lambda x: x[1]['defects'])
        worst_defects = max(farms_data.items(), key=lambda x: x[1]['defects'])
        best_uptime = max(farms_data.items(), key=lambda x: x[1]['machinery_uptime'])
        worst_uptime = min(farms_data.items(), key=lambda x: x[1]['machinery_uptime'])
        
        insights.append(f"✅ {best_defects[0]} has lowest defect rate ({best_defects[1]['defects']:.1f}%) - quality leader")
        if worst_defects[1]['defects'] > 8:
            insights.append(f"🔧 {worst_defects[0]} has high defects ({worst_defects[1]['defects']:.1f}%) - quality review needed")
            recommendations.append("Implement quality checkpoints and staff training")
            recommendations.append("Review processing procedures")
        elif worst_defects[1]['defects'] > 5:
            insights.append(f"⚠️ {worst_defects[0]} has elevated defects ({worst_defects[1]['defects']:.1f}%) - monitor closely")
            recommendations.append("Improve quality control processes")
        else:
            insights.append(f"📊 {worst_defects[0]} has defects at {worst_defects[1]['defects']:.1f}% - acceptable")
        
        if worst_uptime[1]['machinery_uptime'] < 85:
            insights.append(f"⚙️ {worst_uptime[0]} needs machinery maintenance ({worst_uptime[1]['machinery_uptime']:.0f}% uptime)")
            recommendations.append("Schedule preventive equipment maintenance")
            recommendations.append("Consider upgrading aging machinery")
        if best_uptime[1]['machinery_uptime'] > 95:
            insights.append(f"✅ {best_uptime[0]} has excellent machinery performance ({best_uptime[1]['machinery_uptime']:.0f}%)")
        
        # Defect gap analysis
        defect_gap = worst_defects[1]['defects'] - best_defects[1]['defects']
        if defect_gap > 3:
            insights.append(f"📈 Defect rate gap of {defect_gap:.1f}% - standardization opportunity")
            recommendations.append("Share quality control best practices")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['defects'] == worst_defects[1]['defects'] and metrics['defects'] > 5:
                farm_insights[farm] = f"High defects ({metrics['defects']:.1f}%)"
            elif metrics['machinery_uptime'] == best_uptime[1]['machinery_uptime'] and metrics['machinery_uptime'] > 95:
                farm_insights[farm] = f"Excellent machinery ({metrics['machinery_uptime']:.0f}%)"
            else:
                farm_insights[farm] = f"Defects: {metrics['defects']:.1f}%"
    
    # Transportation insights
    elif section == 'transportation':
        best_delays = min(farms_data.items(), key=lambda x: x[1]['delays'])
        worst_delays = max(farms_data.items(), key=lambda x: x[1]['delays'])
        # Calculate fuel usage from data if available
        fuel_data = {}
        for farm_name, data in all_farms.items():
            fuel_data[farm_name] = float(data['FuelUsage_L_per_100km'].mean())
        best_fuel = min(fuel_data.items(), key=lambda x: x[1]) if fuel_data else None
        worst_fuel = max(fuel_data.items(), key=lambda x: x[1]) if fuel_data else None
        
        insights.append(f"✅ {best_delays[0]} has best on-time delivery ({100-best_delays[1]['delays']:.0f}%) - logistics leader")
        if worst_delays[1]['delays'] > 15:
            insights.append(f"🚨 {worst_delays[0]} has high delays ({worst_delays[1]['delays']:.0f}%) - urgent optimization needed")
            recommendations.append("Optimize delivery routes and schedules")
            recommendations.append("Review carrier performance and contracts")
        elif worst_delays[1]['delays'] > 10:
            insights.append(f"⚠️ {worst_delays[0]} needs delay reduction ({worst_delays[1]['delays']:.0f}%)")
            recommendations.append("Optimize route planning and scheduling")
        else:
            insights.append(f"📊 {worst_delays[0]} has delays at {worst_delays[1]['delays']:.0f}% - acceptable")
        
        if best_fuel and worst_fuel:
            if best_fuel[1] < worst_fuel[1] * 0.8:
                insights.append(f"⛽ {best_fuel[0]} has best fuel efficiency ({best_fuel[1]:.0f}L/100km)")
            if worst_fuel[1] > 30:
                insights.append(f"⛽ {worst_fuel[0]} has high fuel consumption ({worst_fuel[1]:.0f}L/100km) - optimize routes")
                recommendations.append("Consider fuel-efficient vehicles and route optimization")
        
        # Delay gap analysis
        delay_gap = worst_delays[1]['delays'] - best_delays[1]['delays']
        if delay_gap > 5:
            insights.append(f"📈 Delivery delay gap of {delay_gap:.0f}% - logistics improvement opportunity")
            recommendations.append("Share best practices for logistics optimization")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['delays'] == worst_delays[1]['delays'] and metrics['delays'] > 10:
                farm_insights[farm] = f"High delays ({metrics['delays']:.0f}%)"
            elif metrics['delays'] == best_delays[1]['delays']:
                farm_insights[farm] = f"On-time ({100-metrics['delays']:.0f}%)"
            else:
                farm_insights[farm] = f"Delays: {metrics['delays']:.0f}%"
    
    # Retail insights
    elif section == 'retail':
        best_waste = min(farms_data.items(), key=lambda x: x[1]['waste'])
        worst_waste = max(farms_data.items(), key=lambda x: x[1]['waste'])
        
        insights.append(f"✅ {best_waste[0]} has lowest retail waste ({best_waste[1]['waste']:.1f}%)")
        if worst_waste[1]['waste'] > 12:
            insights.append(f"🗑️ {worst_waste[0]} has high waste ({worst_waste[1]['waste']:.1f}%)")
            recommendations.append("Implement dynamic pricing strategy")
        elif worst_waste[1]['waste'] > 10:
            insights.append(f"⚠️ {worst_waste[0]} needs waste reduction ({worst_waste[1]['waste']:.1f}%)")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['waste'] == worst_waste[1]['waste'] and metrics['waste'] > 10:
                farm_insights[farm] = f"High waste ({metrics['waste']:.1f}%)"
            elif metrics['waste'] == best_waste[1]['waste']:
                farm_insights[farm] = f"Low waste ({metrics['waste']:.1f}%)"
            else:
                farm_insights[farm] = f"Waste: {metrics['waste']:.1f}%"
    
    # Consumption insights
    elif section == 'consumption':
        best_satisfaction = max(farms_data.items(), key=lambda x: x[1]['satisfaction'])
        worst_satisfaction = min(farms_data.items(), key=lambda x: x[1]['satisfaction'])
        
        insights.append(f"⭐ {best_satisfaction[0]} has highest satisfaction ({best_satisfaction[1]['satisfaction']:.1f}/10)")
        if worst_satisfaction[1]['satisfaction'] < 7:
            insights.append(f"😞 {worst_satisfaction[0]} needs quality improvement ({worst_satisfaction[1]['satisfaction']:.1f}/10)")
            recommendations.append("Improve product quality and customer service")
        elif worst_satisfaction[1]['satisfaction'] < 8:
            insights.append(f"⚠️ {worst_satisfaction[0]} has moderate satisfaction ({worst_satisfaction[1]['satisfaction']:.1f}/10)")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['satisfaction'] == best_satisfaction[1]['satisfaction']:
                farm_insights[farm] = f"Top satisfaction ({metrics['satisfaction']:.1f}/10)"
            elif metrics['satisfaction'] == worst_satisfaction[1]['satisfaction'] and metrics['satisfaction'] < 7:
                farm_insights[farm] = f"Low satisfaction ({metrics['satisfaction']:.1f}/10)"
            else:
                farm_insights[farm] = f"Satisfaction: {metrics['satisfaction']:.1f}/10"
    
    # Waste insights
    elif section == 'waste':
        best_segregation = max(farms_data.items(), key=lambda x: x[1]['segregation'])
        worst_segregation = min(farms_data.items(), key=lambda x: x[1]['segregation'])
        best_upcycling = max(farms_data.items(), key=lambda x: x[1]['upcycling'])
        worst_upcycling = min(farms_data.items(), key=lambda x: x[1]['upcycling'])
        best_biogas = max(farms_data.items(), key=lambda x: x[1]['biogas'])
        worst_biogas = min(farms_data.items(), key=lambda x: x[1]['biogas'])
        
        # Show meaningful differences even if small
        seg_diff = best_segregation[1]['segregation'] - worst_segregation[1]['segregation']
        upcy_diff = best_upcycling[1]['upcycling'] - worst_upcycling[1]['upcycling']
        bio_diff = best_biogas[1]['biogas'] - worst_biogas[1]['biogas']
        
        insights.append(f"🏆 {best_segregation[0]} leads in waste segregation ({best_segregation[1]['segregation']:.1f}%) - best practice")
        if seg_diff > 0.5:
            insights.append(f"⚠️ {worst_segregation[0]} needs segregation improvement ({worst_segregation[1]['segregation']:.1f}%)")
            recommendations.append("Implement waste sorting training and clear labeling")
        else:
            insights.append(f"📊 All farms have similar segregation accuracy ({worst_segregation[1]['segregation']:.1f}%-{best_segregation[1]['segregation']:.1f}%)")
        
        if upcy_diff > 2:
            insights.append(f"🌱 {best_upcycling[0]} has best upcycling rate ({best_upcycling[1]['upcycling']:.1f}%) - circular economy leader")
            if worst_upcycling[1]['upcycling'] < 45:
                insights.append(f"🔄 {worst_upcycling[0]} needs upcycling boost ({worst_upcycling[1]['upcycling']:.1f}%) - opportunity identified")
                recommendations.append("Develop upcycling partnerships and processes")
                recommendations.append("Explore new upcycling markets")
            else:
                insights.append(f"📊 Upcycling rates range from {worst_upcycling[1]['upcycling']:.1f}% to {best_upcycling[1]['upcycling']:.1f}%")
        
        if bio_diff > 5:
            insights.append(f"⚡ {best_biogas[0]} generates most biogas ({best_biogas[1]['biogas']:.1f}m³) - energy efficiency leader")
            if worst_biogas[1]['biogas'] < 48:
                insights.append(f"⚠️ {worst_biogas[0]} can improve biogas output ({worst_biogas[1]['biogas']:.1f}m³)")
                recommendations.append("Optimize biogas production processes")
                recommendations.append("Review anaerobic digestion efficiency")
            else:
                insights.append(f"📊 Biogas output ranges from {worst_biogas[1]['biogas']:.1f}m³ to {best_biogas[1]['biogas']:.1f}m³")
        
        # Overall waste management performance
        if best_upcycling[1]['upcycling'] > 50 and best_biogas[1]['biogas'] > 50:
            insights.append(f"✅ {best_upcycling[0]} demonstrates excellent circular economy practices")
        
        # Farm-specific insights
        for farm, metrics in farms_data.items():
            if metrics['segregation'] == best_segregation[1]['segregation']:
                farm_insights[farm] = f"Best segregation ({metrics['segregation']:.1f}%)"
            elif metrics['upcycling'] == best_upcycling[1]['upcycling']:
                farm_insights[farm] = f"Best upcycling ({metrics['upcycling']:.1f}%)"
            elif metrics['biogas'] == best_biogas[1]['biogas']:
                farm_insights[farm] = f"Highest biogas ({metrics['biogas']:.1f}m³)"
            elif metrics['segregation'] == worst_segregation[1]['segregation'] and seg_diff > 0.5:
                farm_insights[farm] = f"Segregation: {metrics['segregation']:.1f}%"
            elif metrics['upcycling'] == worst_upcycling[1]['upcycling'] and upcy_diff > 2:
                farm_insights[farm] = f"Upcycling: {metrics['upcycling']:.1f}%"
            else:
                farm_insights[farm] = f"Seg: {metrics['segregation']:.0f}% | Upcy: {metrics['upcycling']:.0f}%"
    
    # Overview insights
    else:  # overview
        best_yield = max(farms_data.items(), key=lambda x: x[1]['yield'])
        worst_spoilage = max(farms_data.items(), key=lambda x: x[1]['spoilage'])
        best_satisfaction = max(farms_data.items(), key=lambda x: x[1]['satisfaction'])
        worst_performer = min(farms_data.items(), key=lambda x: (
            x[1]['yield'] / 10 - x[1]['spoilage'] / 20 + x[1]['satisfaction'] / 10
        ))
        
        insights.append(f"🏆 {best_yield[0]} leads in production ({best_yield[1]['yield']:.1f}t/ha)")
        if worst_spoilage[1]['spoilage'] > 15:
            insights.append(f"❌ {worst_spoilage[0]} needs attention - high spoilage ({worst_spoilage[1]['spoilage']:.1f}%)")
            recommendations.append("Improve storage and cold chain management")
        insights.append(f"⭐ {best_satisfaction[0]} has highest satisfaction ({best_satisfaction[1]['satisfaction']:.1f}/10)")
        
        # Farm-specific insights based on performance score
        for farm, metrics in farms_data.items():
            score = (metrics['yield'] / 10 * 20 + 
                    (1 - metrics['spoilage'] / 30) * 15 +
                    metrics['satisfaction'] / 10 * 15)
            if score > 70:
                farm_insights[farm] = "Excellent performance"
            elif score > 55:
                farm_insights[farm] = "Good performance"
            else:
                farm_insights[farm] = "Needs improvement"
    
    # Ensure all farms have insights
    for farm in farms_data.keys():
        if farm not in farm_insights or not farm_insights[farm]:
            farm_insights[farm] = "Performance within range"
    
    # Ensure we have 5-6 insights for better UI appearance
    if len(insights) < 5:
        # Add more comparison insights if needed
        if section == 'production':
            best_uptime = max(farms_data.items(), key=lambda x: x[1]['harvest_uptime'])
            insights.append(f"⚙️ {best_uptime[0]} has best harvest uptime ({best_uptime[1]['harvest_uptime']:.0f}%)")
        elif section == 'storage':
            best_temp = min(farms_data.items(), key=lambda x: abs(x[1]['storage_temp'] - 3.5))
            insights.append(f"🌡️ {best_temp[0]} has optimal storage temperature ({best_temp[1]['storage_temp']:.1f}°C)")
        elif section == 'processing':
            best_uptime = max(farms_data.items(), key=lambda x: x[1]['machinery_uptime'])
            insights.append(f"⚙️ {best_uptime[0]} has best machinery uptime ({best_uptime[1]['machinery_uptime']:.0f}%)")
    
    # Limit insights to top 5-6 most important
    if len(insights) > 6:
        # Prioritize critical insights
        critical = [i for i in insights if '❌' in i or '🚨' in i]
        warnings = [i for i in insights if '⚠️' in i]
        positives = [i for i in insights if '🏆' in i or '⭐' in i or '✅' in i]
        others = [i for i in insights if i not in critical and i not in warnings and i not in positives]
        insights = (critical[:2] + warnings[:2] + positives[:1] + others[:1])[:6]
    
    # Limit recommendations to top 3-4
    if len(recommendations) > 4:
        recommendations = recommendations[:4]
    
    return jsonify({
        'insights': insights, 
        'recommendations': recommendations,
        'type': 'comparison',
        'farm_insights': farm_insights
    })

def generate_farm_insights(farm_name, data, section):
    """Generate comprehensive insights for a specific farm and section - 5-6 insights with optimization suggestions"""
    insights = []
    recommendations = []
    
    if section == 'overview' or section == 'production':
        yield_avg = float(data['Yield_tonnes_per_ha'].mean())
        yield_std = float(data['Yield_tonnes_per_ha'].std())
        pest_risk = float(data['PestRiskScore'].mean())
        uptime = float(data['HarvestRobotUptime_%'].mean())
        fertilizer = float(data['Fertilizer_kg_per_ha'].mean())
        rainfall = float(data['Rainfall_mm'].mean())
        
        optimal_yield = 7.0
        critical_pest = 50
        optimal_uptime = 90
        
        # Yield insights
        if yield_avg < optimal_yield * 0.8:
            insights.append(f"⚠️ Low yield ({yield_avg:.1f}t/ha) - below optimal threshold")
            recommendations.append("Optimize soil nutrition and crop rotation")
            recommendations.append("Consider precision agriculture techniques")
        elif yield_avg > optimal_yield:
            insights.append(f"✅ Good yield ({yield_avg:.1f}t/ha) - above industry average")
        else:
            insights.append(f"📊 Yield at {yield_avg:.1f}t/ha - within acceptable range")
        
        # Yield variability
        if yield_std > yield_avg * 0.3:
            insights.append(f"📈 High yield variability ({yield_std:.1f}) - inconsistent practices detected")
            recommendations.append("Standardize farming procedures across fields")
        
        # Pest management
        if pest_risk > critical_pest:
            insights.append(f"🐛 High pest risk ({pest_risk:.0f}) - requires immediate attention")
            recommendations.append("Implement integrated pest management (IPM)")
            recommendations.append("Schedule regular field inspections")
        elif pest_risk < 20:
            insights.append(f"✅ Excellent pest control (risk: {pest_risk:.0f})")
        else:
            insights.append(f"🛡️ Pest risk at {pest_risk:.0f} - monitor regularly")
        
        # Equipment uptime
        if uptime < optimal_uptime:
            insights.append(f"⚙️ Low harvest uptime ({uptime:.0f}%) - maintenance needed")
            recommendations.append("Schedule preventive maintenance for harvest equipment")
        elif uptime > 95:
            insights.append(f"✅ Excellent machinery uptime ({uptime:.0f}%)")
        else:
            insights.append(f"⚙️ Harvest uptime at {uptime:.0f}% - can be improved")
        
        # Fertilizer optimization
        if fertilizer > 250:
            insights.append(f"🌾 High fertilizer usage ({fertilizer:.0f}kg/ha) - optimize for cost efficiency")
            recommendations.append("Conduct soil tests to optimize fertilizer application")
    
    if section == 'overview' or section == 'storage':
        spoilage = float(data['SpoilageRate_%'].mean())
        temp = float(data['StorageTemperature_C'].mean())
        humidity = float(data['Humidity_%'].mean())
        shelf_life = float(data['PredictedShelfLife_days'].mean())
        storage_days = float(data['StorageDays'].mean())
        critical_spoilage = 15
        optimal_temp_range = (2, 5)
        optimal_humidity = (75, 85)
        
        # Spoilage insights
        if spoilage > critical_spoilage:
            insights.append(f"❌ Critical spoilage ({spoilage:.1f}%) - immediate intervention required")
            recommendations.append("Review cold chain integrity and storage protocols")
            recommendations.append("Implement real-time monitoring systems")
        elif spoilage > 10:
            insights.append(f"⚠️ Elevated spoilage ({spoilage:.1f}%) - monitor closely")
            recommendations.append("Optimize storage conditions")
        elif spoilage < 5:
            insights.append(f"✅ Low spoilage ({spoilage:.1f}%) - excellent storage management")
        else:
            insights.append(f"📦 Spoilage at {spoilage:.1f}% - within acceptable limits")
        
        # Temperature control
        if temp < optimal_temp_range[0] or temp > optimal_temp_range[1]:
            insights.append(f"🌡️ Temperature out of range ({temp:.1f}°C) - optimal is 2-5°C")
            recommendations.append("Calibrate refrigeration systems")
            recommendations.append("Install temperature monitoring alarms")
        else:
            insights.append(f"✅ Optimal storage temperature ({temp:.1f}°C)")
        
        # Humidity control
        if humidity < optimal_humidity[0] or humidity > optimal_humidity[1]:
            insights.append(f"💧 Humidity at {humidity:.0f}% - optimal range is 75-85%")
            recommendations.append("Adjust humidity control systems")
        else:
            insights.append(f"✅ Optimal humidity levels ({humidity:.0f}%)")
        
        # Shelf life optimization
        if shelf_life < 10:
            insights.append(f"⏱️ Short shelf life ({shelf_life:.1f} days) - quality preservation needs improvement")
            recommendations.append("Review harvest timing and handling practices")
        else:
            insights.append(f"✅ Good shelf life ({shelf_life:.1f} days)")
    
    if section == 'overview' or section == 'processing':
        defect_rate = float(data['DefectRate_%'].mean())
        machinery_uptime = float(data['MachineryUptime_%'].mean())
        packaging_speed = float(data['PackagingSpeed_units_per_min'].mean())
        critical_defects = 5
        optimal_uptime = 95
        
        # Defect rate
        if defect_rate > critical_defects:
            insights.append(f"🔧 High defect rate ({defect_rate:.1f}%) - quality control review needed")
            recommendations.append("Implement quality checkpoints and staff training")
            recommendations.append("Review processing procedures")
        elif defect_rate < 2:
            insights.append(f"✅ Excellent quality control ({defect_rate:.1f}% defects)")
        else:
            insights.append(f"📊 Defect rate at {defect_rate:.1f}% - within acceptable range")
        
        # Machinery uptime
        if machinery_uptime < optimal_uptime:
            downtime = 100 - machinery_uptime
            insights.append(f"⚙️ High machinery downtime ({downtime:.0f}%) - affecting productivity")
            recommendations.append("Schedule equipment maintenance")
            recommendations.append("Consider upgrading aging machinery")
        elif machinery_uptime > 98:
            insights.append(f"✅ Excellent machinery performance ({machinery_uptime:.0f}% uptime)")
        else:
            insights.append(f"⚙️ Machinery uptime at {machinery_uptime:.0f}% - good performance")
        
        # Processing efficiency
        if packaging_speed < 300:
            insights.append(f"📦 Low packaging speed ({packaging_speed:.0f} units/min) - efficiency can be improved")
            recommendations.append("Optimize packaging workflows")
        else:
            insights.append(f"✅ Good packaging efficiency ({packaging_speed:.0f} units/min)")
        
        # Process type analysis
        defect_by_process = data.groupby('ProcessType')['DefectRate_%'].mean()
        if len(defect_by_process) > 0:
            worst_process = defect_by_process.idxmax()
            if defect_by_process.max() > critical_defects:
                insights.append(f"🔍 {worst_process} process has highest defects ({defect_by_process.max():.1f}%)")
                recommendations.append(f"Review and optimize {worst_process} procedures")
    
    if section == 'overview' or section == 'transportation':
        delays = float((data['DeliveryDelayFlag'].sum() / len(data) * 100))
        fuel_usage = float(data['FuelUsage_L_per_100km'].mean())
        transit_spoilage = float(data['SpoilageInTransit_%'].mean())
        distance = float(data['TransportDistance_km'].mean())
        critical_delays = 15
        optimal_fuel = 25
        
        # Delivery delays
        if delays > critical_delays:
            insights.append(f"🚨 High delay rate ({delays:.0f}%) - logistics optimization urgent")
            recommendations.append("Optimize delivery routes and schedules")
            recommendations.append("Review carrier performance and contracts")
        elif delays > 10:
            insights.append(f"⚠️ Moderate delays ({delays:.0f}%) - monitor transportation efficiency")
            recommendations.append("Optimize route planning")
        elif delays < 5:
            insights.append(f"✅ Excellent on-time delivery ({100-delays:.0f}%)")
        else:
            insights.append(f"🚚 Delivery delays at {delays:.0f}% - within acceptable range")
        
        # Fuel efficiency
        if fuel_usage > optimal_fuel * 1.2:
            insights.append(f"⛽ High fuel consumption ({fuel_usage:.0f}L/100km) - route optimization needed")
            recommendations.append("Optimize delivery routes")
            recommendations.append("Consider fuel-efficient vehicles")
        else:
            insights.append(f"✅ Fuel efficiency at {fuel_usage:.0f}L/100km - good performance")
        
        # Transit spoilage
        if transit_spoilage > 5:
            insights.append(f"📦 Transit spoilage ({transit_spoilage:.1f}%) - handling issues detected")
            recommendations.append("Improve packaging and handling during transportation")
        else:
            insights.append(f"✅ Low transit spoilage ({transit_spoilage:.1f}%)")
        
        # Distance optimization
        if distance > 1000:
            insights.append(f"📍 Long average distance ({distance:.0f}km) - consider distribution centers")
            recommendations.append("Evaluate distribution center locations")
    
    if section == 'overview' or section == 'retail':
        waste = float(data['WastePercentage_%'].mean())
        inventory = float(data['RetailInventory_units'].sum())
        sales_velocity = float(data['SalesVelocity_units_per_day'].mean())
        pricing_index = float(data['DynamicPricingIndex'].mean())
        critical_waste = 12
        
        # Waste management
        if waste > critical_waste:
            insights.append(f"🗑️ High retail waste ({waste:.1f}%) - pricing strategy review needed")
            recommendations.append("Implement dynamic pricing and markdown strategies")
            recommendations.append("Optimize inventory levels")
        elif waste < 5:
            insights.append(f"✅ Low waste ({waste:.1f}%) - excellent waste management")
        else:
            insights.append(f"📊 Waste at {waste:.1f}% - within acceptable range")
        
        # Inventory optimization
        if sales_velocity > 0:
            days_of_inventory = inventory / (sales_velocity * len(data)) if len(data) > 0 else 0
            if days_of_inventory > 30:
                insights.append(f"📦 High inventory levels ({days_of_inventory:.0f} days) - risk of overstocking")
                recommendations.append("Adjust procurement to match sales velocity")
            elif days_of_inventory < 7:
                insights.append(f"⚡ Low inventory ({days_of_inventory:.0f} days) - risk of stockouts")
                recommendations.append("Increase safety stock levels")
            else:
                insights.append(f"✅ Optimal inventory levels ({days_of_inventory:.0f} days)")
        
        # Pricing optimization
        if pricing_index < 0.9:
            insights.append(f"💰 Low pricing index ({pricing_index:.2f}) - revenue optimization opportunity")
            recommendations.append("Implement dynamic pricing strategies")
        else:
            insights.append(f"✅ Good pricing strategy (index: {pricing_index:.2f})")
    
    if section == 'overview' or section == 'consumption':
        satisfaction = float(data['SatisfactionScore_0_10'].mean())
        household_waste = float(data['HouseholdWaste_kg'].mean())
        recipe_accuracy = float(data['RecipeRecommendationAccuracy_%'].mean())
        
        # Customer satisfaction
        if satisfaction < 7:
            insights.append(f"😞 Low customer satisfaction ({satisfaction:.1f}/10) - quality improvement needed")
            recommendations.append("Gather customer feedback and improve product quality")
            recommendations.append("Enhance customer service")
        elif satisfaction > 8:
            insights.append(f"⭐ High customer satisfaction ({satisfaction:.1f}/10) - excellent performance")
        else:
            insights.append(f"📊 Customer satisfaction at {satisfaction:.1f}/10 - good performance")
        
        # Household waste
        if household_waste > 3:
            insights.append(f"🍽️ High household waste ({household_waste:.2f}kg) - consumer education needed")
            recommendations.append("Promote meal planning and portion control education")
        else:
            insights.append(f"✅ Low household waste ({household_waste:.2f}kg)")
        
        # Recipe recommendations
        if recipe_accuracy < 80:
            insights.append(f"📱 Recipe accuracy at {recipe_accuracy:.1f}% - improvement needed")
            recommendations.append("Improve recipe recommendation algorithms")
        else:
            insights.append(f"✅ Good recipe accuracy ({recipe_accuracy:.1f}%)")
    
    if section == 'overview' or section == 'waste':
        segregation = float(data['SegregationAccuracy_%'].mean())
        upcycling = float(data['UpcyclingRate_%'].mean())
        biogas = float(data['BiogasOutput_m3'].mean())
        
        # Waste segregation
        if segregation < 85:
            insights.append(f"♻️ Low segregation accuracy ({segregation:.0f}%) - training needed")
            recommendations.append("Implement waste sorting training and clear labeling")
        elif segregation > 90:
            insights.append(f"✅ Excellent waste segregation ({segregation:.0f}%)")
        else:
            insights.append(f"📊 Segregation at {segregation:.0f}% - good performance")
        
        # Upcycling opportunities
        if upcycling < 45:
            insights.append(f"🔄 Low upcycling rate ({upcycling:.0f}%) - circular economy opportunity")
            recommendations.append("Develop upcycling partnerships and processes")
            recommendations.append("Explore new upcycling markets")
        elif upcycling > 70:
            insights.append(f"🌱 Excellent upcycling performance ({upcycling:.0f}%)")
        else:
            insights.append(f"♻️ Upcycling at {upcycling:.0f}% - can be improved")
        
        # Biogas production
        if biogas < 48:
            insights.append(f"⚡ Low biogas output ({biogas:.0f}m³) - optimization opportunity")
            recommendations.append("Optimize biogas production processes")
            recommendations.append("Review anaerobic digestion efficiency")
        elif biogas > 55:
            insights.append(f"✅ High biogas production ({biogas:.0f}m³)")
        else:
            insights.append(f"📊 Biogas output at {biogas:.0f}m³ - within range")
    
    # Ensure we have 5-6 insights for better UI appearance
    if len(insights) < 5:
        # Add some general insights if we don't have enough
        if section == 'overview':
            score = calculate_performance_score_from_data(data)
            if score > 75:
                insights.append(f"🏆 Overall performance score: {score:.0f}/100 - excellent")
            elif score > 60:
                insights.append(f"📊 Overall performance score: {score:.0f}/100 - good")
            else:
                insights.append(f"⚠️ Overall performance score: {score:.0f}/100 - needs improvement")
    
    # Limit to 6 most important insights
    if len(insights) > 6:
        critical = [i for i in insights if '❌' in i or '🚨' in i]
        warnings = [i for i in insights if '⚠️' in i]
        positives = [i for i in insights if '✅' in i or '🏆' in i or '⭐' in i]
        others = [i for i in insights if i not in critical and i not in warnings and i not in positives]
        insights = (critical[:2] + warnings[:2] + positives[:1] + others[:1])[:6]
    
    # Limit recommendations to 4-5 most actionable
    if len(recommendations) > 5:
        recommendations = recommendations[:5]
    
    # If no insights, provide status
    if not insights:
        insights.append("✅ All metrics optimal")
        insights.append("📊 Continue monitoring key performance indicators")
    
    # Generate concise one-line summary for card display
    concise_insight = ""
    if insights:
        critical_insights = [i for i in insights if '❌' in i or '⚠️' in i or '🚨' in i]
        if critical_insights:
            concise_insight = critical_insights[0].replace('❌ ', '').replace('⚠️ ', '').replace('🚨 ', '')
        else:
            concise_insight = insights[0].replace('✅ ', '').replace('🏆 ', '').replace('⭐ ', '')
        if len(concise_insight) > 50:
            concise_insight = concise_insight[:47] + '...'
    
    return jsonify({
        'insights': insights,
        'recommendations': recommendations,
        'type': 'farm_specific',
        'farm': farm_name,
        'section': section,
        'concise_insight': concise_insight
    })

@app.route('/details/all/<stage>')
def view_comparison_details(stage):
    """View comparison details for all farms for a specific stage"""
    all_farms = load_all_farms_data()
    
    stage_fields = {
        'production': ['BatchID', 'CropType', 'FarmLocation', 'SoilMoisture_%', 'Temperature_C', 'Rainfall_mm', 'Fertilizer_kg_per_ha', 'Yield_tonnes_per_ha', 'PestRiskScore', 'HarvestRobotUptime_%'],
        'storage': ['BatchID', 'CropType', 'GradingScore', 'StorageTemperature_C', 'Humidity_%', 'SpoilageRate_%', 'PredictedShelfLife_days', 'StorageDays'],
        'processing': ['BatchID', 'ProcessType', 'PackagingType', 'PackagingSpeed_units_per_min', 'DefectRate_%', 'MachineryUptime_%'],
        'transportation': ['BatchID', 'TransportMode', 'TransportDistance_km', 'FuelUsage_L_per_100km', 'DeliveryTime_hr', 'DeliveryDelayFlag', 'SpoilageInTransit_%'],
        'retail': ['BatchID', 'CropType', 'RetailInventory_units', 'SalesVelocity_units_per_day', 'DynamicPricingIndex', 'WastePercentage_%'],
        'consumption': ['BatchID', 'HouseholdWaste_kg', 'RecipeRecommendationAccuracy_%', 'SatisfactionScore_0_10'],
        'waste': ['BatchID', 'WasteType', 'SegregationAccuracy_%', 'UpcyclingRate_%', 'BiogasOutput_m3'],
        'overview': ['BatchID', 'CropType', 'Yield_tonnes_per_ha', 'SpoilageRate_%', 'DefectRate_%', 'WastePercentage_%']
    }

    fields = stage_fields.get(stage, [])
    if not fields:
        return "Stage not found", 404

    # Aggregate data by farm and create a pivoted table with farms as columns
    farm_stats = {}
    for farm_name, data in all_farms.items():
        farm_data = data[[f for f in fields if f in data.columns]].copy()
        # Calculate mean for numeric columns, mode for categorical
        stats = {}
        for col in farm_data.columns:
            if farm_data[col].dtype in ['int64', 'float64']:
                stats[col] = farm_data[col].mean()
            else:
                # For categorical, get the most common value
                stats[col] = farm_data[col].mode()[0] if len(farm_data[col].mode()) > 0 else farm_data[col].iloc[0]
        farm_stats[farm_name] = stats
    
    # Create a DataFrame with metrics as rows and farms as columns
    metrics_df = pd.DataFrame.from_dict(farm_stats, orient='index').T
    # Transpose so farms are columns and metrics are rows
    comparison_df = metrics_df.T
    comparison_df.index.name = 'Metric'
    comparison_df = comparison_df.reset_index()

    stage_titles = {
        'production': 'Production Stage',
        'storage': 'Storage & Post-Harvest',
        'processing': 'Processing & Packaging',
        'transportation': 'Distribution & Transportation',
        'retail': 'Retail Insights',
        'consumption': 'Consumption & Household',
        'waste': 'Waste Management',
        'overview': 'Dashboard Overview'
    }

    stage_title = stage_titles.get(stage, stage.title())
    
    # Format numeric values
    for col in comparison_df.columns:
        if col != 'Metric':
            comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else str(x))
    
    table_html = comparison_df.to_html(classes='details-table', index=False, escape=False)
    total_records = len(comparison_df)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Farms - {stage_title} Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 30px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid #1a5f7a; padding-bottom: 15px; }}
        .header h1 {{ color: #1a5f7a; font-size: 28px; }}
        .back-btn {{ background: #1a5f7a; color: white; padding: 10px 20px; border: none; border-radius: 12px; cursor: pointer; font-size: 14px; transition: background 0.3s; text-decoration: none; display: inline-block; }}
        .back-btn:hover {{ background: #0f3a4f; }}
        .record-info {{ background: #ecf0f1; padding: 15px; border-radius: 12px; margin-bottom: 20px; }}
        .table-wrapper {{ overflow-x: auto; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .details-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .details-table thead {{ background-color: #1a5f7a; color: white; }}
        .details-table th {{ padding: 12px; text-align: left; font-weight: 600; position: sticky; top: 0; }}
        .details-table td {{ padding: 10px 12px; border-bottom: 1px solid #ddd; text-align: left; }}
        .details-table tbody tr:hover {{ background-color: #f5f5f5; }}
        .details-table tbody tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .details-table td:first-child {{ font-weight: 600; color: #1a5f7a; background-color: #f0f8ff; }}
        .details-table th:first-child {{ background-color: #0f3a4f; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>All Farms - {stage_title} Comparison</h1>
            </div>
            <a href="/" class="back-btn">← Back to Dashboard</a>
        </div>

        <div class="record-info">
            <strong>Total Metrics:</strong> {total_records} | 
            <strong>View:</strong> Farm Comparison (Farms as Columns)
        </div>

        <div class="table-wrapper">
            {table_html}
        </div>
    </div>
</body>
</html>"""

    return html_content

@app.route('/details/<farm_name>/<stage>')
def view_details(farm_name, stage):
    """View detailed records for each stage with pagination"""
    data = load_farm_data(farm_name)
    if data.empty:
        return f"Farm {farm_name} not found", 404
    
    stage_fields = {
        'production': ['BatchID', 'CropType', 'FarmLocation', 'SoilMoisture_%', 'Temperature_C', 'Rainfall_mm', 'Fertilizer_kg_per_ha', 'Yield_tonnes_per_ha', 'PestRiskScore', 'HarvestRobotUptime_%'],
        'storage': ['BatchID', 'CropType', 'GradingScore', 'StorageTemperature_C', 'Humidity_%', 'SpoilageRate_%', 'PredictedShelfLife_days', 'StorageDays'],
        'processing': ['BatchID', 'ProcessType', 'PackagingType', 'PackagingSpeed_units_per_min', 'DefectRate_%', 'MachineryUptime_%'],
        'transportation': ['BatchID', 'TransportMode', 'TransportDistance_km', 'FuelUsage_L_per_100km', 'DeliveryTime_hr', 'DeliveryDelayFlag', 'SpoilageInTransit_%'],
        'retail': ['BatchID', 'CropType', 'RetailInventory_units', 'SalesVelocity_units_per_day', 'DynamicPricingIndex', 'WastePercentage_%'],
        'consumption': ['BatchID', 'HouseholdWaste_kg', 'RecipeRecommendationAccuracy_%', 'SatisfactionScore_0_10'],
        'waste': ['BatchID', 'WasteType', 'SegregationAccuracy_%', 'UpcyclingRate_%', 'BiogasOutput_m3'],
        'overview': ['BatchID', 'CropType', 'Yield_tonnes_per_ha', 'SpoilageRate_%', 'DefectRate_%', 'WastePercentage_%']
    }

    fields = stage_fields.get(stage, [])
    if not fields:
        return "Stage not found", 404

    stage_data = data[[f for f in fields if f in data.columns]].copy()

    page = request.args.get('page', 1, type=int)
    per_page = 50
    total_records = len(stage_data)
    total_pages = (total_records + per_page - 1) // per_page

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_data = stage_data.iloc[start_idx:end_idx]

    stage_titles = {
        'production': 'Production Stage',
        'storage': 'Storage & Post-Harvest',
        'processing': 'Processing & Packaging',
        'transportation': 'Distribution & Transportation',
        'retail': 'Retail Insights',
        'consumption': 'Consumption & Household',
        'waste': 'Waste Management',
        'overview': 'Dashboard Overview'
    }

    stage_title = stage_titles.get(stage, stage.title())
    table_html = paginated_data.to_html(classes='details-table', index=False)

    pagination_html = ''
    if page > 1:
        pagination_html += f'<a href="?page=1">« First</a> <a href="?page={page-1}">‹ Previous</a> '
    for p in range(max(1, page-2), min(total_pages+1, page+3)):
        if p == page:
            pagination_html += f'<span class="current">{p}</span> '
        else:
            pagination_html += f'<a href="?page={p}">{p}</a> '
    if page < total_pages:
        pagination_html += f'<a href="?page={page+1}">Next ›</a> <a href="?page={total_pages}">Last »</a>'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{farm_name} - {stage_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 30px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid #1a5f7a; padding-bottom: 15px; }}
        .header h1 {{ color: #1a5f7a; font-size: 28px; }}
        .back-btn {{ background: #1a5f7a; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; transition: background 0.3s; text-decoration: none; display: inline-block; }}
        .back-btn:hover {{ background: #0f3a4f; }}
        .record-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .table-wrapper {{ overflow-x: auto; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .details-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        .details-table thead {{ background-color: #1a5f7a; color: white; }}
        .details-table th {{ padding: 12px; text-align: left; font-weight: 600; }}
        .details-table td {{ padding: 10px 12px; border-bottom: 1px solid #ddd; }}
        .details-table tbody tr:hover {{ background-color: #f5f5f5; }}
        .details-table tbody tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .pagination {{ display: flex; justify-content: center; gap: 10px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        .pagination a, .pagination span {{ padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; text-decoration: none; color: #1a5f7a; transition: all 0.2s; }}
        .pagination a:hover {{ background: #1a5f7a; color: white; }}
        .pagination .current {{ background: #1a5f7a; color: white; border: 1px solid #1a5f7a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>{farm_name} - {stage_title}</h1>
            </div>
            <a href="/" class="back-btn">← Back to Dashboard</a>
        </div>

        <div class="record-info">
            <strong>Total Records:</strong> {total_records} | 
            <strong>Showing:</strong> {start_idx + 1}-{min(end_idx, total_records)} | 
            <strong>Page:</strong> {page} of {total_pages}
        </div>

        <div class="table-wrapper">
            {table_html}
        </div>

        <div class="pagination">
            {pagination_html}
        </div>
    </div>
</body>
</html>"""

    return html_content

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """AI Chatbot endpoint that answers questions about farms and metrics using Ollama"""
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'response': 'Please ask me a question about the farms!'})
        
        # Load all farm data for context
        all_farms = load_all_farms_data()
        
        # Prepare simple context with farm data
        context = prepare_farm_context(all_farms)
        
        # Create simple prompt for Ollama
        prompt = f"""Food Supply Chain Data:
{context}

Question: {question}

Answer the question based on the data provided above. Be accurate and helpful."""
        
        # Call Ollama API
        ollama_model = os.environ.get('OLLAMA_MODEL', 'llama2')
        
        try:
            ollama_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 200
                    }
                },
                timeout=30
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response_text = result.get('response', '').strip()
                if response_text:
                    return jsonify({'response': response_text})
                else:
                    return jsonify({
                        'response': 'I received an empty response from Ollama. Please ensure Ollama is running and the model is properly installed.'
                    })
            else:
                error_msg = ollama_response.text if hasattr(ollama_response, 'text') else 'Unknown error'
                try:
                    error_json = ollama_response.json()
                    if 'error' in error_json and 'not found' in error_json['error'].lower():
                        return jsonify({
                            'response': f'Model "{ollama_model}" not found. Please install it by running: ollama pull {ollama_model}'
                        })
                except:
                    pass
                
                return jsonify({
                    'response': f'Ollama API error: {error_msg}'
                })
        except requests.exceptions.ConnectionError:
            return jsonify({
                'response': 'Unable to connect to Ollama. Please ensure Ollama is running on your local machine.'
            })
        except requests.exceptions.Timeout:
            return jsonify({
                'response': 'Ollama request timed out. Please try again.'
            })
        except requests.exceptions.RequestException as e:
            return jsonify({
                'response': f'Ollama connection error: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'})

def prepare_farm_context(all_farms):
    """Prepare simple farm data context"""
    context = []
    for farm_name, data in all_farms.items():
        score = calculate_performance_score_from_data(data)
        yield_val = float(data['Yield_tonnes_per_ha'].mean())
        spoilage = float(data['SpoilageRate_%'].mean())
        defects = float(data['DefectRate_%'].mean())
        waste = float(data['WastePercentage_%'].mean())
        satisfaction = float(data['SatisfactionScore_0_10'].mean())
        pest_risk = float(data['PestRiskScore'].mean())
        machinery_uptime = float(data['MachineryUptime_%'].mean())
        
        # Get crop types and their yields for this farm
        crop_yields = data.groupby('CropType')['Yield_tonnes_per_ha'].mean().to_dict()
        crop_spoilage = data.groupby('CropType')['SpoilageRate_%'].mean().to_dict()
        crop_waste = data.groupby('CropType')['WastePercentage_%'].mean().to_dict()
        
        context.append(f"{farm_name}: Score:{score:.0f} Yield:{yield_val:.1f}t/ha Spoilage:{spoilage:.1f}% Defects:{defects:.1f}% Waste:{waste:.1f}% Satisfaction:{satisfaction:.1f}/10")
        context.append(f"  Crops: {', '.join([f'{crop} (yield:{crop_yields[crop]:.1f}t/ha, spoilage:{crop_spoilage.get(crop,0):.1f}%, waste:{crop_waste.get(crop,0):.1f}%)' for crop in crop_yields.keys()])}")
    
    return "\n".join(context)

def calculate_performance_score_from_data(data):
    """Create a comprehensive prompt for Ollama that ensures accurate, professional responses"""
    question_lower = question.lower().strip()
    original_question = question.strip()
    
    # STRICT greeting detection - check if question is ONLY a greeting
    greeting_only_patterns = [
        r'^(hi|hello|hey|greetings)[\s!?.,]*$',
        r'^(good\s+(morning|afternoon|evening))[\s!?.,]*$',
        r'^hi[\s!?.,]*$',
        r'^hello[\s!?.,]*$'
    ]
    
    is_greeting_only = False
    for pattern in greeting_only_patterns:
        if re.match(pattern, question_lower):
            is_greeting_only = True
            break
    
    # Also check if question is just punctuation or very short with no meaningful words
    if not is_greeting_only:
        # Remove greetings and check if anything meaningful remains
        cleaned = re.sub(r'^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))[\s,]*', '', question_lower, flags=re.IGNORECASE)
        cleaned = re.sub(r'[\s,]+(hi|hello|hey|greetings)[\s!?.,]*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip(' \t\n\r!?.,')
        # If nothing meaningful remains after removing greetings, treat as greeting only
        if len(cleaned) == 0 or cleaned in ['', '?', '!', '.', ',']:
            is_greeting_only = True
    
    # For greetings ONLY - return simple prompt without context to avoid timeouts and irrelevant data
    if is_greeting_only:
        return """You are an AI assistant for an AI Food Supply Chain Platform. Answer only what is asked  in the question after thinking and understanding properly based on the question asked and the data provided. Be accurate and helpful."""
    
    # Remove greetings from question while preserving actual question content
    cleaned_question = original_question
    greeting_removal_patterns = [
        r'^(hi|hello|hey|greetings)[\s,]+',
        r'^(good\s+(morning|afternoon|evening))[\s,]+',
        r'[\s,]+(hi|hello|hey|greetings)[\s,]*$'
    ]
    for pattern in greeting_removal_patterns:
        cleaned_question = re.sub(pattern, '', cleaned_question, flags=re.IGNORECASE).strip()
    
    # Use cleaned question for analysis
    question_lower = cleaned_question.lower() if cleaned_question else original_question.lower()
    
    # Detect question type
    is_specific_farm = any(farm in question_lower for farm in ['farma', 'farm a', 'farmb', 'farm b', 'farc', 'farm c', 'farmd', 'farm d'])
    is_comparison = any(word in question_lower for word in ['compare', 'comparison', 'difference', 'versus', 'vs', 'better', 'worse', 'best', 'worst'])
    is_ranking = any(word in question_lower for word in ['rank', 'ranking', 'top', 'bottom', 'highest', 'lowest', 'best', 'worst'])
    is_loss_question = any(word in question_lower for word in ['loss', 'losing', 'lost', 'maximum loss', 'max loss', 'minimum loss', 'min loss'])
    is_crop_question = any(word in question_lower for word in ['crop', 'crops', 'tomato', 'potato', 'wheat', 'corn', 'rice'])
    is_metric_question = any(word in question_lower for word in ['yield', 'spoilage', 'waste', 'defect', 'satisfaction', 'pest', 'machinery', 'delay', 'performance'])
    
    # Build specialized prompt based on question type
    prompt_parts = []
    prompt_parts.append("You are a professional AI assistant for a Food Supply Chain Analytics Platform.")
    prompt_parts.append("")
    prompt_parts.append(context)
    prompt_parts.append("")
    prompt_parts.append(f"User Question: {question}")
    prompt_parts.append("")
    prompt_parts.append("CRITICAL INSTRUCTIONS - READ CAREFULLY:")
    prompt_parts.append("2. Use EXACT numbers from the data - never estimate, guess, or add information")
    prompt_parts.append("3. Be direct and concise")
    prompt_parts.append("4. If the question asks for one thing, provide only that one thing")
    prompt_parts.append("")
    
    # Add specific instructions based on question type
    if is_specific_farm:
        prompt_parts.append("SPECIFIC FARM QUESTION:")
        prompt_parts.append("- Find the farm name (FarmA, FarmB, FarmC, or FarmD) in the question")
        prompt_parts.append("- Use ONLY the 'FARM-LEVEL DETAILS' section for that specific farm")
        prompt_parts.append("- Answer ONLY what is asked about that farm - do not compare or add other farms")
        prompt_parts.append("- If asking about a crop on that farm, provide ONLY that crop's data from that farm")
        prompt_parts.append("")
    
    if is_comparison or is_ranking:
        prompt_parts.append("COMPARISON/RANKING QUESTION:")
        prompt_parts.append("- Use the 'QUICK REFERENCE - FARM RANKINGS' section for rankings")
        prompt_parts.append("- Compare ONLY what is asked - do not provide all metrics")
        prompt_parts.append("- State which farm is better/worse and by how much (use exact numbers)")
        prompt_parts.append("- Keep it focused on the comparison requested")
        prompt_parts.append("")
    
    if is_loss_question:
        prompt_parts.append("LOSS QUESTION:")
        prompt_parts.append("- Check the 'CROP RANKINGS' section for 'Maximum Loss Crop' or 'Lowest Loss Crop'")
        prompt_parts.append("- Answer ONLY the loss question - provide the crop name and loss percentage")
        prompt_parts.append("- Do NOT provide yield, performance scores, or other metrics unless asked")
        prompt_parts.append("- Loss = Spoilage % + Waste % + (Defects % × 0.5)")
        prompt_parts.append("")
    
    if is_crop_question:
        prompt_parts.append("CROP QUESTION:")
        prompt_parts.append("- Use the 'CROP-LEVEL ANALYSIS' section for crop data across all farms")
        prompt_parts.append("- Use 'FARM-LEVEL DETAILS' for crop data on specific farms")
        prompt_parts.append("- Answer ONLY what is asked about the crop - do not provide all metrics")
        prompt_parts.append("")
    
    if is_metric_question:
        prompt_parts.append("METRIC QUESTION:")
        prompt_parts.append("- Identify which metric is being asked about (yield, spoilage, waste, etc.)")
        prompt_parts.append("- Use rankings from 'QUICK REFERENCE' if asking about best/worst")
        prompt_parts.append("- Use 'FARM-LEVEL DETAILS' for specific farm metrics")
        prompt_parts.append("- Answer ONLY the metric asked - do not provide other metrics")
        prompt_parts.append("")
    
    prompt_parts.append("RESPONSE RULES:")
    prompt_parts.append("- Answer ONLY the question asked - nothing more, nothing less")
    prompt_parts.append("- Use exact numbers from data (include units)")
    prompt_parts.append("- If question cannot be answered from data, say so clearly in one sentence")
    prompt_parts.append("")
    prompt_parts.append("Answer only what is asked:")
    
    return "\n".join(prompt_parts)

def answer_question(question, all_farms):
    """Answer questions based on farm data"""
    question_lower = question.lower()
    
    # Farm performance questions
    if any(word in question_lower for word in ['best', 'top', 'highest', 'excellent', 'performing']):
        return get_best_farm_info(all_farms)
    
    if any(word in question_lower for word in ['worst', 'lowest', 'poor', 'needs attention', 'worst performing']):
        return get_worst_farm_info(all_farms)
    
    # Specific farm questions
    for farm_name in ['farma', 'farm a', 'farb', 'farm b', 'farc', 'farm c', 'farmd', 'farm d']:
        if farm_name in question_lower:
            actual_farm = 'FarmA' if 'a' in farm_name else 'FarmB' if 'b' in farm_name else 'FarmC' if 'c' in farm_name else 'FarmD'
            return get_farm_summary(actual_farm, all_farms.get(actual_farm))
    
    # Metric-specific questions
    if any(word in question_lower for word in ['yield', 'production']):
        return get_yield_comparison(all_farms)
    
    if any(word in question_lower for word in ['spoilage', 'spoil']):
        return get_spoilage_comparison(all_farms)
    
    if any(word in question_lower for word in ['waste']):
        return get_waste_comparison(all_farms)
    
    if any(word in question_lower for word in ['satisfaction', 'customer']):
        return get_satisfaction_comparison(all_farms)
    
    if any(word in question_lower for word in ['pest', 'pest risk']):
        return get_pest_comparison(all_farms)
    
    if any(word in question_lower for word in ['machinery', 'uptime', 'downtime']):
        return get_machinery_comparison(all_farms)
    
    if any(word in question_lower for word in ['defect', 'defects']):
        return get_defect_comparison(all_farms)
    
    if any(word in question_lower for word in ['delay', 'delivery']):
        return get_delay_comparison(all_farms)
    
    if any(word in question_lower for word in ['storage', 'temperature', 'humidity']):
        return get_storage_comparison(all_farms)
    
    # Comparison questions
    if any(word in question_lower for word in ['compare', 'comparison', 'difference']):
        return get_general_comparison(all_farms)
    
    # Score questions
    if any(word in question_lower for word in ['score', 'performance score', 'rating']):
        return get_performance_scores(all_farms)
    
    # General help
    if any(word in question_lower for word in ['help', 'what can', 'how can', 'what do you']):
        return get_help_message()
    
    # Default response with suggestions
    return f"I understand you're asking about: '{question}'. Here's what I can help with:\n\n" + get_help_message()

def get_best_farm_info(all_farms):
    """Get information about the best performing farm"""
    scores = {}
    for farm_name, data in all_farms.items():
        score = calculate_performance_score_from_data(data)
        scores[farm_name] = score
    
    best_farm = max(scores, key=scores.get)
    best_score = scores[best_farm]
    data = all_farms[best_farm]
    
    yield_val = float(data['Yield_tonnes_per_ha'].mean())
    spoilage = float(data['SpoilageRate_%'].mean())
    waste = float(data['WastePercentage_%'].mean())
    satisfaction = float(data['SatisfactionScore_0_10'].mean())
    
    return f"🏆 {best_farm} is the best performing farm with a score of {best_score:.1f}/100!\n\n" \
           f"Key metrics:\n" \
           f"• Yield: {yield_val:.2f} tonnes/ha\n" \
           f"• Spoilage: {spoilage:.2f}%\n" \
           f"• Waste: {waste:.2f}%\n" \
           f"• Customer Satisfaction: {satisfaction:.1f}/10\n\n" \
           f"This farm demonstrates excellent performance across multiple metrics."

def get_worst_farm_info(all_farms):
    """Get information about the worst performing farm"""
    scores = {}
    for farm_name, data in all_farms.items():
        score = calculate_performance_score_from_data(data)
        scores[farm_name] = score
    
    worst_farm = min(scores, key=scores.get)
    worst_score = scores[worst_farm]
    data = all_farms[worst_farm]
    
    yield_val = float(data['Yield_tonnes_per_ha'].mean())
    spoilage = float(data['SpoilageRate_%'].mean())
    waste = float(data['WastePercentage_%'].mean())
    satisfaction = float(data['SatisfactionScore_0_10'].mean())
    
    return f"⚠️ {worst_farm} needs attention with a score of {worst_score:.1f}/100.\n\n" \
           f"Key metrics:\n" \
           f"• Yield: {yield_val:.2f} tonnes/ha\n" \
           f"• Spoilage: {spoilage:.2f}%\n" \
           f"• Waste: {waste:.2f}%\n" \
           f"• Customer Satisfaction: {satisfaction:.1f}/10\n\n" \
           f"Recommendations: Focus on reducing spoilage and waste, improving yield, and enhancing customer satisfaction."

def get_farm_summary(farm_name, data):
    """Get summary for a specific farm"""
    if data is None or data.empty:
        return f"Sorry, I couldn't find data for {farm_name}."
    
    score = calculate_performance_score_from_data(data)
    yield_val = float(data['Yield_tonnes_per_ha'].mean())
    spoilage = float(data['SpoilageRate_%'].mean())
    defects = float(data['DefectRate_%'].mean())
    waste = float(data['WastePercentage_%'].mean())
    satisfaction = float(data['SatisfactionScore_0_10'].mean())
    pest_risk = float(data['PestRiskScore'].mean())
    machinery_uptime = float(data['MachineryUptime_%'].mean())
    
    status = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Needs Attention"
    
    return f"📊 {farm_name} Summary:\n\n" \
           f"Performance Score: {score:.1f}/100 ({status})\n\n" \
           f"Key Metrics:\n" \
           f"• Yield: {yield_val:.2f} tonnes/ha\n" \
           f"• Spoilage Rate: {spoilage:.2f}%\n" \
           f"• Defect Rate: {defects:.2f}%\n" \
           f"• Waste: {waste:.2f}%\n" \
           f"• Customer Satisfaction: {satisfaction:.1f}/10\n" \
           f"• Pest Risk: {pest_risk:.1f}\n" \
           f"• Machinery Uptime: {machinery_uptime:.1f}%\n\n" \
           f"Total Records: {len(data)}"

def get_yield_comparison(all_farms):
    """Compare yields across farms"""
    yields = {}
    for farm_name, data in all_farms.items():
        yields[farm_name] = float(data['Yield_tonnes_per_ha'].mean())
    
    sorted_farms = sorted(yields.items(), key=lambda x: x[1], reverse=True)
    response = "🌱 Yield Comparison (tonnes/ha):\n\n"
    for farm, yield_val in sorted_farms:
        response += f"• {farm}: {yield_val:.2f}\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n🏆 Best: {best[0]} ({best[1]:.2f})\n"
    response += f"⚠️ Needs Improvement: {worst[0]} ({worst[1]:.2f})"
    
    return response

def get_spoilage_comparison(all_farms):
    """Compare spoilage rates"""
    spoilage = {}
    for farm_name, data in all_farms.items():
        spoilage[farm_name] = float(data['SpoilageRate_%'].mean())
    
    sorted_farms = sorted(spoilage.items(), key=lambda x: x[1])
    response = "❄️ Spoilage Rate Comparison (%):\n\n"
    for farm, rate in sorted_farms:
        response += f"• {farm}: {rate:.2f}%\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n✅ Lowest: {best[0]} ({best[1]:.2f}%)\n"
    response += f"⚠️ Highest: {worst[0]} ({worst[1]:.2f}%)"
    
    return response

def get_waste_comparison(all_farms):
    """Compare waste percentages"""
    waste = {}
    for farm_name, data in all_farms.items():
        waste[farm_name] = float(data['WastePercentage_%'].mean())
    
    sorted_farms = sorted(waste.items(), key=lambda x: x[1])
    response = "♻️ Waste Comparison (%):\n\n"
    for farm, rate in sorted_farms:
        response += f"• {farm}: {rate:.2f}%\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n✅ Lowest: {best[0]} ({best[1]:.2f}%)\n"
    response += f"⚠️ Highest: {worst[0]} ({worst[1]:.2f}%)"
    
    return response

def get_satisfaction_comparison(all_farms):
    """Compare customer satisfaction"""
    satisfaction = {}
    for farm_name, data in all_farms.items():
        satisfaction[farm_name] = float(data['SatisfactionScore_0_10'].mean())
    
    sorted_farms = sorted(satisfaction.items(), key=lambda x: x[1], reverse=True)
    response = "👥 Customer Satisfaction Comparison (/10):\n\n"
    for farm, score in sorted_farms:
        response += f"• {farm}: {score:.2f}\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n🏆 Highest: {best[0]} ({best[1]:.2f})\n"
    response += f"⚠️ Lowest: {worst[0]} ({worst[1]:.2f})"
    
    return response

def get_pest_comparison(all_farms):
    """Compare pest risk scores"""
    pest = {}
    for farm_name, data in all_farms.items():
        pest[farm_name] = float(data['PestRiskScore'].mean())
    
    sorted_farms = sorted(pest.items(), key=lambda x: x[1])
    response = "🐛 Pest Risk Comparison:\n\n"
    for farm, score in sorted_farms:
        response += f"• {farm}: {score:.1f}\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n✅ Lowest Risk: {best[0]} ({best[1]:.1f})\n"
    response += f"⚠️ Highest Risk: {worst[0]} ({worst[1]:.1f})"
    
    return response

def get_machinery_comparison(all_farms):
    """Compare machinery uptime"""
    uptime = {}
    for farm_name, data in all_farms.items():
        uptime[farm_name] = float(data['MachineryUptime_%'].mean())
    
    sorted_farms = sorted(uptime.items(), key=lambda x: x[1], reverse=True)
    response = "⚙️ Machinery Uptime Comparison (%):\n\n"
    for farm, rate in sorted_farms:
        response += f"• {farm}: {rate:.1f}%\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n🏆 Best: {best[0]} ({best[1]:.1f}%)\n"
    response += f"⚠️ Needs Improvement: {worst[0]} ({worst[1]:.1f}%)"
    
    return response

def get_defect_comparison(all_farms):
    """Compare defect rates"""
    defects = {}
    for farm_name, data in all_farms.items():
        defects[farm_name] = float(data['DefectRate_%'].mean())
    
    sorted_farms = sorted(defects.items(), key=lambda x: x[1])
    response = "🔧 Defect Rate Comparison (%):\n\n"
    for farm, rate in sorted_farms:
        response += f"• {farm}: {rate:.2f}%\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n✅ Lowest: {best[0]} ({best[1]:.2f}%)\n"
    response += f"⚠️ Highest: {worst[0]} ({worst[1]:.2f}%)"
    
    return response

def get_delay_comparison(all_farms):
    """Compare delivery delays"""
    delays = {}
    for farm_name, data in all_farms.items():
        delays[farm_name] = float((data['DeliveryDelayFlag'].sum() / len(data) * 100))
    
    sorted_farms = sorted(delays.items(), key=lambda x: x[1])
    response = "🚚 Delivery Delay Comparison (%):\n\n"
    for farm, rate in sorted_farms:
        response += f"• {farm}: {rate:.1f}%\n"
    
    best = sorted_farms[0]
    worst = sorted_farms[-1]
    response += f"\n✅ Lowest: {best[0]} ({best[1]:.1f}%)\n"
    response += f"⚠️ Highest: {worst[0]} ({worst[1]:.1f}%)"
    
    return response

def get_storage_comparison(all_farms):
    """Compare storage conditions"""
    response = "❄️ Storage Conditions Comparison:\n\n"
    for farm_name, data in all_farms.items():
        temp = float(data['StorageTemperature_C'].mean())
        humidity = float(data['Humidity_%'].mean())
        spoilage = float(data['SpoilageRate_%'].mean())
        response += f"{farm_name}:\n"
        response += f"  • Temperature: {temp:.1f}°C\n"
        response += f"  • Humidity: {humidity:.1f}%\n"
        response += f"  • Spoilage: {spoilage:.2f}%\n\n"
    
    return response

def get_general_comparison(all_farms):
    """Get general comparison of all farms"""
    scores = {}
    for farm_name, data in all_farms.items():
        scores[farm_name] = calculate_performance_score_from_data(data)
    
    sorted_farms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    response = "📊 Overall Farm Comparison:\n\n"
    response += "Performance Scores:\n"
    for farm, score in sorted_farms:
        status = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Needs Attention"
        response += f"• {farm}: {score:.1f}/100 ({status})\n"
    
    return response

def get_performance_scores(all_farms):
    """Get performance scores for all farms"""
    scores = {}
    for farm_name, data in all_farms.items():
        scores[farm_name] = calculate_performance_score_from_data(data)
    
    sorted_farms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    response = "📈 Performance Scores:\n\n"
    for farm, score in sorted_farms:
        status = "Excellent ✅" if score >= 80 else "Good ✅" if score >= 65 else "Average ⚠️" if score >= 50 else "Needs Attention ❌"
        response += f"• {farm}: {score:.1f}/100 - {status}\n"
    
    return response

def get_help_message():
    """Get help message with available commands"""
    return "I can help you with:\n\n" \
           "• Farm Performance: 'Which farm is best?', 'Show me Farm A'\n" \
           "• Metrics: 'Compare yields', 'Show spoilage rates', 'Waste comparison'\n" \
           "• Specific Data: 'Pest risk', 'Machinery uptime', 'Customer satisfaction'\n" \
           "• Comparisons: 'Compare all farms', 'Performance scores'\n" \
           "• Storage: 'Storage conditions', 'Temperature comparison'\n\n" \
           "Just ask me anything about the farms!"

def calculate_performance_score_from_data(data):
    """Calculate performance score from farm data"""
    yield_score = min(20, (float(data['Yield_tonnes_per_ha'].mean()) / 10) * 20)
    spoilage_score = max(0, 15 - (float(data['SpoilageRate_%'].mean()) / 2))
    defect_score = max(0, 15 - (float(data['DefectRate_%'].mean()) / 0.5))
    delay_score = max(0, 10 - (float(data['DeliveryDelayFlag'].sum() / len(data) * 100) / 2))
    waste_score = max(0, 10 - (float(data['WastePercentage_%'].mean()) / 2))
    satisfaction_score = (float(data['SatisfactionScore_0_10'].mean()) / 10) * 15
    pest_score = max(0, 10 - (float(data['PestRiskScore'].mean()) / 10))
    uptime_score = (float(data['MachineryUptime_%'].mean()) / 100) * 5
    
    total = yield_score + spoilage_score + defect_score + delay_score + waste_score + satisfaction_score + pest_score + uptime_score
    return min(100, max(0, total))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
