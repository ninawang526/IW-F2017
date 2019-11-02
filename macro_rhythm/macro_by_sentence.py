import json
import sys
import pydub
import numpy as np
import math
import re 

import polly
import utils
import macroUtils

from praatUtils import *
from clean import cleanData 

import wave
import contextlib


def macroBySentence(source, debug=True):
	# Step 1: read text file
	source_text = open(source).read()
	
	sentences = re.split('\. |\! |\? |\n', source_text)

	pitch_listings = [[]]
	for sentence in sentences:
		# Step 2: use Polly to get audio file
		mp3 = polly.getPollyAudio(sentence, isFile=False)
		audio = pydub.AudioSegment.from_mp3("audio.mp3")
		audio.export("./macro_files/audio.wav", format="wav")

		# Step 3: extract pitch listings -- per **PHRASE** in a sentence
		with contextlib.closing(wave.open("./macro_files/audio.wav",'r')) as f:
		    frames = f.getnframes()
		    if debug:
		    	print "FRAMES", frames
		
		if frames > 75000:
			output = runPraat("pitchlisting.praat")
		else:
			output = runPraat("pitchlisting2.praat")
		
		lines = output.split("\n")
		start = float(lines[0].split()[0])
		end = float(lines[-2].split()[0])
		#print "duration:", end-start

		for i in range(len(lines)):
			line = lines[i]
			info = line.split()

			if len(info) == 2:
				time = float(info[0])
				val = float(info[1])
				pitch_listings[-1].append([time,val])
				
		pitch_listings.append([])
			
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
			
			# intervals greater than 0.02 (the default)
			ts = []
			for i in range(1,len(pl)): 
				t1 = pl[i-1][0]
				t2 = pl[i][0]
				if (t2-t1) > .021:
					ts.append((t2-t1))
			timecutoff = np.mean(np.array(ts)) / 3.
			trends = macroUtils.cleanTrends(t, cutoff, timecutoff)

			# Step 6: Generate the dict of tones
			tones = macroUtils.generateTones(trends)
			final_trends = final_trends + trends
			final_tones.update(tones)
			contours.append({"trends":trends,"tones":tones})

		# Step 7: visualize as TextGrid
		if debug:
			cleaned = cleanData(source_text)
			timestamps = json.loads(utils.gentleAlign("audio.mp3", cleaned))
			aligned_words_phones = utils.alignPhones(timestamps)
			macroUtils.toTonesGrid(aligned_words_phones, final_tones, final_trends)

	# Step 8: calculate macrorhythmicity
	frequency = []
	rf, pv = [], []
	pitchranges = []
	scores = []

	for c in contours:
		tones = c["tones"]
		trends = c["trends"]
		
		if debug:
			print "start:", trends[0]["points"][0][0], " end:", trends[-1]["points"][-1][0],
			print "duration:", trends[-1]["points"][-1][0]-trends[0]["points"][0][0]

		# metric 1 - low/high alternation
		freq = macroUtils.metric1(c)
		freq_score = 1
		if freq > 0:
			freq_score = (2/(float(freq)))

		# metric 2 - similarity of subtonal units (rise-fallss)
		r, f, SDr, SDf = macroUtils.metric2(c)
		std_sim = SDr + SDf
		if SDr > 0 and SDf > 0:
			std_sim = std_sim / 2.

		# metric 3 - regular interval of subtonal units
		p, v, SDp, SDv = macroUtils.metric3(c)
		std_reg = SDp + SDv
		if SDp > 0 and SDv > 0:
			std_reg = std_reg / 2.
		
		# metric 4
		prange = macroUtils.metric4(c)
		prange_score = 1
		if prange > 0:
			prange_score = (1/float(prange))

		frequency.append(freq)
		pitchranges.append(prange)
		rf.append(std_sim)
		pv.append(std_reg)

		score = std_reg + std_sim + freq_score #+ prange_score
		
		# sanity check!
		if score > 10:
			print "really high score!", score
		elif score == 0:
			print "zero score"
		else:
			scores.append(score)
		
		if debug:
			print "freq =", freq, freq_score
			print "SDrise =", SDr
			print "SDfall =", SDf
			print "SDpeak =", SDp
			print "SDvalley =", SDv
			print "SDpitch =", SDpt

			print "MacR_Var =", score

			print "\n"


	# MEASUREMENTS
	minv = min(scores)
	within_sentence = np.mean(np.array(scores))
	
	topscores = scores[:21]
	stdstd = np.std(topscores) / np.mean(topscores)

	freqval = (np.std(frequency) / np.mean(frequency))
	rsval = (np.std(rs) / np.mean(rs))
	fsval = abs(np.std(fs) / np.mean(fs))
	psval = (np.std(ps) / np.mean(ps))
	vsval = (np.std(vs) / np.mean(vs))
	ptval = (np.std(pitchranges)) / np.mean(pitchranges)

	across_sentence = freqval + (rsval + fsval)/2 + (psval + vsval)/2 + ptval
	
	if debug:
		print "\n"
		print "std frequency:", freqval
		print "std rises:", rsval
		print "std falls:", fsval
		print "std peaks:", psval
		print "std valleys:", vsval
		print "std pitch change:", ptval

		print "within_sentence:", within_sentence
		print "stdstd:", stdstd
		print "across_sentence:", across_sentence
		print "\n"

	return (frequency, rf, pv, pitchranges)



if __name__ == '__main__':
	macroBySentence(sys.argv[1])



	#



