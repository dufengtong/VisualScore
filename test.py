import cv2

cap = cv2.VideoCapture('D:\dft\program\VisualScore\data\\videos\\video.mp4')

ret = True
# idx = 1409
# while ret == True:
# cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, idx-1)
# ret, frame = cap.read()
# im_path = 'test1\\%s.jpg' % (str(idx-1))
# cv2.imwrite(im_path, frame)
# ret, frame = cap.read()
# im_path = 'test1\\%s.jpg' % (str(idx))
# cv2.imwrite(im_path, frame)
# idx+=1

idx = 1408
while ret == True:
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    im_path = 'test1\\%s.jpg' % (str(idx))
    cv2.imwrite(im_path, frame)
    idx+=1


