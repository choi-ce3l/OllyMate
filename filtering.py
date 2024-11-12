import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.spatial.distance import euclidean
import os


class FastSkincareRecommender:
    def __init__(self, df, encoded_file="data/encoded_features.csv"):
        self.df = df
        self.encoded_features = None
        self.target = None
        self.mlb = None
        self.encoded_file = encoded_file  # 인코딩 파일 저장 경로 설정

    def encode_features(self, save_to_file=True):
        """특성을 인코딩하고, 필요하면 파일에 저장"""
        if os.path.exists(self.encoded_file):
            # 파일이 존재하면 불러오기
            self.encoded_features = pd.read_csv(self.encoded_file)
        else:
            # 각 특성 인코딩
            skintype_encoded = pd.get_dummies(self.df['skintype'], prefix='type')
            skinton_encoded = pd.get_dummies(self.df['skinton'], prefix='tone')
            pricecategory_encoded = pd.get_dummies(self.df['price_category'], prefix='price_category')

            # 'skinconcerns' 열을 문자열 리스트로 처리
            # 혹시 전처리가 안된 행을 빼기 위해 설정
            concerns_list = self.df['skinconcerns'].apply(
                lambda x: x.split(',') if pd.notna(x) and x != '' else []
            ).tolist()  # 리스트의 리스트 형태로 변환

            # MultiLabelBinarizer로 인코딩
            self.mlb = MultiLabelBinarizer(sparse_output=False)
            concerns_encoded_array = self.mlb.fit_transform(concerns_list)

            # concerns_encoded DataFrame 생성
            concerns_encoded = pd.DataFrame(
                concerns_encoded_array,
                columns=[f'concern_{c}' for c in self.mlb.classes_],
                index=self.df.index  # 인덱스가 원래 DataFrame과 일치하도록 설정
            )

            # 모든 인코딩된 특성 결합
            self.encoded_features = pd.concat(
                [skintype_encoded, skinton_encoded, concerns_encoded, pricecategory_encoded],
                axis=1
            ).fillna(0)

            # 필요하면 파일로 저장
            if save_to_file:
                os.makedirs(os.path.dirname(self.encoded_file), exist_ok=True)
                self.encoded_features.to_csv(self.encoded_file, index=False)

        # 상품명을 타깃 변수로 설정
        self.target = self.df['product_name'].reindex(self.encoded_features.index)

    def encode_new_data(self, new_data):
        """새로운 데이터 인코딩 single user profile"""
        skintype_encoded = pd.get_dummies(new_data['skintype'], prefix='type')
        skinton_encoded = pd.get_dummies(new_data['skinton'], prefix='tone')
        pricecategory_encoded = pd.get_dummies(new_data['price_category'], prefix='price_category')

        # 'skinconcerns' 열을 문자열 리스트로 처리
        concerns_list = new_data['skinconcerns'].apply(
            lambda x: x.split(',') if pd.notna(x) and x != '' else []
        ).tolist()  # Convert Series of lists to a list of lists for MultiLabelBinarizer

        # MultiLabelBinarizer로 인코딩 & concerns_encoded DataFrame 생성
        mlb = MultiLabelBinarizer(sparse_output=False)
        concerns_encoded = pd.DataFrame(
            mlb.fit_transform(concerns_list),
            columns=[f'concern_{c}' for c in mlb.classes_],
            index=new_data.index
        )

        # 모든 인코딩된 특성 결합
        new_encoded_features = pd.concat(
            [skintype_encoded, skinton_encoded, concerns_encoded, pricecategory_encoded], axis=1
        ).reindex(columns=self.encoded_features.columns, fill_value=0).fillna(0)

        return new_encoded_features.iloc[0].values.astype(float)

    def calculate_similarity(self, item_vector, n_recommendations=5):
        """유사도 계산"""
        similarities = []
        for idx, row in self.encoded_features.iterrows():
            distance = euclidean(item_vector, row.values.astype(float))
            similarity = 1 / (1 + distance)  # 거리가 가까운 순으로
            similarities.append((idx, similarity)) # 현재 순서가 판매량 순서이기 때문에 순서대로 저장

        return sorted(similarities, key=lambda x: x[1], reverse=True)[:n_recommendations]

    def fit_and_recommend(self, item_idx=None, new_data=None, n_recommendations=3):
        self.encode_features() # 인코딩 불러오기

        if new_data is not None: # 새로운 데이터가 아니면 밑에거 실행 -> 새로운 유저
            item_vector = self.encode_new_data(new_data)
        elif item_idx is not None: # item_idx가 아니면 밑에거 실행 -> 기존 데이터
            item_vector = self.encoded_features.iloc[item_idx].values.astype(float)
        else:
            raise ValueError("item_idx, new_data 중 하나는 입력해야 합니다.")

        recommendations = self.calculate_similarity(item_vector, n_recommendations)
        return [(self.target.iloc[idx], similarity) for idx, similarity in recommendations]


'''
사용 방법
# 객체 생성
recommender = FastSkincareRecommender(df)

# 기존 데이터에서 찾는 경우
item_idx = 614
recommendations = recommender.fit_and_recommend(item_idx=item_idx, n_recommendations=3)
print("기존 데이터에서 추천합니다.:")
for product_name, similarity in recommendations:
    print(f"Product: {product_name}, Similarity: {similarity:.4f}")

# 새로운 유저 정보가 입력된 경우
recommendations = recommender.fit_and_recommend(new_data=test_df, n_recommendations=3)
print("유저 정보에 따라 추천합니다.")
for product_name, similarity in recommendations:
    print(f"Product: {product_name}, Similarity: {similarity:.4f}")

recommentations examples (product_name, similarity)
[('[11월 올영픽/토너 250ml증정]바이오더마 하이드라비오 토너 500ml 기획(+토너 250ml 증정)', 1.0),
 ('[스누피키링증정] 아누아 어성초 77 깐달걀 토너 500ml 스누피 한정 기획세트', 1.0),
 ('[쿨링진정]넘버즈인 1번 진정 맑게담은 청초토너 300ml 리필기획(+300ml 증정)', 1.0)]
'''