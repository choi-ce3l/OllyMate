import pymysql
from dotenv import load_dotenv
import os
import pandas as pd


def mk_df():
    load_dotenv()

    # 데이터베이스 연결에 필요한 정보들 저장
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWD")
    database = os.getenv("DB_NAME")

    con = pymysql.connect(
        host=host,             # 예: "localhost"
        port=int(port),        # MySQL 포트 넘버
        user=user,             # MySQL 사용자 이름
        password=password,     # MySQL 비밀번호
        database=database,     # MySQL 데이터베이스 이름
        charset="utf8mb4"      # 문자 인코딩
    )

    query = 'select * from cosmetic_data;'

    df = pd.read_sql(query, con)

    # 연결 종료
    con.close()

    return df