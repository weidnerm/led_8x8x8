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

    @patch('led_cube.serial')
    def test_default(self, mock_serial):
            
        myled = Led_Cube_8x8x8()
        
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
    def test_default(self, mock_serial):
            
        myled = Led_Cube_8x8x8()
        
        myled.display = [0x7e] + [0]*63
        
        linetext = myled.display_buffer_to_rgb_commands()
        
        self.assertEqual(0, linetext)



if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999


if __name__ == "__main__":
    main()
