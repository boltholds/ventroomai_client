import cv2
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import RPi.GPIO as GPIO
import enum

class DoorState(enum.Enum):
    open = 1
    close = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN)

door_state = None
app = FastAPI()
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
templates = Jinja2Templates(directory="page")


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)

def door_state_change():
    if door_state == DoorState.open:
        door_state = DoorState.close
    door_state = DoorState.open

GPIO.add_event_detect(12, GPIO.BOTH, callback=door_state_change,bouncetime = 10)

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try:
        uvicorn.run(app, host='10.21.0.110', port=8080)
    except KeyboardInterrupt:
        pass
    except:
        pass
    finally:
        GPIO.cleanup()