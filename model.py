#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Neural Style Transfer Model
'''



__author__ = 'Sneh Sagar'
__copyright__ = None
__credits__ = ['Sneh Sagar']
__license__ = 'GPL'
__version__ = '1.0.1'
__email__ = 'snehsagarajput@gmail.com'
__status__ = 'Production'




import PIL
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np


def load_img(path_to_img, DEBUG_PRINT=False):
    max_dim = 512
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    if DEBUG_PRINT:
        print('Loading Image from ' + path_to_img + ' Success')
    return img


def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return tensor  # PIL.Image.fromarray(tensor)


def model(hub_module, content_path, style_path, DEBUG_PRINT=False):
    content_image = load_img(content_path, DEBUG_PRINT)
    style_image = load_img(style_path, DEBUG_PRINT)
    stylized_image = hub_module(tf.constant(content_image),
                                tf.constant(style_image))[0]
    image = tf.squeeze(stylized_image, axis=0)
    if DEBUG_PRINT:
        print('Image Stylized......... :)')
    return PIL.Image.fromarray(tensor_to_image(image), 'RGB')



			
