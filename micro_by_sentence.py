import json
import sys
import pydub
import numpy as np
import re

import polly

from clean import cleanData 
from utils import *
from praatUtils import *


def microBySentence(source, debug=False):
	# Step 1: read text file
	source_text = open(source).read()

	stddevs = []
	means = []

	sentences = re.split('\. |\! |\? |\n', source_text)

	for sentence in sentences:

		if len(sentence) == 0: 
			continue

		# Step 2: use Polly to get audio file
		mp3 = polly.getPollyAudio(sentence, isFile=False)
		audio = pydub.AudioSegment.from_mp3("audio.mp3")
		audio.export("audio.wav", format="wav")
		audio.export("examples/audio.wav", format="wav")


		# Step 3: clean data & use gentle to align text 
		cleaned = cleanData(sentence)

		if debug:
			print cleaned

		j = gentleAlign("audio.mp3", cleaned)
		timestamps = json.loads(j)


		# Step 4: parse gentle output -> words & phones 
		aligned_words_phones = alignPhones(timestamps)


		# Step 5: determine stressed phones
		stresses = fillStress(cleaned, aligned_words_phones)


		# Step 6: fix false-positives
		toTextGrid(stresses)
		fixByScore(stresses)


		# Step 7: calculate time between stresses
		durations = []

		for i in range(len(stresses)):
			for ph in stresses[i]["phones"]:
				if ph["stress"]:  
					durations.append(0)
				else:
					if len(durations) == 0:
						durations.append(0)
					durations[-1] += (ph["end"] - ph["start"])

		if durations[len(durations)-1]==0:
			durations = durations[:-1]

		np_durations = np.array(durations)
		std = np.std(np_durations)
		mean = np.mean(np_durations)
		stddevs.append(std)
		means.append(mean)
		

		if debug:
			print durations
			print "std:", std
			print "scaled:", std/mean
			print "\n"


	within_sentence = np.mean(np.array(stddevs)) / np.mean(np.array(means))
	across_sentence = np.std(np.array(means))/np.mean(np.array(means))

	if debug:
		print "final stddevs"
		print stddevs
		print "final stddev:", np.mean(np.array(stddevs))
		print "scaled stddev:", within_sentence

		print "\n"

		#on a sentence-to-sentence level
		print "stddev of means:", np.std(np.array(means))
		print "scaled stddev:", across_sentence

	return [source, within_sentence, across_sentence]




if __name__ == '__main__':
	folder = os.path.join("texts", "prose")
	f = os.path.join(folder, "sula.txt")

	data = microBySentence(f,debug=True)
	print data



#