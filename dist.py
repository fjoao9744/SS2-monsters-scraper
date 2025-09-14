import boto3
import os
from dotenv import load_dotenv

load_dotenv()


s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("ENDPOINT"), # R2
    aws_access_key_id=os.getenv("AWS_SECRET_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),)

for family in os.listdir("images"):
    for monster in os.listdir(f"images/{family}"):
        print(family, monster)
        with open(f"images/{family}/{monster}", "rb") as f:
            s3.put_object(Bucket="ss2-monsters", Key=f"{family}/{monster}", Body=f)


