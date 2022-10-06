import os
import json
import numpy as np
from pydantic import BaseModel
from os import PathLike
from decimal import Decimal
from typing import Union, Tuple, List

# from utils import json2coordinates, yolo2coordinates, calculate_IoU

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


def computeArea(predicted_bound: Tuple[Decimal, Decimal, Decimal, Decimal],
                ground_truth_bound: Tuple[Decimal, Decimal, Decimal, Decimal]) -> int:
    """
    computing the IoU of two boxes.
    Args:
        :param predicted_bound: (x_min, y_min, x_max, y_max)
        :param ground_truth_bound: (x_min, y_min, x_max, y_max)
    Return:
        IoU: IoU of box1 and box2.

    """
    ax1, ay1, ax2, ay2 = predicted_bound
    bx1, by1, bx2, by2 = ground_truth_bound
    area1 = (ax2 - ax1) * (ay2 - ay1)
    area2 = (bx2 - bx1) * (by2 - by1)
    overlapWidth = min(ax2, bx2) - max(ax1, bx1)
    overlapHeight = min(ay2, by2) - max(ay1, by1)
    overlapArea = max(overlapWidth, 0) * max(overlapHeight, 0)
    return area1 + area2 - overlapArea


class ImgPoints:
    def __init__(self, img_data: Union[str, PathLike, bytes], width, height):
        self.width = width
        self.height = height
        self.points_yolo = []
        self.count = -1
        self._label_number = len(self.points_yolo)
        if isinstance(img_data, str):
            with open(img_data) as f:
                for line in f.readlines():
                    self.points_yolo.append(line.split())
        self.points_coordinates = []

    def get_output(self) -> str:
        out = ""
        print(self.points_yolo)
        print(self.count)
        for x in self.points_yolo[self.count]:
            out = out + f" {x}"
        return out

    @staticmethod
    def yolo2coordinates(x: str, y: str, width_pro: str, height_pro: str,
                         image_width: int, image_height: int) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        yolo format too coordinates
        :param x: x coordinate relative to image size
        :param y: y coordinate relative to image size
        :param width_pro: targe proportion relative to image size
        :param height_pro: targe proportion relative to image size
        :param image_width: image real width
        :param image_height: image real height
        :return: x_min,y_min,x_max,y_max full coord
        """
        real_x = Decimal(x) * Decimal(image_width)
        real_y = Decimal(y) * Decimal(image_height)
        real_width = Decimal(width_pro) * Decimal(image_width)
        real_height = Decimal(height_pro) * Decimal(image_height)

        real_width_half = Decimal(real_width) * Decimal('0.5')
        real_height_half = Decimal(real_height) * Decimal('0.5')

        x_min = Decimal(real_x) - Decimal(real_width_half)
        y_min = Decimal(real_y) - Decimal(real_height_half)
        x_max = Decimal(real_x) + Decimal(real_width_half)
        y_max = Decimal(real_y) + Decimal(real_height_half)
        return x_min, y_min, x_max, y_max

    def data_conversion(self):
        for points in self.points_yolo:
            self.points_coordinates.append(self.yolo2coordinates(*points, self.width, self.height))


class MePoints:
    def __init__(self, me_data: Union[str, PathLike, bytes]):
        if isinstance(me_data, str):
            with open(me_data) as fp:
                points_data = json.loads(fp.read())
        self.height = points_data["imageHeight"]
        self.width = points_data["imageWidth"]
        self.points = points_data["shapes"]
        self.count = -1
        self._label_number = len(self.points)

    def get_output(self) -> str:
        out = ""
        for x in self.normalized(self.points[self.count]["points"], self.height, self.width):
            out = out + f" {x}"
        return out

    @staticmethod
    def json2coordinates(points: List) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        x_min = (Decimal(points[0][0]) + Decimal(points[1][0])) * Decimal(0.5)
        x_max = (Decimal(points[2][0]) + Decimal(points[3][0])) * Decimal(0.5)
        y_min = (Decimal(points[0][1]) + Decimal(points[3][1])) * Decimal(0.5)
        y_max = (Decimal(points[1][1]) + Decimal(points[2][1])) * Decimal(0.5)
        return x_min, y_min, x_max, y_max

    @staticmethod
    def normalized(points: List, height, width) -> List[Decimal]:
        """

        :param points:
        :param height:
        :param width:
        :return:
        """
        # t_m_x = lambda x: (Decimal(x[0][0]) + Decimal(x[1][0]) + Decimal(x[2][0]) + Decimal(x[3][0])) / (4 * width)
        # t_m_y = lambda x: (Decimal(x[0][1]) + Decimal(x[1][1]) + Decimal(x[2][1]) + Decimal(x[3][1])) / (4 * height)
        # t_i_w = lambda x: (Decimal(x[3][0]) - Decimal(x[0][0]) + Decimal(x[2][0]) - Decimal(x[1][0])) / (2 * width)
        # t_i_h = lambda x: (Decimal(x[1][1]) - Decimal(x[0][1]) + Decimal(x[3][1]) - Decimal(x[2][1])) / (2 * height)
        t_x = lambda x: Decimal(x[0]) / Decimal(width)
        t_y = lambda x: Decimal(x[1]) / Decimal(height)

        return [
            # t_m_x(points), t_m_y(points),
            #     t_i_w(points), t_i_h(points),
            t_x(points[0]), t_y(points[0]),
            t_x(points[1]), t_y(points[1]),
            t_x(points[2]), t_y(points[2]),
            t_x(points[3]), t_y(points[3])]


def main():
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    list_json = os.listdir(labelme_dir)

    for cnt, json_name in enumerate(list_json):
        labelme_path = labelme_dir + json_name
        labelimg_path = labelimg_dir + json_name.replace('.json', '.txt')
        final_path = final_dir + json_name.replace('.json', '.txt')

        labelme_data = MePoints(labelme_path)
        labelimg_data = ImgPoints(labelimg_path, labelme_data.width, labelme_data.width)

        for me_point in labelme_data.points:
            labelme_data.count = labelme_data.count + 1
            for img_point in labelimg_data.points_yolo:
                labelimg_data.count = labelimg_data.count + 1
                a = labelme_data.json2coordinates(me_point["points"])
                b = labelimg_data.yolo2coordinates(*img_point[1:], labelimg_data.width, labelimg_data.height)
                calculate_result = computeArea(a, b)
                if calculate_result > 0:
                    # print("Yes")
                    label = label_list.index(me_point["label"])
                    out1 = ""
                    out2 = ""
                    for x in img_point[1:]:
                        out1 = out1 + f" {x}"
                    for x in labelme_data.normalized(me_point["points"], labelimg_data.height, labelimg_data.width):
                        out2 = out2 + f" {x}"
                    out = str(label) + out1 + out2
                    with open(final_path, 'w+') as f:
                        f.writelines(out + "\n")
                else:
                    print("No")


if __name__ == '__main__':
    main()
