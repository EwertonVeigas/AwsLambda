import boto3

region = 'us-east-1'
instances = ['i-123456789', 'i-02365478']

def lambda_handler(event, context):
    
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances)