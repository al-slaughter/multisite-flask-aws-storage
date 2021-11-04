import boto3


def create_folder(folder_name, bucket):
    s3_client = boto3.client('s3')
    folder = "uploads/" + folder_name + "/"
    response = s3_client.put_object(Bucket=bucket, Key=folder)
    return response


def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def list_files(bucket):
    s3_client = boto3.client('s3')
    contents = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            # print(item)
            contents.append(item)
    except Exception as e:
        pass
    return contents


def show_image(user, bucket):
    s3_client = boto3.client('s3')
    # location = boto3.client('s3').get_bucket_location(Bucket=bucket)['LocationConstraint']
    public_urls = []
    try:
        upload_folder = "uploads/" + user + "/"
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            if upload_folder in item['Key'] and item['Key'] != upload_folder:
                presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
                # print("[DATA] : presigned url = ", presigned_url)
                public_urls.append(presigned_url)
    except Exception as e:
        print(e)
        pass
    # print("[DATA] : The contents inside show_image = ", public_urls)
    return public_urls
