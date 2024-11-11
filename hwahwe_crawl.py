from bs4 import BeautifulSoup
import requests
import re
import sys

# 1. DB에서 제품명 가져오기
def preprocessing_product_name(text):
    patterns = [
        r'\[.*?\]|\(.*?\)|\d+ml.*'

    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    processed_text = re.sub(r'\s+', ' ', text).strip()
    return processed_text

# 2. 화해에서 제품명 검색하기
def get_product_href_tag(processed_text):
   source_url=f'https://www.hwahae.co.kr/search?q={processed_text}'
   response = requests.get(source_url)
   soup = BeautifulSoup(response.text, 'html.parser')

   a_tag=soup.select('#__next > main > section > section > div.px-20 > ul > li:nth-child(1) > div > a')
   href=a_tag[0]['href']
   # print(href) -> ex.) products/4900
   return href

# 3. 해당 제품의 AI 리뷰 데이터 추출하기
def get_product_ai_review(href):
   s = requests.Session()
   s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Cookie": "_ga_3V19ZGJ84W=GS1.1.1731286911.1.0.1731286911.0.0.0; _ga=GA1.1.1456301248.1731286912; _tt_enable_cookie=1; _ttp=J_Y3wZSgjwteQLHGjuCc8fENzKT; _fbp=fb.2.1731286926465.175496475186567195; aws-waf-token=5808b6ac-e973-45a5-b954-aa7fb0ec561e:AQoAhXQjLjqzAAAA:YV2/E4qkeGZhD2EZQlq5fsBhU3ZNyWVYfHw6tyh2h6DB3SAuTom2b/E4Re9zRYL7wPd9El9bg/pF+p9bDgp8HbPdKVaLBo4qBecA/eNYiQIOXkkxuNjKv4A1d4lJfLB6MtARVfnVuqTv3i7rZca8/Xyz18oETRzJiqTvTE8PuIYhZAlSu0DqeR/9kBsoGlc2Fv1g; _ga_36NCBJ5CBH=GS1.1.1731301644.4.1.1731302309.59.0.1961747604; CHECK_IS_REPRESENT_GOODS_42788=true",
        }
    )

   product_url=f"https://www.hwahae.co.kr/{href}"
   response2=s.get(product_url)
   soup2=BeautifulSoup(response2.text, 'html.parser')

   good_review_tag=soup2.select_one('div.grow')
   feature_tags = good_review_tag.select('ul li')

   features = []
   for tag in feature_tags:
        text_only = re.sub(r'\d+', '', tag.text)
        features.append(text_only.strip())

   return features

if __name__ == "__main__":
    # Get the product name from the command line argument
    if len(sys.argv) > 1:
        product_name = ' '.join(sys.argv[1:])  # Join the arguments to form the full product name
    else:
        print("Product name argument is missing!")
        sys.exit(1)

    # Process the product name and get the reviews
    text = preprocessing_product_name(product_name)
    href = get_product_href_tag(text)
    features = get_product_ai_review(href)
    print(features)

# 사용법 예시
# python hwahwe_crawl.py [변우석pick] 피지오겔 DMT 페이셜 로션 200ml+50ml+포토스티커 한정기획