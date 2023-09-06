from flask import Flask, render_template, request
import urllib.request
import numpy as np
import easyocr
import cv2
import base64

THRESHOLD = 0.5

reader = easyocr.Reader(['ko', 'en'])

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/read_image', methods=['POST'])
def read_image():
    image_url = request.form['image_url']
    image_file = request.files['image_file']
    
    if image_file:
        image = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    elif image_url:
        with urllib.request.urlopen(image_url) as url:
            image = np.asarray(bytearray(url.read()), dtype=np.uint8)
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else:
        return render_template('index.html', error_message='No image URL or file provided.')

    result = reader.readtext(img)

    processed_result = []

    for bbox, text, conf in result:
        if conf > THRESHOLD:
            processed_result.append(text)
            cv2.rectangle(img, pt1=(int(bbox[0][0]), int(bbox[0][1])), pt2=(int(bbox[2][0]), int(bbox[2][1])), color=(0, 255, 0), thickness=3)

    ret, buffer = cv2.imencode('.png', img)
    img_encoded = base64.b64encode(buffer).decode('utf-8')

    return render_template('index.html', result=processed_result, image_data=img_encoded)

if __name__ == '__main__':
    app.run()
