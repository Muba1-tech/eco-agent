"""
test_pipeline.py - Automated End-to-End Verification of the 3-Agent Sustainability Pipeline.
"""

import os
import sys

# Critical environment variables to prevent OpenMP conflict on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure console output to handle UTF-8 symbols like INR rupee
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agents.diagnosis_agent import run_diagnosis
from agents.recommendation_agent import generate_recommendations
from agents.impact_agent import calculate_impact, generate_pdf_report
from db import save_audit, get_all_audits, get_community_impact

def test_full_pipeline():
    print("==================================================")
    print("  ECOAGENT 3-AGENT PIPELINE VERIFICATION TEST")
    print("==================================================")
    
    test_profile = {
        "user_name": "Test Household (Delhi NCR)",
        "property_type": "Residential Apartment",
        "occupants": 4,
        "monthly_kwh": 500,
        "monthly_bill": 4000,
        "tariff_inr_per_kwh": 8.0,
        "ac_count": 2,
        "ac_star_rating": "Unrated / >5 yrs old",
        "ac_temp_setting": 20,
        "fan_count": 4,
        "fan_type": "Conventional Induction (75W)",
        "lighting_type": "Mixed",
        "has_solar": False,
        "rooftop_sqft": 350,
        "water_consumption_lpcd": 180,
        "has_water_aerators": False,
        "segregates_waste": False,
        "home_composting": False,
        "single_use_plastic_usage": "Frequent"
    }
    
    # 1. Test Diagnosis Agent
    print("\n[Step 1] Running Diagnosis Agent...")
    profile = run_diagnosis(test_profile)
    assert "metrics" in profile, "Diagnosis Agent failed to return metrics"
    assert "flagged_inefficiencies" in profile, "Diagnosis Agent failed to flag inefficiencies"
    print(f"-> Success! Flagged {profile['total_inefficiencies_flagged']} inefficiencies.")
    print(f"-> Baseline Per Capita kWh: {profile['metrics']['per_capita_kwh']} kWh/mo (Benchmark: {profile['metrics']['benchmark_kwh']})")
    
    # 2. Test Recommendation Agent
    print("\n[Step 2] Running Recommendation Agent (RAG Grounding)...")
    recs = generate_recommendations(profile)
    assert len(recs) > 0, "Recommendation Agent returned 0 recommendations"
    print(f"-> Success! Generated {len(recs)} grounded recommendations.")
    sample_rec = recs[0]
    print(f"-> Sample Rec: '{sample_rec['title']}'")
    print(f"   Authority: {sample_rec['source_authority']}")
    print(f"   Reference: {sample_rec['source_reference']}")
    print(f"   RAG Cosine Score: {sample_rec['rag_similarity_score']}")
    
    # 3. Test Impact Agent
    print("\n[Step 3] Running Impact Agent...")
    impact = calculate_impact(profile, recs)
    summary = impact["summary"]
    assert summary["total_annual_cost_savings_inr"] > 0, "Impact Agent savings should be positive"
    assert summary["total_annual_co2_reduction_kg"] > 0, "Impact Agent CO2 reduction should be positive"
    print(f"-> Total Annual Cost Savings: INR {summary['total_annual_cost_savings_inr']:,.0f}")
    print(f"-> Total Annual CO2 Avoided: {summary['total_annual_co2_reduction_kg']:,.0f} kg ({summary['total_annual_co2_reduction_tonnes']} tonnes)")
    print(f"-> Trees Equivalent: {summary['trees_equivalent_annual']} trees/year")
    print(f"-> Water Saved: {summary['total_water_saved_liters_year']:,.0f} Liters/year")
    print(f"-> Landfill Waste Diverted: {summary['total_waste_diverted_kg_year']:,.0f} kg/year")
    
    # Test PDF Generation
    pdf_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "verification_report.pdf")
    generate_pdf_report(profile, impact, pdf_out)
    assert os.path.exists(pdf_out), "PDF Report file was not created"
    print(f"-> Success! Generated PDF report at: {pdf_out} (Size: {os.path.getsize(pdf_out)} bytes)")
    
    # 4. Test Database Logging
    print("\n[Step 4] Logging Audit to SQLite...")
    audit_id = save_audit(
        user_name=test_profile["user_name"],
        property_type=test_profile["property_type"],
        occupants=test_profile["occupants"],
        city_state="Delhi NCR",
        monthly_kwh=test_profile["monthly_kwh"],
        monthly_bill=test_profile["monthly_bill"],
        water_lpcd=test_profile["water_consumption_lpcd"],
        waste_kg_day=1.8,
        segregates_waste=test_profile["segregates_waste"],
        has_solar=test_profile["has_solar"],
        profile=profile,
        recommendations=recs,
        impact=impact
    )
    print(f"-> Audit successfully logged with ID: {audit_id}")
    
    audits = get_all_audits(limit=5)
    print(f"-> Stored Audits count: {len(audits)}")
    community = get_community_impact()
    print(f"-> Community Total CO2 Reduction: {community['total_annual_co2_kg']:,.0f} kg across {community['total_audits']} audits.")
    
    print("\n==================================================")
    print("  ALL PIPELINE INTEGRATION TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_full_pipeline()
