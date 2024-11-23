from langchain_community.document_loaders import DataFrameLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm
import time
import os
import pymysql
from datetime import datetime
import faiss
import numpy as np


def get_database():
    
    # 데이터베이스 연결 설정
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    passwd = os.getenv('DB_PASSWD')
    db_name = os.getenv('DB_NAME')

    con = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        passwd=passwd,
        db=db_name,
        charset="utf8",
    )

    cur = con.cursor()

    query = 'select * from cosmetic_data;'

    df = pd.read_sql(query, con)

    # 연결 종료
    con.close()

    return df

def load_documents(df, page_content_column):
    
    loader = DataFrameLoader(df, page_content_column=page_content_column)
    docs_generator = loader.lazy_load()
    docs = list(docs_generator)
    contents = [content.page_content for content in docs]

    return docs, contents

def create_doc_id(docs):
    
    today = datetime.now()

    for i in range(len(docs)):
        docs[i].metadata['id'] = f'{today}--001--00{i}'

def create_embedded_documents(contents, model, batch_size):

    # Initialize embeddings model
    embeddings = OpenAIEmbeddings(model=model)

    # Define batch size and delay
    batch_size = batch_size  # 배치 크기 설정
    delay = int(os.getenv("EMBEDDING_DELAY", 1))  # 기본 대기 시간 1초, 환경변수로 조정 가능

    embedded_docs = []
    error_batches = []  # 에러가 발생한 배치를 저장

    # Retry logic
    max_retries = 3  # 최대 재시도 횟수

    # Start timing
    start_time = time.time()

    # Process contents in batches
    for i in tqdm(range(0, len(contents), batch_size), desc="Embedding Progress", unit="batch"): # 재민: 변수를 바꿔주세요.
        batch = contents[i:i + batch_size]  # 배치 슬라이싱 # 재민: 변수를 바꿔주세요.
        batch_start_time = time.time()  # 각 배치 시작 시간 기록
        retries = 0  # 현재 재시도 횟수

        while retries <= max_retries:
            try:
                embedded_docs.extend(embeddings.embed_documents(batch))  # 배치 임베딩 및 결과 추가
                break  # 성공하면 루프 탈출
            except Exception as e:
                retries += 1
                print(f"\nError in batch {i // batch_size + 1} (retry {retries}/{max_retries}): {e}")
                if retries > max_retries:
                    print(f"Failed batch {i // batch_size + 1} after {max_retries} retries. Skipping...")
                    error_batches.append((i, batch))  # 에러 발생한 배치 저장
                    break
                time.sleep(2 ** retries)  # 지수적 대기 증가

        batch_end_time = time.time()
        print(f"Processed batch {i // batch_size + 1} in {batch_end_time - batch_start_time:.2f} seconds.")
        time.sleep(delay)  # API 속도 제한을 피하기 위해 지연 시간 추가

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nEmbedding completed in {elapsed_time:.2f} seconds.")
    print(f"Total embedded documents: {len(embedded_docs)}")
    if error_batches:
        print(f"Encountered errors in {len(error_batches)} batches. Check error_batches for details.")
        for idx, (batch_num, failed_batch) in enumerate(error_batches, 1):
            print(f"\nError batch {idx}: Batch index {batch_num}, Batch content: {failed_batch}")

    return embedded_docs

def create_faiss_index(embedded_docs):

    temp_vectors = np.array(embedded_docs=embedded_docs, dtype=np.float32)

    #index 생성
    nlist = 512
    nprobe = 25
    d = 3072
    quantizer = faiss.IndexFlatL2(d)  # the quantizer

    index = faiss.IndexIVFFlat(
        quantizer,
        d,
        nlist,
        faiss.METRIC_INNER_PRODUCT
    )

    # Train the index
    index.train(temp_vectors) # 인덱스 빌드하기
    index.add(temp_vectors) # 인덱스에 벡터 추가하기

    return index

def create_vectorstore(model, index, docs):

    embeddings = OpenAIEmbeddings(model=model)

    docs_vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    docs_faiss = docs_vector_store.from_documents(
        documents=docs,
        embedding=embeddings
    )

    return docs_faiss


# 실행 코드
if __name__ == '__main__':

    # 1. openai api key 불러오기
    load_dotenv()

    # 2. 문서 로드
    df = get_database()
    docs, contents = load_documents(df, 'review')
    create_doc_id(docs)

    # 3. 임베딩
    embedded_docs = create_embedded_documents(contents, 'text-embedding-3-large', 128)

    # 4. 벡터스토어 생성
    index = create_faiss_index(embedded_docs)
    docs_faiss = create_vectorstore('text-embedding-3-large', index, docs)
    
    docs_faiss.save_local(
    folder_path='./faiss_db_openai', # 해당 디렉토리에 벡터스토어 저장
    index_name='docs_faiss'
    )