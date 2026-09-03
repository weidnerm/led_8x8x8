import time
from rpi_ws281x import *
import random
import os
import traceback
from TextWrap import (
    USER_WRAP_EFFECT,
    USER_WRAP_FILE,
    write_seq_file,
    normalize_text,
)

# LED strip configuration:
LED_COUNT      = 512     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 32      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class Effects:
    def __init__(self, premadeDir, light):
        self.off = Color(0,0,0)
        self.on = Color(0,255,0)
        self.len = LED_COUNT
        self.python_indent = '        '
        self.premadeDir = premadeDir
        self.light = light
        self.effect_name_list = []
        self.effect_filenames = {}  # indexed by effect name

        files = os.listdir(self.premadeDir)
        for file in files:
            if file.startswith('seq_') and file.endswith('.txt'):
                effect_name = file.replace('seq_', '').replace('.txt', '').replace('_', ' ')  # transform filename to effect name.  drop prefix, suffix and use spaces
                self.effect_name_list.append(effect_name)
                self.effect_filenames[effect_name] = file

        if USER_WRAP_EFFECT not in self.effect_name_list:
            self.effect_name_list.append(USER_WRAP_EFFECT)
        self.effect_filenames[USER_WRAP_EFFECT] = USER_WRAP_FILE
        self.effect_name_list.sort() # alphabetize the list

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        delay = 0.001


    def delay(self, delayMsec):

        exit_processing = False  # track flag to help parent to know when to abort sequence.  check it here since we are waiting anyway

        expiration_time = delayMsec/1000 + self.last_time  # try to skip over time spent doing processing.

        while expiration_time > time.time():
            if self.light.get_work_queue_length() > 0:
                exit_processing = True
                break
            time.sleep(0.001)

        self.last_time = time.time()

        return exit_processing


    def generate_user_wrap_seq(self, text):
        text = normalize_text(text) or 'HELLO'
        dest = os.path.join(self.premadeDir, USER_WRAP_FILE)
        write_seq_file(text, dest)
        print('wrote wrap seq for %r -> %s' % (text, dest))
        return dest


    def play_effect(self, effect):
        if effect == 'random_loop':
            pool = [n for n in self.effect_name_list if n != USER_WRAP_EFFECT]
            while self.light.get_work_queue_length() == 0:
                random_effect = random.choice(pool)

                self.light.state['effect'] = random_effect  # update the state tracking
                self.light.mqtt.send_state_update(self.light.state)

                filename = self.effect_filenames[random_effect]
                self.play_seq(self.strip, filename)
        else:
            self.light.state['effect'] = effect  # update the state tracking
            self.light.mqtt.send_state_update(self.light.state)

            if effect == USER_WRAP_EFFECT:
                self.generate_user_wrap_seq(getattr(self.light, 'wrap_text', 'HELLO'))

            filename = self.effect_filenames[effect]
            self.play_seq(self.strip, filename)

        self.light.state['state'] = 'OFF'  # sequence ends with light off
        self.light.state.pop('effect', None)
        self.light.mqtt.send_state_update(self.light.state)


    def play_seq(self, strip, filename):
        basefilename = filename.split('/')[-1].replace('.txt','')
        self.on = self.deg2color(random.randint(0,255))

        path = os.path.join(self.premadeDir, filename)
        if not os.path.isfile(path):
            print('missing sequence file %s' % path)
            return

        fh = open(path, 'r')
        in_lines = fh.readlines()
        fh.close()

        self.last_time = time.time()

        for in_line in in_lines:
            cmds = in_line.split(';')
            for cmd in cmds:
                cmd = cmd.strip()
            
                if cmd.startswith('fill 1,0000ff,'):  # gather up the individual led numbers for monocrome
                    fields = cmd.split(',')
                    color = fields[1]
                    startpos = int(fields[2])
                    num = int(fields[3])
                    for index in range(num):
                        strip.setPixelColor(startpos+index, self.on)
                                     
                elif cmd.startswith('fill 1,'):  # some color other than the to-be-replaced one
                    fields = cmd.split(',')
                    color = fields[1]
                    startpos = int(fields[2])
                    num = int(fields[3])
                    colorObj = Color(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
                    for index in range(num):
                        strip.setPixelColor(startpos+index, colorObj)

                elif (cmd == 'fill 1'):  # blank the leds
                    self.clear_strip(strip)

                elif cmd.startswith('delay'):
                    fields = cmd.split()
                    exit_needed = self.delay(int(fields[1]))
                    if exit_needed:
                        return  # new command arrived.  abort sequence

                if (cmd == 'render'):  # render the line
                    strip.show()
                    if self.light.get_work_queue_length():
                        return  # new command arrived.  abort sequence


    def deg2color(self, wheelPos):
        if(wheelPos < 85):
            return Color(255 - wheelPos * 3,wheelPos * 3 , 0)
        elif(wheelPos < 170):
            wheelPos -= 85
            return Color(0, 255 - wheelPos * 3, wheelPos * 3)
        else:
            wheelPos -= 170
            return Color(wheelPos * 3, 0, 255 - wheelPos * 3)


    def clear_strip(self, strip):
        for index in range(self.len):
            strip.setPixelColor(index, self.off)

    def set_pixel_list(self, strip, pixels, color=None):
        for pixel in pixels:
            if color == None:  # use default
                strip.setPixelColor(pixel, self.on)
            else:
                colorObj = Color(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
                strip.setPixelColor(pixel, colorObj)

    def fill_full_cube_color(self, state):

        self.strip.setBrightness(state['brightness'])
        
        if state['state'] == 'ON':
            color = Color(state['color']['g'], state['color']['r'], state['color']['b'])
        else:
            color = self.off

        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()


    def strip_test(self):

        result = self.play_seq(self.strip, 'seq_rotating_rainbow_square.txt')
        result = self.play_seq(self.strip, 'seq_full_sheet_crumbling_and_falling_quickly_2.txt')
        result = self.play_seq(self.strip, 'seq_laser_printed_msg.txt')
        result = self.play_seq(self.strip, 'seq_a_cone.txt')
        result = self.play_seq(self.strip, 'seq_drum_1.txt')

        # render
        self.strip.show()

# Main program logic follows:
if __name__ == '__main__':
    myEffects = Effects('/home/pi/proj/led_8x8x8/8x8x8/pre_made/')

    myEffects.strip_test()
