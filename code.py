from matplotlib import pyplot as plt
from PIL import Image
import random
import pymysql
import boto3
import os

filename = "分析する画像のパス"

# 画像を開いてサイズを取得する
img = Image.open(filename)
img_width = img.size[0]
img_height = img.size[1]

# 使用するバケットを指定する
bucket = "s3andrekognition"
# 使用するリージョンを指定する
region = "ap-northeast-1"

access_key = "アクセスキー"
secret_key = "シークレットアクセスキー"

ENDPOINT = "RDSのエンドポイント"
PORT = 3306
USER = "mysqlのユーザー名"
REGION = "RDSのリージョン"
DBNAME = "mysqlのDB名"
DBPASS = "mysqlのパスワード"
TABLE = "テーブル名"
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

session = boto3.Session(
    aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region
)

# S3サービスに接続する
s3 = session.client("s3")
# Rekognitionサービスに接続する
rekognition = session.client("rekognition")

# ファイルを読み込む
with open(filename, "rb") as f:
    # 読み込んだファイルをS3サービスにアップロード
    s3.put_object(Bucket=bucket, Key=filename, Body=f)

# S3に置いたファイルをRekognitionに認識させる
res = rekognition.detect_faces(
    Image={"S3Object": {"Bucket": bucket, "Name": filename}},
    Attributes=['AGE_RANGE']
)

print("result:")
print()
for detail in res["FaceDetails"]:
    # print(detail)
    agerange = str(detail["AgeRange"])


try:
    conn =  pymysql.connect(host=ENDPOINT, user=USER, passwd=DBPASS, port=PORT, database=DBNAME)
    cur = conn.cursor()
    # 実行するSQL
    cur.execute(f"""INSERT INTO {TABLE} agerange VALUES {agerange}""")
    query_results = cur.fetchall()
    print(query_results)
except Exception as e:
    print("Database connection failed due to {}".format(e))  

# S3サービスにアップロードしたファイルを削除する
s3.delete_object(Bucket=bucket, Key=filename)
