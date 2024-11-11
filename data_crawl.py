import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

# 카테고리별 시작 URL 설정
categories = {
    "스킨/토너": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010013&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
    "에센스/세럼/엠플": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010014&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
    "크림": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010015&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
    "로션": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010016&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
    "미스트/오일": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010010&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx="
}


def fetch_product_urls(category_name, base_url):
    page = 1
    product_urls = []

    while True:
        url = f"{base_url}{page}"
        response = requests.get(url)

        # 요청이 성공적인지 확인
        if response.status_code != 200:
            print(f"Failed to retrieve page {page} for category {category_name}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # 상품 URL 추출 (a 태그의 href 속성값을 가져옴)
        product_links = soup.select("#Contents > ul.cate_prd_list > li > div > a")

        # 상품 링크가 없는 경우 루프 종료
        if not product_links:
            break

        for link in product_links:
            product_url = link.get("href")
            if product_url:
                # 절대 URL로 변환하여 저장
                full_url = f"{product_url}"
                product_urls.append({"category": category_name, "product_url": full_url})

        print(f"Fetched {len(product_links)} products from page {page} of category {category_name}")

        # 다음 페이지로 이동
        page += 1

    return product_urls


# 모든 카테고리 크롤링
all_product_urls = []
for category, base_url in categories.items():
    all_product_urls.extend(fetch_product_urls(category, base_url))

all_data = []

for product in all_product_urls:
    url = product['product_url']
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')

    goodsNo = soup.select_one('button.btnZzim').attrs['data-ref-goodsno']
    product_name = soup.select_one("p.prd_name").text
    price = soup.select_one('span.price-2 strong').text
    img_link = soup.select_one('img#mainImg').attrs['src']

    for i in range(0, 100):
        url = f"https://www.oliveyoung.co.kr/store/goods/getGdasNewListJson.do?goodsNo={goodsNo}&gdasSort=05&itemNo=all_search&pageIdx={i + 1}&colData=&keywordGdasSeqs=&type=&point=&hashTag=&optionValue=&cTypeLength=0"

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }

        res = requests.get(url, headers=headers, verify=False).text
        res = json.loads(res)

        for review_data in res["gdasList"]:
            memberNo = review_data["memberNo"]
            gdasContent = review_data["gdasCont"]
            gdasValue = review_data["gdasScrVal"]
            skintype = (
                [item['mrkNm'] for item in review_data['addInfoNm'] if "A" in item['colDataCd']]
                if review_data['addInfoNm'] is not None
                else None
            )
            skinton = (
                [item['mrkNm'] for item in review_data['addInfoNm'] if "B" in item['colDataCd']]
                if review_data['addInfoNm'] is not None
                else None
            )
            skinconcerns = (
                [item['mrkNm'] for item in review_data['addInfoNm'] if "C" in item['colDataCd']]
                if review_data['addInfoNm'] is not None
                else None
            )
            date = review_data["dispRegDate"]

            data = {
                'product_name': product_name,
                'category': product['category'],
                'price': price,
                'product_url': product['product_url'],
                'img_link': img_link,

                'memberNo': memberNo,
                'skintype': skintype,
                'skinton': skinton,
                'skinconcerns': skinconcerns,

                'goodsNo': goodsNo,
                'gdasContent': gdasContent,
                'gdasValue': gdasValue,
                'date': date,
            }
            all_data.append(data)
        print(f"Fetched {goodsNo}, page {i + 1}")

df = pd.DataFrame(all_data)
df.to_csv('에센스,세럼,앰플.csv', index=False, encoding='utf-8-sig')
