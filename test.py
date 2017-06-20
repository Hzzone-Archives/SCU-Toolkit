import json
tparam = {
    "kch": "",
    "cxkxh": "",
    "kcm" : "",
    "skjs": "",
    "kkxsjc": "",
    "skxq": "",
    "skjc": "",
    "pageNumber": "-2",
    "preActionType": "2",
    "actionType": "5"
}
f = open("lessons.json", encoding='utf-8')
lessons = json.load(f)
lessons = lessons["lessons"]
tparam = lessons[0]
print(tparam)
