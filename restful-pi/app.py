from flask import Flask
from flask_restplus import Api, Resource, fields
import os
import psutil
import signal

app = Flask(__name__)
api = Api(app,
          version='1.0',
          title='RESTful Pi',
          description='A RESTful API to control the LED CUBE of a Raspbery Pi',
          doc='/docs')

ns = api.namespace('light', description='Pin related operations')

light_model = api.model('light', {
    'brightness': fields.Integer(required=True, description='Light brighness 0-255'),
    'rgb': fields.String(required=True, description='Light color. 6 digit hex rgb'),
    'state': fields.String(required=True, description='Light on or off'),
    'effect': fields.String(required=False, description='Active effect or empty string')
})


class LightUtil(object):
    def __init__(self):
        self.counter = 0
        # ~ self.pins = []
        self.light = {
            "rgb": "ffffff",
            "state": "off",
            "brightness": 32,
            "effect": ''
        }
            

    def get(self):
        return self.light
        
    def get_pre_made_filenames(self):
        pre_made_files = []

        files = os.listdir('/home/pi/proj/led_8x8x8/8x8x8/pre_made')
        for filename in files:
            if filename.startswith('seq_') and filename.endswith('.txt'):
                filename = filename[4:-4]  # drop leading seq_ and trailing .txt
                pre_made_files.append(filename)

        pre_made_files.sort()
        
        return pre_made_files

    def create(self, data):
        self.light = data
        self.generate_command_file()
        self.send_command_file()
        return self.light


    def update(self, data):
        cmd = 'sudo python3 /home/pi/proj/rest/restful-pi/ptk_light.py'
        os.system(cmd)
        self.light['effect'] = '' # clear out effect since done
        if data:
            print('update data: %s' % (data))
            self.light.update(data)  # this is the dict_object update method
            if 'effect' in data and data['effect'] != '':  # run effect
                self.run_effect(data['effect'])
            else:  
                self.generate_command_file()
                self.send_command_file()
        return self.light

    def delete(self):
        pass

    def run_effect(self, effect):
        if effect == 'random_loop':            
            cmd = 'python /home/pi//proj/led_8x8x8/8x8x8/led_cube.py '\
                  '--premade_dir /home/pi//proj/led_8x8x8/8x8x8/pre_made '\
                  '--random_pre %s &' % (5000)
        else:
            cmd = 'python /home/pi//proj/led_8x8x8/8x8x8/led_cube.py '\
                  '--premade_dir /home/pi//proj/led_8x8x8/8x8x8/pre_made '\
                  '--premade seq_%s.txt &' % (effect)
        os.system(cmd)

    def generate_command_file(self, filename='temp.txt'):
        text = []
    
        text.append('setup channel_1_count=512')
        text.append('brightness 1,%d' % (self.light['brightness']))
        grb = self.light['rgb'][2:4] + self.light['rgb'][0:2] + self.light['rgb'][4:6] # swap red and green since its green-red-blue in hw.
        if self.light['state'] == 'on':
            text.append('fill 1,%s,0,LEN' % (grb))
        else:
            text.append('fill 1,000000,0,LEN')
        text.append('render')
        
        fh = open(filename, "w")
        fh.write('\n'.join(text)+'\n')
        fh.close()

    def send_command_file(self, filename='temp.txt'):
        cmd = 'sudo /home/pi/proj/led_strip/rpi-ws2812-server/test -f /home/pi/proj/rest/restful-pi/%s &' %(filename)
        os.system(cmd)
        

    # ~ def kill_process_and_children(self, pid, sig=signal.SIGTERM):
        # ~ """Kill a process and all its children processes."""
        # ~ try:
            # ~ process = psutil.Process(pid)
        # ~ except psutil.NoSuchProcess:
            # ~ return

        # ~ children = process.children(recursive=True)
        # ~ for child in children:
            # ~ try:
                # ~ child.send_signal(sig)
            # ~ except psutil.NoSuchProcess:
                # ~ pass

        # ~ try:
            # ~ process.send_signal(sig)
        # ~ except :
            # ~ pass

    # ~ def find_and_kill_process(self):
        # ~ """Find and kill all processes matching the given name."""
        # ~ process_name = 'test'
        # ~ parent_py = 'led_cube.py'
        # ~ for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline']):
            # ~ if proc.info['name'] == process_name:
                # ~ print('name:%s' % (proc.info['name']))
                # ~ print(proc.info)
                # ~ self.kill_process_and_children(proc.info['pid'])
            # ~ if parent_py in proc.info['cmdline']:
                # ~ print('name:%s' % (proc.info['name']))
                # ~ print(proc.info)
                # ~ self.kill_process_and_children(proc.info['pid'])
                


@ns.route('/')  # keep in mind this our ns-namespace (light/)
class PinList(Resource):
    """Shows a list of all light, and lets you POST to add new light"""

    @ns.marshal_list_with(light_model)
    def get(self):
        """List all light"""
        return light_util.light

    @ns.expect(light_model)
    @ns.marshal_with(light_model, code=201)
    def post(self):
        """Create a new pin"""
        return light_util.create(api.payload)

    @ns.expect(light_model, validate=True)
    @ns.marshal_with(light_model)
    def put(self):
        """Update a pin given its identifier"""
        return light_util.update(api.payload)
    
    @ns.expect(light_model)
    @ns.marshal_with(light_model)
    def patch(self):
        """Partially update a pin given its identifier"""
        return light_util.update(api.payload)


@ns.route('/effect_list')
class Pin(Resource):
    """Gets list of possible effects"""

    def get(self):
        """Fetch a pin given its resource identifier"""
        return {"effect_list": light_util.get_pre_made_filenames()+['random_loop']}

    def delete(self):
        """Delete a pin given its identifier"""
        return '', 204

    def put(self):
        """Fully update a pin given its identifier"""
        return '', 204
    
    def patch(self):
        """Partially update a pin given its identifier"""
        return '', 204




light_util = LightUtil()

if __name__ == '__main__':
    app.run(debug=True, host='192.168.86.70')
