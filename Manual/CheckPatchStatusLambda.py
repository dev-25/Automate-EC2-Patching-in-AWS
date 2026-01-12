import boto3

ssm = boto3.client('ssm')

def lambda_handler(event, context):
    instance_id = event['InstanceId']
    command_id = event['PatchCommand']['CommandId']

    invocations = ssm.list_command_invocations(
        CommandId=command_id,
        InstanceId=instance_id,
        Details=True
    )['CommandInvocations']

    if not invocations:
        return {"status": "IN_PROGRESS"}

    status = invocations[0]['Status']

    if status in ['Pending', 'InProgress', 'Delayed']:
        return {"status": "IN_PROGRESS"}

    if status == 'Success':
        reboot_required = False
        plugins = invocations[0]['CommandPlugins']
        for p in plugins:
            if 'Reboot is required' in (p.get('Output') or ''):
                reboot_required = True

        return {
            "status": "SUCCESS",
            "rebootRequired": reboot_required
        }

    return {"status": "FAILED"}
