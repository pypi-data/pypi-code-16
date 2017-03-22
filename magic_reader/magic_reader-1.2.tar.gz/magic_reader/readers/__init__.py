import re
import boto3


def parse_source_path(source_path):
    values = re.findall(r'\(([^()]+)\)', source_path)
    keys = [c for c in re.sub(r"\([^)]*\)", " ", source_path).split(' ') if c]
    return {key: value for key, value in zip(keys, values)}


def s3_read(path, chunk_size=None):
    conn = boto3.client("s3")
    path = path.replace("s3://", "")
    bucket = path.split('/')[0]
    rest = "/".join(path.split('/')[1:])
    print bucket, rest
    obj = conn.get_object(Bucket=bucket, Key=rest)
    if chunk_size:
        for chunk in obj["Body"].read(chunk_size):
            yield chunk
    else:
        yield obj["Body"].read()

