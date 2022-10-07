# label-match

This is a script that will match the labels of labelimg and labelme of the same image one by one and output them
together in another file.

The label output format of labelimg is YOLO Darknet TXT, ex:

```
1 0.408 0.30266666666666664 0.104 0.15733333333333333
1 0.245 0.424 0.046 0.08
```

You can get further information [here](https://roboflow.com/formats/yolo-darknet-txt)

There are only one standard output format of labelme and you can get an
example [here](https://github.com/wkentaro/labelme/blob/main/examples/tutorial/apc2016_obj3.json).

## Run

### 1.Poetry(recommend)

```shell
poetry run python3 label-match.py \
--labelme_dir <your_labelme_path>
--labelimg_dir <your_labelimg_path>
--output_dir <your_output_path>
```

*: poetry will help you install dependencies when you first run it.

### 2.Pip3

Install environment first:

```shell
pip3 install -r requirements.txt
```

Then run it:

```shell
python3 label-match.py \
--labelme_dir <your_labelme_path>
--labelimg_dir <your_labelimg_path>
--output_dir <your_output_path>
```
