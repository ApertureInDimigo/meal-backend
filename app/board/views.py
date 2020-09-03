from flask import Blueprint
from flask_restful import Api
from app.board.api import _MealBoard, _MealBoardLike, _MealBoardDetail

board_bp = Blueprint('board', __name__)

api = Api(board_bp)


api.add_resource(_MealBoard, '/meal')
api.add_resource(_MealBoardDetail, "/meal/<int:post_seq>")
api.add_resource(_MealBoardLike, '/meal/like')
#
# api.add_resource(IdCheck, '/check-duplicate/id/<string:id>', '/check-duplicate/id/')
# api.add_resource(NicknameCheck, '/check-duplicate/nickname/<string:nickname>', '/check-duplicate/nickname/')