from pynput import keyboard
import time

def on_press(key):
    print("[key_press]\t{}".format(key))

    if key == keyboard.Key.esc:
        quit()

def on_release(key):
    print("[key_release]\t{}".format(key))

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

while True:
    time.sleep(0.1)
