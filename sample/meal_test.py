import requests
import pickle
import json
import re
import clipboard

#from . import menu_classifier
from sample import menu_classifier

target_word_list = set()
target_word = "찹"
def add_target_word_list(data):
    if type(target_word_list) == set:
        target_word_list.add(data)
    elif type(target_word_list) == list:
        target_word_list.append(data)

def is_end_target_word(menu):
    if menu["menu"][-len(target_word):] == target_word:
        add_target_word_list(menu["menu"])

def is_contain_word(menu):
    if target_word in menu["menu"]:
        add_target_word_list(menu["menu"])

def is_number_contain(menu):
    if any(map(str.isdigit, menu["menu"])):
        add_target_word_list(menu["menu"])

def test(menu):
    if menu["menu"][-1] != "배" and "배" in menu["menu"]:
        add_target_word_list(menu["menu"])



with open('전국 고등학교 급식 데이터.pickle', 'rb') as fr:
    schools = pickle.load(fr)


# with open('경기도 고등학교 급식 데이터.pickle', 'rb') as fr:
#     schools = pickle.load(fr)

# print(schools)

for school in schools:

    for day in school["data"]:
        for time in school["data"][day]:
            for menu in school["data"][day][time]:
                print(menu)

                # is_end_target_word(menu)
                # is_number_contain({"menu" : menu, "schoolName" : school["schoolName"]})
                is_contain_word({"menu" : menu, "schoolName" : school["schoolName"]})

if type(target_word_list) == set:
    target_word_list = list(target_word_list)
    target_word_list.sort()

for menu in target_word_list:
    print(menu,end=" ")
    print(menu_classifier.classify_menu(menu))
    # print(menu.split("뿌링클"))
print(len(target_word_list))
clipboard.copy("\n".join(target_word_list))