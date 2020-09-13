import re
import datetime

import requests
import json

from app.db import Student, MealRatingQuestion
from sample.menu_classifier import classify_menu

from config import DISCORD_WEBHOOK_URL
import asyncio


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



def get_identify(student_id):
    student = Student.query.filter_by(id=student_id).first()
    school = student.school
    return student, school


def get_question_rows(menu):
    category = classify_menu(menu)
    question_rows = MealRatingQuestion.query.filter_by(is_available=True, school=None,
                                                       category=category).order_by(
        MealRatingQuestion.priority.desc(),
        MealRatingQuestion.add_date.desc()).all()
    return question_rows


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
