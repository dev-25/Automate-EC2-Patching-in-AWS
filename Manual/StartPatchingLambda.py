import boto3

ssm = boto3.client('ssm')

def lambda_handler(event, context):
    instance_id = event['InstanceId']

    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunPatchBaseline",
        Parameters={
            "Operation": ["Install"],
            "RebootOption": ["RebootIfNeeded"]
        }
    )

    return {
        "CommandId": response['Command']['CommandId']
    }
