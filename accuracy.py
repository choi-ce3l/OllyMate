from filtering import *

class RecommenderEvaluator:
    def __init__(self, df):
        # 데이터프레임 및 모델 초기화
        self.df = df
        self.recommender = FastSkincareRecommender(df)

    def accuracy(self):
        prediction = []

        for i in range(len(self.df)):
            new_data = self.df[i:i + 1]
            recommendations = self.recommender.fit_and_recommend(new_data=new_data, n_recommendations=3)
            recommend_product = [goodsName for goodsName, _ in recommendations]
            prediction.append(self.hit_rate(new_data['goodsName'][i], recommend_product))

        return prediction

    def hit_rate(self, gt_item, pred_items):
        if gt_item in pred_items:
            return 1
        return 0

    def evaluate(self):
        # 정확도를 계산하고 결과 출력
        prediction = self.accuracy()
        accuracy_score = sum(prediction) / len(prediction) if prediction else 0
        print(f"Accuracy: {accuracy_score:.2f}")
        return accuracy_score


'''# 클래스 사용 예시
if __name__ == "__main__":
    # df는 데이터프레임으로 정의되어 있어야 함
    evaluator = RecommenderEvaluator(df)
    evaluator.evaluate()'''
