import time
from rpi_ws281x import *
import random
import os
import traceback

# LED strip configuration:
LED_COUNT      = 500     # Number of LED pixels.
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


    def play_effect(self, effect):
        if effect == 'random_loop':
            while self.light.get_work_queue_length() == 0:
                random_effect = random.choice(self.effect_name_list)

                self.light.state['effect'] = random_effect  # update the state tracking
                self.light.mqtt.send_state_update(self.light.state)

                filename = self.effect_filenames[random_effect]
                self.play_seq(self.strip, filename)
        else:
            self.light.state['effect'] = effect  # update the state tracking
            self.light.mqtt.send_state_update(self.light.state)

            filename = self.effect_filenames[effect]
            self.play_seq(self.strip, filename)

        self.light.state['state'] = 'OFF'  # sequence ends with light off
        # self.light.state.pop('effect', None)  # drop the completed effect.
        self.light.state['effect'] = None  # drop the completed effect.
        self.light.mqtt.send_state_update(self.light.state)


    def play_seq(self, strip, filename):
        basefilename = filename.split('/')[-1].replace('.txt','')
        self.on = self.deg2color(random.randint(0,255))

        fh = open(os.path.join(self.premadeDir, filename), 'r')
        in_lines = fh.readlines()
        fh.close()

        loops = []

        self.last_time = time.time()

        for line_index in range(len(in_lines)):
            in_line = in_lines[line_index]

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
                
                elif cmd.startswith('do'):  # do loop
                    entry = {'do_pos':line_index+1, 'n_loops':0}

                elif cmd.startswith('brightness 1,'):  # brightness 1,64
                    fields = cmd.split(',')
                    brightness = int(fields[1])
                    strip.setBrightness(brightness)

                elif cmd.startswith('rainbow 1,'):  # rainbow 1,1,0,LEN
                    fields = cmd.split(',')
                    repeats = int(fields[1])
                    startpos = int(fields[2])
                    length = fields[3]
                    if length == 'LEN':
                        length = LED_COUNT
                    else:
                        length = int(length)
                    angle = 0
                    increment = 256*repeats/length
                    for index in range(length):
                        colorObj = self.deg2color(int(angle+0.5+85))
                        angle += increment
                        strip.setPixelColor(startpos+index, colorObj)

                # <channel>,         #channel to rotate (default 1)
                # <places>,          #number of places to move each color value (default 1)
                # <direction>,       #direction (0 or 1) for forward and backwards rotating (default 0)
                # <start>,           #at which led should we start (default is 0)
                # <len>              #number of leds to fill with the given color after start (default all leds)
                # <RRGGBB>           #first led(s) get this color instead of the color of the last led
                elif cmd.startswith('rotate 1,'):  #rotate 1,1,1,0,LEN;
                    fields = cmd.split(',')
                    places = int(fields[1])
                    direction = int(fields[2])
                    startpos = int(fields[3])
                    length = fields[4]
                    if len(fields) > 5:
                        color = fields[5]
                    else:
                        color = None
                    if length == 'LEN':
                        length = LED_COUNT
                    else:
                        length = int(length)

                    for place in range(places):
                        if direction == 1:
                            tmpColor = strip.getPixelColor(startpos)
                            for index in range(1+startpos, startpos+length):
                                strip.setPixelColor(index-1, strip.getPixelColor(index))
                            if color == None:
                                strip.setPixelColor(length-1+startpos, tmpColor)
                            else:
                                strip.setPixelColor(length-1+startpos, Color(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)))
                        else:
                            tmpColor = strip.getPixelColor(length -1 + startpos)
                            for index in range(length -1 + startpos, startpos, -1):
                                strip.setPixelColor(index, strip.getPixelColor(index-1))
                            if color == None:
                                strip.setPixelColor(startpos, tmpColor)
                            else:
                                strip.setPixelColor(startpos, Color(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)))
        # for(n=0;n<nplaces;n++){
        #     if (direction==1){
        #         tmp = ledstring.channel[channel].leds[start];
        #         for(i=1+start;i<numPixels+start;i++){
        #             ledstring.channel[channel].leds[i-1] = ledstring.channel[channel].leds[i];
        #         }
        #         if (new_color!=-1)
        #             ledstring.channel[channel].leds[numPixels-1+start]=new_color;
        #         else
        #             ledstring.channel[channel].leds[numPixels-1+start]=tmp;
        #     }else{
        #         tmp = ledstring.channel[channel].leds[numPixels-1+start];
        #         for(i=numPixels-1+start;i>0+start;i--){
        #             ledstring.channel[channel].leds[i] = ledstring.channel[channel].leds[i-1];
        #         }
        #         if (new_color!=-1)
        #             ledstring.channel[channel].leds[0+start]=new_color;
        #         else
        #             ledstring.channel[channel].leds[0+start]=tmp;
        #     }
        # }

                elif (cmd == 'fill 1'):  # blank the leds
                    self.clear_strip(strip)

                elif cmd.startswith('delay'):
                    fields = cmd.split()
                    exit_needed = self.delay(int(fields[1]))
                    if exit_needed:
                        return  # new command arrived.  abort sequence

                elif (cmd == 'render'):  # render the line
                    strip.show()
                    if self.light.get_work_queue_length():
                        return  # new command arrived.  abort sequence


    def deg2color(self, fullWheelPos):
        wheelPos = fullWheelPos % 256  # wrap around 
        if(wheelPos < 85):
            return Color(255 - wheelPos * 3,wheelPos * 3 , 0)
        elif(wheelPos < 170):
            wheelPos -= 85
            return Color(0, 255 - wheelPos * 3, wheelPos * 3)
        else:
            wheelPos -= 170
            return Color(wheelPos * 3, 0, 255 - wheelPos * 3)





# /home/pi/proj/led_8x8x8/8x8x8/pre_made
#     seq_a_cone.txt
#     seq_a_few_blinking_eyes.txt
#     seq_all_leds_on.txt
#     seq_back_and_forth_twisting_plane.txt
#     seq_bouncing_moto_logo.txt
#     seq_bouncing_sphere.txt
#     seq_corner_pulses.txt
#     seq_drum_1.txt
#     seq_falling_streamer.txt
#     seq_flat_plan_falling_down_1
#     seq_flat_plan_falling_down_2
#     seq_flat_plan_falling_down_3
#     seq_full_cube_fill_in_from_top.txt
#     seq_full_cube_fill_in_from_top_2.txt
#     seq_full_cube_fill_in_from_top_3.txt
#     seq_full_sheet_crumbling_and_falling_quickly_1.txt
#     seq_full_sheet_crumbling_and_falling_quickly_2.txt
#     seq_full_sheet_crumbling_and_falling_quickly_3.txt
#     seq_hourglass_pyramid.txt
#     seq_hypercube.txt
#     seq_i_heart_u_around_edge.txt
#     seq_i_heart_u_swiped_in.txt
#     seq_i_heart_you_rotating.txt
#     seq_laser_printed_msg.txt
#     seq_multi_axis_pacman.txt
#     seq_open_arrow_around_edge_1.txt
#     seq_open_arrow_around_edge_2.txt
#     seq_raining_dots_and_rising_dots_1.txt
#     seq_raining_dots_and_rising_dots_2.txt
#     seq_raining_dots_and_rising_dots_3.txt
#     seq_rains_asian_words.txt
#     seq_random_all_leds.txt
#     seq_random_all_leds_fast.txt
#     seq_random_rising_dots_1.txt
#     seq_random_rising_dots_2.txt
#     seq_random_rising_dots_3.txt
#     seq_rotating_biting_pacman.txt
#     seq_rotating_concentric_rings_like_contact.txt
#     seq_rotating_earth.txt
#     seq_rotating_edge_and_corner_volumes.txt
#     seq_rotating_i_heart_u.txt
#     seq_rotating_rainbow_square.txt
#     seq_rotating_rings_axis_thick.txt
#     seq_rotating_rings_axis_thin.txt
#     seq_rotating_rings_pulses_thin.txt
#     seq_sideways_pulsing_pyramid_plane.txt
#     seq_stargate_transport_guy.txt
#     seq_stretching_in_i_heart_u.txt
#     seq_twisting_planes_and_more.txt
#     seq_twisting_rotating_sheet_1.txt
#     seq_twisting_rotating_sheet_2.txt
#     seq_up_and_down_plane_from_corner.txt
#     seq_up_down_sheet_waves.txt
#     seq_vertical_plane_sweeping_sideways.txt
#     seq_vertical_plane_waving_sideways.txt
#     seq_vertically_waving_sheet_1.txt
#     seq_vertically_waving_sheet_2.txt
#     seq_vertically_waving_sheet_3.txt

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

        # self.seq_full_sheet_crumbling_and_falling_quickly_1(self.strip)
        # self.seq_drum_1(self.strip)
        result = self.play_seq(self.strip, 'seq_rotating_rainbow_square.txt')
        result = self.play_seq(self.strip, 'seq_full_sheet_crumbling_and_falling_quickly_2.txt')
        result = self.play_seq(self.strip, 'seq_laser_printed_msg.txt')
        result = self.play_seq(self.strip, 'seq_a_cone.txt')
        result = self.play_seq(self.strip, 'seq_drum_1.txt')
        # result = self.play_seq(self.strip, 'seq_rotating_earth.txt')


        # render
        self.strip.show()

# Main program logic follows:
if __name__ == '__main__':
    myEffects = Effects('/home/pi/proj/led_8x8x8/8x8x8/pre_made/')

    myEffects.strip_test()
