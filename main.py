import cv2
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import gpiod
import enum

class DoorState(enum.Enum):
    open = 1
    close = 0

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



def door_state_changed_event(event):
    if event.type == gpiod.LineEvent.RISING_EDGE:
        door_state = DoorState.close
    elif event.type == gpiod.LineEvent.FALLING_EDGE:
        door_state = DoorState.open
        
    


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    with gpiod.Chip(0) as chip:
        lines = chip.get_lines(27)
        lines.request(0, type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        while True:
            ev_lines = lines.event_wait(sec=1)
            if ev_lines:
                for line in ev_lines:
                    event = line.event_read()
                    door_state_changed_event(event)

    try:
        uvicorn.run(app, host='10.21.0.110', port=8080)
    except KeyboardInterrupt:
        pass
    except:
        pass
    finally:
        pass
