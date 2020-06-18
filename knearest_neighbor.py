# -*- coding: utf-8 -*-
"""knearest_neighbor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12v8ep_PksAOXEBztXfF9oQlHqhegP0dt
"""

from google.colab import auth
auth.authenticate_user()
project_id = 'colab-bucket'
!gcloud config set project {project_id}

!  curl https://storage.googleapis.com/gcping-release/gcping_linux_amd64_0.0.3 > gcping && chmod +x gcping
! ./gcping

# to mount gcs to colab (THIS SAVED MY LIFE DAMNNNNNNNN)
!echo "deb http://packages.cloud.google.com/apt gcsfuse-bionic main" > /etc/apt/sources.list.d/gcsfuse.list
!curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
!apt -qq update
!apt -qq install gcsfuse

# mount the folder
bucket_name = 'colab-bucket-recipe1m-train-2'
!mkdir gcstorage
!gcsfuse --implicit-dirs --limit-bytes-per-sec -1 --limit-ops-per-sec -1 {bucket_name} /content/gcstorage/

import keras
from keras.preprocessing import image
from keras.models import Model, load_model
from keras.applications.imagenet_utils import preprocess_input as preprocess_input_vgg

import os
from tqdm import tqdm

import random
import numpy as np
import pandas as pd
import _pickle as pickle
from pprint import pprint

import tables

model = keras.applications.VGG16(weights='imagenet', include_top=True)
feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)

# load dataset features and name
hdf5_path = '/content/gcstorage/vgg16_bottleneck_features7.hdf5'
hdf5_file_temp = tables.open_file(hdf5_path, mode='r')
features = hdf5_file_temp.root.img_features
images = hdf5_file_temp.root.img_paths

# load saved approximate nearest neighbor 
!pip install annoy
from annoy import AnnoyIndex

t = AnnoyIndex(4096)
t.load('/content/gcstorage/annoy_ann/test2_all.ann')

# load json image_id to recipe
img_to_recipe = pd.read_csv('/content/gcstorage/layers/img_to_recipe.csv')
recipe_id_to_recipe = pd.read_csv('/content/gcstorage/layers/layer1m.csv')

def get_image_vgg(path):
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input_vgg(x)
    return img, x
  

# nearest neighbor
def get_closest_images_fast_annoy(query_features, num_results=6):
    return t.get_nns_by_vector(query_features, num_results)

clean_image_id = np.load('/content/gcstorage/clean_images_id.npy')

# INPUT IMAGE HERE
query_image, x = get_image_vgg('/content/20180625-no-churn-vanilla-ice-cream-vicky-wasik-13-1500x1125.jpg');
query_features = feat_extractor.predict(x)[0]

idx_closest = get_closest_images_fast_annoy(query_features, 3)

results = []

# print(idx_closest)

for i in idx_closest:
  results.append(clean_image_id[i])

print(results)

import json

test = img_to_recipe[img_to_recipe['image_id'].isin(results)]['recipe_id'].values
# print(test)
recipes = recipe_id_to_recipe[recipe_id_to_recipe['id'].isin(test)]

recipe_title = recipes['url'].values
recipes_title = recipes['title'].values
recipes_ingredients = recipes['ingredients'].values.tolist()
recipes_instructions = recipes['instructions'].values

for i in recipe_title:
  print(i)

# for recipe in recipes:
#   recipe = recipe.replace('"', ' minutes')
#   recipe = recipe.replace("'",'"')
#   cleaned_recipe = json.loads(recipe)

#   for v in cleaned_recipe:
#     print(v['text'])
#   print("")

