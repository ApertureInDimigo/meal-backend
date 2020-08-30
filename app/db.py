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
    id = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    password_salt = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(20), nullable=False)
    school_grade = db.Column(db.Integer, nullable=False)
    school_class = db.Column(db.Integer, nullable=False)
    register_date = db.Column(db.DateTime, nullable=False)
    point = db.Column(db.Integer, nullable=False)

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

    comment_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    school_seq = db.Column(db.Integer, ForeignKey('school.school_seq'), nullable=False)
    student_seq = db.Column(db.Integer, ForeignKey('student.student_seq'), nullable=False)


    school = relationship("School", backref=backref('menurating', order_by=comment_seq))
    student = relationship("Student", backref=backref('menurating', order_by=comment_seq))

    menu_name = db.Column(db.String(30), nullable=False)
    menu_date = db.Column(db.DateTime, nullable=False)

    star = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String(100), nullable=True)


    banned = db.Column(db.Boolean, nullable=False)

    rating_date = db.Column(db.DateTime, nullable=False)

