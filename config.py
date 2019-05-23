from easydict import EasyDict as edict

__C = edict()
cfg = __C

# External influence variables
__C.EXTERNAL = edict()
__C.EXTERNAL.PEAK_Y = 213
__C.EXTERNAL.SCREEN_W = 1080
__C.EXTERNAL.SCREEN_H = 720
__C.EXTERNAL.SPATIAL_ANGLE = 0.03
__C.EXTERNAL.SPATIAL_ENV = {'class1': 12,
                           'class2': 3,
                           'class3': 8,
                           'class4': 88,
                           'class5': 47}
__C.EXTERNAL.ENV_IMPACT = {'class1': 74,
                           'class2': 85,
                           'class3': 14}


# Internal influence variables
__C.INTERNAL = edict()
__C.INTERNAL.IMAGE_W = 1920
__C.INTERNAL.IMAGE_H = 1080
__C.INTERNAL.BLOCK_NUM = 9
__C.INTERNAL.UNCOMFORT_BLOCK_NUM = 3
__C.INTERNAL.FRAME_RANGE = 1
# threshold of difference between average luma of two blocks
__C.INTERNAL.LUMA_DIFF_THRESH = 10
__C.INTERNAL.CENTER_LUMA_DIFF_THRESH = 10

__C.INTERNAL.THRESH_B = 20

__C.INTERNAL.COLOR_UNCOMFORT_BLOCK_NUM = 3
__C.INTERNAL.COLOR_DIFF_THRESH = 2.5
__C.INTERNAL.CENTER_COLOR_DIFF_THRESH = 2.5

__C.INTERNAL.TOP_LUMA_THRESH = 10
__C.INTERNAL.CENTER_LUMA_THRESH = 10
__C.INTERNAL.BOTTOM_LUMA_THRESH = 10

__C.INTERNAL.TOP_COLOR_THRESH = 10
__C.INTERNAL.CENTER_COLOR_THRESH = 10
__C.INTERNAL.BOTTOM_COLOR_THRESH = 10








