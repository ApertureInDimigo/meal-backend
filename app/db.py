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
    id = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    password_salt = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    school_grade = db.Column(db.Integer, nullable=False)
    school_class = db.Column(db.Integer, nullable=False)
    register_date = db.Column(db.DateTime, nullable=False)
    point = db.Column(db.Integer, nullable=False)
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