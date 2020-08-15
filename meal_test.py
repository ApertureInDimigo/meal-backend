import requests

import json
import re
# url = "https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE=J10&SD_SCHUL_CODE=7530560&MLSV_FROM_YMD=20200101&MLSV_TO_YMD=20210101&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=365&Type=json"
url = "https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE=F10&SD_SCHUL_CODE=7380031&MLSV_FROM_YMD=20200101&MLSV_TO_YMD=20210101&KEY=cea5e646436e4f5b9c8797b9e4ec7a2a&pSize=1000&Type=json"
payload = {}
headers = {
  'Cookie': 'WMONID=mzfMsQnxiV_'
}

response = requests.request("GET", url, headers=headers, data = payload)

data = json.loads(response.text.encode('utf8'))
# print(data)

result = {}
def remove_allergy(str):
    temp = re.sub("\([^)]*\)|[0-9]*\.", '', str)
    return re.sub("[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"A-Za-z]+$", "", temp)

for row in data["mealServiceDietInfo"][1]["row"]:

    if row["MLSV_YMD"] not in result:
        result[row["MLSV_YMD"]] = {}
    result[row["MLSV_YMD"]][row["MMEAL_SC_NM"]] = [remove_allergy(menu) for menu in row["DDISH_NM"].split("<br/>")]

    # result[row["MLSV_YMD"]] =


print(result)