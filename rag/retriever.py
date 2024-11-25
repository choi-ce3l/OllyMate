from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
import pickle

def load_docs_object():
    with open("objects_docs/docs.pkl", "rb") as f:
        docs = pickle.load(f)
    return docs

def load_vectorstore(model, folder_path):
    
    # Initialize embeddings model
    embeddings = OpenAIEmbeddings(model=model)

    loaded_docs_db = FAISS.load_local(
    folder_path=folder_path,
    index_name='docs_faiss',
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)
    return loaded_docs_db

def get_recommended_product_objects(docs, recommended_goodsNo):
    docs_of_recommended_product = []
    contents_of_recommended_product = []
    for doc in docs:
        if doc.metadata['goodsNo'] == f'{recommended_goodsNo}':
            docs_of_recommended_product.append(doc)
            contents_of_recommended_product.append(doc.page_content)

    return docs_of_recommended_product, contents_of_recommended_product

def build_emsemble_retriever(docs_of_recommended_product, llm_model, loaded_docs_db, recommended_goodsNo, user_data):
# def build_emsemble_retriever(docs_of_recommended_product, loaded_docs_db, recommended_goodsNo, user_data):

    # sparse retriever 생성
    bm25_retriever = BM25Retriever.from_documents(docs_of_recommended_product) # BM25Retriever에 doc 넣어서 바로 쿼리 진행하는 방식 (db x, 메모리 o)
    bm25_retriever.k = 5

    # dense retriever with compression 생성
    mmr_retriever= loaded_docs_db.as_retriever(
            search_type="mmr",
            search_kwargs={'k': 5,
                        'fetch_k' : 300,
                        'lambda_mult' :0.25,
                        'filter':{'goodsNo': recommended_goodsNo, 'skintype': user_data['skintype']}}) # product = goodsNo

    llm = ChatOpenAI(temperature=0, model=llm_model)
    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        # 문서 압축기와 리트리버를 사용하여 컨텍스트 압축 리트리버 생성
        base_compressor=compressor,
        base_retriever=mmr_retriever,
    )

    # ensemble retriever 생성
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, compression_retriever],
        # retrievers=[bm25_retriever, mmr_retriever],
        weights=[0.5, 0.5],
    )

    return ensemble_retriever
    
def invoke_user_query(retriever, user_query):

    result = retriever.invoke(user_query)

    return result


# # 실행 코드
# # 1. 사용자 정보 로드
# # (작업 필요) 추천받은 사용자 대상에 대한 정보 찾아오는 함수 필요 => return user_data (emsemble_retriever 함수 참고)
# user_data = {
#         "skintype": '지성',
#         "skintone": '쿨톤',
#         "skinconcerns": '미백 잡티 트러블',
#         "function": '수분 진정',
#         "formulation": '무거운 제형',
#         "category": '에센스/세럼/엠플',
#         }

# # 2. 추천 받은 상품 정보 로드
# # (작업 필요) 추천받은 goodsNo 찾아오는 함수 필요 => return recommended_goodsNo
# recommended_goodsNo = 'A000000183731'

# # 3. 문서 로드
# docs = load_docs_object()   
# docs_of_recommended_product, contents_of_recommended_product = get_recommended_product_objects(docs, recommended_goodsNo) # <- recommended_goodsNo 예시: 'A000000183731'
# loaded_docs_db = load_vectorstore('text-embedding-3-large', 'faiss_db_openai_test')

# # 4. retriever 생성
# retriever = build_emsemble_retriever(docs_of_recommended_product, "gpt-4o-mini", loaded_docs_db, recommended_goodsNo, user_data)

# # 5. retriever 실행
# user_query = '미백 효과가 얼마나 좋은지 알려줘'
# results_docs = retriever.invoke(user_query)

# results_contents = [docs.page_content for docs in results_docs]