import pandas as pd
import ast
import re

def preprocessing(file_path):
    df = pd.read_csv(file_path)

    # NaN값 있는 행 제거
    df.dropna(subset=['skintype', 'skintone', 'skinconcern','function','formulation'], inplace=True)

    # 상품 이름 전처리
    df['goodsName'] = df['goodsName'].str.replace(r'\[.*?\]|\(.*?\)|\d+ml.*|기획|단품', '', regex=True).str.strip()

    # 가격 데이터 전처리
    df['price'] = df['price'].str.replace(',', '').astype(int) # 쉼표 제거 및 int 변경
    # df['price']=df['price'].astype(int) # int 변경

    # 가격 범주 설정 및 가격 카테고리 생성
    bins = [0, 20000, 30000, 50000, float('inf')]
    labels = ['2이하', '2-3', '3-5', '5이상']
    df['price_category'] = pd.cut(df['price'], bins=bins, labels=labels)

    # 리스트를 문자열로 변환
    for col in ['skintype', 'skintone', 'skinconcern','function','formulation']:
        df[col] = df[col].apply(ast.literal_eval).apply(' '.join)

    # 모든 컬럼에 빈 문자열이 없는 행만 필터링
    mask = (df['skintype'] != '') & (df['skintone'] != '') & (df['skinconcern'] != '') & (df['function'] != '') & (df['formulation'] != '')
    processed_df = df[mask].reset_index(drop=True)

    return processed_df
