import json
import os

import boto3
import psycopg2
import requests
from psycopg2 import Error

# TODO: The code in this lambda will be updated in the next PR
# to reflect the schema that will be needed by the SDC.
# Its current state is the bare minimum to get a table
# created to allow files to be indexed.

# Add code to get Secret instead
s3 = boto3.client("s3")


def send_response(event, context, response_data, response_status):
    response_url = event["ResponseURL"]
    response_body = {
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: "
        + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": response_data,
    }

    json_response_body = json.dumps(response_body)

    headers = {"content-type": "", "content-length": str(len(json_response_body))}

    try:
        response = requests.put(response_url, data=json_response_body, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending response: {e}")


def lambda_handler(event, context):
    secret_name = os.environ["SECRET_NAME"]
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    secret_string = client.get_secret_value(SecretId=secret_name)["SecretString"]
    secret = json.loads(secret_string)

    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(
            host=secret["host"],
            database=secret["dbname"],
            user=secret["username"],
            password=secret["password"],
            port=secret["port"],
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # SQL query to create a table
        create_table_query = """
            CREATE TABLE IF NOT EXISTS metadata (
                id VARCHAR(100) PRIMARY KEY,
                mission VARCHAR(100),
                type VARCHAR(100),
                instrument VARCHAR(100),
                level VARCHAR(10),
                year INT,
                month INT,
                day INT,
                version VARCHAR(100),
                extension VARCHAR(10)
            )
        """

        # Execute the create table query
        cursor.execute(create_table_query)
        response_status = "SUCCESS"
        response_data = create_table_query

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        response_status = "FAILED"
        response_data = error

    finally:
        # Close the cursor and connection
        if connection:
            connection.commit()
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")
        send_response(event, context, response_data, response_status)
