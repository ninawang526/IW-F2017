import json
import sys
import pydub
import numpy as np


import polly
import utils
import macroUtils

from praatUtils import *
from clean import cleanData 



# Step 1: read text file
source = sys.argv[1]
source_text = open(source).read()


# Step 2: use Polly to get audio file
mp3 = polly.getPollyAudio(source_text, isFile=False)
audio = pydub.AudioSegment.from_mp3("audio.mp3")
audio.export("./macro_files/audio.wav", format="wav")


# Step 3: extract pitch listings -- per sentence
output = runPraat("pitchlisting.praat")
lines = output.split("\n")

pitch_listings = [[]]
curr_time = 0
for i in range(len(lines)):
	line = lines[i]
	info = line.split()

	if len(info) == 2:
		time = float(info[0])
		val = float(info[1])

		entry = [time,val]
		if time > curr_time + .25 and len(pitch_listings[-1]) > 0:
			pitch_listings.append([])
		pitch_listings[-1].append(entry)
		
		curr_time = time
		

final_trends = []
final_tones = {}
contours = []


for pl in pitch_listings:
	if len(pl) > 0:

		# Step 4: calculate H/L peaks 
		t = macroUtils.HLPeaks(pl)

		
		# Step 5: Clean trends
		s = []
		for tr in t:
			if tr["avg"] is not None:
				s.append(abs(tr["avg"])) 

		avgslope = np.mean(np.array(s))
		cutoff = (1/6.)*abs(avgslope)

		trends = macroUtils.cleanTrends(t, cutoff)


		# Step 6: Generate the dict of tones
		tones = macroUtils.generateTones(trends)

		final_trends = final_trends + trends
		final_tones.update(tones)

		contours.append({"trends":trends,"tones":tones})




# Step 7: visualize as TextGrid
#cleaned = cleanData(source_text)
timestamps = json.loads(utils.gentleAlign("audio.mp3", source_text))
aligned_words_phones = utils.alignPhones(timestamps)

macroUtils.toTextGrid(aligned_words_phones)
macroUtils.toTonesGrid(final_trends, final_tones)


# Step 6: calculate macrorhythmicity
# 1. a pitch contour with a sequence of level tones is less macro-rhythmic 
# than a contour with a sequence of rising or falling tones (HHHH < HLHLL)
#		weigh by time? -- i think this means  ** more **  h/l alternations
# 		div by time
def metric1(contour):
	# number of alternations div by time.
	tones = contour["tones"]
	trends = contour["trends"]

	high = (tones[0]["label"] == "H") 
	alts = 0
	for i in range(1, len(tones)):
		if (tones[i]["label"] == "H") != high:
			alts += 1
		high = (tones[i]["label"] == "H")

	start = trends[0]["points"][0][0]
	end = trends[-1]["points"][-1][0]

	return (alts / float(end-start))

	#should be low for monotonic things.


# 2. a pitch contour with a sequence of similar sub-tonal units is more macro-rhythmic 
# than that with less similar ones. (you want your rise-fall hills to be similar to each other)

# 3. a pitch contour with a regular interval of sub-tonal unit is more macro-rhythmic 
# than that of irregular intervals (regular timing or interval of sub-tonal unit matters) 
#	i think this means *regularity of* h/l alternations (time)


print ("\n\n")

peak = []
valley = []
rise = []
fall = []

for c in contours:
	tones = c["tones"]
	trends = c["trends"]
	
	for t in sorted(tones.iterkeys()):
		print tones[t]

	SDp, SDv, SDr, SDf = macroUtils.macVar(c)

	peak.append(SDp)
	valley.append(SDv)
	rise.append(SDr)
	fall.append(SDf)

	# metric 1 - low/high alternation

	# metric 2 - similarity of subtonal units (rise-falls)
	print "SDrise =", SDr
	print "SDfall =", SDf

	# metric 3 - regular interval of subtonal units
	print "SDpeak =", SDp
	print "SDvalley =", SDv

	print "MacR_Var =", SDp + SDv + SDr + SDf
	print "\n"

# data = [peak, valley, rise, fall]
# norms = macroUtils.normalize(data)

# for n in norms:
# 	print n








	#



