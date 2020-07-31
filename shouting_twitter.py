import tweepy
import time
import pyaudio
import struct
import math
import speech_recognition as sr

# Using recognize_speech_from_mic() from https://realpython.com/python-speech-recognition/ because I AM LAZY
def recognize_speech_from_mic(recognizer, microphone):
    print("Listening...")
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
            successful
    "error":   `None` if no error occured, otherwise a string containing
            an error message if the API could not be reached or
            speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
            otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {"success": True, "error": None, "transcription": None}

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

# got this from https://stackoverflow.com/questions/25868428/pyaudio-how-to-check-volume because if it works why would I not use this
def find_decibel_level(data):
    count = len(data) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    return math.sqrt(sum_squares / count)

def listen_decibel():
    # Define parameters and stuff for recognizer
    sample_rate = 48000
    chunk_size = 2048
    r = sr.Recognizer()
    mic = sr.Microphone(sample_rate=sample_rate, chunk_size=chunk_size)
    CHUNK = 1024

    # Define pyaudio
    p = pyaudio.PyAudio()

    # Start stream
    stream = p.open(
        format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK
    )

    # Keep on building data buffer until done
    while 1:
        data = stream.read(CHUNK) # reading buffer to var
        decibel = find_decibel_level(data) # checking decibel level
        print(decibel) # printing decibel level out because it looks cool

        # If you are yelling...
        if decibel > 0.4:
            stream.close() # Stop the stream to make sure that nothing extra is being picked up
            return(recognize_speech_from_mic(r, mic)) # Turn captured audio data into text

def tweet(message):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("VaNB20TfNqH1lQxYCEYR6A6Z3", "1gVqKIwaZb4v27G5YuxB1XLylp5YYg7hBr8P4pMd4raQhFtGwA")
    auth.set_access_token("787314212381089792-xLOWhfrRa7kFIQsb8Hfe0MXHs8hmIv8", "YF5oTmqHGhncn7Pp5ehst73HRRbiY1xSZWUCvWorH9goa")

    # Create API object
    api = tweepy.API(auth)

    try:
        api.verify_credentials() # Checks if it authenticates
        print("Credentials Verified!")
        api.update_status(message.upper()) # Tweet audio message in all caps!
        print("Tweeted!")
    except:
        print("Nope something is wrong with your credentials.")

def main():
    # Forever check decibel level and tweet if its loud enough
    while 1:
        print("Listening for your yelling!")
        res = listen_decibel()
        print("You said: {0}".format(res["transcription"]))
        tweet(res["transcription"])

if __name__ == "__main__":
    # execute only if run as a script
    main()
