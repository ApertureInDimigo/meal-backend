import re
import time

Noodle = ["면", "국수", "우동", "모밀", "스파게티", "파스타", "라멘"]
Reg_Noodle = "[면|국수|우동|모밀|스파게티|파스타|라멘]"

Carb = ["밥", "죽", "[^슬|후]라이스[^볼|바]"] + Noodle  # 탄수화물
Reg_Carb = "[밥|죽|[^슬|후]라이스[^볼|바]|면|국수|우동|모밀|스파게티|파스타|라멘]"

Soup = ["국", '찌개', "[^맛]탕[국]*$", "개장", "전골", "스프", "수프"]  # 물
Reg_Soup = "[국|찌개|[^맛]탕[국]*$|개장|전골|스프|수프]"

Fruit = ["바나나", '수박', '딸기[^파이]*', '복숭아', '황도', '백도', '포도', '거봉', '블루베리', '사과[^파이]*', '키위',
         '오렌지', '토마토', "레몬", "자두", "스위티", "천혜향", "황금향", "파파야", "용과", "감[^자]", "망고",
         "체리", "모과", "^.*살구[^이]", "낑깡", "오디", "메론", "무화과", "석류", "유자", "한라봉", "구아바", "라임",
         "람부탄", "멜론", "칼라만시", "깔라만시", "라임", "자몽", "코코넛", "참외", "파인애플",
         "패션후루츠", "레드향", "샤인머스켓", "복분자", "홍시", "아사베리", "아로니아", "라즈베리", "매실",
         "망고스틴", "배[^추]"]
Reg_Fruit = "[바나나|수박|딸기[^파이]*|복숭아|황도|백도|포도|거봉|블루베리|사과[^파이]*|키위|오렌지|"\
            "토마토|레몬|자두|스위티|천혜향|황금향|파파야|용과|감[^자]|망고|체리|모과|살구[^이]|낑깡|"\
            "오디|메론|무화과|석류|유자|한라봉|구아바|라임|람부탄|멜론|칼라만시|깔라만시|라임|자몽|코코넛|"\
            "참외|파인애플|패션후루츠|레드향|샤인머스켓|복분자|홍시|아사베리|아로니아|라즈베리|매실|망고스틴|배[^추]]"

Drink = ["아이스", "티", "에이드", "주스", "드링크", "마시는", "차$", "스무디", "라떼", "식혜", "요구르트", "[^스]쿨", "미숫가루", "피크닉"]
Reg_Drink = "[아이스|티|에이드|주스|드링크|마시는|차$|스무디|라떼|식혜|요구르트|[^스]쿨|미숫가루|피크닉]"

Desert = ["푸딩", "츄러스", "떡[^국]", "요거트", "시리얼", "크로칸슈", "티라미수", "고로케", "초코", "쿠키", "크런치", "파이", "빼빼로",
          "과자", "스낵", "케익", "도넛", "카롱", "쉐이크"] + Fruit + Drink  # 후식
Reg_Desert = "[푸딩|츄러스|떡[^국]|요거트|시리얼|크로칸슈|티라미수|고로케|초코|쿠키|크런치|파이|빼빼로|"\
             "과자|스낵|케익|도넛|카롱|쉐이크|바나나|수박|딸기[^파이]*|복숭아|황도|백도|포도|거봉|블루베리|"\
             "사과[^파이]*|키위|오렌지|토마토|레몬|자두|스위티|천혜향|황금향|파파야|용과|감[^자]|망고|체리|"\
             "모과|^.*살구[^이]|낑깡|오디|메론|무화과|석류|유자|한라봉|구아바|라임|람부탄|멜론|칼라만시|"\
             "깔라만시|라임|자몽|코코넛|참외|파인애플|패션후루츠|레드향|샤인머스켓|복분자|홍시|아사베리|"\
             "아로니아|라즈베리|매실|망고스틴|배[^추]|아이스|티|에이드|주스|드링크|마시는|차$|스무디|라떼|"\
             "식혜|요구르트|[^스]쿨|미숫가루|피크닉]"

Spicy = ["매콤", "매운", "맵", "떡볶이", "칠리", "[^숯]불[^고기]", "짬뽕", "고추", "비빔", "핫[^초코|쵸코|초콜릿|도그|바|케이크|케익]", "깐쇼",
         "깐풍", "볼케이노", "땡초", "할라피뇨", "[^고구]마라", "[^물]김치"]
Reg_Spicy = "[매콤|매운|맵|떡볶이|칠리|불[^고기]|짬뽕|고추|비빔|핫[^초코|쵸코|초콜릿|도그|바|케이크|케익]|깐쇼|깐풍|볼케이노|땡초|할라피뇨|[^고구]마라|[^물]김치]"


Fry = ["튀김", "탕수", "가스[^오]", "까스", "후라이드", "프라이드", "강정", "꿔바로우", "너겟", "치킨", "가라아게", "카라아게"]
Reg_Fry = "[튀김|탕수|가스[^오]|까스|후라이드|프라이드|강정|꿔바로우|너겟|치킨|가라아게|카라아게]"

Meat = ["[^물]고기", "갈비", "돼지", "닭", "한우", "^.*육$", "보쌈", "제육", "오리", "장각", "차슈", "[^케]찹[^쌀]", "돈"]
Reg_Meat = "[[^물]고기|갈비|돼지|닭|한우|^.*육$|보쌈|제육|오리|장각|차슈|[^케]찹[^쌀]|돈]"

Fish = ["물고기", "고등어", "임연수", "가자미", "코다리", "연어", "삼치", "매운탕", "아구찜", "쥐치", "생선", "조기", "굴비", "장어"]
Reg_Fish = "[물고기|고등어|임연수|가자미|코다리|연어|삼치|매운탕|아구찜|쥐치|생선|조기|굴비|장어]"

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
            if re.compile(t).search(menu):
                return "type_2"
        elif t in menu:
            return "type_2"

    for t in Desert:
        if is_regex(t):
            if re.compile(t).search(menu):
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
                if re.compile(t).search(menu):
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

def classify_menu_list(menu):
    result_list = []

    category_list = ["면", "밥", "국", "과일", "후식", "매운", "튀김", "육류", "생선"]
    regex_list = [Noodle, Carb, Soup, Fruit, Desert, Spicy, Fry, Meat, Fish]

    for category, regex in zip(category_list, regex_list):
        for t in regex:
            if is_regex(t):
                if re.compile(t).search(menu):
                    result_list.append(category)
                    break
            elif t in menu:
                result_list.append(category)
                break

    if not any((category in result_list) for category in ["면", "밥", "국", "과일", "후식"]):
        result_list.insert(0, "반찬")

    return result_list


def classify_menu_regex(menu):
    result_list = []
    category_list = ["면", "밥", "국", "과일", "후식", "매운", "튀김", "육류", "생선"]
    regex_list = [Reg_Noodle, Reg_Carb, Reg_Soup, Reg_Fruit, Reg_Desert, Reg_Spicy, Reg_Fry, Reg_Meat, Reg_Fish]

    for category, regex in zip(category_list, regex_list):
        if re.compile(regex).search(menu):
            result_list.append(category)

    if not any((category in result_list) for category in ["면", "밥", "국", "과일", "후식"]):
        result_list.insert(0, "반찬")

    return result_list

'''
reg = "[^맛]탕[국]*$"
str = "소고기탕국"

if re.compile(reg).search(str):
    print(str+" search "+reg)
else:
    print("search Error")

if re.compile(reg).match(str):
    print(str+" match "+reg)
else:
    print("match Error")
'''


def list_to_reg(List):
    print("\"[", end="")
    for tmp, num in zip(List, range(len(List))):
        if num == len(List) - 1:
            print(tmp, end="")
        else:
            print(tmp, end="|")
    print("]\"")


'''
word="맛없는단감"
type=""

start = time.time()
for f in Fruit:
    if is_regex(f):
        if re.compile(f).search(word):
            type = "과일"
    else:
        if f in word:
            type="과일"
print(type)
print("일반 반복문 : ",time.time()-start)

type =""
start = time.time()
if re.compile(Reg_Fruit).search(word):
    type = "과일"

print(type)
print("정규 문자열 : ",time.time()-start)
'''

'''
menu_list = ["보조밥", "충무김밥", "떡만줏국&김가루", "오징어어묵무침", "야채튀김&초감장", "석박지", "피크닉"]

start = time.time()
min_time = 100
max_time = 0

for menu in menu_list:
    tmp_start = time.time()
    print(menu, end="  ")
    print(classify_menu_list(menu))
    tmp_time = time.time()-start
    if tmp_time < min_time:
        min_time = tmp_time
    if tmp_time > max_time:
        max_time = tmp_time

sum_time = time.time()-start
print("리스트 검사 속도 : ", sum_time)
print("각 메뉴 평균 검사 속도 : ", sum_time / len(menu_list))
print("최단시간 검사 : ", min_time)
print("최장시간 검사 : ", max_time)

start = time.time()
min_time = 100
max_time = 0

for menu in menu_list:
    tmp_start = time.time()
    print(menu, end="  ")
    print(classify_menu_regex(menu))
    tmp_time = time.time() - start
    if tmp_time < min_time:
        min_time = tmp_time
    if tmp_time > max_time:
        max_time = tmp_time

sum_time = time.time()-start
print("리스트 검사 속도 : ", sum_time)
print("각 메뉴 평균 검사 속도 : ", sum_time / len(menu_list))
print("최단시간 검사 : ", min_time)
print("최장시간 검사 : ", max_time)
'''