from typing import List, Tuple
from shapely.geometry import Polygon


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


def xywh2two_coordinate(row, width, height) -> Tuple:
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


def xywh2four_coordinate(row: List, width: int, height: int) -> List[Tuple]:
    """

    :param row: <Label serial number> <x> <y> <w> <h>
    :param width: the width of the image
    :param height: the height of the image
    :return: List of four coordinates
    """
    x_min, y_min, x_max, y_max = xywh2two_coordinate(row, width, height)
    return [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_max),
        (x_max, y_min)
    ]


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


def normalized8point2coordinate4(points: List, width: int, height: int) -> List[Tuple]:
    """
    :param points: a list of eight points, specific numbers
    :param width: the width of the image
    :param height: the height of the image
    :return: four points have ordinary and normal coordinate composition
    """
    t_x = lambda x: x * width
    t_y = lambda x: x * height
    return [
        (t_x(points[0]), t_y(points[1])),
        (t_x(points[2]), t_y(points[3])),
        (t_x(points[4]), t_y(points[5])),
        (t_x(points[6]), t_y(points[7]))
    ]
