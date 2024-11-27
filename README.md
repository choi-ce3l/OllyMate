# beauty AI Agent(OllyMate)

## 사용된 패키지
1. **scrapy**
    - beautifultsoup4 보다 빠르게 많은 양의 데이터를 크롤링하기 위해 사용 되었습니다.
   - [scrapy Documentation](https://docs.scrapy.org/en/latest/)


2. **beautifulsoup4**
   - requests로 받아온 html정보를 파싱하여 필요한 정보를 추출하기 위해 사용 되었습니다.
   - [BeautifulSoup Documentation](https://www.selenium.dev/documentation/)

3. **Selenium**
   - url requests 할 때 헤더에 쿠키를 추가해야되지만 쿠키를 자동으로 가져올수 없는 문제로 인해 사용 되었습니다.
   - [Selenium Documentation](https://pymysql.readthedocs.io/en/latest/)

4. **pymysql**
   - DB 연결 및 조회 및 추가를 위해 사용되었습니다.
   - [pymysql Documentation](https://pymysql.readthedocs.io/en/latest/)

5. **openai**
   - 주로 OpenAI API와의 통신을 위해 활용되며, GPT를 사용하기 위해 사용 되었습니다.
   - [OpenAI Documentation](https://beta.openai.com/docs/)
     
6. **langchain**
   - 프롬프트 체이닝을 통해 간단한 출력흐름을 구성하여 사용하기 위해 사용 되었습니다.
   - [LangChain Documentation](https://python.langchain.com/docs/)

7. **streamlit**
   - 웹 애플리케이션을 쉽게 만들고 데이터 시각화 및 사용자 인터페이스 구축을 지원합니다.
   - [Streamlit Documentation](https://docs.streamlit.io/)
  
8. **pandas**
   - 데이터를 로드하고 전처리하며, DataFrame 형식으로 구조화하여 데이터 변환 및 조작을 용이하게 합니다.
   - [Pandas Documentation](https://pandas.pydata.org/docs/)

## 사용 방법
- 의존성
```aiignore
$ pip install poetry
$ poetry update
```
- 크롤링
```aiignore
$ scrapy crawl oliveyoung
```
```aiignore
$ python hwahae.py [oliveyoung 크롤링.csv]
```

- streamlit
```aiignore
$ streamlit run main.py
```

## 프로젝트 주요 흐름
- 크롤링
  - scrapy와 beautifulsoup, Selenium을 사용해 제품과 리뷰 데이터 크롤링
- 추천 시스템
  - 제품과 사용자의 정보를 바탕으로 콘텐츠 기반 필터링 사용
- RAG
  - 사용자 질문에 대해 리뷰에서 참고할 정보가 있다면 사용

## 실행 화면
![beauty AI Agent - 시현 영상.gif](../../../Downloads/beauty%20AI%20Agent%20-%20%EC%8B%9C%ED%98%84%20%EC%98%81%EC%83%81.gif)