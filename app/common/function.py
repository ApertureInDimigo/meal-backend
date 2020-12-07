import re
import datetime
from datetime import datetime as dtt
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from config import NEIS_KEY
import requests
import json
from dateutil.rrule import rrule, DAILY
from flask import copy_current_request_context, g, render_template, abort
import calendar
from app.db import Student, MealRatingQuestion, MealBoard
from sample.menu_classifier import classify_menu, get_menu_category_list

from config import DISCORD_WEBHOOK_URL
import asyncio
from app.redis import rd
from app.db import *
import sqlalchemy

from config import GOOGLE_CREDENTIALS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.cache import cache
import copy


def get_region_code(region):
    region_code_list = ["B10", "C10", "D10", "E10", "F10", "G10", "H10", "I10", "J10", "K10", "M10", "N10", "P10",
                        "Q10", "R10", "S10", "T10"]
    region_list = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원도", "충청북도",
                   "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]

    return dict(zip(region_list, region_code_list))[region]


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

    temp = re.sub("\d*$", "", temp)
    temp = re.sub("/$", "", temp)
    temp = re.sub("[^망]]고$", "", temp)
    temp = re.sub("[남고|여고|공고]$", "", temp)
    temp = re.sub("과고[^구마]", "", temp)  # 과고구마

    return temp


def str_to_date(str):
    date = datetime.datetime.strptime(str, "%Y%m%d")

    return date


def date_to_str(d):
    return f"{d.year}{str(d.month).zfill(2)}{str(d.day).zfill(2)}"


def datetime_to_str(dt):
    string = dt.strpttime("%m/%d/%Y, %H:%M:%S")
    print(string)
    return string


def get_range_meal_db(school, start_date, end_date, target_time="중식"):
    result = []
    school_id = school.school_id
    if school_id == 7530560:

        start_dt = str_to_date(start_date)
        end_dt = str_to_date(end_date)

        range_date = list(rrule(DAILY, dtstart=start_dt, until=end_dt))

        meal_rows = Meal.query.filter_by(school=school).filter(Meal.menu_date.in_(range_date)).all()
        print(meal_rows)

        saved_date_list = []
        not_filled_row_list = []
        not_filled_date_list = []
        for meal_row in meal_rows:
            if datetime.datetime.now() > meal_row.menu_date or meal_row.menus is not None:
                if meal_row.menus is not None:
                    result.append(TimeOfMeal(from_db_data={
                        "date": date_to_str(meal_row.menu_date), "time": meal_row.menu_time, "menus": meal_row.menus
                    }))

                saved_date_list.append(meal_row.menu_date)

            if meal_row.menus is None:
                not_filled_row_list.append(meal_row)
                not_filled_date_list.append(meal_row.menu_date)

        not_saved_date_list = list(set(range_date) - set(saved_date_list))
        print(not_saved_date_list)

        for dt in not_saved_date_list:

            if datetime.datetime.now() + datetime.timedelta(days=45) <= dt:  # 현재로부터 45일 이후의 급식 일 경우

                continue

            dt_str = date_to_str(dt)

            is_update = False

            if dt in not_filled_date_list:  # db에 null 로 저장이 되어있음
                meal_row = [x for x in not_filled_row_list if x.menu_date == dt][0]
                if datetime.datetime.now() < meal_row.menu_date + datetime.timedelta(days=1):  # 미래 급식일 때
                    if datetime.datetime.now() >= meal_row.add_date + datetime.timedelta(
                            hours=18):  # 업데이트 되고 나서 18시간 지남
                        is_update = True
                    else:
                        continue
                else:  # 과거 급식일 때
                    if meal_row.add_date > meal_row.menu_date:  # 이미 설정 됨
                        continue

            url = f"https://dev-api.dimigo.in/dimibobs/{dt_str}"
            meal_response = requests.request("GET", url)
            meal_data = json.loads(meal_response.text)

            print(meal_data)

            if is_update is True:
                Meal.query.filter_by(school=school, menu_date=dt).delete()

            if "breakfast" in meal_data:

                db.session.add(
                    Meal(school=school, menus=meal_data["breakfast"].split("/"), menu_date=dt, menu_time="조식",
                         add_date=datetime.datetime.now(), is_alg_exist=False))

                result.append(TimeOfMeal(from_db_data={
                    "date": dt_str,
                    "time": "조식",
                    "menus": meal_data["breakfast"].split("/")

                }))
            else:

                db.session.add(
                    Meal(school=school, menus=None, menu_date=dt, menu_time="조식",
                         add_date=datetime.datetime.now(), is_alg_exist=False))

            if "dinner" in meal_data:
                db.session.add(
                    Meal(school=school, menus=meal_data["dinner"].split("/"), menu_date=dt, menu_time="석식",
                         add_date=datetime.datetime.now(), is_alg_exist=False))
                result.append(TimeOfMeal(from_db_data={
                    "date": dt_str,
                    "time": "석식",
                    "menus": meal_data["dinner"].split("/")

                }))
            else:
                db.session.add(
                    Meal(school=school, menus=None, menu_date=dt, menu_time="석식",
                         add_date=datetime.datetime.now(), is_alg_exist=False))

            if dt.weekday() >= 5:  # 토요일 or 일요일
                if "lunch" in meal_data:
                    db.session.add(
                        Meal(school=school, menus=meal_data["lunch"].split("/"), menu_date=dt, menu_time="중식",
                             add_date=datetime.datetime.now(), is_alg_exist=False))
                    result.append(TimeOfMeal(from_db_data={
                        "date": dt_str,
                        "time": "중식",
                        "menus": meal_data["lunch"].split("/")

                    }))
                else:
                    db.session.add(
                        Meal(school=school, menus=None, menu_date=dt, menu_time="중식",
                             add_date=datetime.datetime.now(), is_alg_exist=False))

                db.session.commit()

        # for dt in rrule(DAILY, dtstart=start_dt, until=end_dt):
        #     # print(dt.strpttime())
        #     dt_str = date_to_str(dt)
        #
        #     url = f"https://dev-api.dimigo.in/dimibobs/{dt_str}"
        #     meal_response = requests.request("GET", url)
        #     meal_data = json.loads(meal_response.text)
        #
        #     print(meal_data)
        #     if "breakfast" in meal_data:
        #
        #         result.append(TimeOfMeal(from_db_data={
        #             "date" : dt_str,
        #             "time" : "조식",
        #             "menus" : meal_data["breakfast"].split("/")
        #
        #         }))
        #     if "dinner" in meal_data:
        #         result.append(TimeOfMeal(from_db_data={
        #             "date": dt_str,
        #             "time": "석식",
        #             "menus": meal_data["dinner"].split("/")
        #
        #         }))

    return result


class TimeOfMeal():
    def __init__(self, from_neis_data=None, from_db_data=None):
        if from_neis_data is not None:
            self.menus = from_neis_data["DDISH_NM"].split("<br/>")
            self.time = from_neis_data["MMEAL_SC_NM"]
            self.date = from_neis_data["MLSV_YMD"]

        if from_db_data is not None:
            self.menus = from_db_data["menus"]
            self.time = from_db_data["time"]
            self.date = from_db_data["date"]


def get_day_meal(school, date, target_time="중식"):
    db_meal_data = get_range_meal_db(school, date, date, target_time)
    print(db_meal_data)
    print("!!!!!!!!!!!!!!!!!1")
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={date}&MLSV_TO_YMD={date}&KEY={NEIS_KEY}&pSize=365&Type=json"
    print(url)
    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        day_meal_data = db_meal_data
    else:
        day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]
        day_meal_data = [TimeOfMeal(from_neis_data=x) for x in day_meal_data] + db_meal_data

    if len(day_meal_data) == 0:
        return None

    if target_time == "전체":
        lunch_meal_data = defaultdict(list)
        for time_meal_data in day_meal_data:
            lunch_meal_data[time_meal_data.time] = [remove_allergy(menu) for menu in
                                                    time_meal_data.menus]
    else:
        lunch_meal_data = []
        for time_meal_data in day_meal_data:
            if time_meal_data.time == target_time:
                lunch_meal_data = [remove_allergy(menu) for menu in time_meal_data.menus]
    if len(lunch_meal_data) == 0:
        return None

    # if target_time == "전체":
    #     lunch_meal_data = defaultdict(list)
    #     for time_meal_data in day_meal_data:
    #         lunch_meal_data[time_meal_data["MMEAL_SC_NM"]] = [remove_allergy(menu) for menu in
    #                                                           time_meal_data["DDISH_NM"].split("<br/>")]
    # else:
    #     lunch_meal_data = []
    #     for time_meal_data in day_meal_data:
    #         if time_meal_data["MMEAL_SC_NM"] == target_time:
    #             lunch_meal_data = [remove_allergy(menu) for menu in time_meal_data["DDISH_NM"].split("<br/>")]
    # if len(lunch_meal_data) == 0:
    #     return None

    return lunch_meal_data


def get_day_meal_with_alg(school, date, target_time="중식"):
    db_meal_data = get_range_meal_db(school, date, date, target_time)

    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={date}&MLSV_TO_YMD={date}&KEY={NEIS_KEY}&pSize=365&Type=json"
    print(url)
    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        day_meal_data = db_meal_data
    else:
        day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]
        day_meal_data = [TimeOfMeal(from_neis_data=x) for x in day_meal_data] + db_meal_data

    if len(day_meal_data) == 0:
        return None



    if target_time == "전체":
        lunch_meal_data = defaultdict(list)
        for time_meal_data in day_meal_data:
            lunch_meal_data[time_meal_data.time] = [
                {"menu_name": remove_allergy(menu), "alg": get_allergy(menu)} for menu in
                time_meal_data.menus]
    else:
        lunch_meal_data = []
        for time_meal_data in day_meal_data:
            if time_meal_data.time == target_time:
                lunch_meal_data = [{"menu_name": remove_allergy(menu), "alg": get_allergy(menu)} for menu in
                                   time_meal_data.menus]

    if len(lunch_meal_data) == 0:
        return None

    return lunch_meal_data


def get_allergy(menu):
    alg_list = re.findall("\([^)]*\)|[0-9]*\.", menu)
    result = []
    for i, alg in enumerate(alg_list):
        if alg[-1] != "." or not alg[:-1].isdigit():
            pass
        else:
            result.append(int(alg[:-1]))

    return result


def get_month_meal(school, year, month, target_time="중식", key="date"):
    db_meal_data = get_range_meal_db(school, f"{str(year)}{str(month).zfill(2)}01",
                                     f"{str(year)}{str(month).zfill(2)}{str(calendar.monthrange(int(year), int(month))[1]).zfill(2)}",
                                     target_time)

    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={year}{month.zfill(2)}01&MLSV_TO_YMD={year}{month.zfill(2)}31&KEY={NEIS_KEY}&pSize=365&Type=json"
    print(url)
    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        day_meal_data = db_meal_data
    else:
        day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]
        day_meal_data = [TimeOfMeal(from_neis_data=x) for x in day_meal_data] + db_meal_data

    if len(day_meal_data) == 0:
        return {}

    if target_time == "전체":
        if key == "date":
            lunch_meal_data = defaultdict(dict)
            for time_meal_data in day_meal_data:
                lunch_meal_data[time_meal_data.date][time_meal_data.time] = \
                    [remove_allergy(menu) for menu
                     in
                     time_meal_data.menus]
        elif key == "time":
            print("DD")
            lunch_meal_data = defaultdict(list)
            for time_meal_data in day_meal_data:
                lunch_meal_data[time_meal_data.time].append(
                    {time_meal_data.date: [remove_allergy(menu) for menu
                                           in
                                           time_meal_data.menus]})
    else:
        lunch_meal_data = {}
        for time_meal_data in day_meal_data:
            if time_meal_data.time == target_time:
                lunch_meal_data[time_meal_data.date] = [remove_allergy(menu) for menu in
                                                        time_meal_data.menus]

    if len(lunch_meal_data) == 0:
        return {}

    return lunch_meal_data


def get_range_meal(school, start_date, end_date, target_time="중식", key="date"):
    db_meal_data = get_range_meal_db(school, start_date, end_date, target_time)

    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={get_region_code(school.region)}&SD_SCHUL_CODE={school.school_id}&MLSV_FROM_YMD={start_date}&MLSV_TO_YMD={end_date}31&KEY={NEIS_KEY}&pSize=365&Type=json"
    print(url)
    meal_response = requests.request("GET", url)
    meal_data = json.loads(meal_response.text)
    if "mealServiceDietInfo" not in meal_data:
        day_meal_data = db_meal_data
    else:
        day_meal_data = meal_data["mealServiceDietInfo"][1]["row"]
        day_meal_data = [TimeOfMeal(from_neis_data=x) for x in day_meal_data] + db_meal_data

    if len(day_meal_data) == 0:
        return {}

    if target_time == "전체":
        if key == "date":
            lunch_meal_data = defaultdict(dict)
            for time_meal_data in day_meal_data:
                lunch_meal_data[time_meal_data.date][time_meal_data.time] = \
                    [remove_allergy(menu) for menu
                     in
                     time_meal_data.menus]
        elif key == "time":
            print("DD")
            lunch_meal_data = defaultdict(list)
            for time_meal_data in day_meal_data:
                lunch_meal_data[time_meal_data.time].append(
                    {time_meal_data.date: [remove_allergy(menu) for menu
                                           in
                                           time_meal_data.menus]})
    else:
        lunch_meal_data = {}
        for time_meal_data in day_meal_data:
            if time_meal_data.time == target_time:
                lunch_meal_data[time_meal_data.date] = [remove_allergy(menu) for menu in
                                                        time_meal_data.menus]

    if len(lunch_meal_data) == 0:
        return {}

    return lunch_meal_data


def get_identify(student_id=None):
    try:
        student = Student.query.filter_by(student_seq=g.user_seq).first()
        school = student.school
    except:
        return None
    return student, school


def get_question_rows(menu):
    category_list = get_menu_category_list(menu)
    print(cache.get("question_rows_data"))
    question_rows = [question_row for question_row in cache.get("question_rows_data") if
                     question_row["category"] in category_list]

    question_rows.sort(key=lambda x: x["priority"])

    # question_rows = MealRatingQuestion.query.filter_by(is_available=True, school=None, ).filter(
    #     MealRatingQuestion.category.in_(category_list)).order_by(
    #     MealRatingQuestion.priority.desc(),
    #     MealRatingQuestion.add_date.desc()).all()
    print(question_rows)
    return question_rows


def get_school_by_school_name(school_name):
    url = f"https://open.neis.go.kr/hub/schoolInfo?&SCHUL_NM={school_name}&Type=json&KEY={NEIS_KEY}"
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
    if len(dict_list) == 0:
        return {}

    mean_dict = {}
    for key in dict_list[0].keys():
        mean_dict[key] = sum([d[key] for d in dict_list if key in d]) / len([d[key] for d in dict_list if key in d])
    return mean_dict


def get_host_type():
    import socket
    import os

    hostname = socket.gethostname()
    if hostname[:7] == "DESKTOP" or hostname[:5] == "Chuns":
        host = "LOCAL"
    elif hostname[:5] == "vultr":
        host = "VULTR"
    else:
        host = "HEROKU"
    return host


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
    return len(data)


# fetch_spread_sheet()


def send_mail(receiver, title, html):
    import smtplib
    from email.mime.text import MIMEText
    from config import MAIL_ID, MAIL_PASSWORD

    # 세션 생성
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # TLS 보안 시작
    s.starttls()

    # 로그인 인증
    s.login(MAIL_ID, MAIL_PASSWORD)

    # 보낼 메시지 설정
    msg = MIMEMultipart("alternative")

    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    msg.attach(part2)
    msg['Subject'] = title
    msg["From"] = "YAMMEAL"
    msg["To"] = receiver  # 수신 메일
    # 메일 보내기
    s.sendmail('YAMMEAL', receiver, msg.as_string())

    # 세션 종료
    s.quit()


def is_same_date(a, b):
    if a.year != a.year or a.month != b.month or a.day != b.day:
        return False
    else:
        return True

def edit_distance(s1, s2):


    l1, l2 = len(s1), len(s2)
    if l2 > l1:
        return edit_distance(s2, s1)
    if l2 is 0:
        return l1
    prev_row = list(range(l2 + 1))
    current_row = [0] * (l2 + 1)
    for i, c1 in enumerate(s1):
        current_row[0] = i + 1
        for j, c2 in enumerate(s2):
            d_ins = current_row[j] + 1
            d_del = prev_row[j + 1] + 1
            d_sub = prev_row[j] + (1 if c1 != c2 else 0)
            current_row[j + 1] = min(d_ins, d_del, d_sub)
        prev_row[:] = current_row[:]
    return prev_row[-1]