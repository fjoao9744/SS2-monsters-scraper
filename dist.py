import boto3
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("ENDPOINT"), # R2
    aws_access_key_id=os.getenv("AWS_SECRET_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),)

def upload_file(family, monster):
    with open(f"images/{family}/{monster}", "rb") as f:
        s3.put_object(Bucket="ss2-monsters-v2", Key=f"{family}/{monster}", Body=f)
    print(family, monster)

tasks = []
for family in os.listdir("images"):
    for monster in os.listdir(f"images/{family}"):
        tasks.append((family, monster))

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(lambda args: upload_file(*args), tasks)

with open("monsters.json", "rb") as f:
    s3.put_object(Bucket="ss2-monsters-v2", Key="monsters.json", Body=f)
