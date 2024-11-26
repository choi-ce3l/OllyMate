# 제품 설명으로 찾기 버전 2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from sentence_transformers import SentenceTransformer


class RecommendationSystem:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Sentence Transformer 모델 초기화
        self.model = SentenceTransformer(model_name)
        self.item_embeddings = None
        self.items_df = None

    def create_embeddings(self, items_df, text_column):
        """
        아이템 설명을 임베딩 벡터로 변환

        Parameters:
        items_df (pd.DataFrame): 아이템 정보가 담긴 데이터프레임
        text_column (str): 텍스트 설명이 담긴 칼럼명
        """
        self.items_df = items_df.copy()

        # 텍스트를 임베딩 벡터로 변환
        texts = items_df[text_column].tolist()
        self.item_embeddings = self.model.encode(texts)

    def find_similar_items_by_description(self, description, n_recommendations=5):
        """
        입력된 설명과 가장 유사한 아이템들을 찾음

        Parameters:
        description (str): 검색하고자 하는 제품 설명
        n_recommendations (int): 추천할 아이템 개수

        Returns:
        list: 추천된 아이템 정보와 유사도 점수
        """
        if self.item_embeddings is None:
            raise ValueError("먼저 create_embeddings()를 호출하세요")

        # 입력된 설명을 임베딩 벡터로 변환
        query_embedding = self.model.encode([description])[0]

        # 코사인 유사도 계산
        similarities = cosine_similarity(
            [query_embedding],
            self.item_embeddings
        )[0]

        # 가장 유사한 아이템들의 인덱스 찾기
        similar_indices = np.argsort(similarities)[::-1][:n_recommendations]

        # 결과 형식화
        recommendations = []
        for idx in similar_indices:
            recommendations.append({
                'item_id': self.items_df.index[idx],
                'description': self.items_df.iloc[idx]['description'],
                'similarity_score': float(similarities[idx])
            })

        return recommendations

    def get_user_recommendations(self, user_history, n_recommendations=5):
        """
        사용자의 히스토리를 기반으로 추천

        Parameters:
        user_history (list): 사용자가 본/구매한 아이템 ID 리스트
        n_recommendations (int): 추천할 아이템 개수

        Returns:
        list: 추천된 아이템 ID와 점수
        """
        if self.item_embeddings is None:
            raise ValueError("먼저 create_embeddings()를 호출하세요")

        # 사용자 히스토리의 아이템들의 임베딩 평균 계산
        history_embeddings = []
        for item_id in user_history:
            item_idx = self.items_df.index.get_loc(item_id)
            history_embeddings.append(self.item_embeddings[item_idx])

        user_profile = np.mean(history_embeddings, axis=0)

        # 모든 아이템과의 유사도 계산
        similarities = cosine_similarity([user_profile], self.item_embeddings)[0]

        # 이미 본 아이템을 제외하고 가장 유사한 아이템들 찾기
        already_seen = set(user_history)
        recommendations = []

        sorted_indices = np.argsort(similarities)[::-1]
        for idx in sorted_indices:
            item_id = self.items_df.index[idx]
            if item_id not in already_seen:
                recommendations.append({
                    'item_id': item_id,
                    'description': self.items_df.iloc[idx]['description'],
                    'similarity_score': float(similarities[idx])
                })
                if len(recommendations) >= n_recommendations:
                    break

        return recommendations

'''
df.set_index('goodsName', inplace=True)

# 추천 시스템 초기화
rec_sys = RecommendationSystem()
rec_sys.create_embeddings(df, 'description')

# 특정 아이템과 유사한 아이템 찾기
similar_items = rec_sys.find_similar_items_by_description('스킨/토너 지성 트러블 모공 2-3 수분 진정 가벼운 제형 봄웜톤', n_recommendations=3)'''