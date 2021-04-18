import speech_recognition as sr 

while True:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak")
        audio = r.listen(source)
        try:
            message = r.recognize_google(audio)
            print("You said :{}".format(message))
        except:
            print("Sorry couldnot recognize your voice")