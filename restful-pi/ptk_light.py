import psutil
import signal

class PTK:
    def kill_process_and_children(self, pid, sig=signal.SIGTERM):
        """Kill a process and all its children processes."""
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return

        children = process.children(recursive=True)
        for child in children:
            try:
                child.send_signal(sig)
            except psutil.NoSuchProcess:
                pass

        try:
            process.send_signal(sig)
        except :
            pass

    def find_and_kill_process(self):
        """Find and kill all processes matching the given name."""
        process_name = 'test'
        parent_py = 'led_cube.py'
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline']):
            if proc.info['name'] == process_name:
                print('name:%s' % (proc.info['name']))
                print(proc.info)
                self.kill_process_and_children(proc.info['pid'])
            if parent_py in proc.info['cmdline']:
                print('name:%s' % (proc.info['name']))
                print(proc.info)
                self.kill_process_and_children(proc.info['pid'])
            for entry in proc.info['cmdline']:
                if (entry.endswith('/test') or
                   entry.endswith('led_cube.py')):
                    print('name:%s' % (proc.info['name']))
                    print(proc.info)
                    self.kill_process_and_children(proc.info['pid'])
                       
                

if __name__ == "__main__":
    myptk = PTK()
    myptk.find_and_kill_process()
