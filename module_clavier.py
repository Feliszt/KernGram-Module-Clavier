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
        self.key_history_size       = 10
        self.key_history            = []
        self.key_pressed            = ''
        self.key_held               = ''
        self.key_held_stored         = ''
        self.keyboard_state         = -1
        self.keyboard_state_prev    = -1

        #
        self.launch_thread(self.keyboard_processing)
        self.launch_thread(self.keyboard_listener)
        self.start_play()
        KernGramModule.run_network(self)

    # register a key press
    def on_press(self, key) :
        self.key_pressed = key
        if key == keyboard.Key.esc:
            quit()

    ## methods ##
    # get interaction with keyboard
    def keyboard_listener(self) :
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    # get interaction with keyboard
    def keyboard_processing(self) :
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
                        self.on_key_released(self.key_held_stored)
                    self.on_key_pressed(self.key_held)
                self.key_held_stored = self.key_held

            # no keys have been pressed
            if self.keyboard_state == 0 and self.keyboard_state_prev != 0 and self.keyboard_state_prev != -1 :
                if self.key_held_stored != '' :
                    self.on_key_released(self.key_held_stored)
                self.key_held_stored = ''

            #
            #print(self.key_history)
            self.keyboard_state_prev = self.keyboard_state
            time.sleep(0.05)

    # a key has been pressed
    def on_key_pressed(self, key) :
        print("[key_pressed]\t{}".format(key))

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
        print("[key_released]\t{}".format(key))

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
