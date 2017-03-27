import wave
from pyaudio import PyAudio
from threading import Thread

CHUNK_SIZE = 1024

class Sound:
    def __init__(self, path):
        """ Wrapper for sound playing

        path -- WAV file path
        """
        self.wf     = wave.open(path, 'rb')
        self.pa     = PyAudio()
        self.stream = self.pa.open(
                format=self.pa.get_format_from_width(self.wf.getsampwidth()),
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True
                )
        self.playing = False

    def __del__(self):
        self.close()

    def play(self):
        """ Plays the sound in a different thread (non-blocking) """
        if not self.playing:
            Thread(target=self._play_sound).start()
        return(self)

    def play_wait(self):
        """ Plays the sound in the main thread (blocking) """
        self._play_sound()

    def _play_sound(self):
        self.playing=True
        self.wf.rewind()
        self.stream.start_stream()
        data = self.wf.readframes(CHUNK_SIZE)
        while data:
            self.stream.write(data)
            data = self.wf.readframes(CHUNK_SIZE)
        self.stream.stop_stream()
        self.playing = False
    
    def close(self):
        """ Closes audio stream """
        self.stream.close()
        self.pa.terminate()
