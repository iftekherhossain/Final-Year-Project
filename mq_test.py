import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(11, GPIO.IN)

while True: # Run forever
    if GPIO.input(11) == GPIO.HIGH:
        print("Safe")
    else:
        print("Aguuuun!")