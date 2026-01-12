import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    snapshot_ids = event['SnapshotResult']['SnapshotIds']

    snapshots = ec2.describe_snapshots(
        SnapshotIds=snapshot_ids
    )['Snapshots']

    for snap in snapshots:
        if snap['State'] != 'completed':
            return {"status": "IN_PROGRESS"}

    return {"status": "COMPLETED"}