import threading
import time
import sys
import queue
import webview

class Api:
    def __init__(self):
        self.cancel_heavy_stuff_flag = False
        self.__frame_info_queue = queue.Queue()

    def init(self):
        response = {
            'message': 'Hello from Python {0}'.format(sys.version)
        }
        return response

    def getRandomNumber(self):
        response = {
            'message': 'Here is a random number courtesy of randint: {0}'.format(random.randint(0, 100000000))
        }
        print('aha!')
        return response

    def doHeavyStuff(self):
        time.sleep(0.1)  # sleep to prevent from the ui thread from freezing for a moment
        now = time.time()
        self.cancel_heavy_stuff_flag = False
        for i in range(0, 1000000):
            _ = i * random.randint(0, 1000)
            if self.cancel_heavy_stuff_flag:
                response = {'message': 'Operation cancelled'}
                break
        else:
            then = time.time()
            response = {
                'message': 'Operation took {0:.1f} seconds on the thread {1}'.format((then - now), threading.current_thread())
            }
        return response

    def cancelHeavyStuff(self):
        time.sleep(0.1)
        self.cancel_heavy_stuff_flag = True

    def sayHelloTo(self, name):
        response = {
            'message': 'Hello {0}!'.format(name)
        }
        return response


if __name__ == '__main__':
    api = Api()
    window = webview.create_window('API example','https://unet.run:8443/apps/pydoh/pydoh.html', js_api=api)
    webview.start()

def input_thread(input_queue):
    while True:
        # read single character off stdin
        input_queue.put(readchar.readchar())

input_queue = queue.Queue()
input_thread = threading.Thread(target=input_thread, args=(input_queue,))
input_thread.daemon = True
input_thread.start()
