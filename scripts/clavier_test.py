#import keyboard
from pynput import keyboard
import threading
import time

class Clavier_process() :
    #
    def __init__(self):
        # variables
        self.key_history_size       = 20
        self.key_history            = []
        self.key_pressed            = ''
        self.key_held               = ''
        self.key_held_stored         = ''
        self.keyboard_state         = -1
        self.keyboard_state_prev    = -1

        # process keys pressed
        self.launch_thread(self.keyboard_processing)

        # keyboard collecting
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    # launch thread for function
    def launch_thread(self, function) :
        thread = threading.Thread(target = function)
        thread.daemon = True
        thread.start()

    # register a key press
    def on_press(self, key) :
        self.key_pressed = key
        if key == keyboard.Key.esc:
            quit()

    # get interaction with keyboard
    def keyboard_processing(self):
        while True :
            # create key history list
            self.key_history.append(self.key_pressed)
            self.key_pressed = ''
            if len(self.key_history) > self.key_history_size :
                self.key_history.pop(0)

                # check if a single key has been pressed
                if self.key_history.count(self.key_history[0]) == len(self.key_history) :
                    if self.key_history[0] == '' :
                        self.keyboard_state = 0
                    else :
                        self.keyboard_state = 2
                else :
                    self.keyboard_state = 1

            # a single key has been pressed
            if self.keyboard_state == 2 and self.keyboard_state_prev != 2 :
                self.key_held = self.key_history[0]
                if self.key_held != self.key_held_stored :
                    if self.key_held_stored != '' :
                        print("key released : {}".format(self.key_held_stored))
                    print("key pressed : {}".format(self.key_held))
                self.key_held_stored = self.key_held

            # no keys have been pressed
            if self.keyboard_state == 0 and self.keyboard_state_prev != 0 and self.keyboard_state_prev != -1 :
                if self.key_held_stored != '' :
                    print("key released : {}".format(self.key_held_stored))
                self.key_held_stored = ''

            #
            #print(self.key_history)
            self.keyboard_state_prev = self.keyboard_state
            time.sleep(0.05)

clavier_Test = Clavier_process()
