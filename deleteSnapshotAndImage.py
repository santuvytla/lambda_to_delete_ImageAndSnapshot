
import boto3
import collections
from dateutil.parser import parse
import datetime
import time
import sys
age = 0
ec = boto3.client('ec2', 'us-east-1')
ec2 = boto3.resource('ec2', 'us-east-1')
images = ec.describe_images(Owners=[
        'self'
    ])
imagesList = []

def lambda_handler(event, context):
        def days_old(date):
            get_date_obj = parse(date)
            date_obj = get_date_obj.replace(tzinfo=None)
            diff = datetime.datetime.now() - date_obj
            return diff.days
        
        for ami in images['Images']:
            create_date = ami['CreationDate']
            ami_id = ami['ImageId']

            day_old = days_old(create_date)
            if day_old >= age:
               imagesList.append(ami_id)
                
        myAccount = boto3.client('sts').get_caller_identity()['Account']
        snapshots = ec.describe_snapshots(MaxResults=1000,
                                          OwnerIds=[myAccount])['Snapshots']
        
        for image in imagesList:
            print("deregistering image %s" % image)
            amiResponse = ec.deregister_image(
                DryRun=False,
                ImageId=image,
            )

            for snapshot in snapshots:
                if snapshot['Description'].find(image) > 0:
                    snap = ec.delete_snapshot(
                        SnapshotId=snapshot['SnapshotId'])
                    print("Deleting snapshot " + snapshot['SnapshotId'])
