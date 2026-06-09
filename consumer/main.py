import json
import boto3
from secret_keys import SecretKeys

secret_keys = SecretKeys()
sqs_client = boto3.client("sqs",region_name=secret_keys.REGION_NAME,)
ecs_client = boto3.client("ecs", region_name=secret_keys.REGION_NAME)

def poll_sqs():
    while True:
       response = sqs_client.receive_message(
            QueueUrl=secret_keys.AWS_SQS_VIDEO_PROCESSING,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

       for message in response.get("Messages",[]):
            message_body=json.loads(message.get("Body"))
            if(
                "Service" in message_body and
                "Event" in message_body and
                message_body.get("Event") == "s3:TestEvent"
            ):
                sqs_client.delete_message(
                    QueueUrl=secret_keys.AWS_SQS_VIDEO_PROCESSING,
                    ReceiptHandle=message["ReceiptHandle"],
                )
                continue
            if "Records" in message_body:
                s3_record=message_body['Records'][0]['s3']
                bucket_name=s3_record['bucket']['name']
                s3_key=s3_record['object']['key']
                #spin up a docker container
                response= ecs_client.run_task(
                    cluster=secret_keys.AWS_TRANSCODER_CLUSTER,
                    launchType=secret_keys.AWS_TASK_LAUNCH_TYPE,
                    taskDefinition=secret_keys.AWS_TRANSCODER_TASK_DEF,
                    overrides={
                       "containerOverrides":[
                           {
                                "name":"video-transcoder",
                                "environment":[
                                    {"name":"S3_BUCKET","value": bucket_name},
                                    {"name": "S3_KEY","value": s3_key},
                                ]
                           }
                       ]
                    },
                    networkConfiguration={
                        "awsvpcConfiguration":{
                            "subnets":[
                                "subnet-097ad0a6aaf7f91dd",
                                "subnet-05bf4680cd5f2afae",
                                "subnet-02076733551e33aaf"
                            ],
                            "assignPublicIp":"ENABLED",
                            "securityGroups":["sg-0bf431d7bbfd20998"]
                        }
                    }
                )
                print(response)
                sqs_client.delete_message(
                    QueueUrl=secret_keys.AWS_SQS_VIDEO_PROCESSING,
                    ReceiptHandle=message["ReceiptHandle"],
                )

poll_sqs()