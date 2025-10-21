#!/usr/bin/env python3
"""
Day 2 - CloudMind Analytics
Data gathering: EC2, EBS (volumes), S3 buckets, RDS instances
Outputs JSON files under ./output/
"""

import boto3
import json
import os
import argparse
from botocore.exceptions import NoCredentialsError, ClientError

def create_session(profile=None):
    if profile:
        return boto3.Session(profile_name=profile)
    return boto3.Session()

def list_ec2_instances(session, region):
    ec2 = session.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_instances")
    instances = []
    for page in paginator.paginate():
        for res in page.get("Reservations", []):
            for i in res.get("Instances", []):
                inst = {
                    "InstanceId": i.get("InstanceId"),
                    "InstanceType": i.get("InstanceType"),
                    "State": i.get("State", {}).get("Name"),
                    "PublicIpAddress": i.get("PublicIpAddress"),
                    "PrivateIpAddress": i.get("PrivateIpAddress"),
                    "LaunchTime": i.get("LaunchTime").isoformat() if i.get("LaunchTime") else None,
                    "AvailabilityZone": i.get("Placement", {}).get("AvailabilityZone"),
                    "Tags": i.get("Tags", [])
                }
                vols = []
                for b in i.get("BlockDeviceMappings", []):
                    v = b.get("Ebs", {}).get("VolumeId")
                    if v:
                        vols.append(v)
                inst["AttachedVolumes"] = vols
                instances.append(inst)
    return instances

def list_ebs_volumes(session, region):
    ec2 = session.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_volumes")
    volumes = []
    for page in paginator.paginate():
        for v in page.get("Volumes", []):
            volumes.append({
                "VolumeId": v.get("VolumeId"),
                "Size_GB": v.get("Size"),
                "State": v.get("State"),
                "VolumeType": v.get("VolumeType"),
                "Encrypted": v.get("Encrypted"),
                "AvailabilityZone": v.get("AvailabilityZone"),
                "CreateTime": v.get("CreateTime").isoformat() if v.get("CreateTime") else None,
                "Attachments": [
                    {
                        "InstanceId": a.get("InstanceId"),
                        "Device": a.get("Device"),
                        "AttachTime": a.get("AttachTime").isoformat() if a.get("AttachTime") else None,
                        "State": a.get("State")
                    } for a in v.get("Attachments", [])
                ],
                "Tags": v.get("Tags", [])
            })
    return volumes

def list_s3_buckets(session, count_objects=False, max_objects_per_bucket=None):
    s3 = session.client("s3")
    resp = s3.list_buckets()
    buckets = []
    for b in resp.get("Buckets", []):
        name = b.get("Name")
        created = b.get("CreationDate").isoformat() if b.get("CreationDate") else None
        # get region / location
        region = None
        try:
            region = s3.get_bucket_location(Bucket=name).get("LocationConstraint")
        except ClientError:
            region = None
        info = {"Name": name, "CreationDate": created, "Region": region}
        if count_objects:
            total_size = 0
            total_objects = 0
            paginator = s3.get_paginator("list_objects_v2")
            try:
                for page in paginator.paginate(Bucket=name):
                    contents = page.get("Contents", [])
                    total_objects += len(contents)
                    for obj in contents:
                        total_size += obj.get("Size", 0)
                    if max_objects_per_bucket and total_objects >= max_objects_per_bucket:
                        break
                info["ObjectCount"] = total_objects
                info["TotalSizeBytes"] = total_size
            except ClientError as e:
                info["ObjectCount"] = None
                info["TotalSizeBytes"] = None
                info["Error"] = str(e)
        buckets.append(info)
    return buckets

def list_rds_instances(session, region):
    rds = session.client("rds", region_name=region)
    instances = []
    try:
        resp = rds.describe_db_instances()
        for db in resp.get("DBInstances", []):
            instances.append({
                "DBInstanceIdentifier": db.get("DBInstanceIdentifier"),
                "DBInstanceClass": db.get("DBInstanceClass"),
                "Engine": db.get("Engine"),
                "EngineVersion": db.get("EngineVersion"),
                "DBInstanceStatus": db.get("DBInstanceStatus"),
                "AllocatedStorage_GB": db.get("AllocatedStorage"),
                "Endpoint": db.get("Endpoint", {}).get("Address"),
                "Port": db.get("Endpoint", {}).get("Port"),
                "MultiAZ": db.get("MultiAZ"),
                "InstanceCreateTime": db.get("InstanceCreateTime").isoformat() if db.get("InstanceCreateTime") else None,
                "AvailabilityZone": db.get("AvailabilityZone"),
                "StorageType": db.get("StorageType")
            })
    except ClientError as e:
        raise
    return instances

def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)
    return path

def gather_all(profile, regions, count_s3=False, max_objects=None, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    session = create_session(profile)
    summary = {}
    # S3 (global)
    buckets = list_s3_buckets(session, count_s3, max_objects)
    save_json(buckets, os.path.join(out_dir, "s3_buckets.json"))
    summary["s3_buckets_file"] = "s3_buckets.json"
    for region in regions:
        region_data = {}
        region_data["ec2_instances"] = list_ec2_instances(session, region)
        save_json(region_data["ec2_instances"], os.path.join(out_dir, f"ec2_instances_{region}.json"))
        region_data["ebs_volumes"] = list_ebs_volumes(session, region)
        save_json(region_data["ebs_volumes"], os.path.join(out_dir, f"ebs_volumes_{region}.json"))
        region_data["rds_instances"] = list_rds_instances(session, region)
        save_json(region_data["rds_instances"], os.path.join(out_dir, f"rds_instances_{region}.json"))
        summary[region] = {
            "ec2_instances_file": f"ec2_instances_{region}.json",
            "ebs_volumes_file": f"ebs_volumes_{region}.json",
            "rds_instances_file": f"rds_instances_{region}.json"
        }
    save_json(summary, os.path.join(out_dir, "summary.json"))
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CloudMind Day 2 - Data gathering")
    parser.add_argument("--profile", help="AWS profile name (optional)", default=None)
    parser.add_argument("--regions", nargs="+", help="AWS regions (space separated)", default=["us-east-1"])
    parser.add_argument("--count-s3", action="store_true", help="Count objects and total size for each S3 bucket (can be slow)")
    parser.add_argument("--max-objects", type=int, default=None, help="Max objects to scan per bucket (testing)")
    parser.add_argument("--out", default="output", help="Output directory")
    args = parser.parse_args()
    try:
        summary = gather_all(args.profile, args.regions, args.count_s3, args.max_objects, args.out)
        print("Data gathering complete. Summary:")
        print(json.dumps(summary, indent=2))
        print(f"Output files are in ./{args.out}/")
    except NoCredentialsError:
        print("ERROR: AWS credentials not found. Set AWS_PROFILE or export credentials.")
    except ClientError as e:
        print("AWS ClientError:", e)
