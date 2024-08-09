# -*- encoding: UTF-8 -*-

"""Example: Get Signal from Front Microphone & Save it to a WAV file"""

import qi
import argparse
import sys
import time
import subprocess
import numpy as np
import wave
from naoqi import ALProxy


class SoundProcessingModule(object):
    """
    A simple get signal from the front microphone of Nao & save it to a WAV file.
    It requires numpy.
    """

    def __init__(self, app):
        """
        Initialise services and variables.
        """
        super(SoundProcessingModule, self).__init__()
        app.start()
        session = app.session

        # Get the service ALAudioDevice.
        self.audio_service = session.service("ALAudioDevice")
        self.isRecording = False
        self.module_name = "SoundProcessingModule"
        self.wav_file_path = "recorded_audio.wav"  # Path to save the recorded audio

    def startRecording(self):
        """
        Start recording audio.
        """
        # Open a WAV file for writing
        self.wav_file = wave.open(self.wav_file_path, 'wb')
        self.wav_file.setnchannels(1)  # Set number of channels to 1 (mono)
        self.wav_file.setsampwidth(2)  # Set sample width to 2 bytes (16-bit)
        self.wav_file.setframerate(16000)  # Set the frame rate to 16000 Hz
        self.isRecording = True

        # Subscribe to audio input
        self.audio_service.setClientPreferences(self.module_name, 16000, 3, 0)
        self.audio_service.subscribe(self.module_name)

        start_time = time.time()  # Record the start time

        while self.isRecording:
            current_time = time.time()
            if current_time - start_time >= 5:  # Stop recording after 7 seconds
                self.stopRecording()
            else:
                time.sleep(0.1)  # Check every 0.1 seconds

    def stopRecording(self):
        """
        Stop recording audio and close the WAV file.
        """
        self.isRecording = False
        self.audio_service.unsubscribe(self.module_name)
        self.wav_file.close()
        print("Recording stopped. Audio saved to:", self.wav_file_path)

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Callback function to process incoming audio data.
        """
        if self.isRecording:
            # Write audio data to the WAV file
            self.wav_file.writeframes(inputBuffer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.129",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["SoundProcessingModule", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
              "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    # Create an instance of the SoundProcessingModule class
    my_sound_processing_module = SoundProcessingModule(app)
    app.session.registerService("SoundProcessingModule", my_sound_processing_module)
    tts = ALProxy("ALTextToSpeech", "192.168.0.129", 9559)
    with open("on_off.txt", "r") as file:
         on_off=file.read()
    if on_off =="chaton" :    
        tts.setLanguage("English")
        robot_ip = "192.168.0.129"  # Replace with your robot's IP address
        robot_port = 9559
        behavior_manager = ALProxy("ALBehaviorManager", robot_ip, robot_port)

        behavior_manager.startBehavior("led-sound")
        time.sleep(1)
        my_sound_processing_module.startRecording()
    elif on_off =="chatoff":
      robot_ip = "192.168.0.129"  # Replace with your robot's IP address
      robot_port = 9559
      behavior_manager = ALProxy("ALBehaviorManager", robot_ip, robot_port)
      tts.setLanguage("English")
      tts.say("say , chat on , to trun on the chat")
      behavior_manager.startBehavior("led-sound")
      my_sound_processing_module.startRecording()      
