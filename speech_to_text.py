# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_sample.py
# https://learn.microsoft.com/en-GB/azure/cognitive-services/speech-service/how-to-use-codec-compressed-audio-input-streams?tabs=linux%2Cdebian%2Cjava-android%2Cterminal&pivots=programming-language-python
# pip install azure-cognitiveservices-speech
# sudo apt install libgstreamer1.0-0 \
# gstreamer1.0-plugins-base \
# gstreamer1.0-plugins-good \
# gstreamer1.0-plugins-bad \
# gstreamer1.0-plugins-ugly
import time
import azure.cognitiveservices.speech as speechsdk
import json

# https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-configure-subscription
speechsdk_creds = json.load(open("azure_speechsdk_creds.json"))
speech_key, service_region = speechsdk_creds['SPEECH_KEY'], speechsdk_creds['SERVICE_REGION']

# handle compressed audio input streams
class BinaryFileReaderCallback(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self, filename: str):
        super().__init__()
        self._file_h = open(filename, "rb")

    def read(self, buffer: memoryview) -> int:
        # print('trying to read {} frames'.format(buffer.nbytes))
        try:
            size = buffer.nbytes
            frames = self._file_h.read(size)

            buffer[:len(frames)] = frames
            # print('read {} frames'.format(len(frames)))

            return len(frames)
        except Exception as ex:
            print('Exception in `read`: {}'.format(ex))
            raise

    def close(self) -> None:
        print('closing file')
        try:
            self._file_h.close()
        except Exception as ex:
            print('Exception in `close`: {}'.format(ex))
            raise


def compressed_stream_helper(compressed_format, mp3_file_path):
    callback = BinaryFileReaderCallback(mp3_file_path)
    stream = speechsdk.audio.PullAudioInputStream(stream_format=compressed_format, pull_stream_callback=callback)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, language="he-IL", audio_config=audio_config)
    # speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    text_so_far=''
    def write_cb(evt):
        '''callback that appends the recognized text to a string'''
        nonlocal text_so_far
        text=evt.result.text

        print(f'RECOGNIZED: {text}')
        text_so_far += f'{text}\n'

    # Connect callbacks to the events fired by the speech recognizer
    # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    # speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.recognized.connect(write_cb)
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    print('Starting recognition')
    try:
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)
    except:
        done=True

    print('Stopping recognition')
    speech_recognizer.stop_continuous_recognition()

    return text_so_far

def pull_audio_input_stream_compressed_mp3(mp3_file_path: str):
    # Create a compressed format
    compressed_format = speechsdk.audio.AudioStreamFormat(compressed_stream_format=speechsdk.AudioStreamContainerFormat.MP3)
    return compressed_stream_helper(compressed_format, mp3_file_path)


def str_to_file(s, filename):
    with open(filename, 'w') as f:
        f.write(s)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-f', type=str, default='scratch/test.mp3')

    args = parser.parse_args()
    recognized_text = pull_audio_input_stream_compressed_mp3(args.filename)

    print('Writing to file')
    str_to_file(recognized_text, f'{args.filename}.txt')