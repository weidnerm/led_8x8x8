import serial
import binascii
import struct
import time
import argparse
import numpy as np
import math
import random
from scipy.special import jn, jn_zeros

class LightningController():
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.tty = serial.Serial(self.port, baudrate=self.baudrate, timeout=0.2)
 

    def send_outlet_state(self, outlet, action):
        cmd = 'set outlet %d %s' % (outlet, action)
        time.sleep(0.1)
        
        junk = self.tty.read(1024)
        print("[%s]" % junk)
        self.tty.write(cmd+'\n')
        result = self.tty.read(1024)
        if cmd in result:
            print('all is good')
        else:
            print('cant find <%s> in <%s>' % (cmd, result))
            
        print(result)
       
    def send_get_state(self):
        cmd = 'get outlets\n'
        
        self.tty.write(cmd)
        result = self.tty.read(1024)
        print(result)
        
        return result
        
        

def main():
    parser = argparse.ArgumentParser(description='Send serial data to 8x8x8 led cube v2.')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB1', help='serial port connected to sBB-N15 ibootbar')
    parser.add_argument('-b', '--baud', default=115200, help='serial port baud rate')
    # ~ parser.add_argument('-f', '--file', default=None, help='file of bit data to send')
    parser.add_argument('-d', '--delay', default=20, help='delay in msec between each file frame')
    # ~ parser.add_argument('-m', '--math', default=0, help='do math stuff')
    # ~ parser.add_argument('-c', '--canned', default=0, help='run one of the original canned sequences')
    # ~ parser.add_argument('-r', '--random', default=0, help='run this many random sequences. zero is infinite')
    # ~ parser.add_argument('-l', '--list', action='store_true', help='list the sequences')
    # ~ parser.add_argument('--reps', default=1, help='repetitions')

    args = parser.parse_args()


    myLightningController = LightningController(port=args.port, baudrate=args.baud)

    # ~ if args.math != 0:
        # ~ pass

    # ~ elif args.random != 0:
        # ~ for index in range(int(args.random)):
            # ~ LightningController.run_sequence(random.choice(LightningController.seq_list)[0], args.delay)
            # ~ time.sleep(0.5)
            # ~ LightningController.clear()
            # ~ LightningController.send_display()
            # ~ time.sleep(0.5)

    # ~ elif args.canned != 0:
        # ~ for index in range(int(args.reps)):
            # ~ LightningController.run_sequence(args.canned, args.delay)

    # ~ elif args.list == True:
        # ~ for index in range(len(LightningController.seq_list)):
            # ~ print('%-15s   %s' % (LightningController.seq_list[index][0], LightningController.seq_list[index][1]))

    # ~ elif args.file == None:
        # ~ for index in range(int(args.reps)):
            # ~ LightningController.test_it()
            # ~ LightningController.send_display()

    # ~ else:
        # ~ LightningController.send_file(args.file, args.delay)

    outlet = 1

    myLightningController.send_outlet_state(outlet,'On')
    
    myLightningController.send_get_state()
    
    time.sleep(1.0)

    myLightningController.send_outlet_state(outlet,'Off')

    myLightningController.send_get_state()


if __name__ == "__main__":
    main()
