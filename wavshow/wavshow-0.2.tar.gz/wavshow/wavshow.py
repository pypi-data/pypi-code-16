#!/usr/bin/env python
import sys

import click
import numpy
import scipy.signal
import soundfile
import matplotlib.pyplot as plt


def plotspec(wav, fs):
  freq, time, spec = scipy.signal.spectrogram(wav, fs)
  plt.imshow(10 * numpy.log10(spec),
             aspect='auto', interpolation='nearest', origin='lower')

  # Set x axis (Time)
  locs = list(map(int, numpy.linspace(0, len(time)-1, 10)))
  plt.xticks(locs, time[locs])
  plt.xlabel('Time [s]')

  # Set y axis (Frequency)
  locs = range(0, len(freq), 16)
  plt.yticks(locs, map(int, freq[locs]))
  plt.ylabel('Frequency [Hz]')

def plotwav(wav, fs):
  plt.plot(wav, 'k-')
 
  # Set x axis (Time)
  samples = numpy.fromiter(map(int, numpy.linspace(0, len(wav), 10)),
                           dtype=numpy.int32)
  seconds = list(map(lambda t: '%.2f' % t, 1.0 * samples / fs))
  plt.xticks(samples, seconds)
  plt.xlim(0, len(wav))

  # Set y axis (Amplitude)
  plt.ylim(-1, 1)
  plt.ylabel('Amplitude')

def plot_main(wavname, outfile):
  print('Plot', wavname)
  plt.figure()

  # Load wave file
  obj = soundfile.SoundFile(wavname)
  wav = obj.read()
  fs = obj.samplerate
  is_multichannel = len(wav.shape) == 2

  if is_multichannel:
    plt.subplot(wav.shape[1], 1, 1)
    plt.title(wavname)
    for ch in range(wav.shape[1]):
      plt.subplot(wav.shape[1], 1, ch+1)
      plotwav(wav[:, ch], fs)

  else:
    plt.subplot(2, 1, 1)
    plt.title(wavname)
    plotwav(wav, fs)

    plt.subplot(2, 1, 2)
    plotspec(wav, fs)

  print('Save', outfile)
  if outfile:
    plt.savefig(outfile)
  else:
    plt.show()

@click.command()
@click.option('--outfile', '-o', help='A file name pattern for help.')
@click.option('--infiles', '-i', help='Audio files to plot', multiple=True)
def main(infiles, outfile):
   '''
   Plot given wave files and spectrogram.
   
   \b
   Examples:
     (1) Plot a wave file "sample.wav"
         $ wavshow -i sample.wav
     (2) Plot multiple wave files "sample1.wav", "sample2.wav"
         $ wavshow -i sample1.wav -i sample2.wav
     (3) Plot a wave file "sample.wav" and save it as "sample01.png"
         $ wavshow -i sample.wav -o sample%02d.png

   '''
   for index, wavname in enumerate(infiles):
     if outfile:
       plot_main(wavname, outfile % index)
     else:
       plot_main(wavname, outfile)

if __name__ == '__main__':
  main()

