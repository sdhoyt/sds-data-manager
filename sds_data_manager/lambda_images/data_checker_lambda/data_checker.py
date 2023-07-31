import os

import boto3
from boto3.dynamodb.conditions import Attr, Key


def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

    # Read Dynamodb table to get all data with L1a_status = 'PENDING'
    instrument = event["instrument"]
    query_response = table.query(
        KeyConditionExpression=Key("instrument").eq(instrument),
        FilterExpression=Attr("status").eq("PENDING"),
    )

    if query_response["Count"] == 0:
        print("No data to process")
        return {"status_code": 204}

    print(query_response)
    return {"status_code": 200}
