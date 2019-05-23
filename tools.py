import cv2
import numpy as np
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def videoToImageset(video_path, image_set_path, interval):
    """This function is for generating frames from a video with specified time interval between two frames,
    saving generated frames to a certain directory.
    :param video_path: original video that needs to generate the image set
    :param image_set_path: the directory to save the set of images generated from the video
    :param interval: time interval between adjacent images (in seconds)
    :return: no return
    """
    cap = cv2.VideoCapture(video_path)
    # Frame per second
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Frame per interval
    fpi = int(round(fps * interval))
    if fpi == 0: fpi = 1

    success = True
    # Frame index
    f_idx = 0
    # Image index
    im_idx = 0
    while success == True:
        success, frame = cap.read()
        if f_idx % fpi == 0:
            im_idx += 1
            im_path = '%s\\%s.jpg' % (image_set_path, str(im_idx))
            cv2.imwrite(im_path, frame)
        f_idx += 1

def luminance(image, target_width, target_height):
    """
    Return image luminance with specific size.
    """
    # image = cv2.imread(image_path)
    if image is None:
        raise Exception('image is None, plesase check your image path.')
    image = cv2.resize(image, (target_width, target_height))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    luma = hsv[:, :, 2]

    return luma


def lumaDifference(luma1, luma2):
    """
    Return the difference between two luminance array
    """
    assert luma1.shape == luma2.shape
    luma_difference = luma1 - luma2

    return luma_difference

def averageLuma(luma, block_num):
    """
    Return an array of average luma with block size
    """
    assert (np.sqrt(block_num)).is_integer()
    width = int(np.sqrt(block_num))
    luma_block = np.zeros((width, width))
    block_w = int(luma.shape[1] / width)
    block_h = int(luma.shape[0] / width)
    for i in range(width):
        for j in range(width):
            block = luma[i*block_h : (i+1)*block_h, j*block_w : (j+1)*block_w]
            luma_block[i, j] = block.sum() / block.size
    return luma_block

def averageLuma3Block(luma, block_num):
    """
    Return an array of average luma with block size
    """
    luma_block = np.zeros(block_num)
    block_w = int(luma.shape[1])
    block_h = int(luma.shape[0] / block_num)

    for i in range(block_num):
            block = luma[i*block_h : (i+1)*block_h, :]
            luma_block[i] = block.sum() / block.size
    return luma_block

def uncomfortBlockNum(luma_block_diff, threshold):
    return np.sum((abs(luma_block_diff) > threshold))

def imEvalue(image1_path, image2_path, block_num, threshold,
             target_width, target_height):
    # read images
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    # compute pixel wise luminance of two images
    luma1 = luminance(image1, target_width, target_height)
    luma2 = luminance(image2, target_width, target_height)
    # # compute pixel wise luminance difference of two images
    # luma_diff = lumaDifference(luma1, luma2)
    # block_luma_diff = averageLuma(abs(luma_diff), block_num)
    # compute average luma in each block
    block_luma1 = averageLuma(luma1, block_num)
    block_luma2 = averageLuma(luma2, block_num)
    # compute difference between two images in each block
    block_luma_diff = lumaDifference(block_luma1, block_luma2)
    # compute the number of uncomfortable blocks of two images
    uncomfort_block_num = uncomfortBlockNum(block_luma_diff, threshold)
    return uncomfort_block_num, block_luma_diff


def videoEvalue(frame1, frame2, block_num, threshold,
             target_width, target_height):
    # compute pixel wise luminance of two images
    luma1 = luminance(frame1, target_width, target_height)
    luma2 = luminance(frame2, target_width, target_height)
    # # compute pixel wise luminance difference of two images
    # luma_diff = lumaDifference(luma1, luma2)
    # block_luma_diff = averageLuma(abs(luma_diff), block_num)
    # compute average luma in each block
    block_luma1 = averageLuma(luma1, block_num)
    block_luma2 = averageLuma(luma2, block_num)
    # compute difference between two images in each block
    block_luma_diff = lumaDifference(block_luma1, block_luma2)
    # compute the number of uncomfortable blocks of two images
    uncomfort_block_num = uncomfortBlockNum(block_luma_diff, threshold)
    return uncomfort_block_num, block_luma_diff


def videoColorEvalue(frame1, frame2, block_num, threshold):
    image1 = cv2.resize(frame1, (15, 15))
    image2 = cv2.resize(frame2, (15, 15))

    assert image1.shape == image2.shape

    delta_image = image1[:,:,0]

    # compute pixel wise CIE color difference between two images
    for i in range(image1.shape[0]):
        for j in range(image1.shape[1]):
            rgb_color1 = sRGBColor(image1[i, j, 2] / 255.0, image1[i, j, 1] / 255.0, image1[i, j, 0] / 255.0)
            lab_color1 = convert_color(rgb_color1, LabColor)
            rgb_color2 = sRGBColor(image2[i, j, 2] / 255.0, image2[i, j, 1] / 255.0, image2[i, j, 0] / 255.0)
            lab_color2 = convert_color(rgb_color2, LabColor)
            delta_image[i,j] = delta_e_cie2000(lab_color1, lab_color2)
    # compute average delta in each block
    block_delta = averageLuma(delta_image, block_num)
    # compute the number of uncomfortable blocks of two images
    uncomfort_block_num = uncomfortBlockNum(block_delta, threshold)
    return uncomfort_block_num, block_delta

def video3BlockEvalue(frame1, frame2, threshold_array, target_width, target_height):
    # return True if uncomfort
    # average luminance in every block
    block_num = 3
    luma1 = luminance(frame1, target_width, target_height)
    luma2 = luminance(frame2, target_width, target_height)
    block_luma1 = averageLuma3Block(luma1, block_num)
    block_luma2 = averageLuma3Block(luma2, block_num)
    block_luma_diff = lumaDifference(block_luma1, block_luma2)

    # average color delta in every block
    image1 = cv2.resize(frame1, (15, 15))
    image2 = cv2.resize(frame2, (15, 15))
    assert image1.shape == image2.shape
    delta_image = image1[:, :, 0]
    # compute pixel wise CIE color difference between two images
    for i in range(image1.shape[0]):
        for j in range(image1.shape[1]):
            rgb_color1 = sRGBColor(image1[i, j, 2] / 255.0, image1[i, j, 1] / 255.0, image1[i, j, 0] / 255.0)
            lab_color1 = convert_color(rgb_color1, LabColor)
            rgb_color2 = sRGBColor(image2[i, j, 2] / 255.0, image2[i, j, 1] / 255.0, image2[i, j, 0] / 255.0)
            lab_color2 = convert_color(rgb_color2, LabColor)
            delta_image[i, j] = delta_e_cie2000(lab_color1, lab_color2)

    block_color_diff = averageLuma3Block(delta_image, block_num)

    uncomfortBlockNum = np.sum(block_color_diff>threshold_array[3:]) + np.sum(block_luma_diff>threshold_array[:3])

    return uncomfortBlockNum, block_luma_diff, block_color_diff