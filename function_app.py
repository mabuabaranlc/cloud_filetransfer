
import os
import io
import json
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs_storage
import boto3

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="file_transfer")
def file_transfer(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse request parameters
        req_body = req.get_json()
        source = req_body.get("source")
        source_path = req_body.get("source_path")
        sink = req_body.get("sink")
        sink_path = req_body.get("sink_path")

        # Validate parameters
        if not all([source, source_path, sink, sink_path]):
            return func.HttpResponse("Missing parameters", status_code=400)

        # Stream the file from source and upload to sink
        file_stream = stream_from_source(source, source_path)
        if file_stream is None:
            return func.HttpResponse("Source file not found or could not be accessed.", status_code=404)

        # Write the stream to sink
        write_to_sink(sink, sink_path, file_stream)

        return func.HttpResponse("File transfer completed successfully.", status_code=200)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error occurred: {str(e)}", status_code=500)
    

def stream_from_source(source, path):
    if source == "asa":  # Azure Storage
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("ASA_CONNECTION_STRING"))
        container_name, blob_name = path.split("/", 1)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        return stream

    elif source == "gcs":  # Google Cloud Storage
        gcs_client = gcs_storage.Client()
        bucket_name, blob_name = path.split("/", 1)
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        stream = io.BytesIO()
        blob.download_to_file(stream)
        stream.seek(0)
        return stream

    elif source == "s3":  # Amazon S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION"),
            endpoint_url=os.getenv("S3_ENDPOINT")  # Agregar endpoint para S3
        )
        bucket_name, key = path.split("/", 1)
        stream = io.BytesIO()
        s3_client.download_fileobj(bucket_name, key, stream)
        stream.seek(0)
        return stream

    return None

def write_to_sink(sink, path, file_stream):
    if sink == "asa":  # Azure Storage
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("ASA_CONNECTION_STRING"))
        container_name, blob_name = path.split("/", 1)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(file_stream, overwrite=True)

    elif sink == "gcs":  # Google Cloud Storage
        gcs_client = gcs_storage.Client()
        bucket_name, blob_name = path.split("/", 1)
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file_stream)

    elif sink == "s3":  # Amazon S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION"),
            endpoint_url=os.getenv("S3_ENDPOINT")  # Agregar endpoint para S3
        )
        bucket_name, key = path.split("/", 1)
        file_stream.seek(0)
        s3_client.upload_fileobj(file_stream, bucket_name, key)