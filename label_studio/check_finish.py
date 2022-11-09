import re
import json

pattern = re.compile(r'-(\d+).png')

with open("project-4-at-2022-10-22-03-53-fde670cb") as f:
    datas4 = json.load(f)
with open("project-5-at-2022-10-22-03-55-99c17cac.json") as f:
    datas5 = json.load(f)
keys = []
for data in datas4:
    sn = re.findall(pattern, data["image"])

    if data.get("labelme") is None:
        keys.append(*sn)
    elif data.get("labelimg") is None:
        keys.append(*sn)
uselesss = ["501", "510", "513", "516", "545", "562", "572", "596", "618", "633", "637", "646", "650", "651", "657",
            "663", "666", "687", "694", "720", "721", "730", "734", "736", "740", "753 ", "799 ", "812 ", "818 ",
            "873 ",
            "874 ", "876 ", "891 ", "894 ", "899 ", "954 ", "956 ", "958 ", "1016", "1024", "1042", "1048", "1081",
            "1142", "1161", "1183", "1188", "1206", "1211", "1294", "1327", "1434", "1453", "1300", "1306", "5008",
            "5094", "5117", "5407", "5408"]
for useless in uselesss:
    if useless not in keys:
        print(f"{useless} in keys")
    else:
        keys.remove(useless)

print(keys)
