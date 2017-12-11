import os
from os.path import join

from praatio import tgio
from praatio import pitch_and_intensity


# For pitch extraction, we need the location of praat on your computer
#praatEXE = r"C:\Praat.exe"
praatEXE = "/Applications/Praat.app/Contents/MacOS/Praat"

rootPath = join('..', 'examples', 'files')
pitchPath = join(rootPath, "pitch_extraction", "pitch")

fnList = [('mary.wav', 'mary.TextGrid'),
          ('bobby.wav', 'bobby_words.TextGrid')]

# The names of interest -- in an example working with more data, this would be more comprehensive
nameList = ['mary', 'BOBBY', 'lisa', 'john', 'sarah', 'tim', ]

outputList = []
for wavName, tgName in fnList:
    
    pitchName = os.path.splitext(wavName)[0] + '.txt'

    tg = tgio.openTextgrid(join(rootPath, tgName))
    
    # 1 - get pitch values
    pitchList = pitch_and_intensity.extractPitch(join(rootPath, wavName),
                                                 join(pitchPath, pitchName),
                                                 praatEXE, 50, 350,
                                                 forceRegenerate=True)
    
    # 2 - find the intervals where a name was spoken
    nameIntervals = []
    targetTier = tg.tierDict['word']
    for name in nameList:
        findMatches = targetTier.find(name)
        for i in findMatches:
            nameIntervals.append(targetTier.entryList[i])
    
    # 3 - isolate the relevant pitch values
    matchedIntervals = []
    intervalDataList = []
    for entry in nameIntervals:
        start, stop, label = entry
        
        croppedTier = targetTier.crop(start, stop, "truncated", False)
        intervalDataList = croppedTier.getValuesInIntervals(pitchList)
        matchedIntervals.extend(intervalDataList)
    
    # 4 - find the maximum value
    for interval, subDataList in intervalDataList:
        pitchValueList = [pitchV for timeV, pitchV in subDataList]
        maxPitch = max(pitchValueList)
        
        outputList.append((wavName, interval, maxPitch))

# Output results
for name, interval, value in outputList:
    print((name, interval, value))
