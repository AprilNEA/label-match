import requests
import json
import re
import os
from PIL import Image
import xml.dom.minidom
import xml.etree.ElementTree as ET
from typing import List, Tuple
from shapely.geometry import Polygon

# session = requests.Session()
label_list = ["B1", "B2", "B3", "B4", "B5", "BO", "BS", "R1", "R2", "R3", "R4", "R5", "RO", "RS"]

MAIN_URL = ""
HEADERS = {
    "Authorization": ""
}
PROXY = {
    "http": "127.0.0.1:6152",
    "https": "127.0.0.1:6152"
}
pattern = re.compile(r'-(\d+).jpg')


def get_tasks(id=4):
    reply = requests.get(url=f"http://{MAIN_URL}/api/projects/{id}/tasks/?page_size=-1",
                         headers=HEADERS,
                         proxies=PROXY)
    with open('../src/data.json', 'w') as f:
        json.dump(reply.json(), f)


def xywh2four_coordinate(row: List, width: int, height: int) -> List[Tuple]:
    """

    :param row: <Label serial number> <x> <y> <w> <h>
    :param width: the width of the image
    :param height: the height of the image
    :return: List of four coordinates
    """
    x_min, y_min, x_max, y_max = xywh2two_coordinate2(row, width, height)
    return [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_max),
        (x_max, y_min)
    ]


def find_omission():
    with open('../src/data.json', 'r') as f:
        datas = json.load(f)
    for data in datas:
        try:
            sn = re.findall(pattern, data["data"]["image"])[0]
        except IndexError:
            print(data)
        if os.path.exists(f"../ALL/{sn}.png"):
            os.remove(f"../ALL/{sn}.png")


def xywh2two_coordinate(row, width, height):
    """

    :param row: <Label serial number> <x> <y> <w> <h>
    :param width: the width of the image
    :param height: the height of the image
    :return: Tuple of two coordinates
    """
    len = 0
    for r in row:
        row[len] = float(r)
        len += 1
    x_min = min(max(0.0, row[1] - row[3] / 2), 1.0) * width
    y_min = min(max(0.0, row[2] - row[4] / 2), 1.0) * height
    x_max = min(max(0.0, row[1] + row[3] / 2), 1.0) * width
    y_max = min(max(0.0, row[2] + row[4] / 2), 1.0) * height
    return [
        [x_min, y_min],
        [x_min, y_max],
        [x_max, y_max],
        [x_max, y_min]
    ]


def xywh2two_coordinate2(row, width, height) -> Tuple:
    """

    :param row: <Label serial number> <x> <y> <w> <h>
    :param width: the width of the image
    :param height: the height of the image
    :return: Tuple of two coordinates
    """
    len = 0
    for r in row:
        row[len] = float(r)
        len += 1
    x_min = min(max(0.0, row[1] - row[3] / 2), 1.0) * width
    y_min = min(max(0.0, row[2] - row[4] / 2), 1.0) * height
    x_max = min(max(0.0, row[1] + row[3] / 2), 1.0) * width
    y_max = min(max(0.0, row[2] + row[4] / 2), 1.0) * height
    return x_min, y_min, x_max, y_max


p = lambda x, w, h: [
    [x[0][0] * 100 / w, x[0][1] * 100 / h],
    [x[1][0] * 100 / w, x[1][1] * 100 / h],
    [x[2][0] * 100 / w, x[2][1] * 100 / h],
    [x[3][0] * 100 / w, x[3][1] * 100 / h]
]


def main():
    with open('../src/data.json', 'r') as f:
        datas = json.load(f)
    for data in datas:
        try:
            sn = re.findall(pattern, data["data"]["image"])[0]
        except IndexError:
            print(data)
        tmp = {
            "id": data["id"],
            "data": data["data"],
            "annotations": [
                {
                    "result": [],
                }
            ],
            "predictions": []
        }
        flag = False
        if os.path.exists(f"../all/labelme/{sn}.json"):
            flag = True
            with open(f"../all/labelme/{sn}.json", "r") as f:
                me_data = json.load(f)

                for point in me_data["shapes"]:
                    if len(point["points"]) < 4:
                        print(sn)
                        continue
                    tmp["annotations"][0]["result"].append({
                        "original_width": me_data["imageWidth"],
                        "original_height": me_data["imageHeight"],
                        "image_rotation": 0,
                        "value": {
                            "points": p(point["points"], me_data["imageWidth"], me_data["imageHeight"]),
                            "polygonlabels": [
                                str(point["label"] + "-me")
                            ]},
                        "from_name": "labelme",
                        "to_name": "image",
                        "type": "polygonlabels",
                        "origin": "manual"
                    })
        if os.path.exists(f"../all/labelimg/{sn}.txt"):
            img_data = []
            with open(f"../all/labelimg/{sn}.txt") as f:
                for line in f.readlines():
                    img_data.append(line.split())
            if flag:
                w, h = me_data["imageWidth"], me_data["imageHeight"]
            else:
                img = Image.open(f"../all/images/{sn}.png")
                w, h = img.size
            for point in img_data:
                tmp["annotations"][0]["result"].append({
                    "original_width": w,
                    "original_height": h,
                    "image_rotation": 0,
                    "value": {
                        "x": (float(point[1]) - float(point[3]) / 2) * 100,
                        "y": (float(point[2]) - float(point[4]) / 2) * 100,
                        "width": float(point[3]) * 100,
                        "height": float(point[4]) * 100,
                        "rotation": 0,
                        "rectanglelabels": [
                            str(label_list[int(point[0])] + ("-img"))
                        ]},
                    "from_name": "labelimg",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "origin": "manual"
                })
            flag = True
        elif os.path.exists(f"../all/labelimg/{sn}.xml"):
            # flag = True
            # dom = xml.dom.minidom.parse(f"../all/labelimg/{sn}.xml")
            # root = dom.documentElement
            # w = int(root.getElementsByTagName('width')[0].firstChild.data)
            # h = int(root.getElementsByTagName('height')[0].firstChild.data)
            # # print(sn, w, h)
            # objects = root.getElementsByTagName('object')
            #
            #
            # # Return lis
            tree = ET.parse(f"../all/labelimg/{sn}.xml")
            root = tree.getroot()

            # Get the width, height of images
            #  to normalize the bounding boxes
            size = root.find("size")
            width, height = float(size.find("width").text), float(size.find("height").text)

            # Find all the bounding objects
            for label_object in root.findall("object"):
                # Temp array for csv, initialized by the training types

                # Bounding box coordinate
                bounding_box = label_object.find("bndbox")

                # Add the upper left coordinate
                name = label_object.find("name").text
                xmin = float(bounding_box.find("xmin").text) / width
                ymin = float(bounding_box.find("ymin").text) / height
                xmax = float(bounding_box.find("xmax").text) / width
                ymax = float(bounding_box.find("ymax").text) / height

                tmp["annotations"][0]["result"].append({
                    "original_width": width,
                    "original_height": height,
                    "image_rotation": 0,
                    "value": {
                        "x": xmin * 100,
                        "y": ymin * 100,
                        "width": (xmax - xmin) * 100,
                        "height": (ymax - ymin) * 100,
                        "rotation": 0,
                        "rectanglelabels": [
                            str(name + "-img")
                        ]},
                    "from_name": "labelimg",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "origin": "manual"
                })
        # if flag:
        with open(f"../all/output/{sn}.json", "w") as f:
            json.dump(tmp, f)
        # print(f"{sn}完成")


def updata_task():
    with open('../src/data.json', 'r') as f:
        datas = json.load(f)
    for data in datas:
        try:
            sn = re.findall(pattern, data["data"]["image"])[0]
        except IndexError:
            print(data)
        if os.path.exists(f"../all/output/{sn}.json"):
            with open(f"../all/output/{sn}.json") as f:
                out_data = json.load(f)
    reply = requests.post(url=f"http://{MAIN_URL}/api/{id}/",
                          headers=HEADERS,
                          proxies=PROXY,
                          json={
                              "data": data["data"],
                              "meta": data["meta"],
                              "is_labeled": data["meta"],
                              "overlap": data["overlap"],
                              "inner_id": data["inner_id"],
                              "total_annotations": 0,
                              "cancelled_annotations": 0,
                              "total_predictions": 0,
                              "project": 4,
                              "updated_by": 0,
                              "file_upload": 0
                          })
    with open('../src/data.json', 'w') as f:
        json.dump(reply.json(), f)


def if_intersect(data1: List, data2: List) -> float:
    """
    Calculation of the intersection area of any two figures
    :param data1, data2:Coordinates of two plane figures
    :return: The area intersection of the current object and the object to be compared
    """

    poly1 = Polygon(data1).convex_hull
    poly2 = Polygon(data2).convex_hull

    if not poly1.intersects(poly2):
        inter_area = 0
    else:
        inter_area = poly1.intersection(poly2).area
    return inter_area


def coordinate2normalized4(points: List, width: int, height: int) -> List:
    """
    The four points have ordinary and normal coordinate composition and are converted into normalized four coordinate points.
    :param points: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
    :param width: the width of the image
    :param height: the height of the image
    :return: a list of eight points, specific numbers
    """
    t_x = lambda x: x[0] / width
    t_y = lambda x: x[1] / height
    return [t_x(points[0]), t_y(points[0]),
            t_x(points[1]), t_y(points[1]),
            t_x(points[2]), t_y(points[2]),
            t_x(points[3]), t_y(points[3])]


def output(label: int, img_point: List, me_point: List, final_path) -> None:
    out1 = ""
    out2 = ""
    for x in img_point[1:]:
        out1 = out1 + f" {x}"
    for x in me_point:
        out2 = out2 + f" {x}"
    out = str(label) + out1 + out2
    with open(final_path, 'at') as f:
        f.writelines(out + "\n")


def output_nome(label: int, img_point: List, final_path) -> None:
    out1 = ""
    for x in img_point[1:]:
        out1 = out1 + f" {x}"
    out = str(label) + out1
    with open(final_path, 'at') as f:
        f.writelines(out + "\n")


def output1(labels):
    for label in labels:
        print(label["image"])
        sn = re.findall(pattern, label["image"])[0]
        if "labelme" in label:
            if "labelimg" in label:
                if len(label["labelme"]) == 1 and len(label["labelimg"]) == 1:
                    _img = label["labelimg"][0]
                    _me = label["labelme"][0]
                    w = _img["width"] / 100
                    h = _img["height"] / 100
                    x = (_img["x"] / 100 + w / 2)
                    y = (_img["y"] / 100 + h / 2)
                    ow = _me["original_width"]
                    oh = _me["original_height"]
                    try:
                        me_coor = [(_me["points"][0][0] * ow / 100, _me["points"][0][1] * oh / 100),
                                   (_me["points"][1][0] * ow / 100, _me["points"][1][1] * oh / 100),
                                   (_me["points"][2][0] * ow / 100, _me["points"][2][1] * oh / 100),
                                   (_me["points"][3][0] * ow / 100, _me["points"][3][1] * oh / 100)
                                   ]
                    except IndexError:
                        print(f"{sn}数据出现错误")
                    me_nor = coordinate2normalized4(me_coor, _me["original_width"],
                                                    _me["original_height"])
                    label_sn = label_list.index(_me["polygonlabels"][0].replace('-me', ''))
                    output(label_sn, [0, x, y, w, h], me_nor,
                           f"out/{sn}.txt")
                    continue
                # print(sn)
                for _me in label["labelme"]:
                    for _img in label["labelimg"]:
                        w = _img["width"] / 100
                        h = _img["height"] / 100
                        x = _img["x"] / 100 + w / 2
                        y = _img["y"] / 100 + h / 2
                        img_coor = xywh2four_coordinate([0, x, y, w, h], _img["original_width"],
                                                        _img["original_height"])
                        ow = _me["original_width"]
                        oh = _me["original_height"]
                        try:
                            me_coor = [(_me["points"][0][0] * ow / 100, _me["points"][0][1] * oh / 100),
                                       (_me["points"][1][0] * ow / 100, _me["points"][1][1] * oh / 100),
                                       (_me["points"][2][0] * ow / 100, _me["points"][2][1] * oh / 100),
                                       (_me["points"][3][0] * ow / 100, _me["points"][3][1] * oh / 100)
                                       ]
                        except IndexError:
                            print(f"{sn}数据出现错误")
                        # print(img_coor)
                        # print(me_coor)
                        area = if_intersect(img_coor, me_coor)
                        # print(area)
                        print(me_coor)
                        if area > 0:
                            try:
                                me_nor = coordinate2normalized4(me_coor, _me["original_width"],
                                                                _me["original_height"])
                            except IndexError:
                                print(f"{sn}数据出现错误")
                            # print(me_nor)
                            label_sn = label_list.index(_me["polygonlabels"][0].replace('-me', ''))
                            output(label_sn, [0, x, y, w, h], me_nor,
                                   f"out/{sn}.txt")


def output2(labels):
    pattern = re.compile(r'-(\d+).jpg')
    # pattern = re.compile(r'-cut(\d+)-(\d+).jpg')
    for label in labels:
        sn = re.findall(pattern, label["image"])[0]
        print(sn)
        # name = f"cut{sn[0]}-{sn[1]}"
        # name = f"cut{sn[0]}"
        name = sn
        # print(name)
        if "labelb" in label:
            for _point in label["labelb"]:
                # print(_point)
                _img = _point
                w = _img["width"] / 100
                h = _img["height"] / 100
                x = (_img["x"] / 100 + w / 2)
                y = (_img["y"] / 100 + h / 2)
                label_sn = label_list.index(_img["rectanglelabels"][0])
                output_nome(label_sn, [0, x, y, w, h], f"out/{name}.txt")
                del w, h, x, y

        if "labelr" in label:
            for _point in label["labelr"]:
                _img = _point
                w = _img["width"] / 100
                h = _img["height"] / 100
                x = (_img["x"] / 100 + w / 2)
                y = (_img["y"] / 100 + h / 2)
                label_sn = label_list.index(_img["rectanglelabels"][0])
                output_nome(label_sn, [0, x, y, w, h], f"out/{name}.txt")
                del w, h, x, y


if __name__ == '__main__':
    with open("") as f:
        datas4 = json.load(f)
    output2(datas4)

