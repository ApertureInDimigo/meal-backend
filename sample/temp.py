import re

Carb = ["밥", "면", "국수", "우동", "모밀", "스파게티", "파스타", "라멘", "죽"]  # 탄수화물
Soup = ["국", '찌개', "^.[^맛]탕$", "개장"]  # 물
Desert = ["아이스", "티", "에이드", "주스", "드링크", "마시는", "^.[^스]쿨", "^.*차$", "스무디", "라떼", "초코"]  # 후식


def is_regex(str):
    if "^" in str:
        return True
    else:
        return False


Input = "차돌박이"
menu_type = ""

for t in Carb:
    if t in Input:
        menu_type = "탄수화물(밥/면)"
        break
if menu_type == "":
    for t in Soup:
        if is_regex(t):
            if re.compile(t).match(Input):
                menu_type = "국"
        elif t in Input:
            menu_type = "국"
            break

if menu_type == "":
    for t in Desert:
        if is_regex(t):
            if re.compile(t).match(Input):
                menu_type = "후식"
        elif t in Input:
                menu_type = "후식"
                break
if menu_type == "":
    menu_type = "반찬"

print(Input + "은(는) " + menu_type + "입니다.")