import boto3
import datetime
import json

def strings(l):
    st = ""
    instances = []
    for i in l:
        instances.append(i["instanceId"])
    EC2 = boto3.client("ec2",region_name="eu-west-1")
    instances_details = EC2.describe_instances(InstanceIds=instances)
    print instances_details
    instances_details = instances_details["Reservations"][0]["Instances"]
    for i in instances_details:
        if i["InstanceType"] != "t2.micro":
            st = st + "\t\t" + i["InstanceId"] +  " which is of type " + i["InstanceType"] + "\n"
    print " Instances  ", st
    return st

def lambda_handler(event, context):
    
    dct = dict()
    dct["value"]=event
    dct = json.loads(json.dumps(dct))
    state = dct["value"]["detail"]["eventName"]
    time = dct["value"]["detail"]["eventTime"]
    parameters =""
    if state == "RunInstances":
        parameters="responseElements"
    else:
        parameters="requestParameters"
        
    instances = dct["value"]["detail"][parameters]["instancesSet"]["items"]
    
    k = strings(instances)
    
    if len(k) != 0:
        message = "The " + state + " event was called on the instances on " + time + " UTC in region <Region>\n"
        message = message +  "The instances are: \n" + k
        message = message +  "\n\nThis action was invoked by resource with ARN: " + dct["value"]["detail"]["userIdentity"]["arn"]
        subject = "EC2 " + state + " API called on " + " ".join(time.split("T")) + " UTC in region <Region>"
        print subject
        print message
        SNS = boto3.client("sns", region_name='eu-west-1')
        print SNS.publish(
                TopicArn="arn:aws:sns:eu-west-1:538411234227:Terminate-Instance-Notification",
                Message=message,
                Subject=subject
            )
    else:
        print "All are T2.Micro Instances"
