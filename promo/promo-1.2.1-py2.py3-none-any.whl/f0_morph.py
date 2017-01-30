'''
Created on May 31, 2013

@author: timmahrt

Contains utilities for extracting, creating, and manipulating pitch files in
praat.
'''

from os.path import join

from praatio import tgio
from praatio import dataio
from praatio import praat_scripts

from promo.morph_utils import utils
from promo.morph_utils import audio_scripts
from promo.morph_utils import plot_morphed_data
from promo.morph_utils import morph_sequence


class MissingPitchDataException(Exception):
        
    def __str__(self):
        txt = ("\n\nNo data points available in a region for morphing.\n"
               "Two data points are needed in each region to do the morph\n"
               "Regions with fewer than two samples are skipped, which "
               "should be fine for some cases (e.g. unvoiced segments).\n"
               "If you need more data points, see "
               "promo.morph_utils.interpolation")
        return txt


def getPitchForIntervals(data, tgFN, tierName):
    '''
    Preps data for use in f0Morph
    '''
    tg = tgio.openTextGrid(tgFN)
    data = tg.tierDict[tierName].getValuesInIntervals(data)
    data = [dataList for _, dataList in data]

    return data


def f0Morph(fromWavFN, pitchPath, stepList,
            outputName, doPlotPitchSteps, fromPitchData, toPitchData,
            outputMinPitch, outputMaxPitch, praatEXE, keepPitchRange=False,
            keepAveragePitch=False):
    '''
    Resynthesizes the pitch track from a source to a target wav file

    fromPitchData and toPitchData should be segmented according to the
    portions that you want to morph.  The two lists must have the same
    number of sublists.

    Occurs over a three-step process.

    This function can act as a template for how to use the function
    morph_sequence.morphChunkedDataLists to morph pitch contours or
    other data.
    
    By default, everything is morphed, but it is possible to maintain elements
    of the original speaker's pitch (average pitch and pitch range) by setting
    the appropriate flag)
    '''

    fromDuration = audio_scripts.getSoundFileDuration(fromWavFN)

    # Iterative pitch tier data path
    pitchTierPath = join(pitchPath, "pitchTiers")
    resynthesizedPath = join(pitchPath, "f0_resynthesized_wavs")
    for tmpPath in [pitchTierPath, resynthesizedPath]:
        utils.makeDir(tmpPath)

    # 1. Prepare the data for morphing - acquire the segments to merge
    # (Done elsewhere, with the input fed into this function)
    
    # 2. Morph the fromData to the toData
    try:
        finalOutputList = morph_sequence.morphChunkedDataLists(fromPitchData,
                                                               toPitchData,
                                                               stepList)
    except IndexError:
        raise MissingPitchDataException()

    fromPitchData = [row for subList in fromPitchData for row in subList]
    toPitchData = [row for subList in toPitchData for row in subList]

    # 3. Save the pitch data and resynthesize the pitch
    mergedDataList = []
    for i in range(0, len(finalOutputList)):
        
        outputDataList = finalOutputList[i]
        
        if keepPitchRange is True:
            outputDataList = morph_sequence.morphRange(outputDataList,
                                                       fromPitchData)
            
        if keepAveragePitch is True:
            outputDataList = morph_sequence.morphAveragePitch(outputDataList,
                                                              fromPitchData)
        
        stepOutputName = "%s_%0.3g" % (outputName, stepList[i])
        pitchFNFullPath = join(pitchTierPath, "%s.PitchTier" % stepOutputName)
        outputFN = join(resynthesizedPath, "%s.wav" % stepOutputName)
        pointObj = dataio.PointObject2D(outputDataList, dataio.PITCH,
                                        0, fromDuration)
        pointObj.save(pitchFNFullPath)

        outputTime, outputVals = zip(*outputDataList)
        mergedDataList.append((outputTime, outputVals))
        
        praat_scripts.resynthesizePitch(praatEXE, fromWavFN, pitchFNFullPath,
                                        outputFN, outputMinPitch,
                                        outputMaxPitch)

    # 4. (Optional) Plot the generated contours
    if doPlotPitchSteps:

        fromTime, fromVals = zip(*fromPitchData)
        toTime, toVals = zip(*toPitchData)

        plot_morphed_data.plotF0((fromTime, fromVals),
                                 (toTime, toVals),
                                 mergedDataList,
                                 join(pitchTierPath,
                                      "%s.png" % outputName))
