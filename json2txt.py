import os
import json
import numpy as np

from os import PathLike
from decimal import Decimal
from typing import Union, Tuple, List
from reverse import json2coordinates

label_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'BO', 'BS', 'R1', 'R2', 'R3', 'R4', 'R5', 'RO', 'RS']  # 标签列表
dir_json = 'data/label_me/'  # json文件列表
output_dir = 'data/label_final/'  # txt文件列表


def coordinates2normalized(points: List, rows, cols) -> List[Decimal]:
    t_x = lambda x: Decimal(x[0]) / Decimal(cols)
    t_y = lambda x: Decimal(x[1]) / Decimal(rows)
    return [t_x(points[0]), t_y(points[0]),
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


if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    list_json = os.listdir(dir_json)

    for cnt, json_name in enumerate(list_json):
        path_json = dir_json + json_name
        path_txt = output_dir + json_name.replace('.json', '.txt')
        json2txt(path_json, path_txt)
