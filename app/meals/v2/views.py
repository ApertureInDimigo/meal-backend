from flask import Blueprint
from flask_restful import Api

from app.meals.v2.api.Menu import Menu
from app.meals.v2.api.RatingFavorite import RatingFavorite

meals_bp_v2 = Blueprint('meals_v2', __name__)

api = Api(meals_bp_v2)

api.add_resource(Menu, '/menu')

api.add_resource(RatingFavorite, '/rating/favorite')
