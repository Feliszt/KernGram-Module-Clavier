# add paths
import sys
sys.path.append("./KernGram-Module-Abstract")

# abstract module
from module_abstract import *

# keyboard
import keyboard


# class for module poids inherited from abstract class
class KernGram_Clavier(KernGramModule) :
    # module clavier - init
    def __init__(self) :
        # run init from abstract class
        KernGramModule.__init__(self)
        logging.info("Module type [{}] with name [{}] starts.".format(self.config["module_type"], self.config["unique_name"]))

        #
        self.launch_thread(self.keyboard_processing)
        self.start_play()
        KernGramModule.run_network(self)

    ## methods ##
    # get interaction with keyboard
    def keyboard_processing(self) :
        # pingpong removes event triggering when key is up
        pingpong = True
        while True :
            recorded = keyboard.read_key()
            pingpong = not pingpong

            # key is down
            if pingpong :

                # if play state and calib is not empty
                if self.module_state == 0 and self.calib["events"]:
                    for event in self.calib["events"] :
                        if recorded == event["specs"][0] :
                            logging.info("Event [{} - {}] is UP".format(event["id"], event["id"]))
                            self.send_osc_message("/event", True, (self.ID, 'i'), (event["id"], 'i'), ("UP", 's'))

                # if calibration state
                if self.module_state == 1 :
                    # save level
                    self.can_register_event([recorded])
                    logging.info("Save level [{}] with temp name.".format(recorded))
                    print(self.calib)
                    c = """
                    if recorded in self.calib["events"] :
                        logging.info("Cannot save level [{}], too close to [{}] @ {}".format(_delta, event["name"], event["specs"][0]))
                        self.send_osc_message("/invalid_event", False, (self.ID, 'i'), ("Cannot calibrate this event, it already exists.".format(event["id"]), 's'))
                        """


    # calibration method
    def start_calibration(self, unused_addr, args) :
        if not KernGramModule.start_calibration(self, unused_addr, args) :
            return

        # notify server
        self.send_osc_message("/ready_calibrate", True,(self.ID, 'i'), (self.config["calibration_instruction"], 's'))
