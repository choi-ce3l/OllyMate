import re
import requests
import pandas as pd
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# csv 파일명 입력
def hwahae_crawl(goodsData):
    # 데이터 로드
    df = pd.read_csv(goodsData, encoding='utf-8')

    # 상품명 추출
    product_name = list(df['goodsName'].unique())

    data = []
    for name in product_name:
        try:
            # 화해에 검색 할 수 있게 상품명 처리
            preprocessed_name = re.sub(r'\[.*?\]|\(.*?\)|\d+ml.*|기획|단품', '', name).strip()

            # 화해 검색
            url = f'https://www.hwahae.co.kr/search?q={preprocessed_name}'

            print(preprocessed_name)

            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')

            print("res", res)

            # 검색 후 첫번째 상품 url 추출
            a_tag = soup.select_one('#__next > main > section > section > div.px-20 > ul > li:nth-child(1) > div > a')
            href = a_tag['href']

            # 상품 url
            product_url = f'https://www.hwahae.co.kr/{href}'

            # feature 가져오기
            # 크롬 드라이버 설정
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('disable-blink-features=AutomationControlled')  # 자동화 탐지 방지
            options.add_argument("--headless")  # 헤드리스 모드로 실행
            driver = webdriver.Chrome(service=service, options=options)

            features = []
            function = []
            formulation = []

            try:
                # 페이지로 이동
                driver.get(product_url)
                time.sleep(1)  # 페이지 로딩 대기

                # feature kewword 추출
                li = driver.find_elements(By.CSS_SELECTOR,
                                          'div.flex.justify-between.px-20.my-24 > div.grow.mr-24.w-1\/2 > ul > li ')

                for span in li:
                    span_tag = span.find_element(By.CSS_SELECTOR, 'span').text
                    features.append(span_tag)
                    print(span_tag)


            finally:
                # 드라이버 종료
                driver.quit()

            # 수분
            moisture = [
                "수분있는", "보습잘되는", "속건조에효과있는",
                "흡수잘되는", "겉돌지않는"
            ]

            # 진정
            calmdown = [
                "진정되는", "가렵지않은", "자극없는",
                "따갑지않은", "트러블안생기는", "트러블없어지는",
                "발진안생기는", "발진에효과있는", "피부강화되는",
                "뒤집어지지않는", "편안해지는"
            ]

            # 미백
            whitening = [
                "미백효과가있는", "브리이트닝효과있는",
                "안색이개선되는", "피부톤이개선되는",
                "톤업되는", "맑은"
            ]

            # 모공
            elasticity = [
                "모공관리되는", "피지없어지는", "블랙헤드없어지는",
                "각질제거잘되는", "노폐물제거되는", "화이트헤드없어지는"
            ]

            # 가벼운 제형
            light_formulation = [
                "리치하지않은", "가벼운", "산뜻한",
                "흘러내리지않는", "끈적하지않은",
                "답답하지않은", "얇게발리는", "밀림없는",
                "매트하지않은"
            ]

            # 무거운 제형
            heavy_formulation = [
                "리치한", "쫀득한", "지속력좋은",
                "겨울에사용하기좋은", "윤기나는", "제형묽지않은",
                "매끄러운"
            ]

            if any(keyword in features for keyword in moisture):
                function.append("수분")
            if any(keyword in features for keyword in calmdown):
                function.append("진정")
            if any(keyword in features for keyword in whitening):
                function.append("미백")
            if any(keyword in features for keyword in elasticity):
                function.append("탄력")
            if any(keyword in features for keyword in light_formulation):
                formulation.append("가벼운 제형")
            if any(keyword in features for keyword in heavy_formulation):
                formulation.append("무거운 제형")

            name_feature = {
                'goodsName': name,
                "function": function,
                "formulation": formulation
            }

            data.append(name_feature)


        except:
            print("keyword error")

    file_name = goodsData.replace(".csv", "_fin_after.csv")

    new_df = pd.DataFrame(data)
    new_df.to_csv(file_name, encoding='utf-8-sig', index=False)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argument = sys.argv[1]
        hwahae_crawl(argument)
    else:
        print("No argument provided.")