# app/dashboard.py

import streamlit as st
import json
import os
from datetime import datetime

# -------------------------------
# Step 1: Paths
# -------------------------------
ANALYSIS_PATH = "output/analysis"
PREDICTIONS_PATH = "output/predictions/ml_cost_predictions.json"

# -------------------------------
# Step 2: Load JSON Data
# -------------------------------
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

idle_ec2 = load_json(os.path.join(ANALYSIS_PATH, "idle_ec2.json"))
idle_ebs = load_json(os.path.join(ANALYSIS_PATH, "idle_ebs.json"))
idle_s3 = load_json(os.path.join(ANALYSIS_PATH, "idle_s3.json"))
idle_rds = load_json(os.path.join(ANALYSIS_PATH, "idle_rds.json"))
cost_estimation = load_json(os.path.join(ANALYSIS_PATH, "cost_estimation.json"))
ml_predictions = load_json(PREDICTIONS_PATH)

# -------------------------------
# Step 3: Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="CloudMind Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("☁️ CloudMind Analytics - Cost & Resource Advisor")
st.markdown("AI-powered dashboard to monitor AWS resources, predict cost wastage, and provide actionable recommendations.")
st.markdown("---")

# -------------------------------
# Step 4: Current Cost & Savings Metrics
# -------------------------------
st.header("💰 Current Cost & Potential Savings")

if cost_estimation:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Current Cost (USD)", f"${cost_estimation['total_current_cost_usd']}")
    col2.metric("Potential Savings (USD)", f"${cost_estimation['potential_savings_usd']}")
    col3.metric("Estimated Optimized Cost (USD)", f"${cost_estimation['estimated_optimized_cost_usd']}")
else:
    st.warning("Cost estimation data not found. Run Day 4 module first.")
st.markdown("---")

# -------------------------------
# Step 5: Display Idle Resources
# -------------------------------
st.header("🛠️ Idle / Underutilized Resources")

def display_resources(title, data, keys):
    st.subheader(title)
    if data:
        for i, r in enumerate(data):
            st.write(f"{i+1}. " + ", ".join([f"{k}: {r.get(k, 'N/A')}" for k in keys]))
    else:
        st.success("✅ No idle resources found.")

display_resources("EC2 Instances", idle_ec2, ["InstanceId", "State", "StoppedDays"])
display_resources("EBS Volumes", idle_ebs, ["VolumeId", "Size", "Attachments"])
display_resources("S3 Buckets", idle_s3, ["Name", "AgeDays", "ObjectCount"])
display_resources("RDS Instances", idle_rds, ["DBInstanceIdentifier", "DBInstanceStatus", "IdleDays"])
st.markdown("---")

# -------------------------------
# Step 6: Show ML Predictions
# -------------------------------
st.header("📈 Predicted Future Costs")

if ml_predictions:
    for resource, pred in ml_predictions.items():
        st.subheader(f"{resource}")
        st.write(f"- Current Cost: **${pred['CurrentCost']}**")
        st.write(f"- Predicted Future Cost: **${pred['PredictedFutureCost']}**")
        st.write(f"- Expected Change: **{pred['ChangePercent']}%**")
else:
    st.warning("ML prediction data not found. Run Day 5 module first.")
st.markdown("---")

# -------------------------------
# Step 7: Actionable Recommendations
# -------------------------------
st.header("✅ Recommendations")

if idle_ec2:
    st.info("• Stop EC2 instances that are stopped >7 days to save cost.")
if idle_ebs:
    st.info("• Detach / delete unused EBS volumes.")
if idle_s3:
    st.info("• Delete old or empty S3 buckets to reduce storage cost.")
if idle_rds:
    st.info("• Stop idle RDS instances or downscale.")

if not (idle_ec2 or idle_ebs or idle_s3 or idle_rds):
    st.success("All resources are optimized. No immediate action required.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("Developed by **Samarth Mahadik** | CloudMind Analytics")
