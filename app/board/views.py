from flask import Blueprint
from flask_restful import Api
from app.board.api import _MealBoard, _MealBoardMy, _MealBoardLike, _MealBoardDetail, _MealBoardLikeMy

board_bp = Blueprint('board', __name__)

api = Api(board_bp)


api.add_resource(_MealBoard, '/meal')
api.add_resource(_MealBoardMy, '/meal/my')


api.add_resource(_MealBoardDetail, "/meal/<int:post_seq>")
api.add_resource(_MealBoardLike, '/meal/like/<int:post_seq>')

api.add_resource(_MealBoardLikeMy, '/meal/like/<int:post_seq>/my')

#
# api.add_resource(IdCheck, '/check-duplicate/id/<string:id>', '/check-duplicate/id/')
# api.add_resource(NicknameCheck, '/check-duplicate/nickname/<string:nickname>', '/check-duplicate/nickname/')