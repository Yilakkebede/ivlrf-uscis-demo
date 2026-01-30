"""
Vehicle Risk Scoring for NHTSA Safety Prioritization
"""
import pandas as pd
import numpy as np
import os

def calculate_risk_scores(vehicle_df, crash_data=None):
    """
    Calculate risk scores for vehicles using machine learning
    """
    print("Calculating vehicle risk scores...")
    
    # Prepare features
    features = ['vehicle_age', 'odometer', 'model_year']
    
    # Create synthetic risk scores for demonstration
    # In production, this would use real NHTSA crash data
    np.random.seed(42)
    
    # Base risk increases with age and mileage
    vehicle_df['risk_base'] = (
        0.1 * vehicle_df['vehicle_age'] + 
        0.00001 * vehicle_df['odometer'] +
        0.05 * (2024 - vehicle_df['model_year'])
    )
    
    # Add make-specific risk factors
    make_risk = {'Toyota': 0.8, 'Ford': 1.0, 'Honda': 0.9, 
                 'Chevrolet': 1.1, 'Nissan': 1.2}
    vehicle_df['make_factor'] = vehicle_df['make'].map(make_risk).fillna(1.0)
    
    # Calculate final risk score (0-100 scale)
    vehicle_df['risk_score'] = np.clip(
        vehicle_df['risk_base'] * vehicle_df['make_factor'] * 20 + 
        np.random.normal(0, 5, len(vehicle_df)),
        0, 100
    )
    
    # Categorize risk levels
    conditions = [
        (vehicle_df['risk_score'] < 30),
        (vehicle_df['risk_score'] < 60),
        (vehicle_df['risk_score'] < 80),
        (vehicle_df['risk_score'] >= 80)
    ]
    
    choices = ['Low', 'Medium', 'High', 'Critical']
    vehicle_df['risk_level'] = np.select(conditions, choices)
    
    # Generate NHTSA priority list
    priority_list = generate_nhtsa_priority_list(vehicle_df)
    
    return {
        'risk_scores': vehicle_df[['vin', 'make', 'model_year', 'vehicle_age', 
                                  'odometer', 'risk_score', 'risk_level']],
        'priority_list': priority_list,
        'summary': {
            'critical_count': len(vehicle_df[vehicle_df['risk_level'] == 'Critical']),
            'high_count': len(vehicle_df[vehicle_df['risk_level'] == 'High']),
            'avg_risk_score': vehicle_df['risk_score'].mean()
        }
    }

def generate_nhtsa_priority_list(vehicle_df, top_n=50):
    """
    Generate priority list for NHTSA inspections
    """
    import os
    
    # Create outputs folder if it doesn't exist
    outputs_dir = '../outputs'
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    print(f"Generating NHTSA priority list (top {top_n} vehicles)...")
    
    # Sort by risk score
    priority_df = vehicle_df.sort_values('risk_score', ascending=False).head(top_n)
    
    # Add inspection recommendations
    recommendations = []
    for _, row in priority_df.iterrows():
        if row['risk_score'] >= 80:
            rec = "URGENT: Full safety inspection + emissions test"
        elif row['risk_score'] >= 60:
            rec = "PRIORITY: Brake & tire inspection"
        else:
            rec = "ROUTINE: Standard safety check"
        
        recommendations.append(rec)
    
    priority_df['inspection_recommendation'] = recommendations
    
    # Select relevant columns
    result = priority_df[[
        'vin', 'make', 'model_year', 'vehicle_age', 
        'odometer', 'risk_score', 'risk_level', 'inspection_recommendation'
    ]].copy()
    
    # Save to CSV
    csv_file = os.path.join(outputs_dir, 'nhtsa_priority_list.csv')
    result.to_csv(csv_file, index=False)
    
    print(f"NHTSA priority list saved to: {csv_file}")
    
    return result

def test_risk_scoring():
    """
    Test the risk scoring system
    """
    print("Testing Risk Scoring System...")
    
    # Create test data
    np.random.seed(42)
    n = 1000
    
    test_data = pd.DataFrame({
        'vin': [f'VIN{i:08d}' for i in range(n)],
        'make': np.random.choice(['Toyota', 'Ford', 'Honda', 'Chevrolet', 'Nissan'], n),
        'model_year': np.random.randint(2000, 2023, n),
        'vehicle_age': 2024 - np.random.randint(2000, 2023, n),
        'odometer': np.random.randint(10000, 200000, n)
    })
    
    print(f"Test data: {n} vehicles")
    
    # Calculate risk scores
    results = calculate_risk_scores(test_data)
    
    print("\n" + "=" * 60)
    print("RISK SCORING RESULTS")
    print("=" * 60)
    
    summary = results['summary']
    print(f"Critical Risk Vehicles: {summary['critical_count']}")
    print(f"High Risk Vehicles: {summary['high_count']}")
    print(f"Average Risk Score: {summary['avg_risk_score']:.1f}/100")
    
    print("\nTop 5 High-Risk Vehicles:")
    print(results['priority_list'].head(5).to_string(index=False))
    
    print("\nSUCCESS: Risk scoring complete!")
    print("NHTSA priority list saved to outputs/ folder.")
    
    return results

if __name__ == "__main__":
    test_risk_scoring()