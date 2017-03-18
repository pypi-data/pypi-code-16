from subprocess import Popen, PIPE
import os
import numpy
import numpy.fft
import pyaudio
import scipy
from numpy import *
from scipy.io.wavfile import read


def calcChroma(wav_path="test.wav", frame_len=1024, frame_overlap=0.5):
    total_chroma = []
    sr, data = read(wav_path)
    audio = AudioFile.open(wav_path, sampleRate=sr)
    audio_frames = audio.frames(frame_len, frame_overlap=frame_overlap)
    for frame_item in audio_frames:
        audio_frame_spectrum_ = frame_item.spectrum()
        audio_frame_chroma = audio_frame_spectrum_.chroma()
        total_chroma.append(audio_frame_chroma)
    return total_chroma


def chroma(spectrum):
    """
    Compute the 12-ET chroma vector from this spectrum
    """
    chroma = [0] * 12
    for index in range(0, len(spectrum)):

        # Assign a frequency value to each bin
        f = index * (spectrum.sampleRate / 2.0) / len(spectrum)

        # Convert frequency to pitch to pitch class
        if f != 0:
            pitch = frequencyToMidi(f)
        else:
            pitch = 0
        pitchClass = pitch % 12

        chroma[pitchClass] = chroma[pitchClass] + abs(spectrum[index])

    # Normalize the chroma vector
    maxElement = max(chroma)
    chroma = [c / maxElement for c in chroma]

    return chroma


def frequencyToMidi(frequency):
    """
    Convert a given frequency in Hertz to its corresponding MIDI pitch number (60 = Middle C)
    """
    return int(round(69 + 12 * math.log(frequency / 440.0, 2)))


class Spectrum(numpy.ndarray):
    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. InfoArray():
        #    obj is None
        #    (we're in the middle of the InfoArray.__new__
        #    constructor, and self.info will be set when we return to
        #    InfoArray.__new__)
        if obj is None: return
        # From view casting - e.g arr.view(InfoArray):
        #    obj is arr
        #    (type(obj) can be InfoArray)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is InfoArray
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).

        self.sampleRate = getattr(obj, 'sampleRate', None)

        # We do not need to return anything

    def chroma(self):
        return chroma(self)


class Frame(numpy.ndarray):
    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. InfoArray():
        #    obj is None
        #    (we're in the middle of the InfoArray.__new__
        #    constructor, and self.info will be set when we return to
        #    InfoArray.__new__)
        if obj is None: return
        # From view casting - e.g arr.view(InfoArray):
        #    obj is arr
        #    (type(obj) can be InfoArray)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is InfoArray
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).

        self.sampleRate = getattr(obj, 'sampleRate', None)
        self.channels = getattr(obj, 'channels', None)
        self.format = getattr(obj, 'format', None)

        # We do not need to return anything

    def frames(self, frameSize, frame_overlap=0.5, windowFunction=None):
        """
        Decompose this frame into smaller frames of size frameSize
        """
        frames = []
        start = 0
        end = frameSize
        while start < len(self):

            if windowFunction == None:
                frames.append(self[start:end])
            else:
                window = windowFunction(frameSize)
                window.shape = (frameSize, 1)
                window = numpy.squeeze(window)
                frame = self[start:end]
                if len(frame) < len(window):
                    # Zero pad
                    frameType = frame.__class__.__name__

                    sampleRate = frame.sampleRate
                    channels = frame.channels
                    format = frame.format

                    diff = len(window) - len(frame)
                    frame = numpy.append(frame, [0] * diff)

                    if frameType == "AudioFile":
                        frame = frame.view(AudioFile)
                    else:
                        frame = frame.view(Frame)

                    # Restore frame properties
                    frame.sampleRate = sampleRate
                    frame.channels = channels
                    frame.format = format

                windowedFrame = frame * window
                frames.append(windowedFrame)

            move = int(frameSize * frame_overlap)
            start = start + move
            end = end + move

        return frames

    def spectrum(self):
        """
        Compute the spectrum using an FFT
        Returns an instance of Spectrum
        """
        return fft(self)


class AudioFile(Frame):
    @staticmethod
    def open(filename, sampleRate=44100):
        """
        Open a file (WAV or MP3), return instance of this class with data loaded in
        Note that this is a static method. This is the preferred method of constructing this object
        """
        _, ext = os.path.splitext(filename)

        if ext.endswith('mp3') or ext.endswith('m4a'):

            ffmpeg = Popen([
                "ffmpeg",
                "-i", filename,
                "-vn", "-acodec", "pcm_s16le",  # Little Endian 16 bit PCM
                "-ac", "1", "-ar", str(sampleRate),  # -ac = audio channels (1)
                "-f", "s16le", "-"],  # -f wav for WAV file
                stdin=PIPE, stdout=PIPE, stderr=open(os.devnull, "w"))

            rawData = ffmpeg.stdout

            mp3Array = numpy.fromstring(rawData.read(), numpy.int16)
            mp3Array = mp3Array.astype('float32') / 32767.0
            audioFile = mp3Array.view(AudioFile)

            audioFile.sampleRate = sampleRate
            audioFile.channels = 1
            audioFile.format = pyaudio.paFloat32

            return audioFile

        elif ext.endswith('wav'):
            sampleRate, samples = scipy.io.wavfile.read(filename)

            # Convert to float
            samples = samples.astype('float32') / 32767.0

            # Get left channel
            if len(samples.shape) > 1:
                samples = samples[:, 0]

            audioFile = samples.view(AudioFile)
            audioFile.sampleRate = sampleRate
            audioFile.channels = 1
            audioFile.format = pyaudio.paFloat32

            return audioFile


# Fourier Transforms
def fft(frame):
    """
    Compute the spectrum using an FFT
    Returns an instance of Spectrum
    """
    fftdata = numpy.fft.rfft(frame)  # rfft only returns the real half of the FFT values, which is all we need
    spectrum = fftdata.view(Spectrum)
    spectrum.sampleRate = frame.sampleRate
    return spectrum
