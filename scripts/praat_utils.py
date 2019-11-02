#-------------------------------------------------------------------------------------------------#
#
# Tools for processing through Praat
#
#-------------------------------------------------------------------------------------------------#
import os
import subprocess
import numpy as np

# Turn list of words & phones into textgrid
def toTextGrid(stressed, save_path):
	complete_name = os.path.join(save_path, "audio.TextGrid")
	f = open(complete_name, "w")

	header = "File type = \"ooTextFile\"" + "\n" + "Object class = \"TextGrid\"\n"
	f.write(header)

	start = stressed[0]["phones"][0]["start"]
	i = len(stressed)
	while i >= 0:
		try:
			end = stressed[i]["phones"][-1]["end"]
			break
		except:
			i -= 1

	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")
	f.write("tiers? <exists>" + "\n")
	f.write("size = 2" + "\n")
	f.write("item []:" + "\n")
	f.write("item [1]:" + "\n")
	f.write("class = \"IntervalTier\"" + "\n")
	f.write("name = \"phones\"" + "\n")
	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")

	c = 0
	for wd in stressed:
		for ph in wd["phones"]:
			c += 1

	f.write("intervals: size = " + str(c) + "\n")

	i = 1
	for wd in stressed:
		for ph in wd["phones"]:
			f.write("intervals [" + str(i) + "]\n")			
			start = ph["start"]
			end = ph["end"]
			
			f.write("xmin = " + str(start) + "\n")
			f.write("xmax = " + str(end) + "\n")
			
			if ph["syllable"] and ph["stress"]:
				f.write("text = \"" + ph["str"].upper() + "*\"\n")
			elif ph["syllable"]:
				f.write("text = \"" + ph["str"].upper() + "\"\n")
			else:
				f.write("text = \"" + ph["str"] + "\"\n")

			i += 1

	f.write("item [2]:" + "\n")
	f.write("class = \"IntervalTier\"" + "\n")
	f.write("name = \"words\"" + "\n")
	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")

	f.write("intervals: size = " + str(len(stressed)) + "\n")

	i = 1
	for wd in stressed:
		try:
			start = wd["phones"][0]["start"]
			end = wd["phones"][-1]["end"]
		except:
			start = 0
			end = 0

		f.write("intervals [" + str(i) + "]\n")
			
		f.write("xmin = " + str(start) + "\n")
		f.write("xmax = " + str(end) + "\n")
			
		f.write("text = \"" + wd["word"] + "\"\n")

		i += 1

	f.close()


def calculateScores(dataset, maxval):
	# normalization
	pitches = []
	ints = []
	durs = []
	for key, val in dataset.iteritems():
		duration, pitch, intensity = val[1], val[2], val[3]

		pitches.append(pitch)
		ints.append(intensity)
		durs.append(duration)
		
	data = [durs, pitches, ints]
	norms = []
	for metric in data:

		min_val = min(metric)
		max_val = max(metric)
		range_val = float(max_val - min_val)

		norm = []
		for value in metric:
			if range_val != 0:
				norm.append((value - min_val)/range_val)
			else:
				norm.append(1)

		#print norm
		norms.append(norm)

	i = 0
	scores = []
	normalized_dataset = {}
	for key, val in dataset.iteritems():
		string = val[0]
		duration, pitch, intensity = norms[0][i], norms[1][i], norms[2][i]
		
		score = .75*(duration) + .15*(pitch) + .10*(intensity)
		
		f_pitch = float(format(pitch, '.4f'))
		f_intensity = float(format(intensity, '.4f'))
		f_duration = float(format(duration, '.4f'))
		f_score = float(format(score, '.4f'))

		scores.append(f_score)

		normalized_dataset[key] = [string, f_duration, f_pitch, f_intensity, f_score]
		i+=1

	med = np.median(np.array(scores))
	mn = np.mean(np.array(scores))
	std = np.std(np.array(scores))
	# print "median score:", med
	# print "mean score:", mn
	return min(med, mn), std, normalized_dataset


def runPraat(script):
	output = subprocess.check_output(['/Applications/Praat.app/Contents/MacOS/Praat','--run', script])
	return output


# determine metric scores of each phone
def fixByScore(aligned):
	metric_data = runPraat("stressAnalysis.praat")
	data_lines = metric_data.split("\n")

	formatted = {}
	ind = 0
	for line in data_lines:
		data = line.split()

		if len(data) < 6:
			continue

		label, duration, meanf0, meandb = data[0], data[1], data[2], data[4]

		if label.isupper():
			if duration != "--undefined--" and meanf0 != "--undefined--" and meandb != "--undefined--":
				formatted[ind] = [label, float(duration), float(meanf0), float(meandb)]

		ind += 1

	med_score, std, scores = calculateScores(formatted, ind)

	ind = 0
	corrected = 0
	for entry in aligned:
		phones = entry["phones"]

		for ph in phones:
			if ph["stress"]:
				try:
					low_score = scores[ind][4] < (med_score-(.15*std))
				except:
					ind += 1
					continue

				if low_score:
					corrected += 1
					ph["stress"] = False
			ind += 1 


