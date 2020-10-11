from flask import Blueprint
from flask_restful import Api
from app.meals.api import _RatingStar, _RatingAnswer, _RatingQuestion, _Menu, _RatingFavorite, _RatingStarMy, _RatingAnswerMy

meals_bp = Blueprint('meals', __name__)

api = Api(meals_bp)


api.add_resource(_Menu, '/menu')
api.add_resource(_RatingStar, '/rating/star')
api.add_resource(_RatingStarMy, '/rating/star/my')

api.add_resource(_RatingFavorite, '/rating/favorite')


api.add_resource(_RatingQuestion, '/rating/question')
api.add_resource(_RatingAnswer, '/rating/answer')
api.add_resource(_RatingAnswerMy, '/rating/answer/my')