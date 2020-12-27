import boto3
import json
import os
import datetime
import time
from dateutil.relativedelta import relativedelta


def lambda_handler(event, context):
    
    s3outputbucketname = os.environ['s3outputbucketname']
    outputfolder = os.environ['outputfolder'] + '/'
   
    map_migrated_db = os.environ['map_migrated_db']
    map_migrated_table = os.environ['map_migrated_table']
    extraction_query_name = os.environ['extraction_query_name']
    athena_output_location = os.environ['athena_output_location']
    
    #Check if output folder exists. If it doesn't exist then create an output folder. If it exists, then proceed to empty
    create_s3outputbucketfolder(s3outputbucketname, outputfolder)
    
    # Empty the existing MAP query output bucket for linked accounts
    empty_s3outputbucket(s3outputbucketname, outputfolder)
    
    #Retrieve and run Athena Extraction query- extracts relevant MAP reports for the linked member
    run_athenaextractionquery(map_migrated_db,map_migrated_table,extraction_query_name,athena_output_location)
    return 

def create_s3outputbucketfolder(s3outputbucketname, outputfolder):

    client = boto3.client('s3')
    response = client.list_objects_v2(
            Bucket=s3outputbucketname
    )
    if (response['KeyCount'] == 0):
        response = client.put_object(
            Bucket=s3outputbucketname, 
            Key=outputfolder
        )
        

def empty_s3outputbucket(s3outputbucketname, outputfolder):

    client = boto3.client('s3')
    response = client.list_objects_v2(
            Bucket=s3outputbucketname,
            Prefix=outputfolder
    )
    if (response['KeyCount'] > 0):
        s3objects = response['Contents']
        for s3object in s3objects:
            objectkey = s3object['Key']
            response = client.delete_object(
                Bucket=s3outputbucketname,
                Key=objectkey
            )
            objectkey = s3object['Key']
            response = client.delete_object(
                Bucket=s3outputbucketname,
                Key=objectkey
            )

# Run MAP Extraction Query for linked accounts
def run_athenaextractionquery(map_migrated_db, map_migrated_table, extraction_query_name, athena_output_location):

    client = boto3.client('athena')
    response = client.list_named_queries()
    named_query_IDs = response['NamedQueryIds']
    
    for query_ID in named_query_IDs: 
        named_query = client.get_named_query(
            NamedQueryId=query_ID
        )
        query_string = named_query['NamedQuery']['QueryString']
        query_name = named_query['NamedQuery']['Name']
        
        if extraction_query_name in query_name:
            drop_query_string = 'DROP TABLE ' + map_migrated_db + '.temp_table'
            executionID_drop = client.start_query_execution(
                QueryString=drop_query_string,
                ResultConfiguration={
                    'OutputLocation': athena_output_location,
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'SSE_S3',
                    }
                }
            )
            
            executionID_create = client.start_query_execution(
                QueryString=query_string,
                ResultConfiguration={
                    'OutputLocation': athena_output_location,
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'SSE_S3',
                    }
                }
            )


    