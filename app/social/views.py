from flask import Blueprint
from flask_restful import Api
from app.social.api import _Search

social_bp = Blueprint('social', __name__)

api = Api(social_bp)


api.add_resource(_Search, '/search')