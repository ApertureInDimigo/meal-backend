import re
import datetime

import requests
import json

from flask import copy_current_request_context

from app.db import Student, MealRatingQuestion, MealBoard
from sample.menu_classifier import classify_menu, get_menu_category_list

from config import DISCORD_WEBHOOK_URL
import asyncio
from app.redis import rd
from app.db import db
import sqlalchemy

from config import GOOGLE_CREDENTIALS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.cache import cache
import copy


def get_region_code(region):
    if region == "경기도":
        return "J10"


def remove_allergy(str):
    temp = re.sub("\([^)]*\)|[0-9]*\.", '', str)  # 알레르기 제거
    temp = re.sub("[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"A-Za-z]+$", "", temp)  # 연속되는 의미없는 특수문자 제거
    temp = re.sub("[^가-힣a-zA-Z0-9&+/]", "", temp)  # &+/  외 특수문자 제거
    if re.compile("^\d+[^색|단|번|곡|종|ml|L|월|\d].*").match(temp):
        temp = re.sub("^[0-9]", "", temp)

    temp = re.sub("^[a-z]", "", temp)  # 문자열 맨 앞의 소문자 알파벳 제거
    temp = re.sub("^[&|\+]", "", temp)  # 문자열 맨 앞의 & + / 제거
    temp = re.sub("^/+", "", temp)

    if re.compile("^\d+[^색|단|번|곡|종|ml|L|월|\d].*").match(temp):
        temp = re.sub("^[0-9]", "", temp)
    temp = re.sub("^[a-z]", "", temp)  # 문자열 맨 앞의 소문자 알파벳 제거
    temp = re.sub("^/+", "", temp)

    return temp


def str_to_date(str):
    date = datetime.datetime.strptime(str, "%Y%m%d")

    return date


def datetime_to_str(dt):
    string = dt.strpttime("%m/%d/%Y, %H:%M:%S")
    print(string)
    return string


def get_day_meal(school, date):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={date}&MLSV_TO_YMD={date}&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=365&Type=json"

    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        return None
    day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]

    lunch_meal_data = []
    for time_meal_data in day_meal_data:
        if time_meal_data["MMEAL_SC_NM"] == "중식":
            lunch_meal_data = [remove_allergy(menu) for menu in time_meal_data["DDISH_NM"].split("<br/>")]

    if len(lunch_meal_data) == 0:
        return None

    return lunch_meal_data


def get_month_meal(school, year, month):
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={year}{month.zfill(2)}01&MLSV_TO_YMD={year}{month.zfill(2)}31&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=365&Type=json"
    print(url)
    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        return {}
    day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]

    lunch_meal_data = {}
    for time_meal_data in day_meal_data:
        if time_meal_data["MMEAL_SC_NM"] == "중식":
            lunch_meal_data[time_meal_data["MLSV_YMD"]] = [remove_allergy(menu) for menu in
                                                           time_meal_data["DDISH_NM"].split("<br/>")]

    if len(lunch_meal_data) == 0:
        return {}

    return lunch_meal_data


def get_identify(student_id):
    student = Student.query.filter_by(id=student_id).first()
    school = student.school
    return student, school


def get_question_rows(menu):
    category_list = get_menu_category_list(menu)
    print(cache.get("question_rows_data"))
    question_rows = [question_row for question_row in cache.get("question_rows_data") if
                     question_row["category"] in category_list]

    question_rows.sort(key=lambda x : x["priority"])

    # question_rows = MealRatingQuestion.query.filter_by(is_available=True, school=None, ).filter(
    #     MealRatingQuestion.category.in_(category_list)).order_by(
    #     MealRatingQuestion.priority.desc(),
    #     MealRatingQuestion.add_date.desc()).all()
    print(question_rows)
    return question_rows


def get_school_by_school_name(school_name):
    url = f"https://open.neis.go.kr/hub/schoolInfo?&SCHUL_NM={school_name}&Type=json&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a"
    response = requests.request("GET", url)

    school_data = json.loads(response.text)

    if "schoolInfo" not in school_data:
        return None

    school_data_list = school_data["schoolInfo"][1]["row"]
    return [{
        "schoolId": school_data["SD_SCHUL_CODE"],
        "schoolName": school_data["SCHUL_NM"],
        "schoolAddress": school_data["ORG_RDNMA"],
        "schoolRegion": school_data["LCTN_SC_NM"]
    } for school_data in school_data_list]


def dict_mean(dict_list):
    mean_dict = {}
    for key in dict_list[0].keys():
        mean_dict[key] = sum(d[key] for d in dict_list) / len(dict_list)
    return mean_dict


def is_local():
    import socket
    import os

    hostname = socket.gethostname()
    isLocal = True
    if hostname[:7] == "DESKTOP" or hostname[:5] == "Chuns":
        isLocal = True
    else:
        isLocal = False

    return isLocal


def send_discord_webhook(webhook_body):
    requests.post(
        DISCORD_WEBHOOK_URL,
        json=webhook_body)


# @copy_current_request_context
def update_meal_board_views():
    # from run import app
    # with app.app_context:
    print("start!")
    post_seq_list = []
    view_count_list = []
    for key in rd.scan_iter(match="views:*"):
        post_seq = int(key.decode("utf-8").split("views:")[1])
        post_seq_list.append(post_seq)

        student_seq_list = rd.smembers(key)

        view_count_list.append(len(student_seq_list))
        for student_seq in student_seq_list:
            rd.set("pviews:" + str(post_seq) + "-" + str(int(student_seq)), 1, datetime.timedelta(seconds=60 * 60))

        rd.delete(key)

    print(post_seq_list)
    print(view_count_list)

    post_rows = MealBoard.query.filter(MealBoard.post_seq.in_(post_seq_list)).all()

    for index, post_row in enumerate(post_rows):
        post_row.views = post_row.views + view_count_list[index]
        print(post_row.views)
    db.session.commit()


def list_remove_duplicate_dict(d):
    return [i for n, i in enumerate(d) if i not in d[n + 1:]]


def fetch_spread_sheet():
    from app.cache import cache
    from collections import namedtuple
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


fetch_spread_sheet()
