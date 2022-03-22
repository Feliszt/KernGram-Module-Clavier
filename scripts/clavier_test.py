#import keyboard
from pynput import keyboard
import threading
import time

class Clavier_process() :
    #
    def __init__(self):
        # variables
        self.key_history_size       = 8
        self.key_check_time         = 0.05
        self.key_history            = []
        self.curr_key_pressed       = ''
        self.keys_held              = []
        self.keyboard_state         = -1
        self.keyboard_state_prev    = -1

        # process keys pressed
        self.launch_thread(self.keyboard_processing, None)

        # keyboard collecting
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    # launch thread for function
    def launch_thread(self, _function, _args) :
        if _args == None :
            thread = threading.Thread(target = _function)
        else :
            thread = threading.Thread(target = _function, args=[_args])
        thread.daemon = True
        thread.start()

    # register a key press
    def on_press(self, key) :
        self.curr_key_pressed = key
        if key == keyboard.Key.esc:
            quit()

    # register a key release
    def on_release(self, key) :
        if key in self.keys_held :
            self.launch_thread(self.release_timer, key)

    # a simple timer to delay the processing of a pressed key
    def release_timer(self, key) :
        time.sleep(2 * self.key_check_time)
        for i in range(0, self.key_history_size) :
            if self.key_history[-1] == key :
                return
            time.sleep(self.key_check_time)
        if key in self.keys_held :
            self.keys_held.remove(key)
            #print(self.keys_held)
            print("key released : {}".format(key))


    # get interaction with keyboard
    def keyboard_processing(self):
        while True :
            # create key history list
            self.key_history.append(self.curr_key_pressed)
            self.curr_key_pressed = ''
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
                if self.key_history[0] not in self.keys_held :
                    self.keys_held.append(self.key_history[0])
                    #print(self.keys_held)
                    print("key pressed : {}".format(self.key_history[0]))


            #
            #print(threading.active_count())
            #print(self.key_history)
            #print(self.keyboard_state)
            self.keyboard_state_prev = self.keyboard_state
            time.sleep(self.key_check_time)

clavier_Test = Clavier_process()
