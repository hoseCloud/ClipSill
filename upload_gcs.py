from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name, conn):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    conn.sendall("[3/10] Uploading The File...".encode())
    blob.upload_from_filename(source_file_name)
