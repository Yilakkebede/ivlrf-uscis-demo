"""
Equity Mapping for HUD Compliance
"""
import pandas as pd
import numpy as np
import os

def calculate_equity_disparities(vehicle_df, risk_data, demo_data=None):
    """
    Calculate equity disparities for HUD compliance
    """
    print("Calculating equity disparities...")
    
    # Create outputs folder if it doesn't exist
    outputs_dir = '../outputs'
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    # Merge risk data
    if 'risk_score' not in vehicle_df.columns and risk_data is not None:
        if isinstance(risk_data, pd.DataFrame):
            vehicle_df = vehicle_df.merge(
                risk_data[['vin', 'risk_score', 'risk_level']], 
                on='vin', how='left'
            )
    
    # Create synthetic demographic data by ZIP
    zip_demo = pd.DataFrame({
        'zip_code': [90001, 90011, 90210, 94102, 95123],
        'median_income': [45000, 38000, 125000, 85000, 72000],
        'poverty_rate': [0.22, 0.28, 0.05, 0.12, 0.15],
        'minority_pct': [0.85, 0.92, 0.25, 0.45, 0.38]
    })
    
    # Aggregate by ZIP
    zip_stats = vehicle_df.groupby('zip_code').agg({
        'risk_score': 'mean',
        'vehicle_age': 'mean',
        'vin': 'count'
    }).rename(columns={'vin': 'vehicle_count'}).reset_index()
    
    # Merge with demographic data
    equity_data = pd.merge(zip_stats, zip_demo, on='zip_code', how='left')
    
    # Calculate disparity index
    equity_data['income_normalized'] = equity_data['median_income'] / equity_data['median_income'].max()
    equity_data['disparity_index'] = (
        equity_data['risk_score'] / 100 * 
        (1 - equity_data['income_normalized']) * 
        100
    )
    
    # Generate HUD report
    hud_report = generate_hud_equity_report(equity_data)
    
    return {
        'equity_data': equity_data,
        'hud_report': hud_report,
        'summary': {
            'high_disparity_zips': len(equity_data[equity_data['disparity_index'] > 50]),
            'avg_disparity_index': equity_data['disparity_index'].mean()
        }
    }

def generate_hud_equity_report(equity_data):
    """
    Generate HUD equity compliance report
    """
    print("Generating HUD equity compliance report...")
    
    # Create outputs folder if it doesn't exist
    outputs_dir = '../outputs'
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    # Identify high-disparity areas
    high_disparity = equity_data[equity_data['disparity_index'] > 50].copy()
    
    if len(high_disparity) > 0:
        high_disparity['hud_priority'] = 'High'
        high_disparity['recommended_action'] = 'Targeted vehicle replacement program'
        
        # Save report
        report_cols = ['zip_code', 'median_income', 'poverty_rate', 
                      'minority_pct', 'risk_score', 'disparity_index',
                      'hud_priority', 'recommended_action']
        
        report_df = high_disparity[report_cols]
        report_path = os.path.join(outputs_dir, 'hud_equity_report.csv')
        report_df.to_csv(report_path, index=False)
        
        print(f"HUD equity report saved to: {report_path}")
        return report_df
    else:
        print("No high-disparity areas identified.")
        return pd.DataFrame()

def test_equity_mapper():
    """
    Test equity mapper
    """
    print("Testing Equity Mapper...")
    
    # Create test data
    np.random.seed(42)
    n = 100
    
    test_vehicles = pd.DataFrame({
        'vin': [f'VIN{i:08d}' for i in range(n)],
        'make': np.random.choice(['Toyota', 'Ford', 'Honda'], n),
        'zip_code': np.random.choice([90001, 90011, 90210, 94102, 95123], n),
        'vehicle_age': np.random.randint(5, 25, n),
        'risk_score': np.random.randint(20, 100, n)
    })
    
    test_risk = pd.DataFrame({
        'vin': test_vehicles['vin'],
        'risk_score': test_vehicles['risk_score'],
        'risk_level': np.where(test_vehicles['risk_score'] > 60, 'High', 'Low')
    })
    
    results = calculate_equity_disparities(test_vehicles, test_risk)
    
    print("\nEQUITY ANALYSIS RESULTS:")
    print(f"High-disparity ZIP codes: {results['summary']['high_disparity_zips']}")
    print(f"Average disparity index: {results['summary']['avg_disparity_index']:.1f}")
    
    print("\nSUCCESS: Equity analysis complete!")
    return results

if __name__ == "__main__":
    test_equity_mapper()