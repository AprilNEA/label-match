import os
import json
import numpy as np

from os import PathLike
from decimal import Decimal
from typing import Union, Tuple, List
from reverse import json2coordinates

label_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'BO', 'BS', 'R1', 'R2', 'R3', 'R4', 'R5', 'RO', 'RS']  # 标签列表
dir_json = 'data/label_json/'  # json文件列表
output_dir = 'data/label_final/'  # txt文件列表


def coordinates2normalized(points: List, height, width) -> List[Decimal]:
    t_m_x = lambda x: (Decimal(x[0][0]) + Decimal(x[1][0]) + Decimal(x[2][0]) + Decimal(x[3][0])) / 4 * width
    t_m_y = lambda x: (Decimal(x[0][1]) + Decimal(x[1][1]) + Decimal(x[2][1]) + Decimal(x[3][1])) / 4 * height
    t_i_w = lambda x: (Decimal(x[3][0]) - Decimal(x[0][0]) + Decimal(x[2][0]) - Decimal(x[1][0])) / 2 * width
    t_i_h = lambda x: (Decimal(x[0][1]) - Decimal(x[1][1]) + Decimal(x[3][1]) - Decimal(x[2][1])) / 2 * height
    t_x = lambda x: Decimal(x[0]) / Decimal(width)
    t_y = lambda x: Decimal(x[1]) / Decimal(height)

    return [t_m_x(points), t_m_y(points),
            t_i_w(points), t_i_h(points),
            t_x(points[0]), t_y(points[0]),
            t_x(points[1]), t_y(points[1]),
            t_x(points[2]), t_y(points[2]),
            t_x(points[3]), t_y(points[3])]


def json2txt(json_path: Union[str, PathLike], txt_path: Union[str, PathLike]):
    with open(json_path) as f:
        json_data = json.load(f)
    points_list = json_data["shapes"]
    rows = json_data["imageHeight"]
    cols = json_data["imageWidth"]

    with open(txt_path, 'w+') as f:
        for point in points_list:
            label = str(label_list.index(point["label"]))
            f.writelines(label)
            out: List = coordinates2normalized(point["points"], rows, cols)
            out_str = ''.join(f" {x}" for x in out)
            f.writelines(out_str + "\n")


# 第0位: 装甲板的类别<br>
# 第1-4位: 装甲板标注锚框,用于目标检测。四个数的顺序是x,y,w,h，其中x,y,是锚框中心点的归一化坐标，w,h 是归一化相对宽高。<br>
# 第5-12位: 装甲板灯条的边界点，从前到后分别是:<br>
# * 左上角归一化坐标x1,y1<br>
# * 左下角归一化坐标x2,y2<br>
# * 右下角归一化坐标x3,y3<br>
# * 右上角归一化坐标x4,y4<br>

if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    list_json = os.listdir(dir_json)

    for cnt, json_name in enumerate(list_json):
        path_json = dir_json + json_name
        path_txt = output_dir + json_name.replace('.json', '.txt')
        json2txt(path_json, path_txt)
