# label-match

This is a script that will match the labels of labelimg and labelme of the same image one by one and output them
together in another file.

## Run

### Prepare in advance

1. An empty folder to hold your output files
2. A folder full of labelme label datas


There are only one standard output format of labelme and you can get an
example [here](https://github.com/wkentaro/labelme/blob/main/examples/tutorial/apc2016_obj3.json).

3. A folder full of labelimg label datas

You can get further information [here](https://roboflow.com/formats/yolo-darknet-txt)

The label output format of labelimg is YOLO Darknet TXT, ex:

```
1 0.408 0.302 0.104 0.15
1 0.245 0.424 0.046 0.08
```

4. A file containing a list of labelimg labels

You should separate your labels with spaces

### 1.Poetry(recommend)

```shell
poetry run python3 label-match.py \
--labelme_dir <your_labelme_path> \
--labelimg_dir <your_labelimg_path> \
--output_dir <your_output_path> \
--classes_file <your_classes_path>
```

_*_: poetry will help you install dependencies when you first run it.

### 2.Pip3

Install environment first:

```shell
pip3 install -r requirements.txt
```

Then run it:

```shell
python3 label-match.py \
--labelme_dir <your_labelme_path> \
--labelimg_dir <your_labelimg_path> \
--output_dir <your_output_path> \
--classes_file <your_classes_path>
```

## Contribute

[commit message guidelines](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines)

### TODO lists

- [ ] Add test module
- [x] Add log module
- [x] Use external label lists
- [ ] better matching algorithm
- [ ] Add conversion options
- [x] Async I/O


