import cv2
from main import Utils
from tensorflow.keras.models import load_model
import os
import time 
import speech_recognition as sr 
from gtts import gTTS
from pygame import mixer
from datetime import datetime
import requests
import RPi.GPIO as GPIO

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN)

def nothing(x):
    pass

path_proto = 'deploy.prototxt.txt'
path_model = 'res10_300x300_ssd_iter_140000.caffemodel'
net = cv2.dnn.readNetFromCaffe(path_proto, path_model)
u = Utils()

#-----------------------#
cap = cv2.VideoCapture(0)
faces_li = os.listdir('faces')
faces = [i[:-4] for i in faces_li]
model = load_model("facenet_keras.h5")
#--------------------------dummy----------------------------------#
image = cv2.imread("bean.jpg")
boxes = u.detect_face_dnn(net, image, con=0.5)
box = boxes[0]
x, y, w, h = box[0], box[1], box[2], box[3]
tup_box = (x, y, w, h)
cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
face = u.return_face(image, tup_box)
real_emd = u.face_embedding(model, face)
#-----------------------------------------------------------------#

knowns = {}
for i,person in enumerate(faces_li):
    img = cv2.imread('faces/{}'.format(person))
    #print('faces/{}'.format(person))
    bx = u.detect_face_dnn(net, img)[0]
    roi = u.return_face(img, bx)
    emd = u.face_embedding(model, roi)
    knowns[faces[i]] = emd
print("-----------------------", knowns)
#-------------------------------------------#

# cv2.namedWindow('Digital Switch')
# cv2.createTrackbar("switch_state","Digital Switch",0,1,nothing)
known_people = len(knowns)
print("READYYYYY!")
count=0
while True:
    #state = cv2.getTrackbarPos("switch_state","Digital Switch")
    #print(state)
    if GPIO.input(10) == GPIO.HIGH:
        _, frame = cap.read()
        cv2.imwrite("temp.jpg",frame)
        try:
            box = u.detect_face_dnn(net,frame)[0]
        except:
            continue
        x, y, w, h = box[0], box[1], box[2], box[3]
        tup_box = (x, y, w, h)
        roi = u.return_face(frame,tup_box)
        real_emd = u.face_embedding(model,roi)
        c=0
        person_name = ""
        for name, emd in knowns.items():
            val = u.compare_embeddings(emd, real_emd)
            if val<12:
                person_name=name
                break
            else:
                c+=1
            if c==known_people:
                person_name ="Unknown"

        if person_name=="Unknown":
            first_speech = "Hello Stranger!What is your name?"
            u.speak(first_speech)
            time.sleep(7)
            text1 = None
            while not text1:
                text1= u.speech_text()
            print(text1)
            person_name+="("+text1[10:]+")"
            time.sleep(12)
            u.speak("Do you have any message for Mr Iftekher?Please mention the message I will send it to my owner!")
            text2 = None
            while not text2:
                text2= u.speech_text()
            d = datetime.now()
            d_str = d.strftime("%d/%m/%Y %H:%M:%S")
        else:
            first_speech = "Hello {}!How are you?Do you have any message for Mr Iftekher?Please mention the message I will send it to my owner!".format(person_name)
            u.speak(first_speech)
            time.sleep(12)
            text1 = None
            while not text1:
                text1= u.speech_text()
            d = datetime.now()
            d_str = d.strftime("%d/%m/%Y %H:%M:%S")
            u.post(person_name,text1,d_str)
    else:
        print(count)
        if GPIO.input(11) == GPIO.LOW:
            u.post_fire("Fire!Fire!Fire! CALL FIRE BRIGADE ASAP!")
            count =0
        else:
            count+=1
        if count==10000:
            u.post_fire("You Are Safe Now")
            count=0
 
    if cv2.waitKey(1) & 0xff==ord('q'):
        break  