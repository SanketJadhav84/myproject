# app/services/ec2_services.py
import os
import boto3
from botocore.exceptions import ClientError

# Optional default region (use env var in prod)
REGION = os.environ.get("AWS_REGION", "ap-south-1")

def get_ec2_client():
    """
    Create and return a boto3 EC2 client on demand.
    This avoids creating the client at import time which can block app startup.
    """
    return boto3.client("ec2", region_name=REGION)

def describe(instance_ids=None):
    items = []
    ec2 = get_ec2_client()
    params = {}
    if instance_ids:
        params["InstanceIds"] = instance_ids

    try:
        response = ec2.describe_instances(**params)
    except ClientError as e:
        # return empty list on error, you can also log or re-raise as needed
        print("Error describing instances:", e)
        return items

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            # Get name tag if present
            name = ""
            for tag in instance.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value")
                    break

            data = {
                "instance_id": instance.get("InstanceId"),
                "name": name,
                "instance_type": instance.get("InstanceType"),
                "state": instance.get("State", {}).get("Name"),
                "private_ip": instance.get("PrivateIpAddress"),
                "launch_time": str(instance.get("LaunchTime"))
            }
            items.append(data)

    return items

def start_instance(instance_id, dry_run=True):
    ec2 = get_ec2_client()
    try:
        resp = ec2.start_instances(InstanceIds=[instance_id], DryRun=dry_run)
        # Try to read returned current state if available
        current = None
        try:
            current = resp["StartingInstances"][0]["CurrentState"]["Name"]
        except Exception:
            current = None
        return {"success": True, "dry_run": dry_run, "message": "Start requested", "current_state": current}
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code == "DryRunOperation":
            return {"success": True, "dry_run": True, "message": "DryRunOperation: request would have succeeded."}
        return {"success": False, "dry_run": dry_run, "message": str(e)}

def stop_instance(instance_id, dry_run=True):
    ec2 = get_ec2_client()
    try:
        resp = ec2.stop_instances(InstanceIds=[instance_id], DryRun=dry_run)
        current = None
        try:
            current = resp["StoppingInstances"][0]["CurrentState"]["Name"]
        except Exception:
            current = None
        return {"success": True, "dry_run": dry_run, "message": "Stop requested", "current_state": current}
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code == "DryRunOperation":
            return {"success": True, "dry_run": True, "message": "DryRunOperation: request would have succeeded."}
        return {"success": False, "dry_run": dry_run, "message": str(e)}
