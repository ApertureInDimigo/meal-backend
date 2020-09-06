import re

Carb = ["밥", "면", "국수", "우동", "모밀", "스파게티", "파스타", "라멘", "죽"]  # 탄수화물
Soup = ["국", '찌개', "^.*[^맛]탕$", "개장"]  # 물
Desert = ["아이스", "티", "에이드", "주스", "드링크", "마시는", "^.*[^스]쿨", "^.*차$", "스무디", "라떼",
          "바나나", '수박', '딸기', '복숭아', '황도', '백도', '포도', '거봉', '블루베리', '사과', '키위',
          '오렌지', '토마토', "레몬", "자두", "스위티", "천혜향", "황금향", "파파야", "용과", "감", "망고",
          "체리", "모과", "살구", "낑깡", "오디", "메론", "무화과", "석류", "유자", "한라봉", "구아바", "라임",
          "람부탄", "멜론", "칼라만시", "깔라만시", "라임" , "자몽", "코코넛", "귤", "배", "참외", "파인애플",
          "패션후루츠", "레드향", "샤인머스켓", "복분자", "홍시", "아사베리", "아로니아", "라즈베리", "매실",
          "망고스틴","초코"]  # 후식


def is_regex(str):
    if "^" in str:
        return True
    else:
        return False

def classify_menu(menu):
    for t in Carb:
        if t in menu:
            return "탄수화물(밥/면)"

    for t in Soup:
        if is_regex(t):
            if re.compile(t).match(menu):
                return "국"
        elif t in menu:
            return "국"

    for t in Desert:
        if is_regex(t):
            if re.compile(t).match(menu):
                return "후식"
        elif t in menu:
            return "후식"

    return "반찬"

