import requests
import pickle
import json
import re

final = []

for region_code in ["B10","C10","D10","E10","F10","G10","H10","I10","J10","K10","M10","N10","P10","Q10","R10","S10","T10"]:

    print(region_code)

    school_url = f"https://open.neis.go.kr/hub/schoolInfo?ATPT_OFCDC_SC_CODE={region_code}&Type=json&SCHUL_KND_SC_NM=고등학교&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=999"
    response = requests.request("GET", school_url)

    data = json.loads(response.text.encode('utf8'))
    # print(data)
    school_id_list = [school["SD_SCHUL_CODE"] for school in data["schoolInfo"][1]["row"] if "schoolInfo" in data]

    print(len(school_id_list))

    # exit()
    i = 0
    for schoolId in school_id_list:




        url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={region_code}&SD_SCHUL_CODE={schoolId}&MLSV_FROM_YMD=20190101&MLSV_TO_YMD=20191231&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=365&Type=json"
        payload = {}
        headers = {
            'Cookie': 'WMONID=mzfMsQnxiV_'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = json.loads(response.text.encode('utf8'))
        # print(data)

        result = {}


        def remove_allergy(str):
            temp = re.sub("\([^)]*\)|[0-9]*\.", '', str) #알레르기 제거
            temp = re.sub("[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"A-Za-z]+$", "", temp) #연속되는 의미없는 특수문자 제거
            temp = re.sub("[^가-힣a-zA-Z0-9&+/]", "", temp) #    &+/  외 특수문자 제거
            if re.compile("^\d+[^색|단|번|곡|종|ml|L|월|\d].*").match(temp):
                temp = re.sub("^[0-9]","",temp)

            temp = re.sub("^[a-z]","",temp)         #문자열 맨 앞의 소문자 알파벳 제거
            temp = re.sub("^[&|\+]","",temp)      #문자열 맨 앞의 & + / 제거
            temp = re.sub("^/+","",temp)

            if re.compile("^\d+[^색|단|번|곡|종|ml|L|월|\d].*").match(temp):
                temp = re.sub("^[0-9]","",temp)
            temp = re.sub("^[a-z]", "", temp)  # 문자열 맨 앞의 소문자 알파벳 제거
            temp = re.sub("^/+", "", temp)

            temp = re.sub("\d*$","",temp)
            temp = re.sub("/$","",temp)

            return temp


        if "mealServiceDietInfo" not in data:
            continue

        for row in data["mealServiceDietInfo"][1]["row"]:

            if row["MLSV_YMD"] not in result:
                result[row["MLSV_YMD"]] = {}
            result[row["MLSV_YMD"]][row["MMEAL_SC_NM"]] = [remove_allergy(menu) for menu in row["DDISH_NM"].split("<br/>")]

            # result[row["MLSV_YMD"]] =

        # print(result)

        final.append({
            "schoolId": schoolId,
            "schoolName": row["SCHUL_NM"],
            "data": result

        })

        i+= 1
        print(i)

with open('전국 고등학교 급식 데이터.pickle', 'wb') as fw:
    pickle.dump(final, fw)
