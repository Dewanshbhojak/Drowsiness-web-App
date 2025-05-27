# Importing OpenCV Library for basic image processing functions
import cv2
# Numpy for array related functions
import numpy as np
# Dlib for deep learning-based Modules and face landmark detection
import dlib
# face_utils for basic operations of conversion
from imutils import face_utils

import time 
import datetime
import json

# mixer for sound
from pygame import mixer
import requests 
from twilio.rest import Client
from flask import session




def get_driver_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = response.json()
            location = data.get('loc', '')  
            city = data.get('city', '')
            region = data.get('region', '')
            country = data.get('country', '')
            print(f"[INFO] Location: {location} | {city}, {region}, {country}")
            return {
                "location": location,
                "city": city,
                "region": region,
                "country": country
            }
        else:
            print("[ERROR] Failed to get location info")
            return None
    except Exception as e:
        print(f"[ERROR] Exception occurred while fetching location: {e}")
        return None


def start1():
    mixer.init()
    sound = mixer.Sound('alarm sounds/alarm.wav')

    # Initializing the camera and taking the instance
    cap = cv2.VideoCapture(0)

    # Initializing the face detector and landmark detector
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # Status marking for current state
    sleep = 0
    drowsy = 0
    active = 0
    status = ""
    color = (0, 0, 0)
    sleep_count = 0  # ✅ Count how many times the driver fell asleep

    Ear_Values = []
    Mar_Values = []
    Time_value = []

    def compute(ptA, ptB):	
        dist = np.linalg.norm(ptA - ptB)
        return dist

    def blinked(a, b, c, d, e, f):
        up = compute(b, d) + compute(c, e)
        down = compute(a, f)
        ratio = up / (2.0 * down)

        if ratio > 0.25:	
            return 2, ratio
        elif 0.18 < ratio <= 0.25:
            return 1, ratio
        else:
            return 0, ratio

    def yawn(a, b, c, d, e, f, g, h):
        den = compute(a, e)
        num = compute(b, h) + compute(c, g) + compute(d, f)
        ratio = num / (3.0 * den)
        Mar_Values.append(ratio)

        if ratio >= 0.40:
            return 2
        else:
            return 0

    start_time = time.time()
    location_data = get_driver_location()

    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_blink, ratioL = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink, ratioR = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            yawnned = yawn(landmarks[60], landmarks[61], landmarks[62], landmarks[63], landmarks[64], landmarks[65], landmarks[66], landmarks[67])

            ratioF = (ratioL + ratioR) / 2
            Ear_Values.append(ratioF)
            temp_time = time.time()
            Time_value.append(temp_time - start_time)

            # Status detection
            if left_blink == 0 or right_blink == 0:
                sleep += 1
                drowsy = 0
                active = 0
                if sleep > 6:
                    status = "SLEEPING !!!"
                    color = (255, 0, 0)
                    sleep_count += 1  # ✅ Increment sleep count
                    
                    try:
                        sound.play()
                    except:
                        pass

            elif left_blink == 1 or right_blink == 1:
                sleep = 0
                active = 0
                drowsy += 1
                if drowsy > 6:
                    status = "Drowsy !"
                    color = (0, 0, 255)
                    try:
                        mixer.music.load('alarm sounds/warning_sleep.mp3')
                    except:
                        pass

            elif yawnned == 2:
                sleep = 0
                active = 0
                drowsy += 1
                if drowsy > 6:
                    status = "Drowsy yawned!"
                    color = (0, 0, 255)
                    try:
                        mixer.music.load('alarm sounds/warning_yawn.mp3')
                        mixer.music.play(1, 0.0)
                    except:
                        pass

            else:
                drowsy = 0
                sleep = 0
                active += 1
                if active > 6:
                    status = "Active :)"
                    color = (0, 255, 0)

            # Show text on screen
            cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            cv2.putText(frame, f"Sleep Count: {sleep_count}", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

            for n in range(0, 68):
                (x, y) = landmarks[n]
                cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    end_time =time.time()
    total_time =int(end_time - start_time)
    start_time_readable = datetime.datetime.fromtimestamp(start_time).strftime("%I:%M:%S %p")
    
    
    # Save sleep count to JSON file for frontend to read
    with open("sleep_data.json", "w") as f:
        json.dump({"sleep_count": sleep_count,"duration":total_time,"starting_time":start_time_readable,"location_data":location_data.get("location",""),"city":location_data.get("city",""),"region":location_data.get("region",""),"country":location_data.get("country","")}, f)
    
    with open ("location_data.json","w")as f:
        json.dump({"location_data":location_data.get("location",""),"city":location_data.get("city",""),"region":location_data.get("region",""),"country":location_data.get("country","")},f)


    return
