import asyncio
import os
import json
import argparse

import aiofiles
from os import PathLike
from typing import Union, List

from src import utils


class Points:

    def __init__(self, me_data: Union[str, PathLike, bytes], img_data: Union[str, PathLike, bytes]) -> None:
        self.path = me_data
        self.height: int
        self.width: int
        self.me_points: List
        self.img_points_origin: List = []
        self.img_points: List = []
        if isinstance(me_data, str):
            try:
                with open(me_data) as fp:
                    points_data = json.loads(fp.read())
            except FileNotFoundError as e:
                print("No labelme data")
                raise e
            except json.decoder.JSONDecodeError as e:
                print(f"{me_data}出现错误")
                raise e
            except UnicodeDecodeError as e:
                print(f"{me_data}出现编码错误")
                raise e
            finally:
                self.height = points_data["imageHeight"]
                self.width = points_data["imageWidth"]
                self.me_points = points_data["shapes"]
        if isinstance(img_data, str):
            try:
                with open(img_data) as f:
                    for line in f.readlines():
                        self.img_points_origin.append(line.split())
            except FileNotFoundError as e:
                print(f"{img_data}The corresponding labelimg data is missing")
                raise e
        for points in self.img_points_origin:
            self.img_points.append(utils.xywh2four_coordinate(points, self.width, self.height))

    def get_correspond(self, t_data: List) -> List:
        """
        for the label data of labelimg, find the correct serial number in origin list.
        :param t_data:
        :return:
        """
        sn: int = self.img_points.index(t_data)
        return self.img_points_origin[sn]


async def read_classes(class_data: Union[str, PathLike, bytes]):
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


async def output(label: int, img_point: List, me_point: List, final_path) -> None:
    out1 = ""
    out2 = ""
    for x in img_point[1:]:
        out1 = out1 + f" {x}"
    for x in me_point:
        out2 = out2 + f" {x}"
    out = str(label) + out1 + out2
    async with aiofiles.open(final_path, 'at') as f:
        await f.writelines(out + "\n")
    del out1, out2


async def points_callback(label_data: Points, label_list, final_path):
    for me_point in label_data.me_points:
        for img_point in label_data.img_points:
            area = utils.if_intersect(me_point["points"], img_point)
            if area > 0:
                label = label_list.index(me_point["label"])
                await output(label, label_data.get_correspond(img_point),
                             utils.coordinate2normalized4(me_point["points"], label_data.width,
                                                          label_data.height), final_path)
                print(f"Match success.{label_data.path}")
                break
            else:
                print(f"Match error.{label_data.path}")


async def main(labelme_dir, labelimg_dir, final_dir, classes_path) -> None:
    label_list = await read_classes(classes_path)
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    list_labelme = os.listdir(labelme_dir)

    for cnt, json_name in enumerate(list_labelme):
        labelme_path = labelme_dir + json_name
        if ".json" not in json_name:
            continue
        labelimg_path = labelimg_dir + json_name.replace('.json', '.txt')
        final_path = final_dir + json_name.replace('.json', '.txt')
        label_data = Points(labelme_path, labelimg_path)
        await points_callback(label_data, label_list, final_path)
        del label_data
    await asyncio.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--labelme_dir', type=str, default='', help='Location of the original labelme json datasets')
    parser.add_argument('--labelimg_dir', type=str, default='', help='Location of the original labelimg txt datasets')
    parser.add_argument('--output_dir', type=str, default='', help='Output location of the changed txt dataset')
    parser.add_argument('--classes_file', type=str, default='', help='Path to the file where the list of tags is saved')
    args = parser.parse_args()
    try:
        asyncio.run(
            main(args.labelme_dir, args.labelimg_dir, args.output_dir, args.classes_file)
        )
    except OSError as e:
        print("Some thing wrong with OS system,maybe your path or file have something wrong.")
        print("Check your file and path.The programme will be exited.")
        exit()
    except RuntimeWarning as e:
        print("Some thing wrong with Coroutine system.")
        print("Please make a issue in Github with your ERROR code.")
        raise e
    finally:
        print("Finish")
