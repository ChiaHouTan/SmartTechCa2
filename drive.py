import socketio
import eventlet
from flask import Flask
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

sio = socketio.Server()
app = Flask(__name__)

speed_limit = 25
#track 1 model1 speed limit 30
#track 2 model2 speed limit 25
#All track model3 speed limit 35 for track 1 and for track 2 25
#track 1 time: 1 min 45 secs
#track 2 time: 3 mins 50 secs


def img_preprocess(img):
    img = img[60:135, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img


@sio.on('telemetry')
def telemetry(sid, data):
    print("Telemetry received")
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    speed = float(data['speed'])
    throttle = 1.0 - speed/speed_limit
    
    steering_angle = float(model.predict(image))
    send_control(steering_angle, throttle)



@sio.on('connect')
def connect(sid, environ):
    print("Connected", sid)
    send_control(0, 0)
    print("After send_control")


def send_control(steering_angle, throttle):
    sio.emit('steer', data = {
        'steering_angle' : steering_angle.__str__(),
        'throttle' : throttle.__str__()
    })


if __name__ == '__main__':
    try:
        model = load_model('model3.h5')
        print("Model loaded successfully")
        app = socketio.Middleware(sio, app)
        eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
    except Exception as e:
        print(f"Error: {e}")
