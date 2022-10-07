import os
import json
import argparse

from os import PathLike
from typing import Union, Tuple, List

import utils

label_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'BO', 'BS', 'R1', 'R2', 'R3', 'R4', 'R5', 'RO', 'RS']  # 标签列表


class ImgPoints:
    def __init__(self, img_data: Union[str, PathLike, bytes], width, height) -> None:
        self.width = width
        self.height = height
        self.points_origin = []
        self.points = []
        if isinstance(img_data, str):
            with open(img_data) as f:
                for line in f.readlines():
                    self.points_origin.append(line.split())
        for points in self.points_origin:
            self.points.append(utils.xywh2four_coordinate(points, width, height))


class MePoints:
    def __init__(self, me_data: Union[str, PathLike, bytes]) -> None:
        if isinstance(me_data, str):
            with open(me_data) as fp:
                points_data = json.loads(fp.read())
        self.height = points_data["imageHeight"]
        self.width = points_data["imageWidth"]
        self.points = points_data["shapes"]


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


def main(labelme_dir, labelimg_dir, final_dir) -> None:
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    list_labelme = os.listdir(labelme_dir)

    for cnt, json_name in enumerate(list_labelme):
        labelme_path = labelme_dir + json_name
        labelimg_path = labelimg_dir + json_name.replace('.json', '.txt')
        final_path = final_dir + json_name.replace('.json', '.txt')

        labelme_data = MePoints(labelme_path)
        labelimg_data = ImgPoints(labelimg_path, labelme_data.width, labelme_data.height)

        for me_point in labelme_data.points:
            num = 0
            for img_point in labelimg_data.points:
                area = utils.if_intersect(me_point["points"], img_point)
                if area > 0:
                    labelimg_data.points.remove(img_point)
                    label = label_list.index(me_point["label"])
                    output(label, labelimg_data.points_origin[num],
                           utils.normalized2coordinate4(me_point["points"], labelimg_data.width, labelme_data.height),
                           final_path)
                    num += 1
                    break
                else:
                    print("Wrong")
        del labelme_data
        del labelimg_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--labelme_dir', type=str, default='', help='Location of the original labelme json datasets')
    parser.add_argument('--labelimg_dir', type=str, default='', help='Location of the original labelimg txt datasets')
    parser.add_argument('--output_dir', type=str, default='', help='Output location of the changed txt dataset')
    args = parser.parse_args()
    try:
        main(args.labelme_dir, args.labelimg_dir, args.output_dir)
    finally:
        print("Finish")
