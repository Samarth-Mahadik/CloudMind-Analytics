#!/usr/bin/env python3
"""
Day 9 - CloudMind Analytics
Multi-Account Resource Analysis Module
--------------------------------------
Enhanced version: Handles multiple AWS accounts (dummy/test data)
and analyzes EC2, EBS, S3, and RDS resources for idle usage.
"""

import json
from datetime import datetime, timezone
import os

# ===== Default thresholds =====
EC2_STOPPED_DAYS_THRESHOLD = 7
EBS_UNUSED_DAYS_THRESHOLD = 14
S3_EMPTY_DAYS_THRESHOLD = 30
RDS_IDLE_DAYS_THRESHOLD = 14


# ===== Utility =====
def load_json(file_path):
    """Safely load JSON data from a file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"❌ Error loading {file_path}")
        return []


# ===== Analysis Functions =====
def analyze_ec2_instances(instances):
    idle_ec2 = []
    now = datetime.now(timezone.utc)
    for i in instances:
        state = i.get("State")
        launch_time_str = i.get("LaunchTime")
        launch_time = datetime.fromisoformat(launch_time_str) if launch_time_str else None

        if state == "stopped" and launch_time:
            stopped_days = (now - launch_time).days
            if stopped_days >= EC2_STOPPED_DAYS_THRESHOLD:
                i["StoppedDays"] = stopped_days
                idle_ec2.append(i)
    return idle_ec2


def analyze_ebs_volumes(volumes):
    idle_volumes = []
    for v in volumes:
        if len(v.get("Attachments", [])) == 0:
            idle_volumes.append(v)
    return idle_volumes


def analyze_s3_buckets(buckets):
    idle_buckets = []
    now = datetime.now(timezone.utc)
    for b in buckets:
        creation_str = b.get("CreationDate")
        creation = datetime.fromisoformat(creation_str) if creation_str else None
        object_count = b.get("ObjectCount", 0)
        if creation and object_count == 0:
            age_days = (now - creation).days
            if age_days >= S3_EMPTY_DAYS_THRESHOLD:
                b["AgeDays"] = age_days
                idle_buckets.append(b)
    return idle_buckets


def analyze_rds_instances(instances):
    idle_rds = []
    now = datetime.now(timezone.utc)
    for db in instances:
        status = db.get("DBInstanceStatus")
        create_str = db.get("InstanceCreateTime")
        create_time = datetime.fromisoformat(create_str) if create_str else None
        if status in ["stopped", "available"] and create_time:
            idle_days = (now - create_time).days
            if idle_days >= RDS_IDLE_DAYS_THRESHOLD:
                db["IdleDays"] = idle_days
                idle_rds.append(db)
    return idle_rds


# ===== New: Multi-Account Loader =====
def load_test_accounts(test_data_dir="test_data"):
    """Load all account JSONs (simulated multi-account setup)."""
    accounts = []
    if not os.path.exists(test_data_dir):
        print("⚠️ No test_data folder found — skipping multi-account simulation.")
        return accounts

    for file in os.listdir(test_data_dir):
        if file.endswith(".json"):
            path = os.path.join(test_data_dir, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    accounts.append(data)
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in {file}, skipping.")
    return accounts


# ===== Main Analyzer =====
def analyze_all(input_dir="output", output_dir="output/analysis", multi_account=True):
    os.makedirs(output_dir, exist_ok=True)
    analysis_summary = {}

    # Case 1: Multi-account simulation
    if multi_account:
        accounts = load_test_accounts()
        if accounts:
            print(f"🔹 Found {len(accounts)} test accounts.")
            for acc in accounts:
                acc_id = acc.get("account_id", "unknown")
                print(f"\n=== Analyzing Account: {acc_id} ===")

                res = acc.get("resources", {})
                ec2 = analyze_ec2_instances(res.get("EC2", []))
                ebs = analyze_ebs_volumes(res.get("EBS", []))
                s3 = analyze_s3_buckets(res.get("S3", []))
                rds = analyze_rds_instances(res.get("RDS", []))

                acc_summary = {
                    "EC2_IdleCount": len(ec2),
                    "EBS_IdleCount": len(ebs),
                    "S3_IdleCount": len(s3),
                    "RDS_IdleCount": len(rds)
                }

                analysis_summary[acc_id] = acc_summary
            # Save combined summary
            with open(os.path.join(output_dir, "multi_account_summary.json"), "w") as f:
                json.dump(analysis_summary, f, indent=2)
            return analysis_summary

    # Case 2: Normal single-account mode (existing Day 3 logic)
    ec2_files = [f for f in os.listdir(input_dir) if f.startswith("ec2_instances")]
    ec2_idle_total = []
    for f in ec2_files:
        ec2_data = load_json(os.path.join(input_dir, f))
        idle_ec2 = analyze_ec2_instances(ec2_data)
        ec2_idle_total.extend(idle_ec2)
    with open(os.path.join(output_dir, "idle_ec2.json"), "w") as f:
        json.dump(ec2_idle_total, f, indent=2, default=str)
    analysis_summary["EC2_IdleCount"] = len(ec2_idle_total)

    ebs_files = [f for f in os.listdir(input_dir) if f.startswith("ebs_volumes")]
    ebs_idle_total = []
    for f in ebs_files:
        ebs_data = load_json(os.path.join(input_dir, f))
        idle_ebs = analyze_ebs_volumes(ebs_data)
        ebs_idle_total.extend(idle_ebs)
    with open(os.path.join(output_dir, "idle_ebs.json"), "w") as f:
        json.dump(ebs_idle_total, f, indent=2, default=str)
    analysis_summary["EBS_IdleCount"] = len(ebs_idle_total)

    s3_file = os.path.join(input_dir, "s3_buckets.json")
    idle_s3 = analyze_s3_buckets(load_json(s3_file))
    with open(os.path.join(output_dir, "idle_s3.json"), "w") as f:
        json.dump(idle_s3, f, indent=2, default=str)
    analysis_summary["S3_IdleCount"] = len(idle_s3)

    rds_files = [f for f in os.listdir(input_dir) if f.startswith("rds_instances")]
    rds_idle_total = []
    for f in rds_files:
        rds_data = load_json(os.path.join(input_dir, f))
        idle_rds = analyze_rds_instances(rds_data)
        rds_idle_total.extend(idle_rds)
    with open(os.path.join(output_dir, "idle_rds.json"), "w") as f:
        json.dump(rds_idle_total, f, indent=2, default=str)
    analysis_summary["RDS_IdleCount"] = len(rds_idle_total)

    with open(os.path.join(output_dir, "summary_analysis.json"), "w") as f:
        json.dump(analysis_summary, f, indent=2)

    return analysis_summary


# ===== Entry Point =====
if __name__ == "__main__":
    summary = analyze_all()
    print("\n✅ Resource Analysis Complete. Summary:")
    print(json.dumps(summary, indent=2))
    print("\n📁 Check output/analysis/ for detailed JSON results.")
