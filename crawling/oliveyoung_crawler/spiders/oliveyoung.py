import scrapy

from oliveyoung_crawler.items import OliveyoungCrawlerItem

class OliveyoungSpider(scrapy.Spider):
    name = "oliveyoung"
    allowed_domains = ["www.oliveyoung.co.kr"]

    # 카테고리별 시작 URL 설정
    # dispCatNo=100000100010013 스킨/토너
    # dispCatNo=100000100010014 에센스/세럼/엠플
    # dispCatNo=100000100010015 크림
    # dispCatNo=100000100010016 로션
    # dispCatNo=100000100010010 미스트/오일
    categories = {
        "스킨/토너": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010013&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
        "에센스/세럼/엠플": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010014&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
        "크림": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010015&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
        "로션": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010016&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx=",
        "미스트/오일": "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010010&prdSort=03&rowsPerPage=48&aShowCnt=&bShowCnt=&cShowCnt=&pageIdx="
    }

    def start_requests(self):
        for category, base_url in self.categories.items():
            url = base_url + "1"  # 첫 페이지 URL`
            yield scrapy.Request(url, callback=self.parse, meta={'category': category, 'base_url': base_url, 'page': 1})

    def parse(self, response):
        category = response.meta['category']
        base_url = response.meta['base_url']
        page = response.meta['page']

        # 상품 URL 추출
        product_links = response.css("#Contents > ul.cate_prd_list > li > div > a::attr(href)").getall()

        # 해당 페이지에서 상품 순서
        product_order = response.css('#Contents > ul.cate_prd_list > li::attr(data-index)').getall()

        # 상품 URL이 있는 경우만 데이터 추출
        if product_links:
            for link, order in zip(product_links, product_order):
                rank = (page - 1) * 48 + (int(order) + 1)
                yield scrapy.Request(link, callback=self.parse_product, meta={'purchase_link': link, 'category': category, 'rank': rank})

            # 다음 페이지 요청
            next_page = page + 1
            next_url = f"{base_url}{next_page}"
            yield scrapy.Request(next_url, callback=self.parse, meta={'category': category, 'base_url': base_url, 'page': next_page})

    def parse_product(self, response):
        purchase_link = response.meta['purchase_link']
        category = response.meta['category']
        rank = response.meta['rank']

        goodsNo = response.css('button.btnZzim::attr(data-ref-goodsno)').get()
        goodsName = response.css('p.prd_name::text').get()
        price = response.css('span.price-2 strong::text').get()
        image_link = response.css('img#mainImg::attr(src)').get()

        data = {
            'goodsNo': goodsNo,
        }

        url = "https://www.oliveyoung.co.kr/store/goods/getGoodsArtcAjax.do"
        yield scrapy.FormRequest(url, callback=self.info_parse, method="POST", formdata=data, meta={'purchase_link': purchase_link, 'category': category, 'rank': rank, 'goodsNo': goodsNo, 'goodsName': goodsName, 'price': price, 'image_link': image_link})

    def info_parse(self, response):
        purchase_link = response.meta['purchase_link']
        category = response.meta['category']
        rank = response.meta['rank']
        goodsNo = response.meta['goodsNo']
        goodsName = response.meta['goodsName']
        price = response.meta['price']
        image_link = response.meta['image_link']

        volume = response.css("dt:contains('내용물의 용량 또는 중량') + dd::text").get()
        ingredients = response.css("dt:contains('화장품법에 따라 기재해야 하는 모든 성분') + dd::text").get()

        for i in range(0, 100):
            url = f"https://www.oliveyoung.co.kr/store/goods/getGdasNewListJson.do?goodsNo={goodsNo}&gdasSort=05&itemNo=all_search&pageIdx={i + 1}&colData=&keywordGdasSeqs=&type=&point=&hashTag=&optionValue=&cTypeLength=0"
            yield scrapy.Request(url, callback=self.parse_review, meta={'purchase_link': purchase_link, 'category': category, 'rank': rank, 'goodsNo': goodsNo, 'goodsName': goodsName, 'price': price, 'image_link': image_link, 'volume': volume, 'ingredients': ingredients})

    def parse_review(self, response):
        # item 생성 및 할당
        item = OliveyoungCrawlerItem()

        item['goodsNo'] = response.meta['goodsNo']
        item['goodsName'] = response.meta['goodsName']
        item['category'] = response.meta['category']
        item['price'] = response.meta['price']
        item['purchase_link'] = response.meta['purchase_link']
        item['image_link'] = response.meta['image_link']
        item['rank'] = response.meta['rank']
        item['volume'] = response.meta['volume']
        item['ingredients'] = response.meta['ingredients']

        data = response.json()

        for i in data['gdasList']:

            item['memberNo'] = i['memberNo']
            item['skintype'] = (
                [a['mrkNm'] for a in i['addInfoNm'] if "A" in a['colDataCd']]
                if i['addInfoNm'] is not None
                else None
            )
            item['skintone'] = (
                [a['mrkNm'] for a in i['addInfoNm'] if "B" in a['colDataCd']]
                if i['addInfoNm'] is not None
                else None
            )
            item['skinconcern'] = (
                [a['mrkNm'] for a in i['addInfoNm'] if "C" in a['colDataCd']]
                if i['addInfoNm'] is not None
                else None
            )
            item['review'] = i['gdasCont']
            item['rating'] = i['gdasScrVal']
            item['date'] = i['dispRegDate']
            yield item

