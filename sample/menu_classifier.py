import re

Noodle = ["면", "국수", "우동", "모밀", "스파게티", "파스타", "라멘"]
Carb = ["밥", "죽", "^.*[^슬|후]라이스[^볼|바]"] + Noodle  # 탄수화물

Soup = ["국", '찌개', "^.*[^맛]탕$", "개장", "전골", "스프"]  # 물

Fruit = ["바나나", '수박', '딸기', '복숭아', '황도', '백도', '포도', '거봉', '블루베리', '사과', '키위',
         '오렌지', '토마토', "레몬", "자두", "스위티", "천혜향", "황금향", "파파야", "용과", "감[^자]", "망고",
         "체리", "모과", "살구", "낑깡", "오디", "메론", "무화과", "석류", "유자", "한라봉", "구아바", "라임",
         "람부탄", "멜론", "칼라만시", "깔라만시", "라임", "자몽", "코코넛", "배", "참외", "파인애플",
         "패션후루츠", "레드향", "샤인머스켓", "복분자", "홍시", "아사베리", "아로니아", "라즈베리", "매실",
         "망고스틴", "^.*배[^추]*"]
Desert = ["아이스", "티", "에이드", "주스", "드링크", "마시는", "^.*[^스]쿨", "^.*차$", "스무디", "라떼",
          "푸딩", "츄러스", "식혜", "떡", "요거트", "시리얼", "크로칸슈", "티라미수", "고로케",
          "초코", "쿠키", "크런치"] + Fruit  # 후식

Spicy = ["매콤", "매운", "맵", "떡볶이", "칠리", "불[^고기]", "짬뽕", "고추", "비빔", "핫[^초코|쵸코|초콜릿|도그|바|케이크|케익]"
                                                                   "깐쇼", "깐풍", "볼케이노", "땡초", "할라피뇨", "[^고구]마라"]

Fry = ["튀김", "탕수", "가스[^오]", "까스", "후라이드", "프라이드", "강정", "꿔바로우", "너겟", "치킨", "가라아게", "카라아게"]

Meat = ["[^물]고기", "갈비", "돼지", "닭", "한우", "^.*육$", "보쌈", "제육", "오리", "장각", "차슈", "[^케]찹[^쌀]", "돈"]

Fish = ["물고기", "고등어", "임연수", "가자미", "코다리", "연어", "삼치", "매운탕", "아구찜", "쥐치", "생선", "조기", "굴비", "장어"]


def is_regex(str):
    if "^" in str:
        return True
    else:
        return False


# 대분류(4가지)
'''
탄수화물(밥/면) - type_1
국 - type_2
후식 - type_3
반찬 - type_4
'''


def classify_menu(menu):
    for t in Carb:
        if t in menu:
            return "type_1"

    for t in Soup:
        if is_regex(t):
            if re.compile(t).match(menu):
                return "type_2"
        elif t in menu:
            return "type_2"

    for t in Desert:
        if is_regex(t):
            if re.compile(t).match(menu):
                return "type_3"
        elif t in menu:
            return "type_3"

    return "type_4"


def get_menu_category_list(menu):
    category_result = []

    category_list = ["면", "밥", "국", "과일", "후식", "매운", "튀김", "육류", "생선"]
    regex_list = [Noodle, Carb, Soup, Fruit, Desert, Spicy, Fry, Meat, Fish]

    for category, regex in zip(category_list, regex_list):
        for t in regex:
            if is_regex(t):

                if re.compile(t).match(menu):
                    category_result.append(category)
                    print(t, menu, category)
                    break
            elif t in menu:
                category_result.append(category)
                print(t, menu, category)
                break

    if not any((category in category_result) for category in ["면", "밥", "국", "과일", "후식"]):
        category_result.insert(0, "반찬")

    return category_result


print(get_menu_category_list("배추겉절이"))
