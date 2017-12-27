import json
import sys
import pydub
import numpy as np


import polly
import utils
import macroUtils

from praatUtils import *
from clean import cleanData 

SLOPE_CUTOFF = 40


# Step 1: read text file
source = sys.argv[1]
source_text = open(source).read()


# Step 2: use Polly to get audio file
mp3 = polly.getPollyAudio(source_text, isFile=False)
audio = pydub.AudioSegment.from_mp3("audio.mp3")
audio.export("./macro_files/audio.wav", format="wav")


# Step 3: extract pitch listing
output = runPraat("pitchlisting.praat")

pitch_listing = []
for line in output.split("\n"):
	info = line.split()
	# if len(info) == 1:
	# 	entry = [float(info[0])]
	if len(info) == 2:
		entry = [float(info[0]),float(info[1])]
		pitch_listing.append(entry)


def slope(p1, p2):
	(x1, y1) = p1
	(x2, y2) = p2
	if (x2-x1) == 0:
		return None
	return (y2-y1) / float(x2-x1)


# Step 4: calculate H/L peaks
p1 = (pitch_listing[0][0],pitch_listing[0][1])
trends = [{"avg": None, "points":[p1]}]
incr = True
slopes = []

for i in range(1, len(pitch_listing)):	
	entry = pitch_listing[i]

	p2 = (entry[0], entry[1])
	m = slope(p1, p2)

	if m:
		if (incr and m >= 0) or (not incr and m < 0):
			trends[-1]["points"].append(p2)
			slopes.append(m)
		else:
			if len(slopes) == 0:
				trends[-1]["avg"] = None
			else:
				avg_slope = np.mean(np.array(slopes))
				trends[-1]["avg"] = avg_slope
			
			slopes = []

			incr = not incr
			new = {"avg": None, "points":[p2]}
			trends.append(new)

	# calculate final thingy
	if i == len(pitch_listing) - 1:
		if len(slopes) == 0:
				trends[-1]["avg"] = None
		else:
			avg_slope = np.mean(np.array(slopes))
			trends[-1]["avg"] = avg_slope

	p1 = p2


def absorb(all_trends, curr):
	prev_trend = all_trends[-1]
 	prev_points = prev_trend["points"]
 	prev_avg = prev_trend["avg"]

 	curr_points = curr["points"]
 	curr_avg = curr["avg"]

 	concat = prev_points + curr_points
 	all_trends[-1]["points"] = concat

 	# recalculate slopes
 	slopes = []
	prev = None
	for point in concat:
		if prev is not None:
			m = slope(prev, point)
			slopes.append(m)
		prev = point

 	all_trends[-1]["avg"] = np.mean(np.array(slopes))


# Step 5: Clean trends
new_trends = [trends[0]]

i = 1
while i < len(trends):
 	trend = trends[i]
 	points = trend["points"]
 	avg = trend["avg"]

 	prev_trend = new_trends[-1]
 	prev_points = prev_trend["points"]
 	prev_avg = prev_trend["avg"]

	# if avg slope too small, absorb into previous
	# careful, bc if the jump is significant, you should keep!!
	# greedy will probably be most accurate anyway

	print avg, points


	# if prev too low! absorb him
	if (prev_points[-1][0] - prev_points[0][0] < .05) or (abs(prev_avg) < SLOPE_CUTOFF):
		absorb(new_trends, trend)
		print "absorbed previous"

	elif avg is None: 
		# decide if absorb into old, or into new
		curr = points[0][1]
		
		if i < len(trends)-1:
			new_trend = trends[i+1]
 			new_points = new_trend["points"]

 			new = new_points[0][1]
 			old = prev_points[-1][1]

			dist_to_new = abs(curr-new)
			dist_to_old = abs(curr-old)
			
			#print "comp", dist_to_old, dist_to_new

			if dist_to_new+15 < dist_to_old:
				new_trends.append(trend)
				absorb(new_trends, new_trend)
				print "absorbed new"

				trend = trends[i+1]
			 	points = trend["points"]
			 	avg = trend["avg"]
				print avg, points

				i += 2
				continue

		absorb(new_trends, trend)
		print "absorbed old"


	elif abs(avg) < SLOPE_CUTOFF:
		absorb(new_trends, trend)
		print "low slope"


	# if too short duration
	elif (points[-1][0] - points[0][0]) < .05:
		absorb(new_trends, trend)
		print "too short"


	# if two slopes same, check the jump
	elif (avg >= 0 and prev_avg >= 0) or (avg < 0 and prev_avg < 0):
		pitch_jump = abs(prev_points[-1][1] - points[0][1])
		if pitch_jump < 15:
			absorb(new_trends, trend)
			print "low jump"
		else:
			new_trends.append(trend)


	else:
		new_trends.append(trend)

	i += 1


print "\n\n"

def greater(x, y):
	return x > y

def less(x, y):
	return x < y

def peak(points, comp):
	curr = None
 	for p in points:
 		if curr is None:
 			curr = p
 		elif comp(p[1], curr[1]):
 			curr = p
 	return curr

def getPeak(t, points):
	if t == "max":
		f = greater 
		label = "H"
	else:
		f = less 
		label = "L"
	peakpoint = peak(points, f)
 	time = peakpoint[0]
 	return {"label":label,"time":time}


tones = []
for i in range(len(new_trends)):
	trend = new_trends[i]
 	points = trend["points"]
 	avg = trend["avg"]

 	print avg, points

 	# time will be at min/max 	
 	if i > 0:
 		prev_avg = new_trends[i-1]["avg"]
 		if avg >= 0:
 			if prev_avg >= 0:
 				tones.append(getPeak("min", points))
 			tones.append(getPeak("max", points))
 		else:
 			if prev_avg < 0:
 				tones.append(getPeak("max", points))
 			tones.append(getPeak("min", points))
 	else:
 		if avg >= 0:
 			tones.append(getPeak("max", points))
 		else:
 			tones.append(getPeak("min", points))


# for t in tones:
# 	print t

# Step 5: visualize as TextGrid
# cleaned = cleanData(source_text)
# timestamps = json.loads(utils.gentleAlign("audio.mp3", cleaned))
# aligned_words_phones = utils.alignPhones(timestamps)

macroUtils.toTextGrid(new_trends, tones)


# Step 6: calculate macrorhythmicity







	#