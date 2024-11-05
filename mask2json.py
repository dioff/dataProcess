# -*- encoding: utf-8 -*-
'''
@File    :   mask2json.py
@Time    :   2024/11/05 16:37:58
@Author  :   Lewis
@Version :   1.0
@Contact :   lewis0808zy@gmail.com
@Desc    :   mask转json
'''



import os
import io
import json
import numpy as np
from pycococreatortools import pycococreatortools
from PIL import Image
import base64

def img_tobyte(img_pil):
    '''
    该函数用于将图像转化为base64字符类型
    :param img_pil: Image类型
    :return base64_string: 字符串
    '''
    ENCODING = 'utf-8'
    img_byte = io.BytesIO()
    img_pil.save(img_byte, format='PNG')
    binary_str2 = img_byte.getvalue()
    imageData = base64.b64encode(binary_str2)
    base64_string = imageData.decode(ENCODING)
    return base64_string

# 定义路径
ROOT_DIR = '/home/niubility/project/data' # 请输入你文件的根目录
Image_DIR = os.path.join(ROOT_DIR, "Image") # 目录底下包含图片
Label_DIR = os.path.join(ROOT_DIR, "GT") # 目录底下包含label文件
# 读取路径下的掩码
Label_files = os.listdir(Label_DIR)
# 指定png中index中对应的label
class_names = ['_background_', 'water'] # 分别表示label标注
for Label_filename in Label_files:
    # 创建一个json文件
    Json_output = {
        "version": "3.16.7",
        "flags": {},
        "fillColor": [255, 0, 0, 128],
        "lineColor": [0, 255, 0, 128],
        "imagePath": {},
        "shapes": [],
        "imageData": {}}
    print(Label_filename)
    name = Label_filename.split('.', 3)[0]
    name1 = name + '.tif'
    Json_output["imagePath"] = name1
    # 打开原图并将其转化为labelme json格式
    image = Image.open(Image_DIR + '/' + name1)
    imageData = img_tobyte(image)
    Json_output["imageData"] = imageData
    # 获得注释的掩码
    binary_mask = np.asarray(np.array(Image.open(Label_DIR + '/' + Label_filename))
                             ).astype(np.uint8)
    # 分别对掩码中的label结果绘制边界点
    for i in np.unique(binary_mask):
        if i != 0:
            temp_mask = np.where(binary_mask == i, 1, 0)

            # segmentation = pycococreatortools.binary_mask_to_polygon(temp_mask) # tolerancec参数控制无误差
            import cv2

            contours, _ = cv2.findContours(temp_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = [contour.reshape(-1).tolist() for contour in contours]  # 转换为适合的格式
            segmentation = contours

            
            for item in segmentation:
                if (len(item) > 10):
                    list1 = []
                    for j in range(0, len(item), 2):
                        list1.append([item[j], item[j + 1]])
                    label = class_names[i]  #
                    seg_info = {'points': list1, "fill_color": None, "line_color": None, "label": label,
                                "shape_type": "polygon", "flags": {}}
                    Json_output["shapes"].append(seg_info)
    Json_output["imageHeight"] = binary_mask.shape[0]
    Json_output["imageWidth"] = binary_mask.shape[1]
    # 保存在根目录下的json文件中
    full_path = '{}/json/' + name + '.json'
    with open(full_path.format(ROOT_DIR), 'w') as output_json_file:
        json.dump(Json_output, output_json_file)
