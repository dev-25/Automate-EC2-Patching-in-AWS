import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = event['InstanceId']

    ec2.reboot_instances(
        InstanceIds=[instance_id]
    )

    return {"reboot": "initiated"}
