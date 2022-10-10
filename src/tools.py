import os
import asyncio
import aiofiles
import cv2

from os import PathLike
from typing import Union, List

IGNORE_FILE = [".DS_Store", "classes.txt"]


def draw(img, x, y):
    for i in range(4):
        if i < 4:
            cv2.circle(img, (int(x[i]), int(y[i])), 3, (255, 255, 0), -1)
        else:
            cv2.circle(img, (int(x[i]), int(y[i])), 3, (0, 0, 255), -1)
    return img


async def read_classes(class_data: Union[str, PathLike, bytes]) -> List:
    label_list: List = []
    if isinstance(class_data, str):
        try:
            async with aiofiles.open(class_data) as f:
                for line in await f.readlines():
                    label_list.append(*line.split())
        except OSError as e:
            print("unable to open classes.txt")
            raise e
    return label_list


async def write_classes(class_data: Union[str, PathLike, bytes], data: List):
    if isinstance(class_data, str):
        try:
            async with aiofiles.open(class_data, "w") as f:  # cover write
                out = f"{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}"
                await f.write(out)
        except OSError as e:
            print("unable to open classes.txt")
            raise e
    return True


async def labelimg_order_correction(labelimg_path, classes_now, classes_right):
    label_now: List = await read_classes(classes_now)
    label_right: List = await read_classes(classes_right)
    list_labelimg = os.walk(labelimg_path)
    for path, dir_list, file_list in list_labelimg:
        for file_name in file_list:
            if file_name not in IGNORE_FILE:
                try:
                    print(file_name)
                    with open(os.path.join(path, file_name)) as f:
                        data = f.read().split()
                except FileNotFoundError as e:
                    print("The corresponding labelimg data is missing")
                    raise e
                finally:
                    sn = int(data[0])
                    try:
                        label_name_now = label_now[sn]
                    except IndexError:
                        print(f"{file_name}Wrong")
                        continue
                    right_sn = label_right.index(label_name_now)
                    a = int(file_name.split('.')[0])
                    if a > 2596:
                        data[0] = 7
                    elif a > 2508:
                        data[0] = 10
                    elif a > 2314:
                        data[0] = 5
                    else:
                        data[0] = 6
                    print(f"{file_name}原标签序号{sn}为标签{label_name_now},正确标签序号{right_sn}为标签{label_right[right_sn]}")
                    await write_classes(f"300/out/{file_name}", data)


if __name__ == '__main__':
    asyncio.run(
        labelimg_order_correction("300/labelimg/", "300/labelimg/classes.txt", "300/classes.txt")
    )
