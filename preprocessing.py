import pandas as pd
import ast

def preprocessing(file_path):
    df = pd.read_csv(file_path)
    # skintype, skinton, skinconcerns 중 하나라도 Nan이면 해당 행 제거
    df = df.dropna(subset=['skintype', 'skinton', 'skinconcerns'])
    df.reset_index(drop=True, inplace=True)

    # 가격 데이터 전처리
    df['price'] = df['price'].str.replace(',', '').astype(int)

    # 가격 범주 설정
    bins = [0, 20000, 30000, 50000, float('inf')]
    labels = ['2만원이하', '2-3', '3-5', '5만원이상']

    # 가격 카테고리 생성
    df['price_category'] = pd.cut(df['price'], bins=bins, labels=labels).astype('object')

    # 예비 데이터 생성
    processed_df = pd.DataFrame(df)

    # feature를 합치기 위해 []지우고 문자열로 반환
    processed_df['skintype'] = processed_df['skintype'].apply(ast.literal_eval)
    processed_df['skintype'] = processed_df['skintype'].apply(lambda x: ' '.join(x))
    processed_df['skinton'] = processed_df['skinton'].apply(ast.literal_eval)
    processed_df['skinton'] = processed_df['skinton'].apply(lambda x: ' '.join(x))
    processed_df['skinconcerns'] = processed_df['skinconcerns'].apply(ast.literal_eval)
    processed_df['skinconcerns'] = processed_df['skinconcerns'].apply(lambda x: ' '.join(x))

    for i in range(len(processed_df)):
        if (len(processed_df['skintype'][i]) == 0 or len(processed_df['skinton'][i]) == 0 or len(
                processed_df['skinconcerns'][i]) == 0):
            processed_df.drop([i], inplace=True)
        else:
            continue

    processed_df.reset_index(drop=True, inplace=True)

    return processed_df