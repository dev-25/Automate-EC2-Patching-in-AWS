import boto3
import time

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = event['InstanceId']

    reservations = ec2.describe_instances(InstanceIds=[instance_id])['Reservations']
    volumes = []

    for r in reservations:
        for i in r['Instances']:
            for bd in i['BlockDeviceMappings']:
                volumes.append(bd['Ebs']['VolumeId'])

    snapshot_ids = []

    for vol in volumes:
        snap = ec2.create_snapshot(
            VolumeId=vol,
            Description=f"Pre-patch snapshot for {instance_id}"
        )
        snapshot_ids.append(snap['SnapshotId'])

    return {
        "SnapshotIds": snapshot_ids
    }
