import cv2
import time
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import RPi.GPIO as GPIO
import enum
import asyncio

class DoorState(enum.Enum):
    open = 1
    close = 0

door_sensor = 27
led = 12
door_state = DoorState.close
GPIO.setmode(GPIO.BCM)
GPIO.setup(door_sensor, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
pwmOutput_0 = GPIO.PWM(led, 100)
pwmOutput_0.start(0)

app = FastAPI()
camera = cv2.VideoCapture(0)
templates = Jinja2Templates(directory="templates")

available_cameras = []

def get_available_cameras():
    available_cameras = []
    for i in range(99):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

async def soft_start_led(max_light=100):
    while True:
        for dutyCycle in range(0, max_light+1, 1):
            pwmOutput_0.ChangeDutyCycle(dutyCycle)
            await asyncio.sleep.sleep(0.02)

def stop_led():
    pwmOutput_0.stop()


async def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        await asyncio.sleep(0.03)



async def door_state_changed_event(time_update=0.3):
    while True:
        yield GPIO.input(door_sensor)
        await asyncio.sleep(time_update)

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("page.html", {"request": request,"door_state" : door_state_changed_event()})


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post('/settings/')
def settings(request:Request,focus: int = Form(.),light: int = Form(.)):
    print( f'focus {range_focus},{range_light} light')

if __name__ == '__main__':
    try:
        available_cameras = get_available_cameras()
        uvicorn.run(app, host='10.21.0.110', port=8080)
    except KeyboardInterrupt:
        pass
    except:
        pass
    finally:
        GPIO.cleanup()
