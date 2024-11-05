# -*- encoding: utf-8 -*-
'''
@File    :   showJson.py
@Time    :   2024/11/05 16:38:49
@Author  :   Lewis
@Version :   1.0
@Contact :   lewis0808zy@gmail.com
@Desc    :   在原图中显示json坐标
'''



import json
from PIL import Image, ImageDraw

# 读取原始图像
image = Image.open('/home/niubility/project/data/Image/GF2_PMS1__L1A0000564539-MSS1_3_7.tif')

# 读取JSON实例坐标文件
with open('/home/niubility/project/data/json/GF2_PMS1__L1A0000564539-MSS1_3_7.json') as f:
    instances = json.load(f)
# 在原始图像上绘制实例
draw = ImageDraw.Draw(image)
for i,instance in enumerate(instances['shapes']):
    coords = instance['points']
    # 为每个实例指定不同颜色
    color = (255 * (i%3), 255 * ((i+1)%3), 255 * ((i+2)%3))
    for x, y in coords:
        draw.ellipse((x-2, y-2, x+2, y+2), fill=color)

image.show()
image.save('result.tif')
