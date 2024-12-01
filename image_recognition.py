import copy
import os
import random
import tensorflow as tf


from sklearn.cluster import KMeans

import numpy as np
import scipy
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from IPython.display import display
image_cat = ['apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot', 'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic', 'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion', 'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato', 'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato', 'turnip', 'watermelon'] 

def crop_image(base_img):
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


if __name__ == '__main__':
    cnn = tf.keras.models.load_model("trained_model.h5")
    #test_image = opencv image
    #go through label index
    test_image = cv2.imread('./garlic_black.jpg')
    cropped_image = crop_image(test_image)
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    prediction_image = Image.fromarray(cropped_image, 'RGB')
    prediction_image = prediction_image.resize((64,64))
    prediction_image = np.array(prediction_image)
    prediction_image = np.expand_dims(prediction_image, axis=0)
    # image = tf.keras.preprocessing.image.load_img(test_image, target_size = (64,64))
    # image = tf.keras.preprocessing.image.img_to_array(image)
    prediction = cnn.predict(prediction_image)
    prediction_position = np.argmax(prediction)
    print(image_cat[prediction_position])
   
   
   
   
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

