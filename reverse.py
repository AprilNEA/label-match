#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @time: 2022/9/28 4:34 PM

# 15 0.057813 0.280599 0.109375 0.110677
import cv2
from PIL import Image
from PIL import ImageDraw
from typing import Dict, List, Tuple
import json
from decimal import Decimal


def calculate_IoU(predicted_bound: Tuple[Decimal, Decimal, Decimal, Decimal],
                  ground_truth_bound: Tuple[Decimal, Decimal, Decimal, Decimal]) -> Decimal:
    """
    computing the IoU of two boxes.
    Args:
        :param predicted_bound: (x_min, y_min, x_max, y_max)
        :param ground_truth_bound: (x_min, y_min, x_max, y_max)
    Return:
        IoU: IoU of box1 and box2.

    """
    pxmin, pymin, pxmax, pymax = predicted_bound
    # print("预测框P的坐标是：({}, {}, {}, {})".format(pxmin, pymin, pxmax, pymax))
    gxmin, gymin, gxmax, gymax = ground_truth_bound
    # print("原标记框G的坐标是：({}, {}, {}, {})".format(gxmin, gymin, gxmax, gymax))

    parea = (pxmax - pxmin) * (pymax - pymin)  # 计算P的面积
    garea = (gxmax - gxmin) * (gymax - gymin)  # 计算G的面积
    # print("预测框P的面积是：{}；原标记框G的面积是：{}".format(parea, garea))

    # 求相交矩形的左下和右上顶点坐标(xmin, ymin, xmax, ymax)
    xmin = max(pxmin, gxmin)  # 得到左下顶点的横坐标
    ymin = max(pymin, gymin)  # 得到左下顶点的纵坐标
    xmax = min(pxmax, gxmax)  # 得到右上顶点的横坐标
    ymax = min(pymax, gymax)  # 得到右上顶点的纵坐标

    # 计算相交矩形的面积
    w = xmax - xmin
    h = ymax - ymin
    if w <= 0 or h <= 0:
        return 0

    area = w * h  # G∩P的面积
    # area = max(0, xmax - xmin) * max(0, ymax - ymin)  # 可以用一行代码算出来相交矩形的面积
    # print("G∩P的面积是：{}".format(area))

    # 并集的面积 = 两个矩形面积 - 交集面积
    IoU = area / (parea + garea - area)

    return IoU


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
    :return: x_min,y_min,x_max,y_max
    """
    real_x = Decimal(x) * Decimal(image_width)
    real_y = Decimal(y) * Decimal(image_height)
    real_width = Decimal(width_pro) * Decimal(image_width)
    real_height = Decimal(height_pro) * Decimal(image_height)

    real_width_half = Decimal(real_width) * Decimal('0.5')
    real_height_half = Decimal(real_height) * Decimal('0.5')

    coord_left = Decimal(real_x) - Decimal(real_width_half)
    coord_top = Decimal(real_y) + Decimal(real_height_half)
    coord_right = Decimal(real_x) + Decimal(real_width_half)
    coord_bottom = Decimal(real_y) - Decimal(real_height_half)
    return coord_left, coord_bottom, coord_right, coord_top


def json2coordinates(points: List) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
    point1: List = points[0]
    point2: List = points[1]
    point3: List = points[2]
    point4: List = points[3]
    x_min = (Decimal(point1[0]) + Decimal(point2[0])) * Decimal(0.5)
    x_max = (Decimal(point3[0]) + Decimal(point4[0])) * Decimal(0.5)
    y_min = (Decimal(point1[1]) + Decimal(point4[1])) * Decimal(0.5)
    y_max = (Decimal(point2[1]) + Decimal(point3[1])) * Decimal(0.5)
    return x_min, y_min, x_max, y_max


with open('2.json') as f:
    json_data = json.loads(f.read())

data = []
with open('2.txt') as f:
    for line in f.readlines():
        data.append(line.split()[1:])

main_data = json_data["shapes"]
for i in main_data:
    a = json2coordinates(i["points"])
    for j in data:
        b = yolo2coordinates(j[0], j[1], j[2], j[3], 1280, 768)
        print(calculate_IoU(a, b))
