import cv2
import numpy as np 
import tensorflow as tf 
import speech_recognition as sr 
from gtts import gTTS
from pygame import mixer
import os
import requests

class Utils:
    def detect_face_dnn(self, net, image, con=0.9):
        boxes = []
        blob = cv2.dnn.blobFromImage(cv2.resize(
            image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        (h, w) = image.shape[:2]
        net.setInput(blob)
        detections = net.forward()
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < con:
                continue
            box = (detections[0, 0, i, 3:7] *
                   np.array([w, h, w, h])).astype("int")
            x1_, y1_, x2_, y2_ = box[0], box[1], box[2], box[3]
            w_ = x2_ - x1_
            h_ = y2_ - y1_
            box = [x1_, y1_, w_, h_]
            boxes.append(box)
        return boxes
    
    def return_face(self, image, box):
        x, y, w, h = box
        roi = image[y:y+h, x:x+w]
        roi_resize = cv2.resize(roi, (160, 160))
        return roi_resize

    def face_embedding(self, model, roi):
        roi = np.array(roi)
        face_pix = roi.astype('float32')
        mean, std = face_pix.mean(), face_pix.std()
        face_pix = (face_pix-mean) / std
        sample = np.expand_dims(face_pix, axis=0)
        emd = model.predict(sample)
        return emd[0]

    def compare_embeddings(self, emd1, emd2):
        return np.linalg.norm(emd1-emd2)

    def draw_text(self, image, text, origin):
        cv2.putText(image, text, origin, cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2, cv2.LINE_AA)

    def speech_text(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak")
            audio = r.listen(source)
            try:
                message = r.recognize_google(audio)
                return message
            except:
                return 'Speech was not clear'

    def speak(self, text):
        obj = gTTS(text)
        obj.save('temp.mp3')
        mixer.init()
        mixer.music.load('temp.mp3')
        mixer.music.play()
        
    def post(self,name,message,date):
        url = 'http://amiftekher.pythonanywhere.com/'
        s= requests.session()
        r1 = s.get(url)
        csrf = r1.cookies['csrftoken']
        file= {'image': open('temp.jpg','rb')}
        r2 = s.post(url, files = file,data={'name':name,'message':message,'date':date,'csrfmiddlewaretoken': csrf},headers = dict(Referer=url))
        print(r2.reason)
    
    def post_fire(self,fire_state):
        url = 'http://amiftekher.pythonanywhere.com/firestate/'
        s= requests.session()
        r1 = s.get(url)
        csrf = r1.cookies['csrftoken']
        r2 = s.post(url,data={'fire':fire_state,'csrfmiddlewaretoken': csrf},headers = dict(Referer=url))
        print(r2.reason)
