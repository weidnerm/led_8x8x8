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
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        
        for angle_index in range(16):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_y_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        
        for angle_index in range(16):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_x_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        

        for angle_index in range(64):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_x_matrix( 11.25*angle_index).dot(transform)
            transform = self.get_rotate_y_matrix( 11.25*angle_index).dot(transform)
            transform = self.get_rotate_z_matrix( 11.25*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels_I)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        



        for angle_index in range(120+1):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels_heart)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        
        for angle_index in range(120+1):
            transform = self.get_translate_matrix( -3.5,  -3.5,  -3.5)
            transform = self.get_rotate_z_matrix( 22.5*angle_index).dot(transform)
            transform = self.get_translate_matrix(3.5, 3.5, 3.5).dot(transform)
            
            new_pixels = transform.dot(img_pixels_U)
            self.clear()
            self.store_pixel_array(new_pixels)
            # ~ print(self.display)
            self.send_display()
            time.sleep(0.025)
        
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
                
                self.clear()
                pixel_list = self.correct_orientation(intdata)
                self.store_pixel_array(pixel_list)
                self.send_display()
                                
            bytesread = 0
            
    def store_pixel_array(self, pixel_array):
        cols = np.size(pixel_array,1)
        # ~ print('cols=%d' % (cols))
        for col in range(cols):
            self.store_pixel(x=pixel_array[0,col], y=pixel_array[1,col], z=pixel_array[2,col], state=1) 
            
    def point(self, x, y, z, enable):
        self.store_pixel(x=x, y=y, z=z, state=enable)
        
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



def main():
    parser = argparse.ArgumentParser(description='Send serial data to 8x8x8 led cube v2.')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help='serial port connected to 8x8x8 cube running v2 firmware')
    parser.add_argument('-b', '--baud', default=9600, help='serial port baud rate')
    parser.add_argument('-f', '--file', default=None, help='file of bit data to send')
    parser.add_argument('-d', '--delay', default=20, help='delay in msec between each file frame')
    parser.add_argument('-m', '--math', default=0, help='do math stuff')
    parser.add_argument('-c', '--canned', default=0, help='run one of the original canned sequences')

    args = parser.parse_args()


    led_Cube_8x8x8 = Led_Cube_8x8x8(port=args.port, baudrate=args.baud)

    if args.math != 0:
        # ~ led_Cube_8x8x8.math_test()
        led_Cube_8x8x8.test_it2()

    elif args.canned == '2':
        led_Cube_8x8x8.flash_2()
    elif args.canned == '3':
        led_Cube_8x8x8.flash_3()
    elif args.canned == '4':
        led_Cube_8x8x8.flash_4()
    elif args.canned == '5':
        led_Cube_8x8x8.flash_5()
    elif args.canned == '6':
        led_Cube_8x8x8.flash_6()
    elif args.canned == '7':
        led_Cube_8x8x8.flash_7()

    elif args.file == None:
        led_Cube_8x8x8.test_it()
        led_Cube_8x8x8.send_display()
        
    else:
        led_Cube_8x8x8.send_file(args.file, args.delay)
    


if __name__ == "__main__":
    main()
