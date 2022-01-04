#!/usr/bin/python
# -------------------------------------------------------------------------------
#
#             COPYRIGHT 2021 MOTOROLA SOLUTIONS INC. ALL RIGHTS RESERVED.
#                    MOTOROLA SOLUTIONS CONFIDENTIAL RESTRICTED
#
# -------------------------------------------------------------------------------

from led_cube import Led_Cube_8x8x8
from unittest import TestCase, main
from mock import patch, call, MagicMock
# ~ import binascii
# ~ import json

class RcmpController_test(TestCase):

    def setUp(self):
        # ~ global fail_count
        # ~ fail_count = 0
        pass

    def tearDown(self):
        pass

    def get_default_args(self):
        args = MagicMock()
        args.port='/dev/ttyUSB0'
        args.baud=9600
        args.file=None
        args.delay=20
        args.canned=0
        args.random=0
        args.delay=20
        args.generate=''
        args.list=False
        args.reps=1

        return args

    @patch('led_cube.serial')
    def test_rgb_index_to_serial_xyz(self, mock_serial):

        myled = Led_Cube_8x8x8(self.get_default_args())

        x,y,z = myled.rgb_index_to_serial_xyz(0)

        self.assertEqual( (0,0,7), (x,y,z))

        x,y,z = myled.rgb_index_to_serial_xyz(1)

        self.assertEqual( (0,0,6), (x,y,z))

        x,y,z = myled.rgb_index_to_serial_xyz(7)

        self.assertEqual( (0,0,0), (x,y,z))



        x,y,z = myled.rgb_index_to_serial_xyz(8)

        self.assertEqual( (1,0,0), (x,y,z))

        x,y,z = myled.rgb_index_to_serial_xyz(9)

        self.assertEqual( (1,0,1), (x,y,z))

        x,y,z = myled.rgb_index_to_serial_xyz(15)

        self.assertEqual( (1,0,7), (x,y,z))

        x,y,z = myled.rgb_index_to_serial_xyz(16)

        self.assertEqual( (2,0,7), (x,y,z))



        x,y,z = myled.rgb_index_to_serial_xyz(64)

        self.assertEqual( (0,1,7), (x,y,z))



        x,y,z = myled.rgb_index_to_serial_xyz(511)

        self.assertEqual( (7,7,7), (x,y,z))




    @patch('led_cube.serial')
    def test_xyz_to_rgb_index(self, mock_serial):

        myled = Led_Cube_8x8x8(self.get_default_args())

        rgb_index = myled.serial_xyz_to_rgb_index(0,0,7)

        self.assertEqual( 0, rgb_index)

        rgb_index = myled.serial_xyz_to_rgb_index(0,0,6)

        self.assertEqual( 1, rgb_index)

        rgb_index = myled.serial_xyz_to_rgb_index(0,0,0)

        self.assertEqual( 7, rgb_index)



        rgb_index = myled.serial_xyz_to_rgb_index(1,0,0)

        self.assertEqual( 8, rgb_index)

        rgb_index = myled.serial_xyz_to_rgb_index(1,0,1)

        self.assertEqual( 9, rgb_index)

        rgb_index = myled.serial_xyz_to_rgb_index(1,0,7)

        self.assertEqual( 15, rgb_index)

        rgb_index = myled.serial_xyz_to_rgb_index(2,0,7)

        self.assertEqual( 16, rgb_index)



        rgb_index = myled.serial_xyz_to_rgb_index(0,1,7)

        self.assertEqual( 64, rgb_index)


        rgb_index = myled.serial_xyz_to_rgb_index(7,7,7)

        self.assertEqual( 511, rgb_index)




        # ~ x,y,z = myled.rgb_index_to_serial_xyz(511)

        # ~ self.assertEqual( (7,7,7), (x,y,z))



    @patch('led_cube.serial')
    def test_default(self, mock_serial):

        myled = Led_Cube_8x8x8(self.get_default_args())

        myled.display = [0x7e] + [0]*63

        linetext = myled.display_buffer_to_rgb_commands()

        self.assertEqual(
            'fill 1; fill 1,0000ff,8,1; fill 1,0000ff,23,1; fill 1,0000ff,24,1; fill 1,0000ff,39,1; fill 1,0000ff,40,1; fill 1,0000ff,55,1; render'
            , linetext)


    @patch('led_cube.serial')
    def test_color_wheel(self, mock_serial):

        myled = Led_Cube_8x8x8(self.get_default_args())

        myled.display = [0x7e] + [0]*63

        color = myled.get_color_from_wheel(0)
        self.assertEqual('00ff00', color)

        color = myled.get_color_from_wheel(2)
        self.assertEqual('06f900', color)

        color = myled.get_color_from_wheel(64)
        self.assertEqual('c03f00', color)

        color = myled.get_color_from_wheel(128)
        self.assertEqual('7e0081', color)

        color = myled.get_color_from_wheel(192)
        self.assertEqual('4200bd', color)

        color = myled.get_color_from_wheel(255)
        self.assertEqual('ff0000', color)



if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999


if __name__ == "__main__":
    main()
