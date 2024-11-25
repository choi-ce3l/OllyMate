import streamlit as st
from recommendsystem import *
from search_db import search_db
from dotenv import load_dotenv

load_dotenv()

with st.sidebar:
    # Streamlit UI 구성
    st.title("💬 맞춤형 화장품 추천 챗봇")
    st.write(
        "피부 타입과 고민, 원하는 기능과 제형을 선택하면 챗봇이 제품을 추천해줍니다. 추가로 궁금한 점을 물어보세요!"
    )

    # 챗봇 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 사용자 입력
    with st.form(key="recommendation_form"):
        skin_type = st.selectbox(
            "피부 타입을 선택하세요:",
            ("건성", "지성", "복합성", "민감성", "악건성", "트러블성", "중성"),
            index=None,
            placeholder="피부 타입"
        )
        skin_tone = st.selectbox(
            "피부 톤을 선택하세요:",
            ("쿨톤", "웜톤", "봄웜톤", "여름쿨톤", "가을웜톤", "겨울쿨톤"),
            index=None,
            placeholder="피부톤"
        )
        skin_concern = st.multiselect(
            "피부 고민을 선택하세요:",
            [
                "잡티",
                "주름",
                "미백",
                "각질",
                "트러블",
                "블랙헤드",
                "피지과다",
                "민감성",
                "모공",
                "탄력",
                "홍조",
                "아토피",
                "다크서클",
            ],
            placeholder="피부 고민"
        )
        product_function = st.multiselect(
            "원하는 화장품 기능을 선택하세요:", ["수분", "진정", "미백", "탄력"],
            placeholder="기능"
        )
        product_texture = st.selectbox(
            "원하는 제형을 선택하세요:", ("가벼운 제형", "무거운 제형"),
            index=None,
            placeholder="제형"
        )
        category = st.selectbox(
            "원하는 카테고리를 선택하세요:", ("스킨/토너", "에센스/세럼/앰플", "크림", "로션", "미스트/오일"),
            index=None,
            placeholder="카테고리"
        )

        price_options = {
            "~2만원": "-2",
            "2만원~3만원": "2-3",
            "3만원 ~ 5만원": "3-5",
            "5만원~": "5-"
        }

        selected_pricerange = st.selectbox(
            "원하는 가격대를 선택하세요:",
            options=list(price_options.keys()),
            index=None,
            placeholder="가격대"
        )

        # pricerange 값을 안전하게 가져오기
        if selected_pricerange:  # 사용자가 선택한 경우
            pricerange = price_options[selected_pricerange]
        else:  # 선택하지 않은 경우 기본값 설정
            pricerange = "미정"  # 원하는 기본값으로 변경 가능

        user_data = {
            "skintype": skin_type,
            "skintone": skin_tone,
            "skinconcerns": " ".join(skin_concern),
            "pricerange": pricerange,
            "category": category,
            "function": " ".join(product_function),
            "formulation": product_texture,
        }

        # st.write(user_data)

        # 추천 버튼
        recommand_button = st.form_submit_button("추천받기")
        if recommand_button:
            # 모든 선택지가 설정되었는지 확인
            if not all(
                [
                    user_data["formulation"],  # 제형
                    user_data["function"],  # 기능
                    user_data["skinconcerns"],  # 피부 고민
                    user_data["skintone"],  # 피부 톤
                    user_data["skintype"],  # 피부 타입
                    user_data['category'],  # 카테고리
                    user_data['pricerange'] # 가격대
                ]
            ):
                st.error("모든 선택지를 설정한 후 다시 시도해주세요!")


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []  # 메시지 기록 초기화

st.write(st.session_state.messages)

# db에서 로딩된 df에서 product_info 생성
def db_to_df(df, recommend_list):
    product_info = []
    for goodsName in recommend_list:
        filted_df = df[df['goodsName'] == goodsName]
        # print(filted_df['price'].values[0])
        product_info.append(
            {
                "goodsName": goodsName,
                "price": filted_df['price'].values[0],
                "function": filted_df['function'].values[0],
                "formulation": filted_df['formulation'].values[0],
                "purchase_link": filted_df['purchase_link'].values[0],
                "image_link": filted_df['image_link'].values[0],
            }
        )
    return product_info

def get_product_info(recommand_list):
    recommand_list = [i[0] for i in recommand_list]
    product_info = db_to_df(df, recommand_list)
    return product_info

# 메시지 추가 함수
def add_product_message(product_list):
    """추천 제품 메시지를 세션 상태에 추가"""
    st.session_state.messages.append({
        "role": "assistant",
        "type": "product",
        "content": product_list
    })

# recommend system 객체 생성
@st.cache_data # loading된 dataframe을 캐시에 저장
def load_data():
    df = mk_df()
    return df

df = load_data()
system = RecommendSystem(df)

# 버튼 클릭으로 제품 추천 메시지 추가
if recommand_button:
    if all(
            [
                user_data["formulation"],  # 제형
                user_data["function"],  # 기능
                user_data["skinconcerns"],  # 피부 고민
                user_data["skintone"],  # 피부 톤
                user_data["skintype"],  # 피부 타입
                user_data['category'],  # 카테고리
                user_data['pricerange']  # 가격대
            ]
    ):
        newuser_recommendations = system.recommend_new_user_profile(skintype=user_data["skintype"], skintone=user_data["skintone"], skinconcern=user_data['skinconcerns'], pricerange=user_data["pricerange"], category=user_data["category"], function=user_data["function"], formulation=user_data["formulation"])
        recommand_list = get_product_info(newuser_recommendations)
        add_product_message(recommand_list[:3])  # 첫 3개의 상품 추천

# 사용자 입력에 대한 답변 생성 함수
def generate_response(user_message, product_info, user_data, history):
    # product_info -> retriever 생성
    # 생성된 retriever에서 출력된 context, user_data, history
    return "진정에도 좋은 제품을 찾고 계신 것 같네요! 여러 리뷰에서 언급된 바에 따르면, 또한, 장미수와 알란토인 성분이 포함된 제품은 피부 진정에 효과적이며, 수분 공급도 뛰어나서 건조해지지 않는다고 하네요. 지성 피부를 가지신 사용자님께는 이러한 가벼운 제형의 진정 토너가 잘 맞을 것 같습니다. 특히, 수분 공급과 진정 효과를 동시에 원하신다면 추천드려요!"

# 사용자 입력 처리
user_input = st.chat_input("Your message:")

if user_input:  # 사용자가 메시지를 입력했을 경우
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "type": "text",
        "content": user_input
    })
    # 답변 생성 및 저장
    assistant_response = generate_response(user_input)
    st.session_state.messages.append({
        "role": "assistant",
        "type": "text",
        "content": assistant_response
    })

# 이전 메시지 출력
for message in st.session_state.messages:
    if message["type"] == "product":
        product_list = message["content"]
        with st.chat_message("assistant"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(product_list[0]['image_link'])
                st.write(product_list[0]['goodsName'])
                st.write(product_list[0]['price'], "원")
                st.write(product_list[0]['function'])
                st.write(product_list[0]['formulation'])
                st.link_button("구매하기", product_list[0]['purchase_link'])
            with col2:
                st.image(product_list[1]['image_link'])
                st.write(product_list[1]['goodsName'])
                st.write(product_list[1]['price'], "원")
                st.write(product_list[1]['function'])
                st.write(product_list[1]['formulation'])
                st.link_button("구매하기", product_list[1]['purchase_link'])
            with col3:
                st.image(product_list[2]['image_link'])
                st.write(product_list[2]['goodsName'])
                st.write(product_list[2]['price'], "원")
                st.write(product_list[2]['function'])
                st.write(product_list[2]['formulation'])
                st.link_button("구매하기", product_list[2]['purchase_link'])
    elif message["type"] == "text":
        with st.chat_message(message["role"]):
            st.write(message["content"])
