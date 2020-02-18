import boto3
import os
import datetime

# Get the instance list which have a specific tag key and value
def list_instances_by_tag_value(region, tagkey, tagvalue, action, time, weekend):
    ec2client = boto3.client('ec2', region_name=region)
    if (weekend and action == 'start'):
        response = ec2client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:'+tagkey,
                    'Values': [tagvalue]
                },
                {
                    'Name': 'tag:Weekend',
                    'Values': ['True']
                },
                {
                    'Name': 'tag:Time-'+action,
                    'Values': [time]
                }
            ]    
        )
    else:
        response = ec2client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:'+tagkey,
                    'Values': [tagvalue]
                },
                {
                    'Name': 'tag:Time-'+action,
                    'Values': [time]
                }
            ]    
        )
        
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    return instancelist

# Lambda Main program
def lambda_handler(event, context):
    
    action = event['action']
    region = event['region']
    
    
    # Get the lambda execution time and convert it to Colombia timezone (GMT-5)
    now = datetime.datetime.now() - datetime.timedelta(hours=5)
    time = str(now.hour)
    print(time)
    
    # Check if is weekend
    if (now.isoweekday() == 6 or now.isoweekday() == 7):
        weekend = True
    else:
        weekend = False

    # Get the instance list based on the set conditions, action and hour.
    instances = list_instances_by_tag_value(region, "Schedulable", "True", action, time, weekend)
    
    if instances:
        if (action == 'stop'):
            ec2 = boto3.client('ec2', region_name=region)
            ec2.stop_instances(InstanceIds=instances)
            print ('The following instances were stopped: ' + str(instances))
            
        elif (action == 'start'):
            ec2 = boto3.client('ec2', region_name=region)
            ec2.start_instances(InstanceIds=instances)
            print ('The following instances were started: ' + str(instances))
            
        else:
            print ('Unsupported Action')
    else:
        print ('No instances were changed this time: ' + str(time))    