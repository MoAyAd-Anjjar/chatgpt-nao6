# -*- coding: utf-8 -*-
import re
import threading
from naoqi import ALProxy
import codecs
import time

# Global variable to indicate if the first function is running
is_running = False

# Check if the text contains Arabic characters
def has_arabic(text):
    arabic_pattern = re.compile(u'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))

def function1(tts, contents):
    global is_running
    try:
        # Set is_running to True at the start of the function
        is_running = True
        contents_utf8 = contents.encode("utf-8")
        tts.say(contents_utf8)
    except Exception as e:
        print("Error in text-to-speech: {}".format(e))
    finally:
        # Ensure is_running is set to False when function1 stops
        is_running = False

def function2(behavior_manager, behavior_name,posture_proxy):
    global is_running
    try:
        while is_running:
            
            if not behavior_manager.isBehaviorRunning(behavior_name):
                behavior_manager.startBehavior(behavior_name)
            # Check frequently if the behavior is still running or is_running has changed
            while behavior_manager.isBehaviorRunning(behavior_name):
                if not is_running:
                    behavior_manager.stopBehavior(behavior_name)  # Stop behavior immediately if needed
                    break
                time.sleep(0.05)  # Small sleep to reduce CPU usage and increase responsiveness
    except Exception as e:
        print("Error managing behavior: {}".format(e))

def main(robot_ip):
    global is_running
    try:
        # Initialize proxies
        behavior_manager = ALProxy("ALBehaviorManager", robot_ip, 9559)
        tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
        posture_proxy = ALProxy("ALRobotPosture", robot_ip, 9559)
        
        # Read the contents of the file once
        with codecs.open("chatAI.txt", "r", encoding="utf-8") as file:
            contents = file.read()
            length = len(contents)
            print("Length of the file contents: {}".format(length))
            
            if has_arabic(contents):
                tts.setLanguage("Arabic")
            else:
                tts.setLanguage("English")
        
        # Select behavior based on the length of the contents
        if length >= 500:
            behavior_name = "longspeech"  # Replace with the correct behavior name
        elif length >= 300:
            behavior_name = "midspeech"  # Replace with the correct behavior name
        else:
            behavior_name = "samllspeechs"

        # Set the flag to True before starting the threads
        is_running = True

        # Start function1 in a thread
        thread1 = threading.Thread(target=function1, args=(tts, contents))
        thread1.start()

        # Start function2 in the main thread
        function2(behavior_manager, behavior_name,posture_proxy)

        # Wait for function1 thread to finish
        thread1.join()

    except Exception as e:
        print("Error: {}".format(e))
    finally:
        # Ensure that is_running is set to False when main exits
        is_running = False

if __name__ == "__main__":
    # Change the IP address to your NAO's IP address
    robot_ip = "localhost"  # Example IP address
    main(robot_ip)
