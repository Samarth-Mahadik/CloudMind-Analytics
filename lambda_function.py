import boto3
import os
from botocore.exceptions import ClientError
import json
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-east-1")
SNS_TOPIC_NAME = os.getenv("SNS_TOPIC_NAME", "CloudMindAlerts")

# clients
ec2 = boto3.client("ec2", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)

def get_or_create_topic(name):
    resp = sns.create_topic(Name=name)
    return resp["TopicArn"]

def find_idle_ec2(threshold_days=7):
    out = []
    paginator = ec2.get_paginator("describe_instances")
    now = datetime.now(timezone.utc)
    for page in paginator.paginate():
        for res in page.get("Reservations", []):
            for i in res.get("Instances", []):
                state = i.get("State", {}).get("Name")
                launch = i.get("LaunchTime")
                if state == "stopped" and launch:
                    days = (now - launch).days
                    if days >= threshold_days:
                        out.append({"InstanceId": i.get("InstanceId"), "StoppedDays": days})
    return out

def find_unattached_volumes():
    out = []
    paginator = ec2.get_paginator("describe_volumes")
    for page in paginator.paginate():
        for v in page.get("Volumes", []):
            if not v.get("Attachments"):
                out.append({"VolumeId": v.get("VolumeId"), "Size_GB": v.get("Size")})
    return out

def find_old_empty_buckets(empty_days_threshold=30):
    out = []
    resp = s3.list_buckets()
    now = datetime.now(timezone.utc)
    for b in resp.get("Buckets", []):
        name = b.get("Name")
        created = b.get("CreationDate")
        # try to count a few objects to detect emptiness (fast)
        try:
            obj = s3.list_objects_v2(Bucket=name, MaxKeys=1)
            obj_count = obj.get("KeyCount", 0)
        except ClientError:
            obj_count = None
        if obj_count == 0 and created:
            age = (now - created).days
            if age >= empty_days_threshold:
                out.append({"Name": name, "AgeDays": age})
    return out

def find_idle_rds(threshold_days=14):
    out = []
    resp = rds.describe_db_instances()
    now = datetime.now(timezone.utc)
    for db in resp.get("DBInstances", []):
        status = db.get("DBInstanceStatus")
        create = db.get("InstanceCreateTime")
        if status in ("available", "stopped") and create:
            age = (now - create).days
            if age >= threshold_days:
                out.append({"DBInstanceIdentifier": db.get("DBInstanceIdentifier"), "IdleDays": age})
    return out

def compose_message(ec2s, ebss, s3s, rds_list):
    msg = "🔔 CloudMind Lambda Alert — Idle Resources Report\n\n"
    if ec2s:
        msg += f"EC2 stopped > threshold: {[i['InstanceId'] for i in ec2s]}\n"
    if ebss:
        msg += f"Unattached EBS volumes: {[v['VolumeId'] for v in ebss]}\n"
    if s3s:
        msg += f"Old empty S3 buckets: {[b['Name'] for b in s3s]}\n"
    if rds_list:
        msg += f"Idle RDS instances: {[r['DBInstanceIdentifier'] for r in rds_list]}\n"
    if not (ec2s or ebss or s3s or rds_list):
        msg += "All resources OK — no idle detections.\n"
    msg += f"\nReport generated at {datetime.now(timezone.utc).isoformat()}\n"
    return msg

def lambda_handler(event, context):
    topic_arn = get_or_create_topic(SNS_TOPIC_NAME)
    ec2s = find_idle_ec2()
    ebss = find_unattached_volumes()
    s3s = find_old_empty_buckets()
    rds_list = find_idle_rds()

    message = compose_message(ec2s, ebss, s3s, rds_list)

    try:
        resp = sns.publish(TopicArn=topic_arn, Subject="CloudMind Idle Resource Alert (Lambda)", Message=message)
        return {"status": "success", "MessageId": resp.get("MessageId")}
    except ClientError as e:
        return {"status": "error", "error": str(e)}
