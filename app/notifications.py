import boto3
import json
import os
from botocore.exceptions import ClientError

# ==========================================================
# 🌤️ CloudMind - AWS Idle Resource Notification System
# ==========================================================

ANALYSIS_PATH = "output/analysis"
TOPIC_NAME = "CloudMindAlerts"
REGION = "us-east-1"  # ✅ Free-tier friendly region


# ----------------------------------------------------------
# Step 1: Load JSON Data
# ----------------------------------------------------------
def load_json(file_path):
    """Load JSON data safely."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


# ----------------------------------------------------------
# Step 2: Fetch Idle Resource Data
# ----------------------------------------------------------
idle_ec2 = load_json(os.path.join(ANALYSIS_PATH, "idle_ec2.json"))
idle_ebs = load_json(os.path.join(ANALYSIS_PATH, "idle_ebs.json"))
idle_s3 = load_json(os.path.join(ANALYSIS_PATH, "idle_s3.json"))
idle_rds = load_json(os.path.join(ANALYSIS_PATH, "idle_rds.json"))


# ----------------------------------------------------------
# Step 3: Setup SNS Client
# ----------------------------------------------------------
sns_client = boto3.client("sns", region_name=REGION)


# ----------------------------------------------------------
# Step 4: Create or Use Existing SNS Topic
# ----------------------------------------------------------
def get_or_create_topic(topic_name):
    """Create or get an existing SNS topic."""
    try:
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]
        print(f"✅ SNS Topic Ready: {topic_arn}")
        return topic_arn
    except ClientError as e:
        print(f"❌ Error creating/getting topic: {e}")
        return None


topic_arn = get_or_create_topic(TOPIC_NAME)


# ----------------------------------------------------------
# Step 5: Compose Notification Message
# ----------------------------------------------------------
def compose_message():
    """Create summary message for idle resources."""
    message = "🔔 CloudMind Analytics - Idle Resource Alert:\n\n"

    if idle_ec2:
        message += f"• EC2 Instances: {[i.get('InstanceId') for i in idle_ec2]}\n"
    if idle_ebs:
        message += f"• EBS Volumes: {[v.get('VolumeId') for v in idle_ebs]}\n"
    if idle_s3:
        message += f"• S3 Buckets: {[b.get('Name') for b in idle_s3]}\n"
    if idle_rds:
        message += f"• RDS Databases: {[r.get('DBInstanceIdentifier') for r in idle_rds]}\n"

    if not (idle_ec2 or idle_ebs or idle_s3 or idle_rds):
        message += "✅ All resources are optimized. No idle usage detected.\n"

    return message


# ----------------------------------------------------------
# Step 6: Send Notification via SNS
# ----------------------------------------------------------
def send_notification(topic_arn, message):
    """Publish notification message to SNS topic."""
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="CloudMind Idle Resource Alert",
        )
        print("\n✅ Notification Sent Successfully!")
        print("📩 Message ID:", response["MessageId"])
    except ClientError as e:
        print(f"❌ Error sending notification: {e}")


# ----------------------------------------------------------
# Step 7: Main Execution
# ----------------------------------------------------------
def main():
    if not topic_arn:
        print("❌ SNS topic not available. Exiting.")
        return

    message = compose_message()
    print("\n📊 Generated Alert Message:")
    print("------------------------------------")
    print(message)
    print("------------------------------------")

    send_notification(topic_arn, message)


if __name__ == "__main__":
    main()
