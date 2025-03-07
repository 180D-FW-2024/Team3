import copy
import os
import random
import tensorflow as tf
from picamera2 import Picamera2
import time
from pyzbar.pyzbar import decode
import subprocess
import requests
from openai import OpenAI
from dotenv import load_dotenv
import base64
import json

from sklearn.cluster import KMeans

import numpy as np
import scipy
import cv2
from PIL import Image
image_cat = ['apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot', 'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic', 'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion', 'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato', 'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato', 'turnip', 'watermelon'] 

#methods can call: scan_qr_login, take_pic (have to call before predict_img), predict_img
#1 = intializing didn't work : error code of camera
#2 = error taking image : None
#3 = image to analyze is not there, didn't take image successfully or not found : None
#4 = camera didn't turn on : error code
#5 = cmera didn't sleep : erorr code
#6 = all qr codes for framing the object were not within camera frame : and returns which edges were not detected
#7 = issue with cropping the image with qrs code for framing (most likely reading the image) : None
#8 = no qr scanned within scanning time frame (30) : None
#9 = error when writing file for logging in user : error code
#10 = no response from server : None

load_dotenv()
backend_url = os.getenv('BACKEND_URL')

class IngredientRecog:
    def __init__(self):
        try:
            self.cnn = tf.keras.models.load_model("trained_model.h5")
            self.client = OpenAI(api_key = os.getenv("OPENAI_API"))
            # self.picam2 = Picamera2()
            # config = self.picam2.create_preview_configuration(main={"size": (1640, 1232)})
            # self.picam2.configure(config)
            # Wait for camera to initialize
        except Exception as err:
            #failure to initalize
            return (1, err)

    def scan_qr_login(self):

        ## may help with live feed the cameras
        decoded_qr = None
        self.user_number = None
        start_time = time.time()
        duration = 10  # seconds
        while(time.time() - start_time < duration):
            self.take_pic(file_name = "qrcode.jpg")
            frame = cv2.imread("./qrcode.jpg")
            decoded_qrs = decode(frame)
            for obj in decoded_qrs:
                data = obj.data.decode('utf-8')
                response = requests.get(backend_url + "/get-user/" + json.loads(data)["phoneNumber"])
                if response.status_code == 200:
                    try: 
                        with open("./config.txt", "w") as file:
                            user_id = "USERNAME:" + str(response.json()["username"])
                            file.write(user_id)
                        return
                    except Exception as err:
                        return (9, err) #error code and dcoument
                else:
                    return (10, None)
        return (8, None)

    def __crop_image(self, base_img):
        img = cv2.cvtColor(base_img, cv2.COLOR_BGR2HSV)
        delta = 25
        h, w = img.shape[:2]
        small_window = img[(h//2 -delta): (h//2+delta), (w//2-delta): (w//2+delta)]
        small_window = small_window.reshape((small_window.shape[0] * small_window.shape[1],3))
        clt = KMeans(n_clusters=3)
        clt.fit(small_window)
        colors = clt.cluster_centers_
        h_delta = 20
        # hsv2_lower = np.array([colors[1][0] - h_delta, max(colors[1][1]-50, 100), max(colors[1][2]-50, 100)])
        # hsv2_upper = np.array([colors[1][0] + h_delta, min(colors[1][1]+50, 255), min(colors[1][2]+50, 255)])
        hsv1_lower = np.array([colors[0][0] - h_delta, max(colors[0][1]-75, 0), max(colors[1][2]-75, 0)])
        hsv1_upper = np.array([colors[0][0] + h_delta, min(colors[0][1]+75, 255), min(colors[1][2]+75, 255)])

        hsv2_lower = np.array([colors[1][0] - h_delta, max(colors[1][1]-75, 0), max(colors[1][2]-75, 0)])
        hsv2_upper = np.array([colors[1][0] + h_delta, min(colors[1][1]+75, 255), min(colors[1][2]+75, 255)])

        hsv3_lower = np.array([colors[1][0] - h_delta, max(colors[2][1]-75, 0), max(colors[1][2]-75, 0)])
        hsv3_upper = np.array([colors[1][0] + h_delta, min(colors[2][1]+75, 255), min(colors[1][2]+75, 255)])

        mask1 = cv2.inRange(img , hsv1_lower, hsv1_upper)
        mask2 = cv2.inRange(img , hsv2_lower, hsv2_upper)
        mask3 = cv2.inRange(img , hsv3_lower, hsv3_upper)

        mask_combo1 = cv2.bitwise_or(mask1, mask2)
        mask_all_mix = cv2.bitwise_or(mask_combo1, mask3)

        contours, _ = cv2.findContours(
            mask_all_mix, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        min_contour_area = 2000
        mask = np.zeros_like(base_img)
        largest_contour = max(contours, key=cv2.contourArea)
            # Fill the contour
        # cv2.drawContours(mask, contours, -1, (0, 255, 0), 3)
        cv2.drawContours(mask, [largest_contour], -1, (255))
        x, y, w, h = cv2.boundingRect(largest_contour)
        crop_image = base_img[y:y+h,x:x+w]
        return crop_image

    def take_pic(self, file_name = "test.jpg"):
        # Capture an image
        try:
            subprocess.run([
        "libcamera-still",
        "--width", "1920",
        "--height", "1080",
        "-o", file_name,
        "--immediate"
        ])
        except:
            return(2, None)

    def predict_img(self, use_ai = True):
        if not os.path.exists("./test.jpg"):
            return(3, None) #some exit message
        test_image = self.__crop_img_qr()
        if(type(test_image) == tuple):
            return test_image
        cropped_image = self.__crop_image(test_image)
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        if use_ai:
            return self.predict_img_openai(cropped_image)
        prediction_image = Image.fromarray(cropped_image, 'RGB')
        prediction_image = prediction_image.resize((64,64))
        prediction_image = np.array(prediction_image)
        prediction_image = np.expand_dims(prediction_image, axis=0)
        # image = tf.keras.preprocessing.image.load_img(test_image, target_size = (64,64))
        # image = tf.keras.preprocessing.image.img_to_array(image)
        prediction = self.cnn.predict(prediction_image)
        prediction_position = np.argmax(prediction)
        os.remove("./test.jpg")
        return image_cat[prediction_position]

    def encode_img(self, img):
        _, buffer = cv2.imencode('.jpg', img)  # Convert NumPy array to PNG format in memory
        return base64.b64encode(buffer).decode("utf-8")
    
    def predict_img_openai(self, img):
        prompt = "What food product is in this image. Give me a response in 1 word of what food it is"
        encoded_base_img = self.encode_img(img)
        try:
            response = self.client.chat.completions.create(
            model = "gpt-4o-mini",
            max_tokens = 300, #might need to be changed to load more
            messages = [
                        {
                            "role": "user",
                            content: [
                                {
                                    "type" : "text",
                                    "text" : prompt,
                                },
                                {
                                    "type" : "image_url",
                                    "image_url" : {"url": f"data:image/jpg; base64, {encoded_base_image}"},
                                },
                            ],
                        }
                    ],
                )
            return response.choices[0].message.content
        except:
            return()


    def __crop_img_qr (self):
        try:
            # Capture frame from camera
            frame = cv2.imread('./test.jpg')
            H, W, _ = frame.shape
            H /= 2
            W /= 2
            
            # Decode QR codes
            decoded_objects = decode(frame)
            edges = []
            edge_coord = []
            good_edges =['3', '4', '1', '2'] 
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                if data in good_edges:
                    edges.append(data)
                    points = obj.polygon
                    dist = []
                    for p in points:
                        x = p[0]
                        y = p[1]
                        dist.append( np.sqrt((x-W)**2 + (y-H)**2 ))
                    edge_coord.append(points[np.argsort(dist)[0]])
            if len(edges) != 4:
                return (6, list(set(good_edges) - set(edges)))
            
            x1, x2, y1, y2 = None, None, None, None
            xs = [x for (x, _) in edge_coord]
            ys = [y for (_, y) in edge_coord]
            xs = sorted(xs)
            ys = sorted(ys)
            x1 = xs[0]
            x2 = xs[-1]
            y1 = ys[0]
            y2 = ys[-1]
            cropped_img = frame[y1: y2, x1: x2]
            
            return cropped_img
        except:
            return (7, None) 



if __name__ == '__main__':
    #test_image = opencv image
    #go through label index
    # picam2 = Picamera2()
    # picam2.configure(picam2.create_preview_configuration())
    # picam2.start()
    # frame = picam2.capture_array() #what the
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    load_dotenv()
    recognizer = IngredientRecog()
    # # recognizer.wake()
    # print("take pic")
    # recognizer.take_pic()
    # preditino = recognizer.predict_img()
    # print(preditino)
    print(recognizer.scan_qr_login())
   
   
   
   #for video capture
    # cap = cv2.VideoCapture(0)

    # # Check if the webcam is opened successfully
    # if not cap.isOpened():
    #     print("Error: Could not open camera")
    #     exit()

    # while True:
    #     # Capture frame-by-frame
    #     ret, frame = cap.read()
    #     if not ret:
    #         print("Error: Can't receive frame")
    #         break
    #     rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #     test_image =
    #     test_image = test_image.resize((64,64))
    #     # image = tf.keras.preprocessing.image.load_img(test_image, target_size = (64,64))
    #     # image = tf.keras.preprocessing.image.img_to_array(image)
    #     img = np.array(test_image)
    #     img = np.expand_dims(img, axis=0)
    #     prediction = cnn.predict(img)
    #     prediction_position = np.argmax(prediction)
    #     print(image_cat[prediction_position])



    #     cv2.imshow('Camera Feed', frame)
    #     # Press 'q' to quit
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # # Release the capture and destroy windows
    # cap.release()
    # cv2.destroyAllWindows()



#goal edge detection the largest object, make some algorithm that is able to determine the left and right end most of the edge detection adn then make everything in the middle 1, and with teh image to get the image

