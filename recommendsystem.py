from preprocessing import *
from contentfiltering import *
import pandas as pd

class RecommendSystem:
    def __init__(self, file_path):
        # Load data and initialize the recommender
        # self.df = preprocessing(file_path) # 전처리가 필요한 경우 사용
        self.df=pd.read_csv(file_path) # 전처리가 필요없는 경우 사용
        self.recommender = FastSkincareRecommender(self.df)

    def recommend_existing_product(self, idx):
        """
        Get recommendations based on an existing product by its index.

        :param idx: Index of the existing product in the dataset.
        :return: List of recommendations with product names and similarity scores.
        """
        recommendations = self.recommender.fit_and_recommend(item_idx=idx, n_recommendations=6)

        print("Recommendations based on existing product:")
        for product_name, similarity in recommendations:
            print(f"Product: {product_name}, Similarity: {similarity:.4f}")

        return recommendations

    def recommend_new_user_profile(self, skintype='복합성', skintone='가을웜톤', skinconcern='트러블 모공',
                                   pricerange='2-3', category='스킨/토너', function='수분', formulation='가벼운 제형'):
        """
        Get recommendations based on a new user profile.
        :param skintype: User's skin type (default is '복합성').
        :param skintone: User's skin tone (default is '가을웜톤').
        :param skinconcern: User's skin concerns (default is '트러블 모공').
        :param pricerange: User's preferred price category (default is '2-3').
        :param category: Product category (default is '스킨/토너').
        :param function: Desired product function (default is '수분').
        :param formulation: Preferred formulation (default is '가벼운 제형').
        :return: List of recommendations with product names and similarity scores.
        """
        # Define the user profile data
        user_profile = [{'skintype': skintype, 'skintone': skintone, 'skinconcern': skinconcern,
                         'pricerange': pricerange, 'category': category,
                         'function': function, 'formulation': formulation}]

        # Convert to DataFrame
        user_profile_df = pd.DataFrame(user_profile)

        recommendations = self.recommender.fit_and_recommend(new_data=user_profile_df, n_recommendations=6)

        print("Recommendations based on new user profile:")
        for product_name, similarity in recommendations:
            print(f"Product: {product_name}, Similarity: {similarity:.4f}")

        return recommendations


'''
사용방법
from recommendsystem import *

file_path='data/final_data.csv'
system=RecommendSystem(file_path)
# existing_recommendations=system.recommend_existing_product(idx=0)
newuser_recommendations=system.recommend_new_user_profile()
'''