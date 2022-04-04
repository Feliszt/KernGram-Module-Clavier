# add paths
import sys
sys.path.append("./KernGram-Module-Abstract")

# abstract module
from module_abstract import *

# keyboard
from pynput import keyboard
import sys


# class for module poids inherited from abstract class
class KernGram_Clavier(KernGramModule) :
    # module clavier - init
    def __init__(self) :
        # run init from abstract class
        KernGramModule.__init__(self)
        logging.info("Module type [{}] with name [{}] starts.".format(self.config["module_type"], self.config["unique_name"]))

        # variables
        self.key_history_size       = self.config["key_history_size"]
        self.key_check_time         = self.config["key_check_time"]
        self.key_history            = []
        self.curr_key_pressed       = ''
        self.keys_held              = []
        self.keyboard_state         = -1
        self.keyboard_state_prev    = -1

        #
        self.launch_thread(self.keyboard_listening, None)
        self.launch_thread(self.keyboard_processing, None)
        self.start_play()
        KernGramModule.run_network(self)

    # register a key press
    def on_press(self, key) :
        self.curr_key_pressed = key
        if key == keyboard.Key.esc:
            quit()

    # register a key release
    def on_release(self, key) :
        self.launch_thread(self.release_timer, key)

    # a simple timer to delay the processing of a pressed key
    def release_timer(self, key) :
        while self.key_history[-1] == key :
            continue
        #print("start timer for {}".format(key))
        for i in range(0, self.key_history_size) :
            if self.key_history[-1] == key :
                #print("has {} in key history".format(key))
                return
            time.sleep(self.key_check_time)
        if key in self.keys_held :
            self.keys_held.remove(key)
            self.on_key_released(key)

    # get interaction with keyboard
    def keyboard_listening(self) :
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    # get interaction with keyboard
    def keyboard_processing(self) :
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
                    self.launch_thread(self.on_key_pressed, self.key_history[0])

            #
            #print(threading.active_count())
            #print(self.key_history)
            #print(self.keys_held)
            #print(self.keyboard_state)
            self.keyboard_state_prev = self.keyboard_state
            time.sleep(self.key_check_time)

    # a key has been pressed
    def on_key_pressed(self, key) :
        #print("[key_pressed]\t{}".format(key))
        # if play state and calib is not empty
        if self.module_state == 0 and self.calib["events"] :
            for event in self.calib["events"] :
                if str(key) == event["specs"][0] :
                    logging.info("Event [{} - {}] is DOWN".format(event["id"], event["id"]))
                    self.send_osc_message("/event", False, (self.ID, 'i'), (event["id"], 'i'), ("DOWN", 's'))

        # if calibration state
        if self.module_state == 1 :
            # save level
            self.can_register_event([str(key)])
            logging.info("Save level [{}] with temp name.".format(key))


    # a key has been released
    def on_key_released(self, key) :
        #print("[key_released]\t{}".format(key))
        # if play state and calib is not empty
        if self.module_state == 0 and self.calib["events"] :
            for event in self.calib["events"] :
                if str(key) == event["specs"][0] :
                    logging.info("Event [{} - {}] is UP".format(event["id"], event["id"]))
                    self.send_osc_message("/event", False, (self.ID, 'i'), (event["id"], 'i'), ("UP", 's'))

    # calibration method
    def start_calibration(self, unused_addr, args) :
        if not KernGramModule.start_calibration(self, unused_addr, args) :
            return

        # notify server
        self.send_osc_message("/ready_calibrate", True,(self.ID, 'i'), (self.config["calibration_instruction"], 's'))
