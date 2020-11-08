import requests
import pickle
import json
import re
from config import NEIS_KEY
final = []

region_codes = ["B10","C10","D10","E10","F10","G10","H10","I10","J10","K10","M10","N10","P10","Q10","R10","S10","T10"]

for region_code in region_codes:

    print(region_code)

    school_url = f"https://open.neis.go.kr/hub/schoolInfo?ATPT_OFCDC_SC_CODE={region_code}&Type=json&SCHUL_KND_SC_NM=고등학교&KEY={NEIS_KEY}&pSize=999"
    response = requests.request("GET", school_url)

    data = json.loads(response.text.encode('utf8'))
    # print(data)
    school_id_list = [school["SD_SCHUL_CODE"] for school in data["schoolInfo"][1]["row"] if "schoolInfo" in data]

    print(len(school_id_list))

    # exit()
    i = 0
    for schoolId in school_id_list:




        url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={region_code}&SD_SCHUL_CODE={schoolId}&MLSV_FROM_YMD=20190101&MLSV_TO_YMD=20191231&KEY={NEIS_KEY}&pSize=365&Type=json"
        payload = {}
        headers = {
            'Cookie': 'WMONID=mzfMsQnxiV_'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = json.loads(response.text.encode('utf8'))
        # print(data)

        result = {}


        def remove_allergy(str):
            return str


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

with open('전국 고등학교 급식 데이터(원본).pickle', 'wb') as fw:
    pickle.dump(final, fw)
