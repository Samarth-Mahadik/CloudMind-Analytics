import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

# Use AWS_PROFILE env var or default profile
session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))

def list_ec2_instances(region="us-east-1"):
    ec2 = session.client("ec2", region_name=region)
    resp = ec2.describe_instances()
    instances = []
    for r in resp.get("Reservations", []):
        for i in r.get("Instances", []):
            instances.append({
                "InstanceId": i.get("InstanceId"),
                "State": i.get("State", {}).get("Name"),
                "InstanceType": i.get("InstanceType"),
                "LaunchTime": i.get("LaunchTime").isoformat() if i.get("LaunchTime") else None,
                "Tags": i.get("Tags", [])
            })
    return instances
