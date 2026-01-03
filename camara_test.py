import cv2
print(cv2.__version__)
flip=2
cam= cv2.VideoCapture(1)
while True:
    ret, frame = cam.read()
    cv2.imshow('nanoCam',frame)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()