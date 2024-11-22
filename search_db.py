import pymysql
from dotenv import load_dotenv
import os

# product_list -> list
def search_db(product_list):
    load_dotenv()

    # 데이터베이스 연결에 필요한 정보들 저장
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWD")
    database = os.getenv("DB_NAME")

    connection = pymysql.connect(
        host=host,             # 예: "localhost"
        port=int(port),        # MySQL 포트 넘버
        user=user,             # MySQL 사용자 이름
        password=password,     # MySQL 비밀번호
        database=database,     # MySQL 데이터베이스 이름
        charset="utf8mb4"      # 문자 인코딩
    )

    try:
        with connection.cursor() as cursor:
            result = []
            for i in product_list:
                query = f"select goodsName, purchase_link, image_link, price, `function`, formulation from cosmetic_data where goodsNo = '{i}';"
                cursor.execute(query)
                fetch = cursor.fetchone()
                fetch = {
                    "goodsName": fetch[0],
                    "purchase_link": fetch[1],
                    "image_link": fetch[2],
                    "price": fetch[3],
                    "function": fetch[4],
                    "formulation": fetch[5]
                }
                result.append(fetch)

            connection.commit()
    finally:
        connection.close()

    return result
