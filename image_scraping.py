import json
import numpy as np
from PIL import Image
from urllib import request
from io import BytesIO
import os

# length of data1 is 1,029,717
data1 = '../data/layer1.json'
data2 = '../data/layer2.json'

OUT_DIR = './img_data01'


# with open(data) as f:
#     layer1 = json.load(f)
#     count = 0
#     for item in layer1:
#         count += 1
#         print(count, item['title'])

# associated image based on a stanford paper 887536
# with open(data2) as f:
#     layer2 = json.load(f)
#     img_count = 0
#     # img_count += len(layer2['images'])
#     for item in layer2:
#         img_count += len(item['images'])
# print('length of layer2.json is', img_count)

error_img = []

# storage before downloading: 76,39 gb
with open(data2) as f:
    layer2 = json.load(f)
    # for recipe in layer2:
    for recipe in layer2:
        # if index == 5:
        #     break
        for images in recipe['images']:
            # id, url

            img_id = images['id']
            url = images['url']
            filename = os.path.join('./img_data01/{}'.format(img_id))

            try:
                response = request.urlopen(url)
                image_data = response.read()
            except:
                error_img.append(img_id)
                print('Warning broken link image: {} '.format(img_id))

            try:
                pil_image = Image.open(BytesIO(image_data))
            except:
                error_img.append(img_id)
                print('Warning: failed to parse image {}'.format(img_id))

            try:
                pil_image.convert('RGB')
            except:
                error_img.append(img_id)
                print('Warning: failed to convert image {}'.format(img_id))

            try:
                pil_image = pil_image.resize((256, 256))
            except:
                error_img.append(img_id)
                print('Warning: failed to resize image {}'.format(img_id))

            try:
                pil_image.save(filename, format='JPEG', quality=90) # not sure why 90
            except:
                error_img.append(img_id)
                print('Warning: failed to save image {}'.format(img_id))
            

# filter 1M recipes based on images associated 

f = open('error_img.txt', 'w')

for i in error_img:
    f.write(i + '\n')

f.close()