# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import logging
import sys
import time
from unittest import result
import boto3
from botocore.exceptions import ClientError
import requests 
import os
region ="us-east-1"
session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'),
    region_name =region
)
S3_BUCKET = os.environ.get('S3_BUCKET')
sys.path.append('../..')
from custom_waiter import CustomWaiter, WaitState
logger = logging.getLogger(__name__)


class TranscribeCompleteWaiter(CustomWaiter):
    def __init__(self, client):
        super().__init__(
            'TranscribeComplete', 'GetTranscriptionJob',
            'TranscriptionJob.TranscriptionJobStatus',
            {'COMPLETED': WaitState.SUCCESS, 'FAILED': WaitState.FAILURE},
            client)

    def wait(self, job_name):
        self._wait(TranscriptionJobName=job_name)
    
class VocabularyReadyWaiter(CustomWaiter):
    """
    Waits for the custom vocabulary to be ready for use.
    """
    def __init__(self, client):
        super().__init__(
            'VocabularyReady', 'GetVocabulary', 'VocabularyState',
            {'READY': WaitState.SUCCESS}, client)

    def wait(self, vocabulary_name):
        self._wait(VocabularyName=vocabulary_name)


def start_job(job_name, media_uri, media_format, language_code, transcribe_client,vocabulary_name=None):
    try:
        job_args = {
            'TranscriptionJobName': job_name,
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code}
        if vocabulary_name is not None:
            job_args['Settings'] = {'VocabularyName': vocabulary_name}
        print("Started transcription job ---2 %s.", job_name)
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logger.info("Started transcription job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't start transcription job %s.", job_name)
        raise
    else:
        return job


def list_jobs(job_filter, transcribe_client):
    try:
        response = transcribe_client.list_transcription_jobs(
            JobNameContains=job_filter)
        jobs = response['TranscriptionJobSummaries']
        next_token = response.get('NextToken')
        while next_token is not None:
            response = transcribe_client.list_transcription_jobs(
                JobNameContains=job_filter, NextToken=next_token)
            jobs += response['TranscriptionJobSummaries']
            next_token = response.get('NextToken')
        logger.info("Got %s jobs with filter %s.", len(jobs), job_filter)
    except ClientError:
        logger.exception("Couldn't get jobs with filter %s.", job_filter)
        raise
    else:
        return jobs


def get_job(job_name, transcribe_client):
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        logger.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logger.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job


def delete_job(job_name, transcribe_client):
    try:
        transcribe_client.delete_transcription_job(
            TranscriptionJobName=job_name)
        logger.info("Deleted job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't delete job %s.", job_name)
        raise

def create_vocabulary(
        vocabulary_name, language_code, transcribe_client,
        phrases=None, table_uri=None):
    try:
        vocab_args = {'VocabularyName': vocabulary_name, 'LanguageCode': language_code}
        if phrases is not None:
            vocab_args['Phrases'] = phrases
        elif table_uri is not None:
            vocab_args['VocabularyFileUri'] = table_uri
        response = transcribe_client.create_vocabulary(**vocab_args)
        logger.info("Created custom vocabulary %s.", response['VocabularyName'])
    except ClientError:
        logger.exception("Couldn't create custom vocabulary %s.", vocabulary_name)
        raise
    else:
        return response

def list_vocabularies(vocabulary_filter, transcribe_client):
    try:
        response = transcribe_client.list_vocabularies(
            NameContains=vocabulary_filter)
        vocabs = response['Vocabularies']
        next_token = response.get('NextToken')
        while next_token is not None:
            response = transcribe_client.list_vocabularies(
                NameContains=vocabulary_filter, NextToken=next_token)
            vocabs += response['Vocabularies']
            next_token = response.get('NextToken')
        logger.info(
            "Got %s vocabularies with filter %s.", len(vocabs), vocabulary_filter)
    except ClientError:
        logger.exception(
            "Couldn't list vocabularies with filter %s.", vocabulary_filter)
        raise
    else:
        return vocabs


def get_vocabulary(vocabulary_name, transcribe_client):
  
    try:
        response = transcribe_client.get_vocabulary(VocabularyName=vocabulary_name)
        logger.info("Got vocabulary %s.", response['VocabularyName'])
    except ClientError:
        logger.exception("Couldn't get vocabulary %s.", vocabulary_name)
        raise
    else:
        return response


def update_vocabulary(
        vocabulary_name, language_code, transcribe_client, phrases=None,
        table_uri=None):
    try:
        vocab_args = {'VocabularyName': vocabulary_name, 'LanguageCode': language_code}
        if phrases is not None:
            vocab_args['Phrases'] = phrases
        elif table_uri is not None:
            vocab_args['VocabularyFileUri'] = table_uri
        response = transcribe_client.update_vocabulary(**vocab_args)
        logger.info("Updated custom vocabulary %s.", response['VocabularyName'])
    except ClientError:
        logger.exception("Couldn't update custom vocabulary %s.", vocabulary_name)
        raise

def delete_vocabulary(vocabulary_name, transcribe_client):

    try:
        transcribe_client.delete_vocabulary(VocabularyName=vocabulary_name)
        logger.info("Deleted vocabulary %s.", vocabulary_name)
    except ClientError:
        logger.exception("Couldn't delete vocabulary %s.", vocabulary_name)
        raise

def upload_bucket(bucket_name ,local_file_path, obj_key):
    
    s3_resource = session.resource('s3')
    print(f"Creating bucket {bucket_name}.")
    s3_resource.meta.client.upload_file(local_file_path , bucket_name, obj_key)
    media_uri = f's3://{bucket_name}/{obj_key}'
    return media_uri

def Transcribe(local_file_path ,object_key):
    transcribe_client = session.client('transcribe')
    media_uri =upload_bucket(S3_BUCKET, local_file_path , object_key)
    job_name_simple = f'demo-{time.time_ns()}'
    print(f"Starting transcription job {job_name_simple}")
    start_job( job_name_simple, media_uri, 'wav', 'ar-AE', transcribe_client)
    time.sleep(70)
    # transcribe_waiter = TranscribeCompleteWaiter(transcribe_client)
    # transcribe_waiter.wait(job_name_simple)
    # job_simple = get_job(job_name_simple, transcribe_client)
    # print("sameh"*5)
    # transcript_simple = requests.get(job_simple['Transcript']['TranscriptFileUri']).json()
    # print(f"Transcript for job {transcript_simple['jobName']}:")
    # result = transcript_simple['results']['transcripts'][0]['transcript']
    result = "sameh mohamed"
    print(result)
    print('-'*88)
    return result   