import serial
import binascii
import struct
import time
import argparse
import numpy as np
import math

class Led_Cube_8x8x8():
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.port = serial.Serial(self.port, baudrate=self.baudrate, timeout=3.0)
        self.clear()

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

    def test_it2(self):
        self.clear()
        
        img =  ['........',
                '..XXXX..',
                '...XX...',
                '...XX...',
                '...XX...',
                '...XX...',
                '..XXXX..',
                '........']
        img_pixels = self.string_plane_to_xyz_list(img, plane='xz')
        img_pixels = self.get_translate_matrix( 0,  3,  0).dot(img_pixels)

        # ~ print(img_pixels)
        
        for angle_index in range(32+1):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 11.25*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.1)
        
    def send_display(self):
        
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
                    
                self.display = intdata
                self.send_display()
                                
            bytesread = 0
            
    def store_pixel_array(self, pixel_array):
        cols = np.size(pixel_array,1)
        # ~ print('cols=%d' % (cols))
        for col in range(cols):
            self.store_pixel(x=pixel_array[0,col], y=pixel_array[1,col], z=pixel_array[2,col], state=1) 
            
    def store_pixel(self, x=0, y=0, z=0, state=0):
        rounded_x = int(x+0.5)
        rounded_y = int(y+0.5)
        rounded_z = int(z+0.5)
        
        if (rounded_x>=0 and rounded_x<8 and rounded_y>=0 and rounded_y<8 and rounded_z>=0 and rounded_z<8):
            index = rounded_z*8+rounded_y
            if state == 1:
                self.display[index] |= 1<<rounded_x
            else:
                self.display[index] &= ~(1<<rounded_x)
        
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
        

def main():
    parser = argparse.ArgumentParser(description='Send serial data to 8x8x8 led cube v2.')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help='serial port connected to 8x8x8 cube running v2 firmware')
    parser.add_argument('-b', '--baud', default=9600, help='serial port baud rate')
    parser.add_argument('-f', '--file', default=None, help='file of bit data to send')
    parser.add_argument('-d', '--delay', default=20, help='delay in msec between each file frame')
    parser.add_argument('-m', '--math', default=0, help='do math stuff')

    args = parser.parse_args()


    led_Cube_8x8x8 = Led_Cube_8x8x8(port=args.port, baudrate=args.baud)

    if args.math != 0:
        # ~ led_Cube_8x8x8.math_test()
        led_Cube_8x8x8.test_it2()

    elif args.file == None:
        led_Cube_8x8x8.test_it()
        led_Cube_8x8x8.send_display()
    else:
        led_Cube_8x8x8.send_file(args.file, args.delay)
    


if __name__ == "__main__":
    main()
