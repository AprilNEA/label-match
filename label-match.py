import os
import json
import numpy as np
from pydantic import BaseModel
from os import PathLike
from decimal import Decimal
from typing import Union, Tuple, List
from utils import json2coordinates, yolo2coordinates, calculate_IoU

label_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'BO', 'BS', 'R1', 'R2', 'R3', 'R4', 'R5', 'RO', 'RS']  # 标签列表

labelme_dir = 'data/label_json/'  # json文件列表
labelimg_dir = 'data/label_img/'  # json文件列表
final_dir = 'data/label_final/'  # txt文件列表



# 第0位: 装甲板的类别<br>
# 第1-4位: 装甲板标注锚框,用于目标检测。四个数的顺序是x,y,w,h，其中x,y,是锚框中心点的归一化坐标，w,h 是归一化相对宽高。<br>
# 第5-12位: 装甲板灯条的边界点，从前到后分别是:<br>
# * 左上角归一化坐标x1,y1<br>
# * 左下角归一化坐标x2,y2<br>
# * 右下角归一化坐标x3,y3<br>
# * 右上角归一化坐标x4,y4<br>
c
# class Points(BaseModel):
#     height: int
#     width: int


def normalized(points: List, height, width) -> List[Decimal]:
    """

    :param points:
    :param height:
    :param width:
    :return:
    """
    t_m_x = lambda x: (Decimal(x[0][0]) + Decimal(x[1][0]) + Decimal(x[2][0]) + Decimal(x[3][0])) / (4 * width)
    t_m_y = lambda x: (Decimal(x[0][1]) + Decimal(x[1][1]) + Decimal(x[2][1]) + Decimal(x[3][1])) / (4 * height)
    t_i_w = lambda x: (Decimal(x[3][0]) - Decimal(x[0][0]) + Decimal(x[2][0]) - Decimal(x[1][0])) / (2 * width)
    t_i_h = lambda x: (Decimal(x[1][1]) - Decimal(x[0][1]) + Decimal(x[3][1]) - Decimal(x[2][1])) / (2 * height)
    t_x = lambda x: Decimal(x[0]) / Decimal(width)
    t_y = lambda x: Decimal(x[1]) / Decimal(height)

    return [t_m_x(points), t_m_y(points),
            t_i_w(points), t_i_h(points),
            t_x(points[0]), t_y(points[0]),
            t_x(points[1]), t_y(points[1]),
            t_x(points[2]), t_y(points[2]),
            t_x(points[3]), t_y(points[3])]


def normalized2(points: List, height, width) -> List[Decimal]:
    """

    :param points:
    :param height:
    :param width:
    :return:
    """
    t_m_x = lambda x: (Decimal(x[0][0]) + Decimal(x[1][0]) + Decimal(x[2][0]) + Decimal(x[3][0])) / 4 * width
    t_m_y = lambda x: (Decimal(x[0][1]) + Decimal(x[1][1]) + Decimal(x[2][1]) + Decimal(x[3][1])) / 4 * height
    t_i_w = lambda x: (Decimal(x[3][0]) - Decimal(x[0][0]) + Decimal(x[2][0]) - Decimal(x[1][0])) / 2 * width
    t_i_h = lambda x: (Decimal(x[0][1]) - Decimal(x[1][1]) + Decimal(x[3][1]) - Decimal(x[2][1])) / 2 * height
    t_x = lambda x: Decimal(x[0]) / Decimal(width)
    t_y = lambda x: Decimal(x[1]) / Decimal(height)

    return [min(t_x(points[0]), t_x(points[1]), t_x(points[2]), t_x(points[3])),
            min(t_y(points[0]), t_y(points[1]), t_y(points[2]), t_y(points[3])),
            max(t_x(points[0]), t_x(points[1]), t_x(points[2]), t_x(points[3])),
            max(t_y(points[0]), t_y(points[1]), t_y(points[2]), t_y(points[3]))]


if __name__ == '__main__':

    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    list_json = os.listdir(labelme_dir)

    for cnt, json_name in enumerate(list_json):
        labelme_path = labelme_dir + json_name
        labelimg_path = labelimg_dir + json_name.replace('.json', '.txt')
        final_path = final_dir + json_name.replace('.json', '.txt')

        with open(labelme_path) as f:
            json_data = json.loads(f.read())

        data = []
        with open(labelimg_path) as f:
            for line in f.readlines():
                data.append(line.split())

        main_data = json_data["shapes"]
        rows = json_data["imageHeight"]
        cols = json_data["imageWidth"]
        for i in main_data:

            a = json2coordinates(i["points"])
            for j in data:
                print(j)
                label = j[0]
                j = j[1:]
                b = yolo2coordinates(j[0], j[1], j[2], j[3], cols, rows)
                c = calculate_IoU(a, b)
                print(i["points"])
                d = normalized(i["points"], rows, cols)
                if c > 0:
                    with open(final_path, 'w+') as f:
                        out_put = label
                        print(out_put)
                        for x in j:
                            out_put = out_put + f" {str(x)}"
                        for x in d:
                            out_put = out_put + f" {str(x)}"
                        print(out_put)
                        f.writelines(out_put + "\n")
                        # json2txt(labelme_path, labelimg_path, final_path)
                else:
                    print("No")
