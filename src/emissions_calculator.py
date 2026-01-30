"""
Emissions Calculator for EPA Targeting
"""
import pandas as pd
import numpy as np
import os

def calculate_emissions(vehicle_df, survival_data=None):
    """
    Calculate emissions using EPA MOVES methodology
    """
    print("Calculating vehicle emissions...")
    
    # EPA emission factors (grams/mile)
    emission_factors = {
        'pre_2000': {'CO2': 500, 'NOx': 1.2, 'PM25': 0.08},
        '2000_2009': {'CO2': 420, 'NOx': 0.8, 'PM25': 0.05},
        '2010_2019': {'CO2': 350, 'NOx': 0.4, 'PM25': 0.02},
        '2020_plus': {'CO2': 280, 'NOx': 0.2, 'PM25': 0.01}
    }
    
    # Assign emission category
    def get_category(year):
        if year < 2000:
            return 'pre_2000'
        elif year < 2010:
            return '2000_2009'
        elif year < 2020:
            return '2010_2019'
        else:
            return '2020_plus'
    
    vehicle_df['emission_category'] = vehicle_df['model_year'].apply(get_category)
    
    # Calculate emissions
    for pollutant in ['CO2', 'NOx', 'PM25']:
        vehicle_df[f'{pollutant}_g_per_mile'] = vehicle_df['emission_category'].apply(
            lambda x: emission_factors[x][pollutant]
        )
    
    # Annual mileage
    vehicle_df['annual_mileage'] = 12000
    
    # Annual emissions
    vehicle_df['CO2_annual_kg'] = vehicle_df['CO2_g_per_mile'] * vehicle_df['annual_mileage'] / 1000
    vehicle_df['NOx_annual_kg'] = vehicle_df['NOx_g_per_mile'] * vehicle_df['annual_mileage'] / 1000
    vehicle_df['PM25_annual_kg'] = vehicle_df['PM25_g_per_mile'] * vehicle_df['annual_mileage'] / 1000
    
    # Generate EPA targeting list
    epa_list = generate_epa_targeting_list(vehicle_df)
    
    return {
        'emissions_data': vehicle_df,
        'epa_target_list': epa_list,
        'summary': {
            'total_CO2_kg': vehicle_df['CO2_annual_kg'].sum(),
            'total_PM25_kg': vehicle_df['PM25_annual_kg'].sum(),
            'high_emitters': len(vehicle_df[vehicle_df['emission_category'] == 'pre_2000'])
        }
    }

def generate_epa_targeting_list(vehicle_df, top_n=50):
    """
    Generate EPA targeting list for scrappage programs
    """
    print(f"Generating EPA targeting list (top {top_n} high-emitters)...")
    
    # Create outputs folder if it doesn't exist
    outputs_dir = '../outputs'
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    # Target oldest, highest-emitting vehicles
    target_df = vehicle_df[vehicle_df['emission_category'].isin(['pre_2000', '2000_2009'])]
    target_df = target_df.sort_values('PM25_annual_kg', ascending=False).head(top_n)
    
    # Calculate benefits
    target_df['estimated_benefit'] = (
        target_df['PM25_annual_kg'] * 1000 +  # Health benefits per kg PM2.5
        target_df['CO2_annual_kg'] * 50       # Social cost of carbon
    )
    
    # Select columns
    result = target_df[[
        'vin', 'make', 'model_year', 'vehicle_age',
        'emission_category', 'PM25_annual_kg', 'CO2_annual_kg',
        'estimated_benefit'
    ]].copy()
    
    # Save
    result.to_csv(os.path.join(outputs_dir, 'epa_target_list.csv'), index=False)
    print(f"EPA target list saved to: {os.path.join(outputs_dir, 'epa_target_list.csv')}")
    
    return result

def test_emissions_calculator():
    """
    Test emissions calculator
    """
    print("Testing Emissions Calculator...")
    
    # Test data
    np.random.seed(42)
    n = 500
    
    test_data = pd.DataFrame({
        'vin': [f'VIN{i:08d}' for i in range(n)],
        'make': np.random.choice(['Toyota', 'Ford', 'Honda'], n),
        'model_year': np.random.randint(1990, 2023, n),
        'vehicle_age': 2024 - np.random.randint(1990, 2023, n)
    })
    
    results = calculate_emissions(test_data)
    
    print("\nEMISSIONS CALCULATION RESULTS:")
    print(f"Total CO2: {results['summary']['total_CO2_kg']:.0f} kg/year")
    print(f"Total PM2.5: {results['summary']['total_PM25_kg']:.0f} kg/year")
    print(f"High-emission vehicles: {results['summary']['high_emitters']}")
    
    print("\nSUCCESS: Emissions calculator complete!")
    return results

if __name__ == "__main__":
    test_emissions_calculator()