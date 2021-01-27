from flask import Blueprint
from flask_restful import Api

from app.meals.v1.api.Menu import Menu
from app.meals.v1.api.MenuSimilar import MenuSimilar
from app.meals.v1.api.RatingAnswer import RatingAnswer
from app.meals.v1.api.RatingAnswerMy import RatingAnswerMy
from app.meals.v1.api.RatingFavorite import RatingFavorite
from app.meals.v1.api.RatingFavoriteAll import RatingFavoriteAll
from app.meals.v1.api.RatingQuestion import RatingQuestion
from app.meals.v1.api.RatingStar import RatingStar
from app.meals.v1.api.RatingStarMy import RatingStarMy
from app.meals.v1.api.UpdateMealQuestion import UpdateMealQuestion

meals_bp_v1 = Blueprint('meals_v1', __name__)

api = Api(meals_bp_v1)

api.add_resource(Menu, '/menu')

api.add_resource(MenuSimilar, '/menu/similar')


api.add_resource(RatingStar, '/rating/star')
api.add_resource(RatingStarMy, '/rating/star/my')

api.add_resource(RatingFavorite, '/rating/favorite')


api.add_resource(RatingFavoriteAll, '/rating/favorite-all')

api.add_resource(RatingQuestion, '/rating/question')
api.add_resource(RatingAnswer, '/rating/answer')
api.add_resource(RatingAnswerMy, '/rating/answer/my')

api.add_resource(UpdateMealQuestion, '/update')
