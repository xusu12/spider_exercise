#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image, ImageOps
import cv2
import time
import os, sys
sys.path.append("../")
from io import BytesIO
from captcha_crack.setting import background_path, VERIFY_PATH
sys.path.append(background_path)
from captcha_crack.training.train_knn import crack_captcha


def matrix_to_img(matrix):
    new_data = np.reshape(matrix, (len(matrix), len(matrix[0])))
    new_im = Image.fromarray(new_data.astype(np.uint8))
    return new_im


def cut_edge(data, im):
    start = time.time()
    transpose_data = data.T
    w, h = len(transpose_data), len(data)

    for x_coordinates, data_x_axis in enumerate(transpose_data):
        x_coordinates_data = min(data_x_axis)
        if x_coordinates_data < 50:
            left_position = x_coordinates
            break

    for nx_coordinates, data_nx_axis in enumerate(transpose_data[::-1]):
        nx_coordinates_data = min(data_nx_axis)
        if nx_coordinates_data < 50:
            right_position = w-nx_coordinates
            break

    for y_coordinates, data_y_axis in enumerate(data):
        y_coordinates_data = min(data_y_axis)
        if y_coordinates_data < 50:
            upper_position = y_coordinates
            break

    for ny_coordinates, data_ny_axis in enumerate(data[::-1]):
        ny_coordinates_data = min(data_ny_axis)
        if ny_coordinates_data < 50:
            lower_position = h-ny_coordinates
            break

    box = (left_position, upper_position, right_position, lower_position)
    region = im.crop(box)
    data = data[upper_position:lower_position, left_position:right_position]
    print(time.time() - start)
    return data, region


def check(data):
    point_count = []
    h = len(data)
    transpose_data = data.T
    quota = (h-2)*255
    temp = 0
    for x_coordinates, data_x_axis in enumerate(transpose_data):
        if sum(data_x_axis) >= quota and (x_coordinates-temp > 16 or x_coordinates-temp < 4):
                point_count.append(x_coordinates)
                temp = x_coordinates

    temp = 0
    for i in range(len(point_count)):
        if i:

            quota_data = point_count[i - temp] - point_count[i - temp - 1]
            if 0 < quota_data < 13:
                point_count.pop(i-temp-1)
                temp += 1

    if 0 in point_count:
        point_count.remove(0)
    return point_count


def cut_char(im, data):
    record = check(data)
    w = len(data.T)
    h = len(data)
    record.sort()
    a = 0

    results = []
    for i, n in enumerate(record):
        x = im.crop((a, 0, n, h))
        NpKernel = np.uint8(np.ones((2, 2)))
        erode = cv2.erode(to_matrix(x), NpKernel)
        opened = cv2.morphologyEx(erode, cv2.MORPH_OPEN, NpKernel)
        ret, opened_img = cv2.threshold(opened, 100, 255, cv2.THRESH_BINARY_INV)
        ag = get_angle(opened_img)
        x = matrix_to_img(opened)
        x = ImageOps.invert(x).rotate(ag, expand=1).crop((0, 0, 45, 45))
        x = ImageOps.invert(x)
        count_list = list(x.getdata())
        black_count = len([n for n in count_list if not n])
        if black_count > 90:
            result = crack_captcha(to_matrix(x))
            results.append(result)
        a = n

    if a and w-a > 13:
        x = im.crop((a, 0, w, h))
        NpKernel = np.uint8(np.ones((2, 2)))
        erode = cv2.erode(to_matrix(x), NpKernel)
        opened = cv2.morphologyEx(erode, cv2.MORPH_OPEN, NpKernel)
        ret, opened_img = cv2.threshold(opened, 100, 255, cv2.THRESH_BINARY_INV)
        ag = get_angle(opened_img)
        x = matrix_to_img(opened)
        x = ImageOps.invert(x).rotate(ag, expand=1).crop((0, 0, 45, 45))
        x = ImageOps.invert(x)
        result = crack_captcha(to_matrix(x))
        results.append(result)
    return results


def get_angle(img):
    blank = cv2.imread(background_path + '/background.jpg', 0)
    rows, cols = img.shape
    n = 60
    blank[n:n + rows, n:n + cols] = img
    ret, thresh = cv2.threshold(blank, 127, 255, 0)
    im1, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    _, (width, hiegth), angle = cv2.minAreaRect(cnt)

    if 9 < min(width, hiegth) < 25:
        if width > hiegth and angle < 0:
            angle += 90
        elif width > hiegth and angle > 0:
            angle -= 90
    else:
        if angle < -45:
            angle += 90
        elif angle > 45:
            angle -= 90

    return angle


def to_matrix(img_data):
    width, height = img_data.size
    data = list(img_data.getdata())
    np_kernel = np.uint8(np.zeros((height, width)))
    for h in range(height):
        np_kernel[h] = data[h * width: (h + 1) * width]
    return np_kernel


def main(filename):
    bytes_string = BytesIO(filename)
    img = to_matrix(Image.open(bytes_string))
    ret, img = cv2.threshold(img, 60, 255, cv2.THRESH_BINARY)
    im = matrix_to_img(img)
    matrix_cut, new_im_cut = cut_edge(img, im)
    results = cut_char(new_im_cut, matrix_cut,)
    return results

if __name__ == '__main__':
    with open(os.path.dirname(__file__) + '/test_captcha/Captcha_52.jpg','rb') as f:
        c = f.read()
    print(c)
    results = main(c)
    print(results)
    pass
