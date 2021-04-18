import cv2
from main import Utils
from tensorflow.keras.models import load_model
import os
import time 

path_proto = 'deploy.prototxt.txt'
path_model = 'res10_300x300_ssd_iter_140000.caffemodel'
net = cv2.dnn.readNetFromCaffe(path_proto, path_model)

f = Utils()
cap = cv2.VideoCapture(0)
faces_li = os.listdir('faces')
faces = [i[:-4] for i in faces_li]
model = load_model("facenet_keras.h5")
#--------------------------dummy----------------------------------#
image = cv2.imread("bean.jpg")
boxes = f.detect_face_dnn(net, image, con=0.5)
box = boxes[0]
x, y, w, h = box[0], box[1], box[2], box[3]
tup_box = (x, y, w, h)
cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
face = f.return_face(image, tup_box)
real_emd = f.face_embedding(model, face)
#-----------------------------------------------------------------#

knowns = {}
for i,person in enumerate(faces_li):
    img = cv2.imread('faces/{}'.format(person))
    #print('faces/{}'.format(person))
    bx = f.detect_face_dnn(net, img)[0]
    roi = f.return_face(img, bx)
    emd = f.face_embedding(model, roi)
    knowns[faces[i]] = emd
    
print("-----------------------", knowns)


while True:
    _, frame = cap.read()
    boxes = f.detect_face_dnn(net, frame)
    for box in boxes:
        x, y, w, h = box[0], box[1], box[2], box[3]
        tup_box = (x, y, w, h)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        for person, embedding in knowns.items():
            print(person)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break