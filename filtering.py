import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.spatial.distance import euclidean
import os


class FastSkincareRecommender:
    def __init__(self, df, encoded_file="data/encoded_features.csv"): # 이거 나중에 DB로 설정하든 해야할듯?
        self.df = df
        self.encoded_features = None
        self.target = None
        self.mlb_concerns = MultiLabelBinarizer(sparse_output=False)
        self.mlb_function = MultiLabelBinarizer(sparse_output=False)
        self.mlb_formulation = MultiLabelBinarizer(sparse_output=False)
        self.encoded_file = encoded_file # 인코딩 파일 저장 경로 설정

    def encode_features(self, save_to_file=True):
        """특성을 인코딩하고, 필요하면 feature_matrix 파일에 저장"""
        if os.path.exists(self.encoded_file):
            # 파일이 존재하면 불러오기
            self.encoded_features = pd.read_csv(self.encoded_file)
        else:
            # 각 특성 인코딩
            skintype_encoded = pd.get_dummies(self.df['skintype'], prefix='type')
            skinton_encoded = pd.get_dummies(self.df['skinton'], prefix='tone')
            pricecategory_encoded = pd.get_dummies(self.df['price_category'], prefix='price_category')
            category_encoded=pd.get_dummies(self.df['category'], prefix='category')

            # MultiLabelBinarizer로 인코딩
            concerns_encoded = self._multi_label_encode(self.df['skinconcerns'], self.mlb_concerns, 'concern')
            function_encoded = self._multi_label_encode(self.df['function'], self.mlb_function, 'function')
            formulation_encoded = self._multi_label_encode(self.df['formulation'], self.mlb_formulation, 'formulation')

            # 모든 인코딩된 특성 결합
            self.encoded_features = pd.concat(
                [category_encoded, skintype_encoded, skinton_encoded, pricecategory_encoded, concerns_encoded, function_encoded,
                 formulation_encoded],
                axis=1
            ).fillna(0)

            # 필요하면 파일로 저장
            if save_to_file:
                os.makedirs(os.path.dirname(self.encoded_file), exist_ok=True)
                self.encoded_features.to_csv(self.encoded_file, index=False)

        # 상품명을 타깃 변수로 설정
        self.target = self.df['goodsName'].reindex(self.encoded_features.index)

    def _multi_label_encode(self, column, mlb, prefix):
        """멀티 라벨 인코딩 처리 부분"""
        # 혹시 안된 전처리 부분 처리하기 위해
        list_of_lists = column.apply(
            lambda x: x.split(',') if pd.notna(x) and x != '' else []
        ).tolist()

        # 멀티 라벨 바이너리로 인코딩
        encoded_array = mlb.fit_transform(list_of_lists)
        return pd.DataFrame(
            encoded_array,
            columns=[f'{prefix}_{c}' for c in mlb.classes_],
            index=column.index
        )

    def encode_new_data(self, new_data):
        """새로운 데이터 인코딩 single user profile"""
        skintype_encoded = pd.get_dummies(new_data['skintype'], prefix='type')
        skinton_encoded = pd.get_dummies(new_data['skinton'], prefix='tone')
        pricecategory_encoded = pd.get_dummies(new_data['price_category'], prefix='price_category')
        category_encoded = pd.get_dummies(new_data['category'], prefix='category')

        concerns_encoded = self._multi_label_encode(new_data['skinconcerns'], self.mlb_concerns, 'concern')
        function_encoded = self._multi_label_encode(new_data['function'], self.mlb_function, 'function')
        formulation_encoded = self._multi_label_encode(new_data['formulation'], self.mlb_formulation,'formulation')

        new_encoded_features = pd.concat(
            [category_encoded, skintype_encoded, skinton_encoded, pricecategory_encoded, concerns_encoded, function_encoded,
             formulation_encoded],
            axis=1
        ).reindex(columns=self.encoded_features.columns, fill_value=0).fillna(0)

        return new_encoded_features.iloc[0].values.astype(float)

    def _multi_label_encode_series(self, series, mlb, prefix):
        """멀티 라벨 인코딩_새로운 유저와 데이터 받는 형식이 달라서 별도 함수 처리"""
        list_of_lists = series.apply(
            lambda x: x.split(',') if pd.notna(x) and x != '' else []
        ).tolist()

        encoded_array = mlb.transform(list_of_lists)
        return pd.DataFrame(
            encoded_array,
            columns=[f'{prefix}_{c}' for c in mlb.classes_],
            index=series.index
        )

    def calculate_similarity(self, item_vector, n_recommendations=5):
        """유사도 계산"""
        distances = self.encoded_features.apply(lambda row: euclidean(item_vector, row.values.astype(float)), axis=1)
        similarities = 1 / (1 + distances) # 거리가 가까운 순으로, 1에 가까울수록 유사한 제품
        return sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)[:n_recommendations] # 현재 순서가 판매량 순서이기 때문에 순서대로 저장

    def fit_and_recommend(self, item_idx=None, new_data=None, n_recommendations=3):
        self.encode_features()

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
for goodsName, similarity in recommendations:
    print(f"Product: {goodsName}, Similarity: {similarity:.4f}")

# 새로운 유저 정보가 입력된 경우
recommendations = recommender.fit_and_recommend(new_data=test_df, n_recommendations=3)
print("유저 정보에 따라 추천합니다.")
for goodsName, similarity in recommendations:
    print(f"Product: {goodsName}, Similarity: {similarity:.4f}")

recommentations examples (goodsName, similarity)
[('[11월 올영픽/토너 250ml증정]바이오더마 하이드라비오 토너 500ml 기획(+토너 250ml 증정)', 1.0),
 ('[스누피키링증정] 아누아 어성초 77 깐달걀 토너 500ml 스누피 한정 기획세트', 1.0),
 ('[쿨링진정]넘버즈인 1번 진정 맑게담은 청초토너 300ml 리필기획(+300ml 증정)', 1.0)]
'''