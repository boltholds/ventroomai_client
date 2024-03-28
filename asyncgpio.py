import asyncio
import logging
from time import sleep
logger = logging.getLogger(__name__)


async def set_light_pwr_on():
    # GPIO_PWM_0 = 12
    # FREQUENCY = 100
    # DELAY_TIME = 0.02
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(GPIO_PWM_0, GPIO.OUT)
    # pwmOutput_0 = GPIO.PWM(GPIO_PWM_0, FREQUENCY)
    # pwmOutput_0.start(0)
    # try:
    #     while True:
    #         for dutyCycle in range(0, 101, 1):
    #             pwmOutput_0.ChangeDutyCycle(dutyCycle)
    #             sleep(DELAY_TIME)
    # except KeyboardInterrupt:
    #     pwmOutput_0.stop()
    #     GPIO.cleanup()
        logger.debug('PWM exiting')

async def wait_door():
    old_state = None
    current_state = None
    while True:
        await asyncio.sleep(0.1)
        # current_state = rpi.GPIO27
        if old_state != current_state:
            logger.debug(f"Door is {current_state}")
            old_state = current_state
            yield current_state
