from typing import List
from shapely.geometry import Polygon


def if_intersect(data1, data2):
    """
    任意两个图形的相交面积的计算
    :param data1: 当前物体
    :param data2: 待比较的物体
    :return: 当前物体与待比较的物体的面积交集
    """

    poly1 = Polygon(data1).convex_hull  # Polygon：多边形对象
    poly2 = Polygon(data2).convex_hull

    if not poly1.intersects(poly2):
        inter_area = 0  # 如果两四边形不相交
    else:
        inter_area = poly1.intersection(poly2).area  # 相交面积
    return inter_area


def xywh2two_coordinate(row, width, height):
    print(width,height)
    len = 0
    for r in row:
        row[len] = float(r)
        len += 1
    print(row)
    x_min = min(max(0.0, row[1] - row[3] / 2), 1.0) * width
    y_min = min(max(0.0, row[2] - row[4] / 2), 1.0) * height
    x_max = min(max(0.0, row[1] + row[3] / 2), 1.0) * width
    y_max = min(max(0.0, row[2] + row[4] / 2), 1.0) * height
    return x_min, y_min, x_max, y_max


def xywh2four_coordinate(row, width, height):
    x_min, y_min, x_max, y_max = xywh2two_coordinate(row, width, height)
    return [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_max),
        (x_max, y_min)
    ]


def normalized2coordinate4(points: List, width, height) -> List:
    t_x = lambda x: x[0] / width
    t_y = lambda x: x[1] / height
    return [t_x(points[0]), t_y(points[0]),
            t_x(points[1]), t_y(points[1]),
            t_x(points[2]), t_y(points[2]),
            t_x(points[3]), t_y(points[3])]
