import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    current_time = datetime.now()

    amis = ec2.describe_images(Owners=['self'])['Images']


    for ami in amis:
        create_time = ami['CreationDate']
        create_time = datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        age = current_time - create_time

        if age.days > 15:
            ami_id = ami['ImageId']
            print(f'Deleting AMI: {ami_id}')
            ec2.deregister_image(ImageId=ami_id)
