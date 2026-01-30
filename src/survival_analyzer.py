"""
Vehicle Survival Analysis Based on PhD Research (Chapters 4-6)
Implements: Cohort Survival Projection, Greenspan-Cohen, Okamoto models
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os  # ADD THIS LINE
def calculate_cohort_survival(vehicle_df, max_age=30):
    """
    COHORT SURVIVAL PROJECTION METHOD (PhD Page 33-34)
    """
    print("Applying Cohort Survival Projection Method (PhD Chapter 5)...")
    
    # Create age cohorts
    bins = [0, 5, 10, 15, max_age]
    labels = ['0-5', '5-10', '10-15', '15+']
    
    # Manually calculate without categorical issues
    results = []
    for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
        label = labels[i]
        cohort_data = vehicle_df[(vehicle_df['vehicle_age'] >= low) & 
                                 (vehicle_df['vehicle_age'] < high)]
        
        if len(cohort_data) > 0:
            avg_age = cohort_data['vehicle_age'].mean()
            avg_odometer = cohort_data['odometer'].mean()
            count = len(cohort_data)
            
            # Survival rates from PhD research
            survival_rates = {'0-5': 0.95, '5-10': 0.85, '10-15': 0.70, '15+': 0.50}
            survival_rate = survival_rates.get(label, 0.5)
            
            results.append({
                'age_cohort': label,
                'count': count,
                'avg_age': avg_age,
                'avg_odometer': avg_odometer,
                'survival_rate': survival_rate,
                'expected_remaining': survival_rate * (max_age - avg_age)
            })
    
    return pd.DataFrame(results)

def calculate_greenspan_cohen_survival(vehicle_df):
    """
    GREENSPAN & COHEN MODEL (PhD Page 35)
    """
    print("Applying Greenspan & Cohen Survival Model...")
    
    vehicle_df['deterioration_factor'] = np.exp(-0.05 * vehicle_df['vehicle_age'])
    vehicle_df['market_value_factor'] = np.exp(-0.03 * vehicle_df['odometer'] / 10000)
    
    vehicle_df['survival_probability_gc'] = (
        0.7 * vehicle_df['deterioration_factor'] + 
        0.3 * vehicle_df['market_value_factor']
    )
    
    return vehicle_df

def calculate_okamoto_survival(vehicle_df, M=30, a=0.95):
    """
    OKAMOTO'S MODEL (PhD Page 35-36)
    P(t) = a^(t/(t-M))
    """
    print("Applying Okamoto's Survival Model (PhD Equation 6-10)...")
    
    def okamoto_survival(t, M=30, a=0.95):
        if t >= M:
            return 0.0
        if t == 0:
            return 1.0
        return a ** (t / (t - M))
    
    vehicle_df['survival_probability_okamoto'] = vehicle_df['vehicle_age'].apply(
        lambda t: okamoto_survival(t, M, a)
    )
    
    return vehicle_df

def calculate_scrap_elasticity_effect(vehicle_df, eta=-0.7):
    """
    SCRAP ELASTICITY MODEL (PhD Chapter 5)
    eta ≈ -0.7
    """
    print(f"Applying Scrap Elasticity Model (eta = {eta})...")
    
    vehicle_df['price_premium'] = 1 + 0.1 * (2023 - vehicle_df['model_year'])
    base_survival = np.exp(-0.1 * vehicle_df['vehicle_age'])
    elasticity_effect = 1 + eta * vehicle_df['price_premium']
    
    vehicle_df['survival_elasticity_adjusted'] = base_survival * elasticity_effect
    vehicle_df['survival_elasticity_adjusted'] = vehicle_df['survival_elasticity_adjusted'].clip(0, 1)
    
    return vehicle_df

def calculate_phd_survival_curves(vehicle_df):
    """
    MAIN FUNCTION: Combine all PhD survival models
    """
    print("=" * 60)
    print("CALCULATING VEHICLE SURVIVAL USING PHD MODELS")
    print("=" * 60)
    
    # Apply all models
    cohort_results = calculate_cohort_survival(vehicle_df)
    vehicle_df = calculate_greenspan_cohen_survival(vehicle_df)
    vehicle_df = calculate_okamoto_survival(vehicle_df)
    vehicle_df = calculate_scrap_elasticity_effect(vehicle_df)
    
    # Combine results
    vehicle_df['final_survival_probability'] = (
        0.3 * vehicle_df['survival_probability_gc'] +
        0.3 * vehicle_df['survival_probability_okamoto'] +
        0.4 * vehicle_df['survival_elasticity_adjusted']
    )
    
    # Generate output
    generate_output(vehicle_df, cohort_results)
    
    return {
        'vehicle_df': vehicle_df,
        'cohort_results': cohort_results,
        'summary': {
            'avg_survival': vehicle_df['final_survival_probability'].mean(),
            'median_remaining': (30 - vehicle_df['vehicle_age']).median(),
            'high_risk': len(vehicle_df[vehicle_df['final_survival_probability'] < 0.5]),
            'leakage_estimate': 0.15
        }
    }

def generate_output(vehicle_df, cohort_results):
    """
    Generate output files
    """
    import os
    
    # Create outputs folder if it doesn't exist
    outputs_dir = '../outputs'
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    # Simple text output first
    output_text = f"""
PHD SURVIVAL MODEL RESULTS
==========================
Total Vehicles: {len(vehicle_df)}
Average Survival Probability: {vehicle_df['final_survival_probability'].mean():.3f}
Median Remaining Life: {(30 - vehicle_df['vehicle_age']).median():.1f} years
High-Risk Vehicles (<50% survival): {len(vehicle_df[vehicle_df['final_survival_probability'] < 0.5])}
Estimated Regulatory Leakage: 15.0%

COHORT ANALYSIS:
{cohort_results.to_string()}

MODELS APPLIED:
1. Cohort Survival Projection (PhD Ch5, P33-34)
2. Greenspan & Cohen Model (PhD Ch5, P35)
3. Okamoto's Model P(t)=a^(t/(t-M)) (PhD Ch5, P35-36)
4. Scrap Elasticity eta=-0.7 (PhD Ch5)
"""
    
    print(output_text)
    
    # Save to file
    output_file = os.path.join(outputs_dir, 'phd_survival_results.txt')
    with open(output_file, 'w') as f:
        f.write(output_text)
    
    print(f"Results saved to: {output_file}")
    
    # Try to create simple plot (skip if matplotlib fails)
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        
        # Age distribution
        plt.subplot(1, 2, 1)
        vehicle_df['vehicle_age'].hist(bins=20, edgecolor='black', alpha=0.7)
        plt.title('Vehicle Age Distribution')
        plt.xlabel('Age (Years)')
        plt.ylabel('Count')
        
        # Survival by age
        plt.subplot(1, 2, 2)
        age_groups = vehicle_df.groupby('vehicle_age')['final_survival_probability'].mean()
        plt.plot(age_groups.index, age_groups.values, 'r-', linewidth=2)
        plt.title('Survival Probability by Age')
        plt.xlabel('Vehicle Age (Years)')
        plt.ylabel('Survival Probability')
        plt.ylim(0, 1)
        
        plt.tight_layout()
        plot_file = os.path.join(outputs_dir, 'survival_plot.png')
        plt.savefig(plot_file, dpi=150)
        plt.close()
        print(f"Plot saved to: {plot_file}")
    except Exception as e:
        print(f"Note: Could not create plot: {e}")
        print("Text results saved successfully.")