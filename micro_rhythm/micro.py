import json
import sys
import pydub
import numpy as np
import re

import polly

from clean import cleanData 
from utils import *
from mylist import *

# Step 1: read text file
source = sys.argv[1]
source_text = open(source).read()


# Step 2: use Polly to get audio file
mp3 = polly.getPollyAudio(source_text, isFile=False)
audio = pydub.AudioSegment.from_mp3("audio.mp3")
audio.export("./examples/audio.wav", format="wav")
audio.export("audio.wav", format="wav")


# Step 3: clean data & use gentle to align text 
cleaned = cleanData(source_text)
print cleaned

j = gentleAlign("audio.mp3", cleaned)
j_file = open("res.json", "w")
j_file.write(j)

timestamps = json.loads(j)


# Step 4: parse gentle output -> words & phones (distinct speech sound/gesture)
aligned_words_phones = alignPhones(timestamps)

# Step 5: determine stressed phones
stresses = fillStress(cleaned, aligned_words_phones)	

# create TextGrid
toTextGrid(stresses)

# Step 6: calculate time between stresses
durations = []

for i in range(len(stresses)):
	for ph in stresses[i]["phones"]:
		if ph["stress"]:  
			durations.append(0)
		else:
			if len(durations) == 0:
				durations.append(0)
			durations[-1] += (ph["end"] - ph["start"])


np_durations = np.array(durations)
std = np.std(np_durations)
mean = np.mean(np_durations)
print "std:", std
print "mean:", mean

