import boto3
import time

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = event['InstanceId']
    snapshot_id = event['SnapshotResult']['SnapshotIds'][0]

    # Stop instance
    ec2.stop_instances(InstanceIds=[instance_id])
    ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

    # Get root volume
    reservations = ec2.describe_instances(InstanceIds=[instance_id])['Reservations']
    instance = reservations[0]['Instances'][0]

    root_device = instance['RootDeviceName']
    root_volume_id = None
    availability_zone = instance['Placement']['AvailabilityZone']

    for bd in instance['BlockDeviceMappings']:
        if bd['DeviceName'] == root_device:
            root_volume_id = bd['Ebs']['VolumeId']

    # Detach old volume
    ec2.detach_volume(VolumeId=root_volume_id)
    time.sleep(10)

    # Create new volume from snapshot
    new_vol = ec2.create_volume(
        SnapshotId=snapshot_id,
        AvailabilityZone=availability_zone
    )

    ec2.get_waiter('volume_available').wait(
        VolumeIds=[new_vol['VolumeId']]
    )

    # Attach new volume
    ec2.attach_volume(
        VolumeId=new_vol['VolumeId'],
        InstanceId=instance_id,
        Device=root_device
    )

    # Start instance
    ec2.start_instances(InstanceIds=[instance_id])

    return {"rollback": "completed"}
