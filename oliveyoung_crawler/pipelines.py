# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

class OliveyoungCrawlerPipeline:
    def open_spider(self, spider):
        # 스파이더가 시작될 때 CSV 파일 열기
        self.file = open('all_data.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=['goodsNo', 'goodsName', 'category', 'price', 'pricerange', 'purchase_link', 'image_link', 'memberNo', 'skintype', 'skintone', 'skinconcern', 'review', 'rating', 'date', 'rank'])
        self.writer.writeheader()

    def process_item(self, item, spider):
        # 아이템 데이터 처리 (예: 데이터 클렌징)

        item['price'] = item['price'].replace(',', '')  # 예: 가격에서 쉼표 제거, int로 변환

        if int(item['price']) <= 20000:
            item['pricerange'] = '-2'
        elif 20000 < int(item['price']) <= 30000:
            item['pricerange'] = '2-3'
        elif 30000 < int(item['price']) <= 40000:
            item['pricerange'] = '3-4'
        elif int(item['price']) >= 50000:
            item['pricerange'] = '5-'

        # CSV 파일에 저장
        self.writer.writerow(item)
        return item

    def close_spider(self, spider):
        # 스파이더가 종료될 때 파일 닫기
        self.file.close()

