import boto3

region = 'us-east-1'
instances = ['i-123456', 'i-789456']

def lambda_handler(event, context):
    
    ec2 = boto3.client('ec2', region_name=region)
    ec2.start_instances(InstanceIds=instances)