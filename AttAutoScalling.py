import boto3
import datetime

def lambda_handler(event, context):
    # Configuração das informações do ambiente
    instance_id = 'i-00123456789'   # Substitua pelo ID da instância que você deseja criar a imagem AMI
    launch_template_name = 'MOD-DEV'   # Substitua pelo nome do Launch Template que você deseja atualizar
    region = 'us-east-1'   # Substitua pela região desejada

    # Cria o cliente do EC2 e do Auto Scaling
    ec2_client = boto3.client('ec2', region_name=region)
    autoscaling_client = boto3.client('autoscaling', region_name=region)

    # Cria uma imagem (AMI) da instância
    image_name = f'{launch_template_name}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    response = ec2_client.create_image(
        InstanceId=instance_id,
        Name=image_name,
        NoReboot=False
    )

    # Obtém o ID da nova AMI criada
    new_ami_id = response['ImageId']

    # Aguarda até que a AMI esteja disponível
    waiter = ec2_client.get_waiter('image_available')
    waiter.wait(
        ImageIds=[new_ami_id],
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
    )

    # Descreve o Launch Template para obter o ID e outras informações
    response = ec2_client.describe_launch_templates(
        LaunchTemplateNames=[launch_template_name]
    )

    # Obtém o ID do Launch Template atual
    launch_template_id = response['LaunchTemplates'][0]['LaunchTemplateId']

    # Cria uma nova versão do Launch Template usando o serviço EC2
    response = ec2_client.create_launch_template_version(
        LaunchTemplateId=launch_template_id,
        SourceVersion='$Latest',
        LaunchTemplateData={
            'ImageId': new_ami_id   # Atualiza o ID da AMI com o novo valor
        }
    )

    # Obtém o ID da nova versão do Launch Template
    new_launch_template_version_id = response['LaunchTemplateVersion']['VersionNumber']
    
    # Converte a versão para string
    new_launch_template_version_id = str(new_launch_template_version_id)

    # Atualiza o Auto Scaling Group para usar o novo Launch Template
    response = autoscaling_client.update_auto_scaling_group(
        AutoScalingGroupName='AutoScalling_Name',   # Substitua pelo nome do Auto Scaling Group correto
        LaunchTemplate={
            'LaunchTemplateName': launch_template_name,
            'Version': new_launch_template_version_id   # Usa a nova versão do Launch Template
        }
    )
    
    # Inicia a atualização de instâncias do Auto Scaling Group
    response = autoscaling_client.start_instance_refresh(
        AutoScalingGroupName='AutoScalling_Name',
        Strategy= 'Rolling',
        Preferences= {
            'MinHealthyPercentage': 100,
            'StandbyInstances': 'Ignore',
            'ScaleInProtectedInstances': 'Ignore',
        }
    )

    return {
        'statusCode': 200,
        'body': 'AMI do Launch Template atualizada com sucesso!'
    }
