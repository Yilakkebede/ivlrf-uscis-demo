#!/usr/bin/env python3
"""
IVLRF End-to-End Pipeline
Run with: python run_pipeline.py --state CA --year 2023
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_collector import collect_all_data
# Note: function names changed in survival_analyzer.py
# from survival_analyzer import calculate_survival_curves
# from risk_scorer import generate_risk_scores
# from emissions_calculator import estimate_emissions
# from equity_mapper import create_equity_maps
# from report_generator import generate_regulatory_report

# We'll import the actual function names from your files
def import_survival_module():
    """Import the survival analysis module"""
    from survival_analyzer import calculate_phd_survival_curves
    return calculate_phd_survival_curves

def import_risk_module():
    """Import the risk scoring module"""
    from risk_scorer import calculate_risk_scores
    return calculate_risk_scores

def import_emissions_module():
    """Import the emissions calculator module"""
    from emissions_calculator import calculate_emissions
    return calculate_emissions

def import_equity_module():
    """Import the equity mapper module"""
    from equity_mapper import calculate_equity_disparities
    return calculate_equity_disparities

def import_report_module():
    """Import the report generator module"""
    from report_generator import generate_regulatory_report
    return generate_regulatory_report

def main():
    parser = argparse.ArgumentParser(description="IVLRF End-to-End Pipeline")
    parser.add_argument("--state", default="CA", help="State code (e.g., CA, TX, NY)")
    parser.add_argument("--year", default=2023, type=int, help="Analysis year")
    parser.add_argument("--output", default="./outputs", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"Starting IVLRF Pipeline for {args.state} ({args.year})")
    print("=" * 60)
    
    # Import modules
    calculate_phd_survival_curves = import_survival_module()
    calculate_risk_scores = import_risk_module()
    calculate_emissions = import_emissions_module()
    calculate_equity_disparities = import_equity_module()
    generate_regulatory_report = import_report_module()
    
    # Step 1: Collect real data from public APIs
    print("STEP 1: Collecting real public data...")
    vehicle_data, crash_data, demo_data = collect_all_data(args.state, args.year)
    
    # Step 2: Calculate survival curves
    print("STEP 2: Calculating vehicle survival curves...")
    survival_results = calculate_phd_survival_curves(vehicle_data)
    
    # Step 3: Generate risk scores
    print("STEP 3: Generating risk scores...")
    risk_results = calculate_risk_scores(vehicle_data, crash_data)
    
    # Step 4: Estimate emissions
    print("STEP 4: Estimating emissions impact...")
    emissions_results = calculate_emissions(vehicle_data, survival_results)
    
    # Step 5: Create equity maps
    print("STEP 5: Creating equity disparity maps...")
    equity_results = calculate_equity_disparities(vehicle_data, risk_results['risk_scores'], demo_data)
    
    # Step 6: Generate regulatory report
    print("STEP 6: Generating regulatory report...")
    report_path = generate_regulatory_report(
        args.state, args.year, 
        survival_results, 
        risk_results['summary'], 
        emissions_results['summary'], 
        equity_results['summary']
    )
    
    print("=" * 60)
    print("Pipeline complete!")
    print(f"Report saved to: {report_path}")
    print(f"All outputs in: {args.output}")
    print("\nKey outputs created:")
    print(f"   • {args.output}/phd_survival_results.txt")
    print(f"   • {args.output}/nhtsa_priority_list.csv")
    print(f"   • {args.output}/epa_target_list.csv")
    print(f"   • {args.output}/hud_equity_report.csv")
    print(f"   • {args.output}/regulatory_report_{args.state}_{args.year}.txt")

if __name__ == "__main__":
    main()