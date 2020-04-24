import cv2
import os, sys
sys.path.append("../")
sys.path.append("../../")
from captcha_crack.setting import knn_data_path
sys.path.append(os.path.dirname(__file__).split('/')[:-1])
import numpy as np


def width_and_height(data):
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
            right_position = w - nx_coordinates
            break

    for y_coordinates, data_y_axis in enumerate(data):
        y_coordinates_data = min(data_y_axis)
        if y_coordinates_data < 50:
            upper_position = y_coordinates
            break

    for ny_coordinates, data_ny_axis in enumerate(data[::-1]):
        ny_coordinates_data = min(data_ny_axis)
        if ny_coordinates_data < 50:
            lower_position = h - ny_coordinates
            break

    width = abs(left_position - right_position)
    height = abs(upper_position - lower_position)
    return width, height


def x_y_list(data):
    transpose_data = data.T
    x_list, y_list = [], []

    for data_x_axis in transpose_data:
        x_pixels = (45*255 - sum(data_x_axis))/255
        x_list.append(x_pixels)

    for data_y_axis in data:
        y_pixels = (45 * 255 - sum(data_y_axis)) / 255
        y_list.append(y_pixels)

    pixels = sum(x_list)
    pixels_scale = pixels*100/(45**2)
    return pixels, pixels_scale, x_list, y_list


def create_train_labels(dir):
    train_labels = np.zeros((len(dir), 1)).astype(np.float32)
    for i, filename in enumerate(dir):
        ch = filename.split('.')[0].split(' ')[0]
        one_label = ord(ch)-ord('A')
        train_labels[i] = one_label
    return train_labels


def crack_captcha(img):
    identify_list = []
    w, h = width_and_height(img)
    pixels, pixels_scale, x_list, y_list = x_y_list(img)
    identify_list.extend([w, h, pixels, pixels_scale])
    identify_list.extend(x_list)
    identify_list.extend(y_list)
    identify_list = np.array(identify_list).astype(np.float32)
    identify_array = np.zeros((1, 94)).astype(np.float32)
    identify_array[0] = np.array(identify_list).astype(np.float32)
    with np.load(knn_data_path + '/knn_data.npz') as data:
        train = data['train']
        train_labels = data['train_labels']
    knn = cv2.ml.KNearest_create()
    knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)
    ret, results, neighbours, dist = knn.findNearest(identify_array, 3)
    return chr(int(results[0][0])+ord('A'))


def demo(filename):
    identify_list = []

    img = cv2.imread(filename, 0)
    w, h = width_and_height(img)
    pixels, pixels_scale, x_list, y_list = x_y_list(img)
    identify_list.extend([w, h, pixels, pixels_scale])
    identify_list.extend(x_list)
    identify_list.extend(y_list)
    identify_list = np.array(identify_list).astype(np.float32)
    test_array = np.zeros((1, 94)).astype(np.float32)
    test_array[0] = np.array(identify_list).astype(np.float32)
    return test_array


if __name__ == '__main__':
    pass
    # demo('')
    # file_list = os.listdir('C:/Users/Guihua/Desktop/deA/conf/string/test_char')
    # m = len(file_list)
    # print(m)
    # train_labels = create_train_labels(file_list)
    # print(train_labels)
    # trainingMat = np.zeros((m, 94)).astype(np.float32)
    # for i, n in enumerate(file_list):
    #     identify_list = []
    #     pic_file = 'string/test_char/' + n
    #     img = cv2.imread(pic_file, 0)
    #     w, h = width_and_height(img)
    #     pixels, pixels_scale, x_list, y_list = x_y_list(img)
    #     identify_list.extend([w, h, pixels, pixels_scale])
    #     identify_list.extend(x_list)
    #     identify_list.extend(y_list)
    #     identify_list = np.array(identify_list).astype(np.float32)
    #     trainingMat[i] = identify_list
    #     print(identify_list)
    #
    # np.savez('knn_data.npz', train=trainingMat, train_labels=train_labels)
    # with np.load('knn_data.npz') as data:
    #     train = data['train']
    #     train_labels = data['train_labels']
    # # for n in train_labels:
    # #     print(n)
    # filename = 'string/test_char/435.tif'
    # x = demo(filename)
    # knn = cv2.ml.KNearest_create()
    # knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)
    # # print(knn)
    # ret, results, neighbours, dist = knn.findNearest(x, 3)
    # result = chr(int(results[0][0])+ord('A'))
    # print("result: ", chr(int(results[0][0])+ord('A')), "\n")
    # print("neighbours: ", neighbours, "\n")
    # print("distance: ", dist)

