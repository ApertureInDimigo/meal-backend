from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey


class CustomModel(Model):
    def as_dict(self):
        temp = {}
        for x in self.__table__.columns:
            if str(type(getattr(self, x.name))) == "<class 'datetime.datetime'>":
                temp[x.name] = str(getattr(self, x.name))
            else:
                temp[x.name] = getattr(self, x.name)
        return temp


db = SQLAlchemy(model_class=CustomModel)


class Student(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    student_seq = db.Column(db.Integer, primary_key=True, nullable=False)
    id = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    password_salt = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(20), nullable=False)
    school_grade = db.Column(db.Integer, nullable=False)
    school_class = db.Column(db.Integer, nullable=False)
    register_date = db.Column(db.DateTime, nullable=False)
    point = db.Column(db.Integer, nullable=False)

    school_verified = db.Column(db.Boolean, nullable=False, server_default='False')

    gender = db.Column(db.String(10), nullable=True)

    kakao_id = db.Column(db.String(20), nullable=True)

    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=False)
    school = relationship("School", backref=backref('student', order_by=student_seq))


class School(db.Model):
    school_seq = db.Column(db.Integer, primary_key=True, nullable=False)
    school_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    verify_code = db.Column(db.String(50), nullable=True)
    is_admin_exist = db.Column(db.Boolean, nullable=False)
    region = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)


class MenuRating(db.Model):
    rating_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=False)
    student_seq = db.Column(db.Integer, ForeignKey('student.student_seq'), nullable=False)

    school = relationship("School", backref=backref('menurating', order_by=rating_seq, cascade='all,delete'))
    student = relationship("Student", backref=backref('menurating', order_by=rating_seq, cascade='all,delete'))

    menu_seq = db.Column(db.Integer, nullable=True)
    menu_name = db.Column(db.String(30), nullable=False)
    menu_date = db.Column(db.DateTime, nullable=False)
    menu_time = db.Column(db.String, nullable=False, server_default="중식")

    star = db.Column(db.Integer, nullable=True)
    questions = db.Column(db.JSON, nullable=True)

    is_favorite = db.Column(db.Boolean, nullable=True)

    banned = db.Column(db.Boolean, nullable=False)

    rating_date = db.Column(db.DateTime, nullable=False)


class MealBoard(db.Model):
    post_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=False)
    student_seq = db.Column(db.Integer, ForeignKey('student.student_seq'), nullable=False)
    school = relationship("School", backref=backref('mealboard', order_by=post_seq))
    student = relationship("Student", backref=backref('mealboard', order_by=post_seq))

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False)

    menus = db.Column(db.JSON, nullable=False)
    menu_date = db.Column(db.DateTime, nullable=False)

    views = db.Column(db.Integer, nullable=False, server_default='0')

    image_url = db.Column(db.String(500), nullable=True)

    banned = db.Column(db.Boolean, nullable=False)

    post_date = db.Column(db.DateTime, nullable=False)


class MealBoardLikes(db.Model):
    like_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    post = relationship("MealBoard", backref=backref('menuRatingLikes', order_by=like_seq, cascade='all,delete'))
    post_seq = db.Column(db.Integer, ForeignKey('meal_board.post_seq'), nullable=False)

    student_seq = db.Column(db.Integer, ForeignKey('student.student_seq', ), nullable=False)
    student = relationship("Student", backref=backref('mealboardlikes', order_by=like_seq, cascade='all,delete'))

    like_date = db.Column(db.DateTime, nullable=False)


class MealRatingQuestion(db.Model):
    question_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    school = relationship("School", backref=backref('MealRatingQuestion', order_by=question_seq, cascade='all,delete'))
    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=True)

    content = db.Column(db.String, nullable=False)

    options = db.Column(db.JSON, nullable=True)

    category = db.Column(db.String, nullable=True)

    is_available = db.Column(db.Boolean, nullable=False)

    priority = db.Column(db.Integer, nullable=False)

    add_date = db.Column(db.DateTime, nullable=False)


class Meal(db.Model):
    meal_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    school = relationship("School", backref=backref('Meal', order_by=meal_seq, cascade='all,delete'))
    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=True)

    menus = db.Column(db.JSON, nullable=True)
    menu_date = db.Column(db.DateTime, nullable=False)
    menu_time = db.Column(db.String, nullable=False, server_default="중식")
    add_date = db.Column(db.DateTime, nullable=False)

    is_alg_exist = db.Column(db.Boolean, nullable=False)
