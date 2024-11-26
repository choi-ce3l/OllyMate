from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from rag.retriever import *
from dotenv import load_dotenv


def retriever(user_query, recommended_goodsName, user_data):
    load_dotenv()

    docs = load_docs_object()
    loaded_docs_db = load_vectorstore('text-embedding-3-large', 'faiss_db_openai_allcategory_final')

    docs_of_recommended_product, contents_of_recommended_product = get_recommended_product_objects(docs, recommended_goodsName)
    retriever = build_emsemble_retriever(docs_of_recommended_product, "gpt-4o-mini", loaded_docs_db, recommended_goodsName, user_data)

    result_contexts = retriever.invoke(user_query)
    result_contexts = [i.page_content for i in result_contexts]
    return result_contexts



def generate_chat_response(context, user_data, history, user_query):
    # 프롬프트 템플릿 정의
    prompt_template = PromptTemplate(
        input_variables=["context", "history", "user_data", "goodsNo", "user_query"],
        template=(
            "당신은 화장품 전문가로, 사용자에게 추천한 화장품을 설명하고, "
            "관련 정보를 제공하는 역할을 맡고 있습니다. "
            "항상 친절하고 전문적인 태도로 답변하세요.\n\n"
            "사용자의 질문:\n{user_query}\n\n"
            "추천한 제품과 사용자와의 대화 이력:\n{history}\n\n"
            "사용자 데이터:\n{user_data}\n\n"
            "다음은 관련 문서들입니다:\n"
            "{context}\n\n"
            "위 정보를 바탕으로 사용자의 질문에 대해 최상의 추천과 유용한 답변을 제공하세요."
            "구매 링크와 이미지는 제외하고 제공하세요"
        )
    )

    # LLM 모델 초기화
    llm = ChatOpenAI(temperature=0, model_name='gpt-4o-mini')  # OpenAI LLM 호출

    # Step 4: 프롬프트 생성
    prompt = prompt_template.format(
        context=context,
        history=history,
        user_data=user_data,
        user_query=user_query
    )

    # 응답 생성
    response = llm.invoke(prompt)

    return response.content
