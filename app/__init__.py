import firebase_admin
from firebase_admin import credentials
import os

from flask import Flask, Response
from flask_cors import CORS
from app.common.function import *
import json
from config import FIREBASE_CREDENTIALS_PATH




class MyResponse(Response):
    default_mimetype = 'application/xml'


# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):

    from app.cache import cache

    #sched import 하자 마자 스케줄링이 시작됩니다.
    from app.scheduler import sched
    # from app.redis import redis_client
    import app.redis




    host_type = get_host_type()
    if host_type == "LOCAL":
        # 제 컴퓨터의 파일 경로였습니다.. 이 코드를 보시는 분이 예쁘게 바꿔주세요..
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

        firebase = firebase_admin.initialize_app(cred)
    elif host_type == "VULTR":
        # Vultr 서버의 firebase 인증 json 경로입니다.
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase = firebase_admin.initialize_app(cred)
    else:
        cred = json.loads(os.environ.get('FIREBASE_CONFIG', None))
        print(os.environ.get('FIREBASE_CONFIG', None))
        firebase = firebase_admin.initialize_app(credentials.Certificate(cred))



    app = Flask(__name__, static_url_path='', static_folder='../static', template_folder='../static')

    app.config.from_object(config_filename)
    # app.response_class = MyResponse

    from app.db import db, Student, School, MealRatingQuestion, MenuRating , MealBoardLikes, MealBoard
    db.init_app(app)
    db.app = app
    cache.init_app(app)

    def fetch_spread_sheet():
        from app.cache import cache
        gc = gspread.authorize(GOOGLE_CREDENTIALS).open("급식질문")

        wks = gc.get_worksheet(0)

        rows = wks.get_all_values()
        print(rows)
        try:

            data = []
            for row in rows[1:]:
                # row_tuple = Munhak(*row)
                # row_tuple = row_tuple._replace(keywords=json.loads(row_tuple.keywords))
                # if row_tuple.is_available == "TRUE":
                #     data.append(row_tuple)
                temp_dict = dict(zip(rows[0], row))
                if temp_dict["is_available"] == "TRUE":
                    temp_dict["options"] = json.loads(temp_dict["options"])
                    temp_dict["question_seq"] = int(temp_dict["question_seq"])
                    temp_dict["priority"] = int(temp_dict["priority"])
                    data.append(temp_dict)

        except Exception as e:
            print(e)

        # global munhak_rows_data
        # munhak_rows_data = data
        #
        # munhak_quiz_rows_data = [munhak_row for munhak_row in munhak_rows_data if len(munhak_row["keywords"]) != 0]
        #
        print(data)
        cache.set('question_rows_data', data, timeout=99999999999999999)
        # cache.set('munhak_quiz_rows_data', munhak_quiz_rows_data, timeout=99999999999999999)
        # print(data)
        # # print(munhak_rows)
        # return len(data)
        return len(data)

    fetch_spread_sheet()


    # sched.init_app(app)
    # redis_client.init_app(app)


    # Blueprints
    from app.auth.views import auth_bp
    from app.students.views import users_bp
    from app.schools.views import schools_bp
    from app.meals.v1.views import meals_bp_v1
    from app.meals.v2.views import meals_bp_v2
    from app.board.views import board_bp
    from app.social.views import social_bp


    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/students')
    app.register_blueprint(schools_bp, url_prefix='/api/schools')
    app.register_blueprint(meals_bp_v1, url_prefix='/api/meals')
    app.register_blueprint(meals_bp_v2, url_prefix='/api/meals/v2')
    app.register_blueprint(board_bp, url_prefix='/api/board')
    app.register_blueprint(social_bp, url_prefix='/api/social')

    # sched.add_job(lambda: update_meal_board_views(), 'cron', second='05', id="update_meal_board_views")
    def update_meal_board_views():
        # from run import app
        with app.app_context():
            print("start!")
            post_seq_list = []
            view_count_list = []
            for key in rd.scan_iter(match="views:*"):
                post_seq_list.append(int(key.decode("utf-8").split("views:")[1]))
                view_count_list.append(len(rd.smembers(key)))
            print(post_seq_list)
            print(view_count_list)

            post_rows = MealBoard.query.filter(MealBoard.post_seq in post_seq_list).all()
            for index, post_row in enumerate(post_rows):
                post_row.views += view_count_list[index]
            db.session.commit()






    CORS(app)
    return app
