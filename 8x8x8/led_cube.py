import serial
import binascii
import struct
import time
import argparse
import numpy as np
import math
import random
from scipy.special import jn, jn_zeros

class Led_Cube_8x8x8():
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.port = serial.Serial(self.port, baudrate=self.baudrate, timeout=3.0)
        self.clear()

        self.dat = [
        0x0,0x20,0x40,0x60,0x80,0xa0,0xc0,0xe0,0xe4,0xe8,0xec,0xf0,0xf4,0xf8,0xfc,0xdc,0xbc,0x9c,0x7c,0x5c,0x3c,
        0x1c,0x18,0x14,0x10,0xc,0x8,0x4,0x25,0x45,0x65,0x85,0xa5,0xc5,0xc9,0xcd,0xd1,0xd5,0xd9,0xb9,0x99,0x79,0x59,0x39,0x35,0x31,
        0x2d,0x29,0x4a,0x6a,0x8a,0xaa,0xae,0xb2,0xb6,0x96,0x76,0x56,0x52,0x4e,0x6f,0x8f,0x93,0x73,0x6f,0x8f,0x93,0x73,0x4a,0x6a,
        0x8a,0xaa,0xae,0xb2,0xb6,0x96,0x76,0x56,0x52,0x4e,0x25,0x45,0x65,0x85,0xa5,0xc5,0xc9,0xcd,0xd1,0xd5,0xd9,0xb9,0x99,0x79,
        0x59,0x39,0x35,0x31,0x2d,0x29,0x0,0x20,0x40,0x60,0x80,0xa0,0xc0,0xe0,0xe4,0xe8,0xec,0xf0,0xf4,0xf8,0xfc,0xdc,0xbc,0x9c,
        0x7c,0x5c,0x3c,0x1c,0x18,0x14,0x10,0xc,0x8,0x4
    ]

        self.table_3p= [[0xff,0x89,0xf5,0x93,0x93,0xf5,0x89,0xff],
                        [0x0e,0x1f,0x3f,0x7e,0x7e,0x3f,0x1f,0x0e],
                        [0x18,0x3c,0x7e,0xff,0x18,0x18,0x18,0x18]];


        self.table_cha = [  [0x51,0x51,0x51,0x4a,0x4a,0x4a,0x44,0x44],
                            [0x18,0x1c,0x18,0x18,0x18,0x18,0x18,0x3c],
                            [0x3c,0x66,0x66,0x30,0x18,0x0c,0x06,0xf6],
                            [0x3c,0x66,0x60,0x38,0x60,0x60,0x66,0x3c],
                            [0x30,0x38,0x3c,0x3e,0x36,0x7e,0x30,0x30],
                            [0x3c,0x3c,0x18,0x18,0x18,0x18,0x3c,0x3c],
                            [0x66,0xff,0xff,0xff,0x7e,0x3c,0x18,0x18],
                            [0x66,0x66,0x66,0x66,0x66,0x66,0x7e,0x3c]];

        self.dat2 = [0x0,0x20,0x40,0x60,0x80,0xa0,0xc0,0xe0,0xe4,0xe8,0xec,0xf0,0xf4,0xf8,0xfc,0xdc,0xbc,0x9c,0x7c,0x5c,0x3c,0x1c,0x18,0x14,0x10,0xc,0x8,0x4]

        self.dat3 = [0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x16,0x26,0x36,0x46,0x56,0x66,0x65,0x64,0x63,0x62,0x61,0x60,0x50,0x40,0x30,0x20,0x10]
            # ~ "0001.dat" , # block of blue with varying brightness.  doesnt work.

        self.seq_list = [
            ("0000.dat" , 'all LEDs on'),
            ("0002.dat" , 'flat plane falling down once'),
            ("0003.dat" , 'flat plane falling down once'),
            ("0004.dat" , 'flat plane falling down once'),
            ("0005.dat" , 'full cube fill in from top'),
            ("0006.dat" , 'full cube fill in from top'),
            ("0007.dat" , 'full cube fill in from top'),
            ("0008.dat" , 'random rising dots'), # 
            ("0009.dat" , 'random rising dots'),
            ("0010.dat" , 'random rising dots'), # random rising dots
            ("0011.dat" , 'raining dots and rising dots. like red rover'),
            ("0012.dat" , 'raining dots and rising dots. like red rover'),
            ("0013.dat" , 'raining dots and rising dots. like red rover'), # raining dots and rising dots. like red rover
            ("0014.dat" , 'full sheet crumbling and falling quickly'),
            ("0015.dat" , 'full sheet crumbling and falling quickly'),
            ("0016.dat" , 'full sheet crumbling and falling quickly'),
            ("0017.dat" , 'vertical waving sheet'),
            ("0018.dat" , 'vertical waving sheet'),
            ("0019.dat" , 'vertical waving sheet'),
            ("0020.dat" , 'up and down plane from corner'),
            ("0021.dat" , 'back and forth twisting plane'),
            ("0022.dat" , 'twisting rotating sheet'),
            ("0023.dat" , 'twisting rotating sheet'),
            ("0024.dat" , 'falling streamer'), # falling streamer
            ("0025.dat" , 'Open arrow around edge'),
            ("0026.dat" , 'Open arrow around edge'),
            ("0027.dat" , 'I heart U - rotating'), # I heart U - rotating
            ("0028.dat" , 'random activation of all leds slowly'),
            ('flash_2'  , 'hourglass pyramid stuff'), # hourglass pyramid stuff
            ('flash_3'  , 'vertical plane sweeping sideways'),
            ('flash_4'  , 'vertical plane waving sideways'),
            ('flash_5'  , 'sideways pulsing pyramid plane'), # sideways pulsing pyramid plane
            ('flash_6'  , 'rains asian words maybe'), # rains asian words maybe
            ('flash_7'  , 'rotating edge and corner volumes'),
            ('flash_8'  , 'swiped in I heart U'),
            ('flash_9'  , 'twisting planes and other sequences'),
            ('flash_10' , 'corner pulses'),
            ('flash_11' , 'up and down sheet waves'),
            ('flash_12' , 'bouncing moto logo'),
            ('flash_13' , 'bouncing spehere'),
            ('flash_14' , 'multi-axis rotating I heart U. ends off'),
            ('flash_15' , 'Stretching in rotating I heart U'),
            ('flash_16' , 'I heart U around edge'),
            ('flash_17' , 'multi-axis flipping ring with axis pulses, thin'),
            ('flash_18' , 'multi-axis rotating ring with axis shafts, thin'),
            ('flash_19' , 'multi-axis rotating ring with axis shafts, thick'),
            ('flash_20' , 'multi-axis pac man'),
            ('flash_21' , 'rotating biting pacman'),
            ('flash_22' , 'stargate transport guy'),
            ('drum_1'   , 'drum surface pulsing'),
        ]
        
        self.u_last = -10000000
        self.zero_cross_count = 0
        
    def clear(self):
        self.display = []
        for x in range(64):
            self.display.append(0)

    def test_it(self):
        msg = 'f2' \
            '0100000000000000' \
            '0002000000000000' \
            '0000040000000000' \
            '0000000800000000' \
            '0000000010000000' \
            '0000000000200000' \
            '0000000000004000' \
            '0000000000000080'

        self.port.write(binascii.unhexlify(msg))

        time.sleep(0.5)

        msg = 'f2' \
            '0000000000000080' \
            '0000000000004000' \
            '0000000000200000' \
            '0000000010000000' \
            '0000000800000000' \
            '0000040000000000' \
            '0002000000000000' \
            '0100000000000000'

        self.port.write(binascii.unhexlify(msg))

        time.sleep(0.5)

        msg = 'f2' \
            '8000000000000000' \
            '0040000000000000' \
            '0000200000000000' \
            '0000001000000000' \
            '0000000008000000' \
            '0000000000040000' \
            '0000000000000200' \
            '0000000000000001'

        self.port.write(binascii.unhexlify(msg))
        time.sleep(0.5)

    def flash_12(self):
        self.clear()

        img =  ['..XXX...',
                '.X.X.X..',
                'XX.X.XX.',
                'X.X.X.X.',
                'X.X.X.X.',
                '.XXXXX..',
                '..XXX...',
                '........']
        img_inv=['........',
                 '..X.X...',
                 '..X.X...',
                 '.X.X.X..',
                 '.X.X.X..',
                 '........',
                 '........',
                 '........']
            # (left/right;  front/back;   up/down)

        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels_Mot = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)

        img_pixels_raw_inv = self.string_plane_to_xyz_list(img_inv, plane='xz')
        img_pixels_Mot_inv = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw_inv)

        self.clear();self.send_display()

        # ~ v_init = 0.4
        # ~ a = -.01
        v_init = 0.8
        a = -.02*2
        v = v_init
        d = 0.0
        for index in range(181):

            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_translate_matrix(  3.0,   4.0,   4.0-d).dot(transform)
            new_pixels = transform.dot(img_pixels_Mot); self.clear(); self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            d = d + v
            v = v + a
            if d < 0:
                d = 0
                v = -v
            # ~ v = v * (1-.01)



        for index in range(8):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_translate_matrix(  3.0,   4.0,   4.0).dot(transform)

            new_pixels = transform.dot(img_pixels_Mot); self.clear(); self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.25)
            new_pixels = transform.dot(img_pixels_Mot_inv); self.clear(); self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.25)



        for angle_index in range(16*2+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   4.0,   4.0).dot(transform)

            new_pixels = transform.dot(img_pixels_Mot)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16*2+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   4.0,   4.0).dot(transform)

            new_pixels = transform.dot(img_pixels_Mot)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16*2+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   4.0,   4.0).dot(transform)

            new_pixels = transform.dot(img_pixels_Mot)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

    def flash_13(self):
        self.clear()

        img =  ['..XXX...',
                '.X...X..',
                'X.....X.',
                'X.....X.',
                'X.....X.',
                '.X...X..',
                '..XXX...',
                '........']


            # (left/right;  front/back;   up/down)

        img_pixels_raw_1 = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels_1 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw_1)
        img_pixels_raw_2 = self.string_plane_to_xyz_list(img, plane='yz')
        img_pixels_2 = self.get_translate_matrix( 3,  0,  0).dot(img_pixels_raw_2)
        img_pixels_raw_3 = self.string_plane_to_xyz_list(img, plane='xy')
        img_pixels_3 = self.get_translate_matrix( 0,  0,  3).dot(img_pixels_raw_3)

        img_pixels_123 = np.append(img_pixels_1, img_pixels_2, axis=1)
        img_pixels_123 = np.append(img_pixels_123, img_pixels_3, axis=1)

        # ~ transform = self.get_translate_matrix( -0.0,  -0.0,  -0.0)

        # ~ self.clear();self.send_display()
        # ~ new_pixels = transform.dot(img_pixels_123); self.clear(); self.store_pixel_array(new_pixels);self.send_display()


        v_init = 0.8*1.4
        a = -.02*2*2
        v = v_init
        d = 0.0
        bounces = 5
        for index in range(1720):

            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0-d).dot(transform)
            new_pixels = transform.dot(img_pixels_123); self.clear(); self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            d = d + v
            v = v + a
            if d < 0:
                d = 0
                v = v_init
                bounces = bounces -1
                if bounces <= 0:
                    break



        for angle_index in range(16*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_123)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_123)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_123)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

    def flash_14(self):
        self.clear()

        img =  ['........',
                '.XXXXXX.',
                '...XX...',
                '...XX...',
                '...XX...',
                '...XX...',
                '.XXXXXX.',
                '........']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_I = np.append(img_pixels0, img_pixels1, axis=1)

        img =  ['.XX..XX.',
                'XXX..XXX',
                'XXXXXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '.XXXXXX.',
                '..XXXX..',
                '...XX...']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_heart = np.append(img_pixels0, img_pixels1, axis=1)


        img =  ['........',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '..XXXX..',
                '........']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_U = np.append(img_pixels0, img_pixels1, axis=1)

        for angle_index in range(16):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(16):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(64+1):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_heart)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(64+1):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_U)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.025)

    def flash_15(self):
        self.clear()

        img =  ['........',
                '.XXXXXX.',
                '...XX...',
                '...XX...',
                '...XX...',
                '...XX...',
                '.XXXXXX.',
                '........']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_I = np.append(img_pixels0, img_pixels1, axis=1)

        img =  ['.XX..XX.',
                'XXX..XXX',
                'XXXXXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '.XXXXXX.',
                '..XXXX..',
                '...XX...']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_heart = np.append(img_pixels0, img_pixels1, axis=1)


        img =  ['........',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '.XX..XX.',
                '..XXXX..',
                '........']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw)
        img_pixels1 = self.get_translate_matrix( 0,  4,  0).dot(img_pixels_raw)
        img_pixels_U = np.append(img_pixels0, img_pixels1, axis=1)

        angle=0
        for scale in range(32,-1,-1):
        # ~ for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            # ~ transform = self.get_scale_matrix( 1,  1,  1.0+scale/8.0).dot(transform)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_I);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            angle += 22.5
            time.sleep(0.025)

        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  0.0)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  0.0).dot(transform)

            new_pixels = transform.dot(img_pixels_I);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5

        # ~ for scale in range(32,-1,-1):
        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_I);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5

        for scale in range(32,-1,-1):
        # ~ for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            # ~ transform = self.get_scale_matrix( 1,  1,  1.0+scale/8.0).dot(transform)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_heart);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            angle += 22.5
            time.sleep(0.025)

        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  0.0)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  0.0).dot(transform)

            new_pixels = transform.dot(img_pixels_heart);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5

        # ~ for scale in range(32,-1,-1):
        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_heart);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5



        for scale in range(32,-1,-1):
        # ~ for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            # ~ transform = self.get_scale_matrix( 1,  1,  1.0+scale/8.0).dot(transform)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_U);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            angle += 22.5
            time.sleep(0.025)

        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  0.0)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  0.0).dot(transform)

            new_pixels = transform.dot(img_pixels_U);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5

        # ~ for scale in range(32,-1,-1):
        for scale in range(32):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -7.0)
            transform = self.get_scale_matrix( 1,  1,  2**(scale/3.0)).dot(transform)
            transform = self.get_rotate_z_matrix( angle).dot(transform)
            transform = self.get_translate_matrix( 3.5,  3.5,  7.0).dot(transform)

            new_pixels = transform.dot(img_pixels_U);self.clear();self.store_pixel_array(new_pixels);self.send_display()
            time.sleep(0.025)
            angle += 22.5

    def flash_16(self):
        self.clear()

        # ~ img =  ['X...X.XXXXX.X.....X......XXX..',
                # ~ 'X...X.X.....X.....X.....X...X.',
                # ~ 'X...X.X.....X.....X.....X...X.',
                # ~ 'XXXXX.XXXX..X.....X.....X...X.',
                # ~ 'X...X.X.....X.....X.....X...X.',
                # ~ 'X...X.X.....X.....X.....X...X.',
                # ~ 'X...X.XXXXX.XXXXX.XXXXX..XXX..',
                # ~ '..............................']
        img =  ['.........XX..XX...........',
                'XXXXXX..XXX..XXX...XX..XX.',
                '..XX....XXXXXXXX...XX..XX.',
                '..XX....XXXXXXXX...XX..XX.',
                '..XX.....XXXXXX....XX..XX.',
                '..XX.....XXXXXX....XX..XX.',
                'XXXXXX....XXXX......XXXX..',
                '...........XX.............']
        img_pixels_raw = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels_msg = self.get_translate_matrix( 0,  0,  0).dot(img_pixels_raw)

        angle = -0.0
        for pos in range(6*5+28):
        # ~ for pos in range(0,):
            self.clear();
            transform = self.get_scale_matrix( 1,  1,  1)
            transform = self.get_rotate_z_matrix(90).dot(transform)
            transform = self.get_translate_matrix( 0,  7-pos,  0).dot(transform)
            new_pixels = transform.dot(img_pixels_msg);self.store_pixel_array(new_pixels)

            transform = self.get_scale_matrix( 1.0,  1.0,  1.0)
            transform = self.get_rotate_z_matrix(180).dot(transform)
            transform = self.get_translate_matrix( -7+pos,  0,  0).dot(transform)
            new_pixels = transform.dot(img_pixels_msg);self.store_pixel_array(new_pixels)

            transform = self.get_scale_matrix( 1,  1,  1)
            transform = self.get_rotate_z_matrix(270).dot(transform)
            transform = self.get_translate_matrix( 7,  pos-14,  0).dot(transform)
            new_pixels = transform.dot(img_pixels_msg);self.store_pixel_array(new_pixels)

            transform = self.get_scale_matrix( 1,  1,  1)
            transform = self.get_rotate_z_matrix(0).dot(transform)
            transform = self.get_translate_matrix( 28-pos,  7,  0).dot(transform)
            new_pixels = transform.dot(img_pixels_msg);self.store_pixel_array(new_pixels)

            self.send_display()


    def flash_17(self):
        self.clear()

        img =  ['..XXX...',
                '.X...X..',
                'X.....X.',
                'X.....X.',
                'X.....X.',
                '.X...X..',
                '..XXX...',
                '........']

        point =  ['XXXXX']


            # (left/right;  front/back;   up/down)

        img_pixels_raw_1 = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels_1 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw_1)

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xz')
        img_pixels_point = self.get_translate_matrix( 0,  0,  0).dot(img_pixels_raw_point)



        for angle_index in range(16*4):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_z_matrix( 90)
            transform2 = self.get_translate_matrix( 3,  3-2-((angle_index*2)%32)+16,  3).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            # ~ time.sleep(0.025)

        for angle_index in range(4*1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_y_matrix( -90)
            transform2 = self.get_translate_matrix( 3,  3,  3-2-((angle_index*2)%32)+16).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            # ~ time.sleep(0.025)

        for angle_index in range(4*1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_y_matrix( 0)
            transform2 = self.get_translate_matrix( 3-2-((angle_index*2)%32)+16,  3,  3).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            # ~ time.sleep(0.025)




    def flash_18(self):
        self.clear()

        img =  ['..XXX...',
                '.X.X.X..',
                'X.....X.',
                'X.....X.',
                'X.....X.',
                '.X.X.X..',
                '..XXX...',
                '........']

        point =  ['XXXXX']


            # (left/right;  front/back;   up/down)

        img_pixels_raw_1 = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels_1 = self.get_translate_matrix( 0,  3,  0).dot(img_pixels_raw_1)

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xz')
        img_pixels_point = self.get_translate_matrix( 0,  0,  0).dot(img_pixels_raw_point)



        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_z_matrix( 90)
            transform2 = self.get_translate_matrix( 3,  3-2-((angle_index*2)%32)+16,  3).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_y_matrix( -90)
            transform2 = self.get_translate_matrix( 3,  3,  3-2-((angle_index*2)%32)+16).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            transform2 = self.get_rotate_y_matrix( 0)
            transform2 = self.get_translate_matrix( 3-2-((angle_index*2)%32)+16,  3,  3).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( -3.0,  -3.0,  -3.0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.0,   3.0,   3.0).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)


    def flash_19(self):
        self.clear()

        img =  ['..XXXX..',
                '.X.XX.X.',
                'X......X',
                'X......X',
                'X......X',
                'X......X',
                '.X.XX.X.',
                '..XXXX..']

        point =  ['XXXXXX',
                  'XXXXXX']


            # (left/right;  front/back;   up/down)

        img_pixels_raw_1 = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels0 = self.get_translate_matrix(-3.5, -0.5, -3.5).dot(img_pixels_raw_1)
        img_pixels1 = self.get_translate_matrix(-3.5,  0.5, -3.5).dot(img_pixels_raw_1)
        img_pixels_1 = np.append(img_pixels0, img_pixels1, axis=1)

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xz')
        img_pixels_point0 = self.get_translate_matrix(-2.5, -0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point1 = self.get_translate_matrix(-2.5,  0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point = np.append(img_pixels_point0, img_pixels_point1, axis=1)


        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_z_matrix( 90)
            transform2 = self.get_translate_matrix( 3.5,  3.5-1-((angle_index*2)%32)+16,  3.5).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_y_matrix( -90)
            transform2 = self.get_translate_matrix( 3.5,  3.5,  3.5-1-((angle_index*2)%32)+16).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(16*4+4+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_y_matrix( 0)
            transform2 = self.get_translate_matrix( 3.5-1-((angle_index*2)%32)+16,  3.5,  3.5).dot(transform2)

            new_pixels = transform.dot(img_pixels_1)
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1)
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

    def get_pac_man_phase(self, raw_phase):
        local_phase = raw_phase % 8
        if local_phase > 4:
            local_phase = 8-local_phase
        return local_phase

    def flash_20(self):

        img = [
               ['..XXXX..',
                '.XXXXXX.',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['..XXXX..',
                '.XXXXXX.',
                'XXXXXXXX',
                '...XXXXX',
                '...XXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['..XXXX..',
                '.XXXXXX.',
                '...XXXXX',
                '...XXXXX',
                '...XXXXX',
                '...XXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['...XXX..',
                '...XXXX.',
                '...XXXXX',
                '....XXXX',
                '....XXXX',
                '...XXXXX',
                '...XXXX.',
                '...XXX..'],

               ['....XX..',
                '....XXX.',
                '....XXXX',
                '....XXXX',
                '....XXXX',
                '....XXXX',
                '....XXX.',
                '....XX..'],
                ]


        point =  ['XX',
                  'XX']



            # (left/right;  front/back;   up/down)
        img_pixels_1 = []
        for frame_index in range(len(img)):
            img_pixels_raw_1 = self.string_plane_to_xyz_list(img[frame_index], plane='xz')
            img_pixels0 = self.get_translate_matrix(-3.5, -0.5, -3.5).dot(img_pixels_raw_1)
            img_pixels1 = self.get_translate_matrix(-3.5,  0.5, -3.5).dot(img_pixels_raw_1)
            img_pixels_1.append( np.append(img_pixels0, img_pixels1, axis=1) )

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xz')
        img_pixels_point0 = self.get_translate_matrix(-0.5, -0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point1 = self.get_translate_matrix(-0.5,  0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point = np.append(img_pixels_point0, img_pixels_point1, axis=1)


        # grow in circle
        for angle_index in range(3,-1,-1):
            transform = self.get_scale_matrix( (4.0-angle_index)/4, (4.0-angle_index)/4, (4.0-angle_index)/4 )
            # transform = self.get_rotate_y_matrix( 22.5*3).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(0)])
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.25)



        for angle_index in range(8*4+1):
            transform = self.get_translate_matrix( 0,0,0)
            # transform = self.get_rotate_y_matrix( 22.5*3).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_z_matrix( 0)
            transform2 = self.get_translate_matrix( 3.5+angle_index-9,  3.5,  3.5).dot(transform2)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(angle_index)])
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            # self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1[0])
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(8*4+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_y_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            # transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_y_matrix( -90)
            transform2 = self.get_translate_matrix( 3.5,  3.5,  3.5-2-angle_index*2+16).dot(transform2)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(angle_index)])
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            # self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1[0])
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        for angle_index in range(8*4+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_x_matrix( 90).dot(transform)
            #transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_y_matrix( 0)
            transform2 = self.get_translate_matrix( 3.5-2-angle_index*2+16,  3.5,  3.5).dot(transform2)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(angle_index)])
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            #self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)

        for angle_index in range(4*1+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_z_matrix( 90).dot(transform)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1[0])
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.125)

        # shrink out circle
        for angle_index in range(0,4):
            transform = self.get_scale_matrix( (4.0-angle_index)/4, (4.0-angle_index)/4, (4.0-angle_index)/4 )
            # transform = self.get_rotate_y_matrix( 22.5*3).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(0)])
            self.clear()
            self.store_pixel_array(new_pixels)
            self.send_display()
            time.sleep(0.25)


    def flash_21(self):

        img = [
               ['..XXXX..',
                '.XXXXXX.',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['..XXXX..',
                '.XXXXXX.',
                'XXXXXXXX',
                '...XXXXX',
                '...XXXXX',
                'XXXXXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['..XXXX..',
                '.XXXXXX.',
                '...XXXXX',
                '...XXXXX',
                '...XXXXX',
                '...XXXXX',
                '.XXXXXX.',
                '..XXXX..'],

               ['...XXX..',
                '...XXXX.',
                '...XXXXX',
                '....XXXX',
                '....XXXX',
                '...XXXXX',
                '...XXXX.',
                '...XXX..'],

               ['....XX..',
                '....XXX.',
                '....XXXX',
                '....XXXX',
                '....XXXX',
                '....XXXX',
                '....XXX.',
                '....XX..'],
                ]


        point =  ['XX',
                  'XX']



            # (left/right;  front/back;   up/down)
        img_pixels_1 = []
        for frame_index in range(len(img)):
            img_pixels_raw_1 = self.string_plane_to_xyz_list(img[frame_index], plane='xz')
            img_pixels0 = self.get_translate_matrix(-3.5, -0.5, -3.5).dot(img_pixels_raw_1)
            img_pixels1 = self.get_translate_matrix(-3.5,  0.5, -3.5).dot(img_pixels_raw_1)
            img_pixels_1.append( np.append(img_pixels0, img_pixels1, axis=1) )

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xz')
        img_pixels_point0 = self.get_translate_matrix(-0.5, -0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point1 = self.get_translate_matrix(-0.5,  0.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point = np.append(img_pixels_point0, img_pixels_point1, axis=1)


        for angle_index in range(8*16+1):
            transform = self.get_translate_matrix( 0,0,0)
            transform = self.get_rotate_z_matrix( 90.0/32*angle_index).dot(transform)
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5).dot(transform)

            transform2 = self.get_rotate_z_matrix( 0)
            transform2 = self.get_translate_matrix( 3.5+angle_index-9,  3.5,  3.5).dot(transform2)

            new_pixels = transform.dot(img_pixels_1[self.get_pac_man_phase(angle_index)])
            new_pixels2 = transform2.dot(img_pixels_point)
            self.clear()
            self.store_pixel_array(new_pixels)
            # self.store_pixel_array(new_pixels2)
            self.send_display()
            time.sleep(0.025)


    def flash_22(self):
        self.clear()

        img =  ['..XXXX..',
                '.X....X.',
                'X......X',
                'X......X',
                'X......X',
                'X......X',
                '.X....X.',
                '..XXXX..']

        point= ['........',
                '........',
                '...XX...',
                '..X..X..',
                '..X..X..',
                '...XX...',
                '........',
                '........']

        guy = [
               ['...XX...',
                '...XX...',
                '..XXXX..',
                '.X.XX.X.',
                '.X.XX.X.',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX...',
                '..XXXXX.',
                '.X.XX..X',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX...',
                '..XXXXXX',
                '.X.XX...',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX..X',
                '..XXXXX.',
                '.X.XX...',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX..X',
                '...XX..X',
                '..XXXXX.',
                '.X.XX...',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX...',
                '..XXXXXX',
                '.X.XX...',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX...',
                '..XXXXX.',
                '.X.XX..X',
                '.X.XX...',
                '...XX...',
                '...XX...'],

               ['...XX...',
                '...XX...',
                '..XXXX..',
                '.X.XX.X.',
                '.X.XX.X.',
                '...XX...',
                '...XX...'],
                ]




            # (left/right;  front/back;   up/down)
        img_pixels_guy = []
        for frame_index in range(len(guy)):
            img_pixels_raw_1 = self.string_plane_to_xyz_list(guy[frame_index], plane='xz')
            img_pixels_guy.append( img_pixels_raw_1 )



            # (left/right;  front/back;   up/down)

        img_pixels_raw_1 = self.string_plane_to_xyz_list(img, plane='xy')
        img_pixels0 = self.get_translate_matrix(-3.5, -3.5,  0.5).dot(img_pixels_raw_1)
        img_pixels1 = self.get_translate_matrix(-3.5, -3.5, -0.5).dot(img_pixels_raw_1)
        img_pixels_1 = np.append(img_pixels0, img_pixels1, axis=1)

        img_pixels_raw_point = self.string_plane_to_xyz_list(point, plane='xy')
        img_pixels_point0 = self.get_translate_matrix(-3.5, -3.5,  3.5).dot(img_pixels_raw_point)
        img_pixels_point1 = self.get_translate_matrix(-3.5, -3.5,  2.5).dot(img_pixels_raw_point)
        img_pixels_point2 = self.get_translate_matrix(-3.5, -3.5,  1.5).dot(img_pixels_raw_point)
        img_pixels_point3 = self.get_translate_matrix(-3.5, -3.5,  0.5).dot(img_pixels_raw_point)
        img_pixels_point4 = self.get_translate_matrix(-3.5, -3.5, -0.5).dot(img_pixels_raw_point)
        img_pixels_point5 = self.get_translate_matrix(-3.5, -3.5, -1.5).dot(img_pixels_raw_point)
        img_pixels_point6 = self.get_translate_matrix(-3.5, -3.5, -2.5).dot(img_pixels_raw_point)
        img_pixels_point7 = self.get_translate_matrix(-3.5, -3.5, -3.5).dot(img_pixels_raw_point)
        img_pixels_point = np.append(img_pixels_point0, img_pixels_point1, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point2, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point3, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point4, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point5, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point6, axis=1)
        img_pixels_point = np.append(img_pixels_point, img_pixels_point7, axis=1)



        for which_half in range(2):
            # no rings.  bring in next
            for pos in range(0,8,2):
                self.clear()
                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)

                if which_half: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

                self.send_display()
                
            self.clear() ;
            if which_half: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()


            # one rings.  bring in next
            for pos in range(0,6,2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)

                if which_half: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()



            # two rings.  bring in next
            for pos in range(0,4,2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)

                if which_half: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()


            # three rings.  bring in next
            for pos in range(0,2,2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)
                
                if which_half: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   5.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()

            time.sleep(1)

            # 4 rings present.  do flash the energy core
            for index in range(8):
                self.clear() ;
                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   5.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

                if (index/4)^which_half: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

                if (index % 2) == 0:
                    transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
                    new_pixels = transform.dot(img_pixels_point); self.store_pixel_array(new_pixels)
                self.send_display()




            time.sleep(1)



            # 3 static rings.  one going out
            for pos in range(0,2,2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)
                
                if which_half^1: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half^1: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()


            # two static rings.  next going out
            for pos in range(2,-2,-2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)
                transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
                new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)
                if which_half^1: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half^1: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   1.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()


            # one static rings.  next going out
            for pos in range(4,-2,-2):
                self.clear()

                transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
                new_pixels = transform.dot(img_pixels0);self.store_pixel_array(new_pixels)

                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)

                if which_half^1: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half^1: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)

            transform = self.get_translate_matrix(  3.5,   3.5,   -0.5)
            new_pixels = transform.dot(img_pixels0); self.store_pixel_array(new_pixels);self.send_display()


            # no static rings.  take out next
            for pos in range(6,-2,-2):
                self.clear()
                transform = self.get_translate_matrix( 0,0,0)
                transform = self.get_translate_matrix(  3.5,   3.5,   6.5-pos).dot(transform)

                new_pixels = transform.dot(img_pixels_1); self.store_pixel_array(new_pixels)

                if which_half^1: # draw guy
                    transform = self.get_translate_matrix( 0,   3.5,   1)
                    new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
                self.send_display()

            self.clear() ;
            if which_half^1: # draw guy
                transform = self.get_translate_matrix( 0,   3.5,   1)
                new_pixels = transform.dot(img_pixels_guy[0]); self.store_pixel_array(new_pixels)
            self.send_display()

            time.sleep(1)

            # guy waving
            if which_half^1:
                for index in range(64+1):
                    self.clear() ;
                    # ~ transform = self.get_translate_matrix( 0,   3.5,   1)
                    transform = self.get_translate_matrix( -3.5,0,0)
                    transform = self.get_rotate_z_matrix( 5.625*index).dot(transform)
                    transform = self.get_translate_matrix(  3.5,   4,   1).dot(transform)
                    
                    
                    new_pixels = transform.dot(img_pixels_guy[index%len(img_pixels_guy)]); self.store_pixel_array(new_pixels)

                    self.send_display()

            time.sleep(1)




    def send_display(self):
        for i in range(len(self.display)):
            # ~ if self.display[i] < 0:
                # ~ print(self.display[i])
            self.display[i] = self.display[i] & 0xff
        format = '>' + 'B'*65
        msg = struct.pack(format, 0xf2, *self.display)
        self.port.write(msg)

    def send_file(self, filename, delay):
        fh = open(filename, 'rb')

        while True:
            data = list(fh.read(0x48))

            if len(data) == 0:
                break;

            if ord(data[0]) == 0xf2:
                # ~ print('found start f2')
                data = data[8:]

                intdata = []
                for index in range(64):
                    intdata.append(ord(data[index]))

                self.clear()
                pixel_list = self.correct_orientation(intdata)
                self.store_pixel_array(pixel_list)
                self.send_display()

            bytesread = 0

    def store_pixel_array(self, pixel_array):
        cols = np.size(pixel_array,1)
        # ~ print(pixel_array)
        for col in range(cols):
            self.store_pixel(x=pixel_array[0,col], y=pixel_array[1,col], z=pixel_array[2,col], state=1)

    def point(self, x, y, z, enable):
        self.store_pixel(x=x, y=y, z=z, state=enable)

    def store_pixel(self, x=0, y=0, z=0, state=0):
        # ~ rounded_x = int(x+0.5)
        # ~ rounded_y = int(y+0.5)
        # ~ rounded_z = int(z+0.5)
        rounded_x = int(math.floor(x+0.5))
        rounded_y = int(math.floor(y+0.5))
        rounded_z = int(math.floor(z+0.5))

        if (rounded_x>=0 and rounded_x<8 and rounded_y>=0 and rounded_y<8 and rounded_z>=0 and rounded_z<8):
            index = rounded_z*8+rounded_y
            if state == 1:
                self.display[index] |= 1<<rounded_x
            else:
                self.display[index] &= ~(1<<rounded_x)

    def correct_orientation(self, orig_display):
        pixel_coords = np.array([[],[],[],[]])
        for old_z in range(8):
            for old_y in range(8):
                for old_x in range(8):
                    index = 8*old_z+old_y
                    if (orig_display[index]>>old_x) & 0x01:
                        new_pixel = np.array([[old_x], [old_y], [old_z], [1]])
                        pixel_coords = np.append(pixel_coords, new_pixel, axis=1)

        transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
        transform = self.get_rotate_y_matrix(-90).dot(transform)
        transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

        new_pixels = transform.dot(pixel_coords)

        return new_pixels


    def string_plane_to_xyz_list(self, pixel_list, plane='xy'):
        pixel_coords = np.array([[],[],[],[]])
        for y in range(len(pixel_list)):
            for x in range(len(pixel_list[y])):
                if pixel_list[y][x] == 'X':
                    if plane == 'xy':
                        new_pixel = np.array([[x], [y], [0], [1]])
                    elif plane == 'yz':
                        new_pixel = np.array([[0], [x], [y], [1]])
                    elif plane == 'xz':
                        new_pixel = np.array([[x], [0], [y], [1]])
                    pixel_coords = np.append(pixel_coords, new_pixel, axis=1)

        return pixel_coords

    def get_translate_matrix(self, tx, ty, tz):
        translate_matrix = np.array([
            [ 1.0 ,0   ,0   ,tx  ],
            [ 0   ,1.0 ,0   ,ty  ],
            [ 0   ,0   ,1.0 ,tz  ],
            [ 0   ,0   ,0   ,1.0 ]])
        return translate_matrix

    def get_scale_matrix(self, sx, sy, sz):
        translate_matrix = np.array([
            [ sx  ,0   ,0   ,0   ],
            [ 0   ,sy  ,0   ,0   ],
            [ 0   ,0   ,sz  ,0   ],
            [ 0   ,0   ,0   ,1.0 ]])
        return translate_matrix

    def get_rotate_x_matrix(self, rotate_degrees):
        thetaX = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [1, 0               ,  0               ,0],
            [0, math.cos(thetaX), -math.sin(thetaX),0],
            [0, math.sin(thetaX),  math.cos(thetaX),0],
            [0, 0               ,  0               ,1]])

        return matrix

    def get_rotate_y_matrix(self, rotate_degrees):
        thetaY = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ math.cos(thetaY),0  , math.sin(thetaY),0],
            [ 0               ,1  ,  0              ,0],
            [-math.sin(thetaY),0  , math.cos(thetaY),0],
            [ 0               ,0  ,  0               ,1]])

        return matrix

    def get_rotate_z_matrix(self, rotate_degrees):
        thetaZ = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ math.cos(thetaZ), -math.sin(thetaZ),0  ,0],
            [ math.sin(thetaZ),  math.cos(thetaZ),0  ,0],
            [ 0               ,  0               ,1  ,0],
            [ 0               ,  0               ,0  ,1]])

        return matrix


    def get_4d_translate_matrix(self, tx, ty, tz, tw):
        translate_matrix = np.array([
            [ 1.0 ,0   ,0   ,0   ,tx  ],
            [ 0   ,1.0 ,0   ,0   ,ty  ],
            [ 0   ,0   ,1.0 ,0   ,tz  ],
            [ 0   ,0   ,0   ,1.0 ,tw  ],
            [ 0   ,0   ,0   ,0   ,1.0 ]])
        return translate_matrix

    def get_4d_scale_matrix(self, sx, sy, sz, sw):
        translate_matrix = np.array([
            [ sx  ,0   ,0   ,0   ,0   ],
            [ 0   ,sy  ,0   ,0   ,0   ],
            [ 0   ,0   ,sz  ,0   ,0   ],
            [ 0   ,0   ,0   ,sw  ,0   ],
            [ 0   ,0   ,0   ,0   ,1.0 ]])
        return translate_matrix

    def get_4d_rotate_zw_matrix(self, rotate_degrees):
        thetaX = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ math.cos(thetaZ), -math.sin(thetaZ),0  ,0  ,0],
            [ math.sin(thetaZ),  math.cos(thetaZ),0  ,0  ,0],
            [ 0               ,  0               ,1  ,0  ,0],
            [ 0               ,  0               ,0  ,1  ,0],
            [ 0               ,  0               ,0  ,0  ,1]])


        return matrix

    def get_4d_rotate_yw_matrix(self, rotate_degrees):
        thetaY = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ math.cos(thetaY),0  ,-math.sin(thetaY),0 ,0],
            [ 0               ,1  ,  0              ,0 ,0],
            [ math.sin(thetaY),0  , math.cos(thetaY),0 ,0],
            [ 0               ,0  ,  0              ,1 ,0],
            [ 0               ,0  ,  0              ,0 ,1]])

        return matrix

    def get_4d_rotate_yz_matrix(self, rotate_degrees):
        thetaZ = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ math.cos(thetaZ),0 ,0 , -math.sin(thetaZ) ,0],
            [ 0               ,1 ,0 ,  0                ,0],
            [ 0               ,0 ,1 ,  0                ,0],
            [ math.sin(thetaZ),0 ,0 ,  math.cos(thetaZ) ,0],
            [ 0               ,0 ,0 ,  0                ,1]])

        return matrix

    def get_4d_rotate_xw_matrix(self, rotate_degrees):
        thetaZ = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ 1 ,0               ,  0               ,0  ,0],
            [ 0 ,math.cos(thetaZ), -math.sin(thetaZ),0  ,0],
            [ 0 ,math.sin(thetaZ),  math.cos(thetaZ),0  ,0],
            [ 0 ,0               ,  0               ,1  ,0],
            [ 0 ,0               ,  0               ,0  ,1]])

        return matrix

    def get_4d_rotate_xz_matrix(self, rotate_degrees):
        thetaZ = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ 1 ,0               ,0 ,  0                ,0],
            [ 0 ,math.cos(thetaZ),0 , -math.sin(thetaZ) ,0],
            [ 0 ,0               ,1 ,  0                ,0],
            [ 0 ,math.sin(thetaZ),0 ,  math.cos(thetaZ) ,0],
            [ 0 ,0               ,0 ,  0                ,1]])

        return matrix

    def get_4d_rotate_xy_matrix(self, rotate_degrees):
        thetaZ = rotate_degrees * 2.0 * np.pi / 360.0
        matrix = np.array([
            [ 1 ,0 ,0               ,  0                ,0],
            [ 0 ,1 ,0               ,  0                ,0],
            [ 0 ,0 ,math.cos(thetaZ), -math.sin(thetaZ) ,0],
            [ 0 ,0 ,math.sin(thetaZ),  math.cos(thetaZ) ,0],
            [ 0 ,0 ,0               ,  0                ,1]])

        return matrix


    def math_test(self):
        # ~ orig = np.array( [[1],[1],[1],[1]])
        orig = np.array( [[0,1],[0,1],[0,1],[1,1]])
        print(orig)

        transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
        transform = self.get_rotate_z_matrix( 90.0).dot(transform)
        transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)

        new = transform.dot(orig)
        print(new)

        new = transform.dot(new)
        print(new)
        new = transform.dot(new)
        print(new)
        new = transform.dot(new)
        print(new)


        grid = ['X.......',
                '........',
                '........',
                '........',
                '........',
                '........',
                '........',
                '.......X']
        print( self.string_plane_to_xyz_list(grid))


# ~ __code uchar dat[128]= { /*railway*/








    # ~ void cirp(char cpp, uchar dir, uchar le)
    # ~ {
    def cirp(self, cpp, dir, le):

        # ~ uchar a, b, c, cp;
        # ~ // if ((cpp < 128) & (cpp >= 0)) {
        # ~ if (cpp >= 0) {
        if (cpp >= 0):

            # ~ if (dir) {
            if (dir):
                # ~ cp = 127 - cpp;
                cp = 127 - cpp

            # ~ }
            # ~ else {
            else:
                # ~ cp = cpp;
                cp = cpp
            # ~ }

            if (cp >= len(self.dat)-1 or cp<0):
                return

            # ~ a = (dat[cp] >> 5) & 0x07;
            a = (self.dat[cp] >> 5) & 0x07;
            # ~ b = (dat[cp] >> 2) & 0x07;
            b = (self.dat[cp] >> 2) & 0x07;
            # ~ c = dat[cp] & 0x03;
            c = self.dat[cp] & 0x03;
            # ~ if (cpp > 63) {
            if (cpp > 63):
                # ~ c=7-c;
                c=7-c
            # ~ }
            # ~ point(a,b,c,le);
            self.store_pixel(a,b,c,le);
        # ~ }
    # ~ }


    # ~ void box_apeak_xy(uchar x1,uchar y1,uchar z1,uchar x2,uchar y2,uchar z2,uchar fill,uchar le)
    # ~ {
        # ~ uchar i;
    def box_apeak_xy(self, x1, y1, z1, x2, y2, z2, fill, le):
        # ~ max(&z1,&z2);
        z1,z2 = self.max(z1,z2)
        # ~ if (fill) {
        if (fill):
            # ~ for (i=z1; i<=z2; i++) {
            for i in range(z1,z2+1,1):
                # ~ line (x1,y1,i,x2,y2,i,le);
                self.line (x1,y1,i,x2,y2,i,le)
            # ~ }
        # ~ } else {
        else:
            # ~ line (x1,y1,z1,x2,y2,z1,le);
            self.line (x1,y1,z1,x2,y2,z1,le)
            # ~ line (x1,y1,z2,x2,y2,z2,le);
            self.line (x1,y1,z2,x2,y2,z2,le)
            # ~ line (x2,y2,z1,x2,y2,z2,le);
            self.line (x2,y2,z1,x2,y2,z2,le)
            # ~ line (x1,y1,z1,x1,y1,z2,le);
            self.line (x1,y1,z1,x1,y1,z2,le)

    # ~ void roll_apeak_yz(uchar n,uint speed)
    def roll_apeak_yz(self, n, speed):
        # ~ switch(n) {
        # ~ case 1:
        if n == 1:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ display[frame][i][7]=0;
                self.display[i*8+7]=0;
                # ~ display[frame][7][6-i]=255;
                self.display[7*8+ 6-i]=255;
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 2:
        elif n == 2:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ display[frame][7][7-i]=0;
                self.display[7*8+ 7-i]=0;
                # ~ display[frame][6-i][0]=255;
                self.display[(6-i)*8+0]=255;
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 3:
        elif n == 3:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ display[frame][7-i][0]=0;
                self.display[(7-i)*8+0]=0;
                # ~ display[frame][0][i+1]=255;
                self.display[0*8+i+1]=255;
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 0:
        elif n == 0:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ display[frame][0][i]=0;
                self.display[0*8+i]=0;
                # ~ display[frame][i+1][7]=255;
                self.display[(i+1)*8+7]=255;
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()


    # ~ void roll_3_xy(uchar n,uint speed)
    def roll_3_xy(self, n, speed):

        # ~ switch(n) {
        # ~ case 1:
        if n == 1:
            # ~ for (i=0; i<8; i++) {
            for i in range(8):
                # ~ box_apeak_xy (0,i,0,7,7-i,7,1,1);
                self.box_apeak_xy (0,i,0,7,7-i,7,1,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
                # ~ if (i<7)
                if (i<7):
                    # ~ box_apeak_xy (3,3,0,0,i,7,1,0);
                    self.box_apeak_xy (3,3,0,0,i,7,1,0);
        # ~ case 2:
        elif n == 2:
            # ~ for (i=0; i<8; i++) {
            for i in range(8):
                # ~ box_apeak_xy (7-i,0,0,i,7,7,1,1);
                self.box_apeak_xy (7-i,0,0,i,7,7,1,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
                # ~ if (i<7)
                if (i<7):
                    # ~ box_apeak_xy (3,4,0,i,7,7,1,0);
                    self.box_apeak_xy (3,4,0,i,7,7,1,0);
        # ~ case 3:
        elif n == 3:
            # ~ for (i=0; i<8; i++) {
            for i in range(8):
                # ~ box_apeak_xy (0,i,0,7,7-i,7,1,1);
                self.box_apeak_xy (0,i,0,7,7-i,7,1,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
                # ~ if (i<7)
                if (i<7):
                    # ~ box_apeak_xy (4,4,0,7,7-i,7,1,0);
                    self.box_apeak_xy (4,4,0,7,7-i,7,1,0);
        # ~ case 0:
        elif n == 0:
            # ~ for (i=0; i<8; i++) {
            for i in range(8):
                # ~ box_apeak_xy (7-i,0,0,i,7,7,1,1);
                self.box_apeak_xy (7-i,0,0,i,7,7,1,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
                # ~ if (i<7)
                if (i<7):
                    # ~ box_apeak_xy (4,3,0,7-i,0,7,1,0);
                    self.box_apeak_xy (4,3,0,7-i,0,7,1,0);




    # ~ void roll_apeak_xy(uchar n,uint speed)
    def roll_apeak_xy(self, n, speed):
        # ~ switch(n) {
        # ~ case 1:
        if n == 1:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ line(0,i,0,0,i,7,0);
                self.line(0,i,0,0,i,7,0);
                # ~ line(i+1,7,0,i+1,7,7,1);
                self.line(i+1,7,0,i+1,7,7,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 2:
        elif n == 2:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ line(i,7,0,i,7,7,0);
                self.line(i,7,0,i,7,7,0);
                # ~ line(7,6-i,0,7,6-i,7,1);
                self.line(7,6-i,0,7,6-i,7,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 3:
        elif n == 3:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ line(7,7-i,0,7,7-i,7,0);
                self.line(7,7-i,0,7,7-i,7,0);
                # ~ line(6-i,0,0,6-i,0,7,1);
                self.line(6-i,0,0,6-i,0,7,1);
                # ~ delay(speed);
                time.sleep(speed*0.000005); self.send_display()
        # ~ case 0:
        elif n == 0:
            # ~ for (i=0; i<7; i++) {
            for i in range(7):
                # ~ line(7-i,0,0,7-i,0,7,0);
                self.line(7-i,0,0,7-i,0,7,0);
                # ~ line(0,i+1,0,0,i+1,7,1);
                self.line(0,i+1,0,0,i+1,7,1);
                time.sleep(speed*0.000005); self.send_display()

    # ~ void tranoutchar(uchar c,uint speed)
    def tranoutchar(self, c, speed):
        # ~ uchar i,j,k,a,i2=0;
        i2=0;
        # ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ if (i<7)
            if (i<7):
                # ~ box_apeak_xy (i+1,0,0,i+1,7,7,1,1);
                self.box_apeak_xy (i+1,0,0,i+1,7,7,1,1);
            # ~ box_apeak_xy (i2,0,0,i2,7,7,1,0);
            self.box_apeak_xy (i2,0,0,i2,7,7,1,0);
            # ~ a=0;
            a=0;
            # ~ i2=i+1;
            i2=i+1;
            # ~ for (j=0; j<=i; j++) {
            for j in range(i+1):
                # ~ a=a|(1<<j);
                a=a|(1<<j);

            # ~ for (k=0; k<8; k++) {
            for k in range(8):
                # ~ display[frame][k][3]|=table_cha[c][k]&a;
                self.display[k*8+3] = self.display[k*8+3] | self.table_cha[c][k]&a;
                # ~ display[frame][k][4]|=table_cha[c][k]&a;
                self.display[k*8+4] = self.display[k*8+4] | self.table_cha[c][k]&a;
            # ~ delay(speed);
            time.sleep(speed*0.000005); self.send_display()

    # ~ void max(uchar *a,uchar *b)
    def max(self, a, b):
        # ~ if ((*a)>(*b)) {
            # ~ t=(*a);
            # ~ (*a)=(*b);
            # ~ (*b)=t;
        if a>b:
            return b,a
        else:
            return a,b


     # ~ /*The function is to figure out the max number and return it.*/
    # ~ uchar maxt(uchar a,uchar b,uchar c)
    def maxt(self, a, b, c):
        # ~ if (a<b)
            # ~ a=b;
        # ~ if (a<c)
            # ~ a=c;
        # ~ return a;
        biggest = a
        if biggest<b:
            biggest = b
        if biggest<c:
            biggest = c
        return biggest

    # ~ // /*To figure out the round number*/
    # ~ uchar abs(uchar a)
    def abs(self, a):
        # ~ b=a/10;
        b=int(a/10);
        # ~ a=a-b*10;
        a=a-b*10;
        # ~ if (a>=5)
        if (a>=5):
            # ~ b++;
            b = b + 1
        # ~ return b;
        return b;


    # ~ /*To figure out the absolute value*/
    # ~ uchar abss(char a)
    def abss(self, a):
        # ~ if (a<0)
        if (a<0):
            # ~ a=-a;
            a=-a
        # ~ return a;
        return a



    # ~ void line(uchar x1,uchar y1,uchar z1,uchar x2,uchar y2,uchar z2,uchar le)
    # ~ {
        # ~ char t,a,b,c,a1,b1,c1,i;
    def line(self, x1, y1, z1, x2, y2, z2, le):
        # ~ a1=x2-x1;
        a1=x2-x1;
        # ~ b1=y2-y1;
        b1=y2-y1;
        # ~ c1=z2-z1;
        c1=z2-z1;
        # ~ t=maxt(abss(a1),abss(b1),abss(c1));
        t=self.maxt(self.abss(a1),self.abss(b1),self.abss(c1));
        if t == 0:
            t=1 # something is wrong with this stupid thing
        # ~ a=x1*10;
        # ~ b=y1*10;
        # ~ c=z1*10;
        # ~ a1=a1*10/t;
        # ~ b1=b1*10/t;
        # ~ c1=c1*10/t;
        a=x1*10
        b=y1*10
        c=z1*10
        a1=a1*10/t
        b1=b1*10/t
        c1=c1*10/t
        # ~ for (i=0; i<t; i++) {
        for i in range(t):
            # ~ point(abs(a),abs(b),abs(c),le);
            self.point(self.abs(a),self.abs(b),self.abs(c),le);
            # ~ a+=a1;
            # ~ b+=b1;
            # ~ c+=c1;
            a+=a1
            b+=b1
            c+=c1
        # ~ }
        # ~ point(x2,y2,z2,le);
        self.point(x2,y2,z2,le)


    # ~ void trans(uchar z,uint speed)
    def trans(self, z, speed):
        # ~ for (j=0; j<8; j++) {
        for j in range(8):
            # ~ for (i=0; i<8; i++) {
            for i in range(8):
                # ~ display[frame][z][i]>>=1;
                self.display[z*8+i] = self.display[z*8+i] >> 1;
            # ~ delay(speed);
            time.sleep(speed*0.000005); self.send_display()


    # ~ void transss()
    def transss(self):
        # ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ for (j=0; j<8; j++)
            for j in range(8):
                # ~ display[frame][i][j]<<=1;
                self.display[i*8+j] = self.display[i*8+j] << 1;



    # ~ void box(uchar x1,uchar y1,uchar z1,uchar x2,uchar y2,uchar z2,uchar fill,uchar le)
    def box(self, x1, y1, z1, x2, y2, z2, fill, le):
        # ~ uchar i,j,t=0;
        t=0;
        # ~ max(&x1,&x2);
        x1,x2 = self.max(x1,x2);
        # ~ max(&y1,&y2);
        y1,y2 = self.max(y1,y2);
        # ~ max(&z1,&z2);
        z1,z2 = self.max(z1,z2);
        # ~ for (i=x1; i<=x2; i++)
        for i in range(x1,x2+1):
            # ~ t|=1<<i;
            t = t | (1<<i);
        # ~ if (!le)
        if (le != 0):
            # ~ t=~t;
            t=(~t)& 0xff;
        # ~ if (fill) {
        if (fill):
            # ~ if (le) {
            if (le):
                # ~ for (i=z1; i<=z2; i++) {
                for i in range(z1,z2+1):
                    # ~ for (j=y1; j<=y2; j++)
                    for j in range(y1, y2+1):
                        # ~ display[frame][j][i]|=t;
                        self.display[j*8+i] = self.display[j*8+i] | t;
            # ~ } else {
            else:
                # ~ for (i=z1; i<=z2; i++) {
                for i in range(z1, z2+1):
                    # ~ for (j=y1; j<=y2; j++)
                    for j in range(y1,y2+1):
                        # ~ display[frame][j][i]&=t;
                        self.display[j*8+i] = self.display[j*8+i] & t;
        # ~ } else {
        else:
            # ~ if (le) {
            if (le):
                # ~ display[frame][y1][z1]|=t;
                self.display[y1*8+z1] = self.display[y1*8+z1] | t;
                # ~ display[frame][y2][z1]|=t;
                self.display[y2*8+z1] = self.display[y2*8+z1] | t;
                # ~ display[frame][y1][z2]|=t;
                self.display[y1*8+z2] = self.display[y1*8+z2] | t;
                # ~ display[frame][y2][z2]|=t;
                self.display[y2*8+z2] = self.display[y2*8+z2] | t;
            # ~ } else {
            else:
                # ~ display[frame][y1][z1]&=t;
                self.display[y1*8+z1] = self.display[y1*8+z1] & t;
                # ~ display[frame][y2][z1]&=t;
                self.display[y2*8+z1] = self.display[y2*8+z1] & t;
                # ~ display[frame][y1][z2]&=t;
                self.display[y1*8+z2] = self.display[y1*8+z2] & t;
                # ~ display[frame][y2][z2]&=t;
                self.display[y2*8+z2] = self.display[y2*8+z2] & t;
            # ~ }
            # ~ t=(0x01<<x1)|(0x01<<x2);
            t=(0x01<<x1)|(0x01<<x2);
            # ~ if (!le)
            if (le != 0):
                # ~ t=~t;
                t=(~t)&0xff
            # ~ if (le) {
            if (le):
                # ~ for (j=z1; j<=z2; j+=(z2-z1)) {
                for j in range(z1,z2+1,(z2-z1)):
                    # ~ for (i=y1; i<=y2; i++)
                    for i in range(y1,y2+1):
                        # ~ display[frame][i][j]|=t;
                        self.display[i*8+j] = self.display[i*8+j] + t;
                # ~ for (j=y1; j<=y2; j+=(y2-y1)) {
                for j in range(y1,y2+1, y2-y1):
                    # ~ for (i=z1; i<=z2; i++)
                    for i in range(z1, z2+1):
                        # ~ display[frame][j][i]|=t;
                        self.display[j*8+i] = self.display[j*8+i] | t;
            else:
                # ~ for (j=z1; j<=z2; j+=(z2-z1)) {
                for j in range(z1,z2+1,z2-z1):
                    # ~ for (i=y1; i<=y2; i++) {
                    for i in range(y1,y2+1):
                        # ~ display[frame][i][j]&=t;
                        self.display[i*8+j] = self.display[i*8+j] & t;
                # ~ for (j=y1; j<=y2; j+=(y2-y1)) {
                for j in range(y1,y2+1,(y2-y1)):
                    # ~ for (i=z1; i<=z2; i++) {
                    for i in range(z1,z2+1):
                        # ~ display[frame][j][i]&=t;
                        self.display[j*8+i] = self.display[j*8+i] & t;



    # ~ ///////////////////////////////////////////////////////////
    # ~ // default animation included in with the ledcube with some modifications
    # ~ __bit flash_2()
    def flash_2(self):
        # ~ uchar i;
        # ~ for (i=129; i>0; i--)
        # ~ {
        for i in range(129, 0, -1):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ cirp(i-2,0,1);
            self.cirp(i-2,0,1)

            # ~ delay(8000);
            time.sleep(8000*0.000005)
            self.send_display()
            # ~ cirp(i-1,0,0);
            self.cirp(i-1,0,0)
        # ~ }

        # ~ delay(8000);
        time.sleep(8000*0.000005)
        self.send_display()

        # ~ for (i=0; i<136; i++)
        # ~ {
        for i in range(136):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ cirp(i,1,1);
            self.cirp(i,1,1)
            # ~ delay(8000);
            time.sleep(8000*0.000005)
            self.send_display()
            # ~ cirp(i-8,1,0);
            self.cirp(i-8,1,0)
        # ~ }

        # ~ delay(8000);
        time.sleep(8000*0.000005)
        self.send_display()

        # ~ for (i=129; i>0; i--)
        # ~ {
        for i in range(129, 0, -1):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ cirp(i-2,0,1);
            self.cirp(i-2,0,1)
            # ~ delay(8000);
            time.sleep(8000*0.000005)
            self.send_display()
        # ~ }

        # ~ delay(8000);
        time.sleep(8000*0.000005)
        self.send_display()
        self.point(0,0,0,0); self.point(0,1,0,0)

        # ~ for (i=0; i<128; i++)
        # ~ {
        for i in range(136):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ cirp(i-8,1,0);
            self.cirp(i-8,1,0)
            # ~ delay(8000);
            time.sleep(8000*0.000005)
            self.send_display()
        # ~ }

        # ~ delay(60000);
        # ~ return 0;
        time.sleep(8000*0.000005)
        self.send_display()


    # ~ __bit flash_3()
    # ~ {
        # ~ char i;
    def flash_3(self):
	# ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ box_apeak_xy(0,i,0,7,i,7,1,1);
            self.box_apeak_xy(0,i,0,7,i,7,1,1)
            # ~ delay(20000);
            time.sleep(20000*0.000005); self.send_display()
            # ~ if (i<7)
            if (i<7):
                # ~ box_apeak_xy(0,i,0,7,i,7,1,0);
                self.box_apeak_xy(0,i,0,7,i,7,1,0)

        # ~ for (i=7; i>=0; i--) {
        for i in range(7,0-1, -1):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ box_apeak_xy(0,i,0,7,i,7,1,1);
            self.box_apeak_xy(0,i,0,7,i,7,1,1)
            # ~ delay(20000);
            time.sleep(20000*0.000005); self.send_display()
            # ~ if (i>0)
            if (i>0):
                # ~ box_apeak_xy(0,i,0,7,i,7,1,0);
                self.box_apeak_xy(0,i,0,7,i,7,1,0)

        for i in range(8):
        # ~ for (i=0; i<8; i++) {
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ box_apeak_xy(0,i,0,7,i,7,1,1);
            self.box_apeak_xy(0,i,0,7,i,7,1,1)
            # ~ delay(20000);
            time.sleep(20000*0.000005); self.send_display()
            # ~ if (i<7)
            if (i<7):
                # ~ box_apeak_xy(0,i,0,7,i,7,1,0);
                self.box_apeak_xy(0,i,0,7,i,7,1,0)


    # ~ __bit flash_4()
    # ~ {
        # ~ char i,j,an[8];
    def flash_4(self):
        an = [0] *8
        # ~ for (j=7; j<15; j++)
        for j in range(7,15):
            # ~ an[j-7]=j;
            an[j-7]=j
        # ~ for (i=0; i<=16; i++) {
        for i in range(0,17):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if ((an[j]<8)&(an[j]>=0))
                if ((an[j]<8)&(an[j]>=0)):
                    # ~ line(0,an[j],j,7,an[j],j,1);
                    self.line(0,an[j],j,7,an[j],j,1);
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if (((an[j]+1)<8)&(an[j]>=0))
                if (((an[j]+1)<8)&(an[j]>=0)):
                    # ~ line(0,an[j]+1,j,7,an[j]+1,j,0);
                    self.line(0,an[j]+1,j,7,an[j]+1,j,0)
            for j in range(8):
                # ~ if (an[j]>0)
                if (an[j]>0):
                    # ~ an[j]--;
                    an[j] = an[j] -1
            # ~ delay(15000);
            time.sleep(15000*0.000005); self.send_display()

        # ~ for (j=0; j<8; j++)
        for j in range(8):
            # ~ an[j]=1-j;
            an[j]=1-j
        # ~ for (i=0; i<=16; i++) {
        for i in range(0,17):
            # ~ if (rx_in > 0) return 1; // RX command detected
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if ((an[j]<8)&(an[j]>=0))
                if ((an[j]<8)&(an[j]>=0)):
                    # ~ line(0,an[j],j,7,an[j],j,1);
                    self.line(0,an[j],j,7,an[j],j,1)
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if (((an[j]-1)<7)&(an[j]>0))
                if (((an[j]-1)<7)&(an[j]>0)):
                    # ~ line(0,an[j]-1,j,7,an[j]-1,j,0);
                    self.line(0,an[j]-1,j,7,an[j]-1,j,0)
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if (an[j]<7)
                if (an[j]<7):
                    # ~ an[j]++;
                    an[j] = an[j] +1
            # ~ delay(15000);
            time.sleep(15000*0.000005); self.send_display()


    # ~ __bit flash_5()
    # ~ {
    def flash_5(self):
        # ~ uint a=15000;//a=delay
        a=15000 # //a=delay
        # ~ char i=8,j,an[4];
        i=8
        an = [0] *4
        # ~ //1
        # ~ for (j=7; j<11; j++)
        for j in range(7,11):
            # ~ an[j-7]=j;
            an[j-7]=j
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]<8)
                if (an[j]<8):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ if (an[j]<7)
                if (an[j]<7):
                    # ~ box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0)
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>3)
                if (an[j]>3):
                    # ~ an[j]--;
                    an[j] = an[j] - 1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
            i = i -1

        # ~ //2
        # ~ i=3;
        i=3;
        # ~ for (j=0; j<4; j++)
        for j in range(4):
            # ~ an[j]=5-j;
            an[j]=5-j
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]<4)
                if (an[j]<4):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ if (an[j]<3)
                if (an[j]<3):
                    # ~ box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0)
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>0)
                if (an[j]>0):
                    # ~ an[j]--;
                    an[j] = an[j] - 1

            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
            i = i -1
        # ~ //3
        # ~ i=3;
        i=3
        # ~ for (j=1; j<4; j++)
        for j in range(4):
            # ~ an[j]=4-j;
            an[j]=4-j
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>=0)
                if (an[j]>=0):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ if (an[j]>0)
                if (an[j]>0):
                    # ~ box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0)
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]<3)
                if (an[j]<3):
                    # ~ an[j]++;
                    an[j] = an[j] + 1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
            i = i -1
        # ~ //4
        # ~ i=3;
        i=3;
        # ~ for (j=0; j<4; j++)
        for j in range(4):
            # ~ an[j]=j+1;
            an[j] = j+1
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>3)
                if (an[j]>3):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ if (an[j]>3)
                if (an[j]>3):
                    # ~ box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0);
            # ~ for (j=0; j<4; j++)
            for j in range(4):
                # ~ an[j]++;
                an[j] = an[j] + 1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
            i = i -1
        # ~ //5
        # ~ i=3;
        i=3;
        # ~ for (j=3; j<6; j++)
        for j in range(3,6):
            # ~ an[j-2]=j;
            an[j-2]=j;
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
                self.box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0)
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>3)
                if (an[j]>3):
                    # ~ an[j]--;
                    an[j] = an[j] - 1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
            i = i -1
        # ~ //6
        # ~ i=3;
        i=3;
        # ~ for (j=0; j<4; j++)
        for j in range(4):
            # ~ an[j]=5-j;
            an[j]=5-j
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=1; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]<4)
                if (an[j]<4):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1)
                # ~ if (an[j]<3)
                if (an[j]<3):
                    # ~ box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0)
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>0)
                if (an[j]>0):
                    # ~ an[j]--;
                    an[j] = an[j] - 1
            i = i -1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
        # ~ //7
        # ~ i=3;
        i=3;
        # ~ for (j=0; j<4; j++)
        for j in range(4):
            # ~ an[j]=3-j;
            an[j]=3-j;
        # ~ an[0]=2;
        an[0]=2;
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=0; j<3; j++) {
            for j in range(3):
                # ~ if (an[j]>=0)
                if (an[j]>=0):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                # ~ if (an[j]>=0)
                if (an[j]>=0):
                    # ~ box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]+1,j,7-j,an[j]+1,7-j,0,0);
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (j<5-i)
                if (j<5-i):
                    # ~ an[j]--;
                    an[j] = an[j] - 1
            i = i -1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()
        # ~ }
        # ~ //8
        # ~ i=10;
        i=10;
        # ~ for (j=0; j<4; j++)
        for j in range(4):
            # ~ an[j]=j-2;
            an[j]=j-2;
        # ~ while(i--) {
        while(i>0):
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]>=0)
                if (an[j]>=0):
                    # ~ box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                    self.box_apeak_xy(j,an[j],j,7-j,an[j],7-j,0,1);
                # ~ if (an[j]>=0)
                if (an[j]>=0):
                    # ~ box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0);
                    self.box_apeak_xy(j,an[j]-1,j,7-j,an[j]-1,7-j,0,0);
            # ~ for (j=0; j<4; j++) {
            for j in range(4):
                # ~ if (an[j]<7)
                if (an[j]<7):
                    # ~ an[j]++;
                    an[j] = an[j] + 1
            i = i -1
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()



    # ~ __bit flash_6()
    def flash_6(self):
        # ~ roll_apeak_yz(1,10000);
        self.roll_apeak_yz(1,10000);
        # ~ roll_apeak_yz(2,10000);
        self.roll_apeak_yz(2,10000);
        # ~ roll_apeak_yz(3,10000);
        self.roll_apeak_yz(3,10000);
        # ~ roll_apeak_yz(0,10000);
        self.roll_apeak_yz(0,10000);
        # ~ roll_apeak_yz(1,10000);
        self.roll_apeak_yz(1,10000);
        # ~ roll_apeak_yz(2,10000);
        self.roll_apeak_yz(2,10000);
        # ~ roll_apeak_yz(3,10000);
        self.roll_apeak_yz(3,10000);
        # ~ for (i=0; i<3; i++) {
        for i in range(3):
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ for (k=0; k<8; k++) {
                for k in range(8):
                    # ~ if ((table_3p[i][j]>>k)&1) {
                    if ((self.table_3p[i][j]>>k)&1):
                        # ~ for (z=1; z<8; z++) {
                        for z in range(1,8):
                            # ~ point (j,7-k,z,1);
                            self.point (j,7-k,z,1)
                            # ~ if (z-1)
                            if (z-1):
                                # ~ point (j,7-k,z-1,0);
                                self.point (j,7-k,z-1,0);
                            # ~ delay(5000);
                            time.sleep(5000*0.000005); self.send_display()
                       # ~ }
                    # ~ }
                # ~ }
            # ~ }
            # ~ trans(7,15000);
            self.trans(7,15000);

    # ~ __bit flash_7()
    def flash_7(self):

        # ~ uint a=3000;
        a=3000;
        # ~ roll_apeak_yz(0,10000);
        self.roll_apeak_yz(0,10000);
        # ~ roll_apeak_yz(1,10000);
        self.roll_apeak_yz(1,10000);
        # ~ roll_apeak_yz(2,10000);
        self.roll_apeak_yz(2,10000);
        # ~ roll_apeak_yz(3,10000);
        self.roll_apeak_yz(3,10000);
        # ~ roll_apeak_yz(0,10000);
        self.roll_apeak_yz(0,10000);
        # ~ roll_apeak_yz(1,10000);
        self.roll_apeak_yz(1,10000);
        # ~ roll_apeak_yz(2,10000);
        self.roll_apeak_yz(2,10000);
        # ~ roll_apeak_yz(3,10000);
        self.roll_apeak_yz(3,10000);

        # ~ roll_apeak_yz(0,10000);
        # ~ roll_apeak_yz(1,10000);
        # ~ roll_apeak_yz(2,10000);
        # ~ roll_apeak_xy(0,10000);
        # ~ roll_apeak_xy(1,10000);
        # ~ roll_apeak_xy(2,10000);
        # ~ roll_apeak_xy(3,10000);
        # ~ roll_apeak_xy(0,10000);
        # ~ roll_apeak_xy(1,10000);
        # ~ roll_apeak_xy(2,10000);
        # ~ roll_apeak_xy(3,10000);

        self.roll_apeak_yz(0,10000);
        self.roll_apeak_yz(1,10000);
        self.roll_apeak_yz(2,10000);
        self.roll_apeak_xy(0,10000);
        self.roll_apeak_xy(1,10000);
        self.roll_apeak_xy(2,10000);
        self.roll_apeak_xy(3,10000);
        self.roll_apeak_xy(0,10000);
        self.roll_apeak_xy(1,10000);
        self.roll_apeak_xy(2,10000);
        self.roll_apeak_xy(3,10000);

        # ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ box_apeak_xy (0,i,0,7-i,i,7,1,1);
            self.box_apeak_xy (0,i,0,7-i,i,7,1,1);
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()

        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(0,a);
        self.roll_3_xy(0,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(1,a);
        self.roll_3_xy(1,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(2,a);
        self.roll_3_xy(2,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(3,a);
        self.roll_3_xy(3,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(0,a);
        self.roll_3_xy(0,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(1,a);
        self.roll_3_xy(1,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(2,a);
        self.roll_3_xy(2,a);
        # ~ delay(30000);
        time.sleep(30000*0.000005); self.send_display()
        # ~ roll_3_xy(3,a);
        self.roll_3_xy(3,a);
        # ~ for (i=7; i>0; i--) {
        for i in range(7,0-1,-1):
            # ~ box_apeak_xy(i,0,0,i,7,7,1,0);
            self.box_apeak_xy(i,0,0,i,7,7,1,0);
            # ~ delay(a);
            time.sleep(a*0.000005); self.send_display()

    # ~ __bit flash_8()
    def flash_8(self):
        # ~ for (i=5; i<8; i++) {
        for i in range(5,8):
            # ~ tranoutchar(i,10000);
            self.tranoutchar(i,10000);
            # ~ delay(60000);
            time.sleep(60000*0.000005); self.send_display()
            # ~ delay(60000);
            time.sleep(60000*0.000005); self.send_display()

    # ~ __bit flash_9()
    def flash_9(self):
        # ~ uchar j,an[8],x,y,t,x1,y1;
        an = [0]*8
        # ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ box_apeak_xy (i,0,0,i,7,7,1,1);
            self.box_apeak_xy (i,0,0,i,7,7,1,1);
            # ~ if (i)
            if (i):
                # ~ box_apeak_xy (i-1,0,0,i-1,7,7,1,0);
                self.box_apeak_xy (i-1,0,0,i-1,7,7,1,0);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()

        # ~ roll_apeak_xy(3,10000);
        self.roll_apeak_xy(3,10000);
        # ~ roll_apeak_xy(0,10000);
        self.roll_apeak_xy(0,10000);
        # ~ roll_apeak_xy(1,10000);
        self.roll_apeak_xy(1,10000);
        # ~ for (i=0; i<7; i++) {
        for i in range(7):
            # ~ line(6-i,6-i,0,6-i,6-i,7,1);
            self.line(6-i,6-i,0,6-i,6-i,7,1);
            # ~ line(i,7,0,i,7,7,0);
            self.line(i,7,0,i,7,7,0);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()

        # ~ for (i=0; i<8; i++)
        for i in range(8):
            # ~ an[i]=14;
            an[i]=14;
        # ~ for (i=0; i<85; i++) {
        for i in range(85):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ t=an[j]%28;
                t=an[j]%28;
                # ~ x=dat2[t]>>5;
                x=self.dat2[t]>>5;
                # ~ y=(dat2[t]>>2)&0x07;
                y=(self.dat2[t]>>2)&0x07;
                # ~ t=(an[j]-14)%28;
                t=(an[j]-14)%28;
                # ~ x1=dat2[t]>>5;
                x1=self.dat2[t]>>5;
                # ~ y1=(dat2[t]>>2)&0x07;
                y1=(self.dat2[t]>>2)&0x07;
                # ~ line(x,y,j,x1,y1,j,1);
                self.line(x,y,j,x1,y1,j,1);

            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if ((i>j)&(j>i-71))
                if ((i>j)&(j>i-71)):
                    # ~ an[j]++;
                    an[j] = an[j] + 1
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()

        # ~ for (i=0; i<85; i++) {
        for i in range(85):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ t=an[j]%28;
                t=an[j]%28;
                # ~ x=dat2[t]>>5;
                x=self.dat2[t]>>5;
                # ~ y=(dat2[t]>>2)&0x07;
                y=(self.dat2[t]>>2)&0x07;
                # ~ t=(an[j]-14)%28;
                t=(an[j]-14)%28;
                # ~ x1=dat2[t]>>5;
                x1=self.dat2[t]>>5;
                # ~ y1=(dat2[t]>>2)&0x07;
                y1=(self.dat2[t]>>2)&0x07;
                # ~ line(x,y,j,x1,y1,j,1);
                self.line(x,y,j,x1,y1,j,1);
            # ~ for (j=0; j<8; j++) {
            for j in range(8):
                # ~ if ((i>j)&(j>i-71))
                if ((i>j)&(j>i-71)):
                    # ~ an[j]--;
                    an[j] = an[j] -1
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()
        # ~ for (i=0; i<29; i++) {
        for i in range(29):
            # ~ clear(frame, 0);
            self.clear();
            # ~ t=an[0]%28;
            t=an[0]%28;
            # ~ x=dat2[t]>>5;
            x=self.dat2[t]>>5;
            # ~ y=(dat2[t]>>2)&0x07;
            y=(self.dat2[t]>>2)&0x07;
            # ~ t=(an[0]-14)%28;
            t=(an[0]-14)%28;
            # ~ x1=dat2[t]>>5;
            x1=self.dat2[t]>>5;
            # ~ y1=(dat2[t]>>2)&0x07;
            y1=(self.dat2[t]>>2)&0x07;
            # ~ box_apeak_xy(x,y,0,x1,y1,7,0,1);
            self.box_apeak_xy(x,y,0,x1,y1,7,0,1);
            # ~ box_apeak_xy(x,y,1,x1,y1,6,0,1);
            self.box_apeak_xy(x,y,1,x1,y1,6,0,1);
            # ~ an[0]++;
            an[0] = an[0] + 1
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()
        # ~ for (i=0; i<16; i++) {
        for i in range(16):
            # ~ clear(frame, 0);
            self.clear();
            # ~ t=an[0]%28;
            t=an[0]%28;
            # ~ x=dat2[t]>>5;
            x=self.dat2[t]>>5;
            # ~ y=(dat2[t]>>2)&0x07;
            y=(self.dat2[t]>>2)&0x07;
            # ~ t=(an[0]-14)%28;
            t=(an[0]-14)%28;
            # ~ x1=dat2[t]>>5;
            x1=self.dat2[t]>>5;
            # ~ y1=(dat2[t]>>2)&0x07;
            y1=(self.dat2[t]>>2)&0x07;
            # ~ box_apeak_xy(x,y,0,x1,y1,7,1,1);
            self.box_apeak_xy(x,y,0,x1,y1,7,1,1);
            # ~ an[0]--;
            an[0] = an[0] - 1
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()
        # ~ for (i=0; i<8; i++) {
        for i in range(8):
            # ~ line(i,i,0,0,0,i,0);
            self.line(i,i,0,0,0,i,0);
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()
        # ~ for (i=1; i<7; i++) {
        for i in range(1,7):
            # ~ line(i,i,7,7,7,i,0);
            self.line(i,i,7,7,7,i,0);
            # ~ delay(5000);
            time.sleep(5000*0.000005); self.send_display()
            self.clear();
            time.sleep(5000*0.000005); self.send_display()
    def flash_9x_drop_this(self):
        an = [0]*8
        # ~ for (i=1; i<8; i++) {
        for i in range(1,8): # fixme fixme fixme
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(7,7,7,7-i,7-i,7-i,0,1);
            self.box(7,7,7,7-i,7-i,7-i,0,1);
            # ~ delay(10000);
            time.sleep(5000*0.000005); self.send_display()
    # ~ def flash_9y(self):
        # ~ for (i=1; i<7; i++) {
        for i in range(1,7):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(0,0,0,7-i,7-i,7-i,0,1);
            self.box(0,0,0,7-i,7-i,7-i,0,1);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=1; i<8; i++) {
        for i in range(1,8):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(0,0,0,i,i,i,0,1);
            self.box(0,0,0,i,i,i,0,1);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=1; i<7; i++) {
        for i in range(1,7):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(7,0,0,i,7-i,7-i,0,1);
            self.box(7,0,0,i,7-i,7-i,0,1);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=1; i<8; i++) {
        for i in range(1,8):
            # ~ box(7,0,0,7-i,i,i,1,1);
            self.box(7,0,0,7-i,i,i,1,1);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=1; i<7; i++) {
        for i in range(1,7):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(0,7,7,7-i,i,i,1,1);
            self.box(0,7,7,7-i,i,i,1,1);
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()

    # ~ __bit flash_10()
    def flash_10(self):
    # ~ {
        # ~ uchar i,j,an[4],x,y,t;
        an = [0] *4
        # ~ for (i=1; i<7; i++) {
        for i in range(1,7):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(0,6,6,1,7,7,1,1);
            self.box(0,6,6,1,7,7,1,1);
            # ~ box(i,6,6-i,i+1,7,7-i,1,1);
            self.box(i,6,6-i,i+1,7,7-i,1,1);
            # ~ box(i,6,6,i+1,7,7,1,1);
            self.box(i,6,6,i+1,7,7,1,1);
            # ~ box(0,6,6-i,1,7,7-i,1,1);
            self.box(0,6,6-i,1,7,7-i,1,1);
            # ~ box(0,6-i,6,1,7-i,7,1,1);
            self.box(0,6-i,6,1,7-i,7,1,1);
            # ~ box(i,6-i,6-i,i+1,7-i,7-i,1,1);
            self.box(i,6-i,6-i,i+1,7-i,7-i,1,1);
            # ~ box(i,6-i,6,i+1,7-i,7,1,1);
            self.box(i,6-i,6,i+1,7-i,7,1,1);
            # ~ box(0,6-i,6-i,1,7-i,7-i,1,1);
            self.box(0,6-i,6-i,1,7-i,7-i,1,1);
            # ~ delay(30000);
            time.sleep(30000*0.000005); self.send_display()
        # ~ }
        # ~ for (i=0; i<4; i++) {
        for i in range(4):
            # ~ an[i]=6*i;
            an[i]=6*i;
        # ~ for (i=0; i<35; i++) {
        for i in range(35):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for(j=0; j<4; j++) {
            for j in range(4):
                # ~ t=an[j]%24;
                t=an[j]%24;
                # ~ x=dat3[t]>>4;
                x=self.dat3[t]>>4;
                # ~ y=dat3[t]&0x0f;
                y=self.dat3[t]&0x0f;
                # ~ box(x,y,0,x+1,y+1,1,1,1);
                self.box(x,y,0,x+1,y+1,1,1,1);
                # ~ box(x,y,6,x+1,y+1,7,1,1);
                self.box(x,y,6,x+1,y+1,7,1,1);

            # ~ for (j=0; j<4; j++)
            for j in range(4):
                # ~ an[j]++;
                an[j] = an[j] + 1
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ }
        # ~ for (i=0; i<35; i++) {
        for i in range(35):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for(j=0; j<4; j++) {
            for j in range(4):
                # ~ t=an[j]%24;
                t=an[j]%24;
                # ~ x=dat3[t]>>4;
                x=self.dat3[t]>>4;
                # ~ y=dat3[t]&0x0f;
                y=self.dat3[t]&0x0f;
                # ~ box(x,y,0,x+1,y+1,1,1,1);
                self.box(x,y,0,x+1,y+1,1,1,1);
                # ~ box(x,y,6,x+1,y+1,7,1,1);
                self.box(x,y,6,x+1,y+1,7,1,1);
            # ~ }
            # ~ for (j=0; j<4; j++)
            for j in range(4):
                # ~ an[j]--;
                an[j] = an[j] - 1
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=0; i<35; i++) {
        for i in range(35):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for(j=0; j<4; j++) {
            for j in range(4):
                # ~ t=an[j]%24;
                t=an[j]%24;
                # ~ x=dat3[t]>>4;
                x=self.dat3[t]>>4;
                # ~ y=dat3[t]&0x0f;
                y=self.dat3[t]&0x0f;
                # ~ box(x,0,y,x+1,1,y+1,1,1);
                self.box(x,0,y,x+1,1,y+1,1,1);
                # ~ box(x,6,y,x+1,7,y+1,1,1);
                self.box(x,6,y,x+1,7,y+1,1,1);
            # ~ for (j=0; j<4; j++)
            for j in range(4):
                # ~ an[j]++;
                an[j] = an[j] - 1
            # ~ delay(10000);
            time.sleep(10000*0.000005); self.send_display()

        # ~ for (i=0; i<36; i++) {
        for i in range(36):
            # ~ clear(frame, 0);
            self.clear();
            # ~ for(j=0; j<4; j++) {
            for j in range(4):
                # ~ t=an[j]%24;
                t=an[j]%24;
                # ~ x=dat3[t]>>4;
                x=self.dat3[t]>>4;
                # ~ y=dat3[t]&0x0f;
                y=self.dat3[t]&0x0f;
                # ~ box(x,0,y,x+1,1,y+1,1,1);
                self.box(x,0,y,x+1,1,y+1,1,1);
                # ~ box(x,6,y,x+1,7,y+1,1,1);
                self.box(x,6,y,x+1,7,y+1,1,1);
            # ~ for (j=0; j<4; j++)
            for j in range(4):
                an[j] = an[j] - 1
            time.sleep(10000*0.000005); self.send_display()
        # ~ for (i=6; i>0; i--) {
        for i in range(6,0,-1):
            # ~ clear(frame, 0);
            self.clear();
            # ~ box(0,6,6,1,7,7,1,1);
            self.box(0,6,6,1,7,7,1,1);
            # ~ box(i,6,6-i,i+1,7,7-i,1,1);
            self.box(i,6,6-i,i+1,7,7-i,1,1);
            # ~ box(i,6,6,i+1,7,7,1,1);
            self.box(i,6,6,i+1,7,7,1,1);
            # ~ box(0,6,6-i,1,7,7-i,1,1);
            self.box(0,6,6-i,1,7,7-i,1,1);
            # ~ box(0,6-i,6,1,7-i,7,1,1);
            self.box(0,6-i,6,1,7-i,7,1,1);
            # ~ box(i,6-i,6-i,i+1,7-i,7-i,1,1);
            self.box(i,6-i,6-i,i+1,7-i,7-i,1,1);
            # ~ box(i,6-i,6,i+1,7-i,7,1,1);
            self.box(i,6-i,6,i+1,7-i,7,1,1);
            # ~ box(0,6-i,6-i,1,7-i,7-i,1,1);
            self.box(0,6-i,6-i,1,7-i,7-i,1,1);
            # ~ delay(30000);
            time.sleep(30000*0.000005); self.send_display()
        self.clear();
        time.sleep(30000*0.000005); self.send_display()

    # ~ __bit flash_11()
    def flash_11(self):
        # ~ uchar i,j,t,x,y;
        # ~ __code uchar daa[13]= {0,1,2,0x23,5,6,7,6,5,0x23,2,1,0};
        daa = [0,1,2,0x23,5,6,7,6,5,0x23,2,1,0]
        # ~ for (j=0; j<5; j++) {
        for j in range(5):
            # ~ for (i=0; i<13; i++) {
            for i in range(13):
                # ~ if (daa[i]>>4) {
                if (daa[i]>>4):
                    # ~ t=daa[i]&0x0f;
                    t=daa[i]&0x0f;
                    # ~ line (0,0,t+1,0,7,t+1,1);
                    self.line (0,0,t+1,0,7,t+1,1);
                # ~ } else
                else:
                    # ~ t=daa[i];
                    t=daa[i];
                # ~ line (0,0,t,0,7,t,1);
                self.line (0,0,t,0,7,t,1);
                # ~ transss();
                self.transss();
                # ~ delay(10000);
                time.sleep(10000*0.000005); self.send_display()
        # ~ for (j=1; j<8; j++) {
        for j in range(1,8):
            # ~ if (j>3)
            if (j>3):
                # ~ t=4;
                t=4;
            # ~ else
            else:
                # ~ t=j;
                t=j;
            # ~ for (i=0; i<24; i+=j) {
            for i in range(24):
                # ~ x=dat3[i]>>4;
                x=self.dat3[i]>>4;
                # ~ y=dat3[i]&0x0f;
                y=self.dat3[i]&0x0f;
                # ~ box_apeak_xy(0,x,y,0,x+1,y+1,1,1);
                self.box_apeak_xy(0,x,y,0,x+1,y+1,1,1);
                # ~ transss();
                self.transss();
                # ~ delay(10000);
                time.sleep(10000*0.000005); self.send_display()
        # ~ for (j=1; j<8; j++) {
        for j in range(1,8):
            # ~ if (j>3)
            if (j>3):
                # ~ t=4;
                t=4;
            # ~ else
            else:
                # ~ t=j;
                t=j;
            # ~ for (i=0; i<24; i+=j) {
            for i in range(24):
                # ~ x=dat3[i]>>4;
                x=self.dat3[i]>>4;
                # ~ y=dat3[i]&0x0f;
                y=self.dat3[i]&0x0f;
                # ~ point (0,x,y,1);
                self.point (0,x,y,1);
                # ~ transss();
                self.transss();
                # ~ delay(10000);
                time.sleep(10000*0.000005); self.send_display()

    def run_sequence(self, seq, delay):

        print('Running sequence %s' % (seq))
        # handle data files
        if seq.endswith('.dat'):
            self.send_file("../../DotMatrixJava/examples/" + seq, delay)

        # handle code sequences
        elif seq == 'flash_2':
            self.flash_2()
        elif seq == 'flash_3':
            self.flash_3()
        elif seq == 'flash_4':
            self.flash_4()
        elif seq == 'flash_5':
            self.flash_5()
        elif seq == 'flash_6':
            self.flash_6()
        elif seq == 'flash_7':
            self.flash_7()
        elif seq == 'flash_8':
            self.flash_8()
        elif seq == 'flash_9':
            self.flash_9()
        elif seq == 'flash_10':
            self.flash_10()
        elif seq == 'flash_11':
            self.flash_11()
        elif seq == 'flash_12':
            self.flash_12()
        elif seq == 'flash_13':
            self.flash_13()
        elif seq == 'flash_14':
            self.flash_14()
        elif seq == 'flash_15':
            self.flash_15()
        elif seq == 'flash_16':
            self.flash_16()
        elif seq == 'flash_17':
            self.flash_17()
        elif seq == 'flash_18':
            self.flash_18()
        elif seq == 'flash_19':
            self.flash_19()
        elif seq == 'flash_20':
            self.flash_20()
        elif seq == 'flash_21':
            self.flash_21()
        elif seq == 'flash_22':
            self.flash_22()
        elif seq == 'drum_1':
            self.drum_1()

    def drum_1(self):

        img =  ['XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX',
                'XXXXXXXX']


            # (left/right;  front/back;   up/down)

        #
        # start with a plane
        #
        img_flat_plane = self.string_plane_to_xyz_list(img, plane='xy')
        transform = self.get_translate_matrix( 0,0,4)
        flat_pane_pixels = transform.dot(img_flat_plane)
        self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()
        
        time.sleep(1)

        #
        # do the vibration mode 0,0
        #
        self.zero_cross_count = 0
        parms={'a':4, 'A':2.8, 'B':2.8, 'C':1, 'D':1, 'm':0, 'n':0, 'c':0.2}
        for time_index in range(1000):
            points_raw = self.calc_drum_x_y(0, 0, 0, time_index*1.0, parms)
            
            if self.zero_cross_count > 20:
                break
                
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(points_raw)
            self.clear();  self.store_pixel_array(new_pixels); self.send_display()
        self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()

        #
        # flip the plane
        #
        # ~ time.sleep(1)
        for index in range(10+1):
            transform = self.get_translate_matrix( -3.5,-3.5,0)
            transform = self.get_rotate_z_matrix( -45.0).dot(transform)
            transform = self.get_rotate_x_matrix( index/10.0*180.0).dot(transform)
            transform = self.get_rotate_z_matrix( 45.0).dot(transform)
            transform = self.get_translate_matrix( 3.5,3.5,0).dot(transform)
            transform = self.get_translate_matrix( 0,0,3.75).dot(transform)
            flat_pane_pixels = transform.dot(img_flat_plane)
            self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()
        # ~ time.sleep(1)

        #
        # do the vibration mode 1,0
        #
        self.zero_cross_count = 0
        parms={'a':4, 'A':2.8, 'B':2.8, 'C':1, 'D':1, 'm':1, 'n':0, 'c':0.1}
        for time_index in range(1000):
            points_raw = self.calc_drum_x_y(0, 0, 0, time_index*1.0, parms)
            
            if self.zero_cross_count > 20:
                break
                
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(points_raw)
            self.clear();  self.store_pixel_array(new_pixels); self.send_display()
        self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()

        #
        # flip the plane
        #
        # ~ time.sleep(1)
        for index in range(10+1):
            transform = self.get_translate_matrix( -3.5,-3.5,0)
            transform = self.get_rotate_y_matrix( index/10.0*180.0).dot(transform)
            transform = self.get_translate_matrix( 3.5,3.5,0).dot(transform)
            transform = self.get_translate_matrix( 0,0,3.75).dot(transform)
            flat_pane_pixels = transform.dot(img_flat_plane)
            self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()
        # ~ time.sleep(1)




        #
        # do the vibration mode 0,1
        #
        self.zero_cross_count = 0
        parms={'a':4, 'A':2.8, 'B':2.8, 'C':1, 'D':1, 'm':0, 'n':1, 'c':0.1}
        for time_index in range(1000):
            points_raw = self.calc_drum_x_y(0, 0, 0, time_index*1.0, parms)
            
            if self.zero_cross_count > 20:
                break
                
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(points_raw)
            self.clear();  self.store_pixel_array(new_pixels); self.send_display()
        self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()


        #
        # flip the plane
        #
        # ~ time.sleep(1)
        for index in range(10+1):
            transform = self.get_translate_matrix( -3.5,-3.5,0)
            transform = self.get_rotate_x_matrix( -index/10.0*180.0).dot(transform)
            transform = self.get_rotate_y_matrix( index/10.0*180.0).dot(transform)
            transform = self.get_translate_matrix( 3.5,3.5,0).dot(transform)
            transform = self.get_translate_matrix( 0,0,3.75).dot(transform)
            flat_pane_pixels = transform.dot(img_flat_plane)
            self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()
        # ~ time.sleep(1)




        #
        # do the vibration mode 0,2
        #
        self.zero_cross_count = 0
        parms={'a':4, 'A':1.5, 'B':1.5, 'C':1, 'D':1, 'm':0, 'n':2, 'c':0.1}
        for time_index in range(1000):
            points_raw = self.calc_drum_x_y(0, 0, 0, time_index*1.0, parms)
            
            if self.zero_cross_count > 100:
                break
                
            transform = self.get_translate_matrix(  3.5,   3.5,   3.5)
            new_pixels = transform.dot(points_raw)
            self.clear();  self.store_pixel_array(new_pixels); self.send_display()
        self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()

        #
        # flip the plane
        #
        # ~ time.sleep(1)
        for index in range(10+1):
            transform = self.get_translate_matrix( -3.5,-3.5,0)
            transform = self.get_rotate_x_matrix( index/10.0*180.0).dot(transform)
            transform = self.get_translate_matrix( 3.5,3.5,0).dot(transform)
            transform = self.get_translate_matrix( 0,0,3.75).dot(transform)
            flat_pane_pixels = transform.dot(img_flat_plane)
            self.clear();  self.store_pixel_array(flat_pane_pixels); self.send_display()
        time.sleep(1)


        
        # a=radius; A - this times sqrt(2) seems to be the height
        parms={'a':4, 'A':2.8, 'B':2.8, 'C':1, 'D':1, 'm':2, 'n':0, 'c':0.05}


    def calc_drum_x_y(self, x_offset, y_offset, z_offset, t, parms):
        
        mmax = 2
        # ~ a = 4 # radius of drum. center to corner of 8x8
        # ~ A = 2.8  # this times sqrt(2) seems to be the height
        # ~ B = A
        # ~ C = 1
        # ~ D = 1
        
        # ~ m = 0
        # ~ n = 0
        # ~ c = .2


        a = parms['a']
        A = parms['A']
        B = parms['B']
        C = parms['C']
        D = parms['D']
        
        m = parms['m']
        n = parms['n']
        c = parms['c']

        k = jn_zeros(n, mmax+1)[m]
        c_k_t = c*k*t - np.pi/4 

        sin_cos_t = A*np.cos(c_k_t) + B*np.sin(c_k_t)

        pixel_coords = np.array([[],[],[],[]])
        for y_index in range(8):
            y_base = y_index-3.5 
            y      = y_index-3.5 + y_offset
            
            x_temp = ['c_k_t=%.4f  sincos=%.3f  ' % (c_k_t, sin_cos_t)]
            x_temp = []
            for x_index in range(8):
                x_base = x_index-3.5 
                x      = x_index-3.5 + x_offset
                
                r = np.sqrt(x*x + y*y)
                
                if r > a:  # make sure we are in the circle
                    u = 0
                else:
                    theta = np.arctan2(x,y)

                    Jn = jn(n, r*k/a)
        
                    u = (sin_cos_t)*Jn*(C*math.cos(n*theta)+D*math.sin(n*theta))
        
                new_pixel = np.array([[x_base], [y_base], [u], [1]])
                pixel_coords = np.append(pixel_coords, new_pixel, axis=1)
                
                if y_index == 3 and x_index == 3:
                    if self.u_last * u < 1: 
                        self.zero_cross_count += 1
                    self.u_last = u
                    
                    
                if y_index == 3:
                    x_temp.append('%0.3f' % (u))
                    
            if len(x_temp) != 0:
                print(','.join(x_temp))

        return pixel_coords
        

def main():
    parser = argparse.ArgumentParser(description='Send serial data to 8x8x8 led cube v2.')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help='serial port connected to 8x8x8 cube running v2 firmware')
    parser.add_argument('-b', '--baud', default=9600, help='serial port baud rate')
    parser.add_argument('-f', '--file', default=None, help='file of bit data to send')
    parser.add_argument('-d', '--delay', default=20, help='delay in msec between each file frame')
    parser.add_argument('-m', '--math', default=0, help='do math stuff')
    parser.add_argument('-c', '--canned', default=0, help='run one of the original canned sequences')
    parser.add_argument('-r', '--random', default=0, help='run this many random sequences. zero is infinite')
    parser.add_argument('-l', '--list', action='store_true', help='list the sequences')
    parser.add_argument('--reps', default=1, help='repetitions')

    args = parser.parse_args()


    led_Cube_8x8x8 = Led_Cube_8x8x8(port=args.port, baudrate=args.baud)

    if args.math != 0:
        # ~ led_Cube_8x8x8.test_it2()
        pass

    elif args.random != 0:
        for index in range(int(args.random)):
            led_Cube_8x8x8.run_sequence(random.choice(led_Cube_8x8x8.seq_list)[0], args.delay)
            time.sleep(0.5)
            led_Cube_8x8x8.clear()
            led_Cube_8x8x8.send_display()
            time.sleep(0.5)

    elif args.canned != 0:
        for index in range(int(args.reps)):
            led_Cube_8x8x8.run_sequence(args.canned, args.delay)

    elif args.list == True:
        for index in range(len(led_Cube_8x8x8.seq_list)):
            print('%-15s   %s' % (led_Cube_8x8x8.seq_list[index][0], led_Cube_8x8x8.seq_list[index][1]))

    elif args.file == None:
        for index in range(int(args.reps)):
            led_Cube_8x8x8.test_it()
            led_Cube_8x8x8.send_display()

    else:
        led_Cube_8x8x8.send_file(args.file, args.delay)



if __name__ == "__main__":
    main()
