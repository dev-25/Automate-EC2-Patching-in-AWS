# EC2 Automated Patching using AWS Step Functions & EventBridge

This project automates EC2 patching using **AWS Lambda**, **Step Functions**, **EventBridge**, and **SSM**, with snapshot backup and automatic rollback.

The solution is deployed using **two CloudFormation stacks**:
1. **Lambda stack** – contains all Python patching logic  
2. **Orchestration stack** – Step Functions + EventBridge scheduler

---

## Architecture Summary

For each EC2 instance:
1. Take EBS snapshot backup  
2. Wait until snapshot is completed  
3. Run SSM patching  
4. Check patch status  
5. Reboot if required  
6. Roll back from snapshot if patching fails  

Each instance runs **independently and in parallel**.

---

## Prerequisites

- AWS account access
- EC2 instances must:
  - Have **SSM Agent installed**
  - Have IAM role with `AmazonSSMManagedInstanceCore`
- AWS CLI access (AWS **CloudShell recommended**)

---

## Deployment Order (Important)

Always deploy stacks in this order:

1. **Lambda stack**
2. **Step Functions + EventBridge stack**

---

## 1. Deploy Lambda Stack

This stack creates all Lambda functions used for patching.

```bash
aws cloudformation deploy \
  --stack-name ec2-patching-lambdas \
  --template-file patching-lambdas.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

### Result
- 6 Lambda functions created
- Copy the Lambda ARNs for the next step

---

## 2. Deploy Step Functions + EventBridge Stack

This stack:
- Creates Step Functions state machine
- Creates EventBridge schedule
- Connects Lambdas to the workflow

```bash
aws cloudformation deploy \
  --stack-name ec2-patch-automation \
  --template-file patch-automation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ScheduleExpression="cron(0 20 ? * SUN *)" \
    InstanceIds="i-aaa,i-bbb,i-ccc" \
    TakeSnapshotLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:TakeSnapshotLambda" \
    CheckSnapshotStatusLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:CheckSnapshotStatusLambda" \
    StartPatchingLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:StartPatchingLambda" \
    CheckPatchStatusLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:CheckPatchStatusLambda" \
    RebootInstanceLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:RebootInstanceLambda" \
    RollbackInstanceLambdaArn="arn:aws:lambda:ap-south-1:XXXX:function:RollbackInstanceLambda"
```

### Parameters Explained

- **ScheduleExpression**  
  Example: `cron(0 20 ? * SUN *)` (weekly, UTC)

- **InstanceIds**  
  Comma-separated EC2 instance IDs

- **Lambda ARNs**  
  Copied from Lambda stack output

---

## Tags

All supported resources are tagged with:

```
Usage = Automate patch
```

---

## Verification

After deployment, verify:

- **CloudFormation**  
  Both stacks show `CREATE_COMPLETE`

- **Lambda**  
  6 functions exist

- **Step Functions**  
  State machine visible with Map state

- **EventBridge**  
  Rule is enabled

---

## Cleanup

Delete stacks in reverse order:

```bash
aws cloudformation delete-stack --stack-name ec2-patch-automation
aws cloudformation delete-stack --stack-name ec2-patching-lambdas
```

---

## Notes

- Always test on non-production instances first
- Start with a small number of instances
- Validate rollback at least once before production use
