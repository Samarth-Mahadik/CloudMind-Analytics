import json
import os
from datetime import datetime

# ---------- Static AWS pricing (Free Tier Simulation) ----------
AWS_PRICING = {
    "EC2": 0.0116,  # USD/hour
    "EBS": 0.10,    # USD/GB-month
    "S3": 0.023,    # USD/GB-month
    "RDS": 0.017    # USD/hour
}

OUTPUT_PATH = "output/analysis/"
os.makedirs(OUTPUT_PATH, exist_ok=True)


# ---------- Helper function to load analysis files ----------
def load_json(file_name):
    file_path = os.path.join(OUTPUT_PATH, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []  # return list instead of dict, since our data is list format


# ---------- Cost calculation logic ----------
def calculate_cost_and_savings():
    ec2_data = load_json("idle_ec2.json")
    ebs_data = load_json("idle_ebs.json")
    s3_data = load_json("idle_s3.json")
    rds_data = load_json("idle_rds.json")

    total_cost = 0
    total_savings = 0

    # --- EC2 ---
    for ec2 in ec2_data:
        hours = ec2.get("running_hours", 100)
        cost = hours * AWS_PRICING["EC2"]
        if ec2.get("idle", False):
            savings = cost * 0.7
            total_savings += savings
        total_cost += cost

    # --- EBS ---
    for ebs in ebs_data:
        size_gb = ebs.get("size", 10)
        cost = size_gb * AWS_PRICING["EBS"]
        if ebs.get("unused", False):
            savings = cost * 0.8
            total_savings += savings
        total_cost += cost

    # --- S3 ---
    for s3 in s3_data:
        size_gb = s3.get("size", 5)
        cost = size_gb * AWS_PRICING["S3"]
        if s3.get("inactive", False):
            savings = cost * 0.5
            total_savings += savings
        total_cost += cost

    # --- RDS ---
    for rds in rds_data:
        hours = rds.get("running_hours", 80)
        cost = hours * AWS_PRICING["RDS"]
        if rds.get("idle", False):
            savings = cost * 0.6
            total_savings += savings
        total_cost += cost

    # ---------- Final Result ----------
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_current_cost_usd": round(total_cost, 2),
        "potential_savings_usd": round(total_savings, 2),
        "estimated_optimized_cost_usd": round(total_cost - total_savings, 2)
    }

    # Save output
    output_file = os.path.join(OUTPUT_PATH, "cost_estimation.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=4)

    print("✅ Cost calculation complete!")
    print(json.dumps(result, indent=4))
    return result


# ---------- Run module ----------
if __name__ == "__main__":
    calculate_cost_and_savings()
