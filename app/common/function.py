import re
import datetime

def get_region_code(region):
    if region == "경기도":
        return "J10"
def remove_allergy(str):
    temp = re.sub("\([^)]*\)|[0-9]*\.", '', str) #알레르기 제거
    temp = re.sub("[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"A-Za-z]+$", "", temp) #연속되는 의미없는 특수문자 제거
    temp = re.sub("[^가-힣a-zA-Z0-9&+/]", "", temp) #    &+/  외 특수문자 제거
    return temp


def str_to_date(str):
    date = datetime.datetime.strptime(str, "%Y%m%d")

    return date