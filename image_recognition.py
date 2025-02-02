import copy
import os
import random
import tensorflow as tf
from picamera2 import Picamera2
import time
from sklearn.cluster import KMeans

import numpy as np
import scipy
import cv2
from PIL import Image

# note to Justin: refactor code such that it calls take_picture.py to get output.py, then uses output.py for ML

image_cat = ['apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot', 'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic', 'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion', 'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato', 'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato', 'turnip', 'watermelon'] 

class IngredientRecog:
    def __init__(self):
        self.cnn = tf.keras.models.load_model("trained_model.h5")
        self.picam2 = Picamera2()
        self.picam2.start() # maybe want to start at the beginning
        # Wait for camera to initialize
        time.sleep(2)

    def crop_image(self, base_img):
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

    def take_pic(self):
        # Capture an image
        self.picam2.capture_file("test.jpg")
        self.picam2.stop()

    def predict_img(self):
        if not os.path.exists("./test.jpg"):
            exit(1) #some exit message
        test_image = cv2.imread('./test.jpg')
        base_image = Image.fromarray(test_image, 'RGB') #image might not be RGB from pi cam
        base_image = base_image.resize((64,64))
        base_image = np.array(base_image)
        base_image = np.expand_dims(base_image, axis=0)
        cropped_image = self.crop_image(test_image)
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        prediction_image = Image.fromarray(cropped_image, 'RGB')
        prediction_image = prediction_image.resize((64,64))
        prediction_image = np.array(prediction_image)
        prediction_image = np.expand_dims(prediction_image, axis=0)
        # image = tf.keras.preprocessing.image.load_img(test_image, target_size = (64,64))
        # image = tf.keras.preprocessing.image.img_to_array(image)
        prediction = self.cnn.predict(prediction_image)
        prediction_position = np.argmax(prediction)
        os.remove("./test.jpg")
        return prediction_position



if __name__ == '__main__':
    cnn = tf.keras.models.load_model("trained_model.h5")
    recognizer = IngredientRecog()
    recognizer.take_pic()
    prediction_position = recognizer.predict_img()
    print("prediction after crop: ")
    print(image_cat[prediction_position])
   



#goal edge detection the largest object, make some algorithm that is able to determine the left and right end most of the edge detection adn then make everything in the middle 1, and with teh image to get the image

#addons camera calibration for the middle of the camera

