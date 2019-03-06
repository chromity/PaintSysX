import PySimpleGUI as sg
import RPi.GPIO as GPIO
import time

signal = 16
s2 = 21
s3 = 20
relay0 = 26
relay1 = 19
NUM_CYCLES = 10


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2, GPIO.OUT)
    GPIO.setup(s3, GPIO.OUT)
    GPIO.setup(relay0, GPIO.OUT)
    GPIO.setup(relay1, GPIO.OUT)


def gui():
    layout = [[sg.Text('PAINT MIXER DEVICE', font=('', 14))],
              [sg.Text('')],
              [sg.Text(' ' * 1), sg.Text('STATUS', font=('', 12), size=(12, 1)), sg.Text('STOPPED', font=('', 12), size=(10, 1), key='_status')],
              [sg.Text(' ' * 1), sg.Text('COLOR', font=('', 12), size=(12, 1)), sg.Drop(values=('RED', 'GREEN', 'BLUE'), font=('', 12), size=(7, 1))],
              [sg.Text(' ' * 1), sg.Text('DELAY (MINS)', font=('', 12), size=(12, 1)),
               sg.Drop(values=('1', '2', '3', '4', '5'), font=('', 12), size=(7, 1))],
              [sg.Text('')],
              [sg.Button('START', font=('', 12)), sg.Button('STOP', font=('', 12))]
              ]

    window = sg.Window('Paint Mixer Device', auto_size_text=True, grab_anywhere=True, resizable=True, no_titlebar=True).Layout(layout)

    status = 0
    while True:
        event, values = window.Read(timeout=10)

        print(values)
        if event == 'START' and status == 0:
            window.FindElement('_status').Update('MIXING')
            status = 1

            GPIO.output(relay0, GPIO.HIGH)
            GPIO.output(relay1, GPIO.LOW)

            while True:
                window.FindElement('_status')
                color = detect_color()
                print(color)

                if values[0].lower() == color:
                    print("i'm inside")
                    result = str(color) + ". WAIT"
                    window.FindElement('_status').Update(result)
                    time.sleep(int(values[1]) * 60 * 1000)

                    GPIO.output(relay0, GPIO.LOW)
                    GPIO.output(relay1, GPIO.HIGH)

                    window.FindElement('_status').Update('FINISHED')
                    break
        elif event == 'STOP':
            window.FindElement('_status').Update('STOPPED')
            status = 0
        elif event == 'Quit' or values is None:
            break
        else:
            pass

    window.Close()


def detect_color():
    temp = 1
    cycle = 0
    red_count = 0
    blue_count = 0
    green_count = 0
    while (1):
        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.LOW)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start
        red = NUM_CYCLES / duration

        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.HIGH)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start
        blue = NUM_CYCLES / duration

        GPIO.output(s2, GPIO.HIGH)
        GPIO.output(s3, GPIO.HIGH)
        time.sleep(0.3)
        start = time.time()
        for impulse_count in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration = time.time() - start
        green = NUM_CYCLES / duration

        print("green: ", green)
        print("blue: ", blue)
        print("red: ", red)

        if green < red and blue < red:
            print("red")
            red_count += 1
            temp = 1
        elif red < green and blue < green:
            print("green")
            green_count += 1
            temp = 1
        elif green < blue and red < blue:
            print("blue")
            blue_count += 1
            temp = 1
        elif red > 10000 and green > 10000 and blue > 10000 and temp == 1:
            print("place the object.....")
            temp = 0

        cycle += 1

        if cycle == 20:
            if blue_count < red_count and green_count < red_count:
                return "red"
            elif blue_count < green_count and red_count < green_count:
                return "green"
            else:
                return "blue"


def end_program():
    GPIO.cleanup()


if __name__ == '__main__':
    setup()

    try:
        gui()

    except KeyboardInterrupt:
        end_program()
