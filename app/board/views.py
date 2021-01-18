from flask import Blueprint
from flask_restful import Api

from app.board.api.MealBoardLike import MealBoardLike
from app.board.api.MealBoardDetail import MealBoardDetail
from app.board.api.MealBoard import MealBoard
from app.board.api.MealBoardLikeMy import MealBoardLikeMy
from app.board.api.MealBoardMy import MealBoardMy

board_bp = Blueprint('board', __name__)

api = Api(board_bp)


api.add_resource(MealBoard, '/meal')
api.add_resource(MealBoardMy, '/meal/my')


api.add_resource(MealBoardDetail, "/meal/<int:post_seq>")
api.add_resource(MealBoardLike, '/meal/like/<int:post_seq>')

api.add_resource(MealBoardLikeMy, '/meal/like/<int:post_seq>/my')

