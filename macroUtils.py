import os
import numpy as np

SLOPE_CUTOFF = 40


def slope(p1, p2):
	(x1, y1) = p1
	(x2, y2) = p2
	if (x2-x1) == 0:
		return None
	return (y2-y1) / float(x2-x1)


def slopeOfList(l):
	ms = []

	if len(l) <= 1:
		return None

	p1 = (l[0][0],l[0][1])

	for i in range(1,len(l)):
		entry = l[i]
		p2 = (entry[0], entry[1])
		m = slope(p1, p2)
		ms.append(m)

		p1 = p2

	if len(ms) == 0:
		return None
	return np.mean(np.array(ms))


# Step 4: calculate H/L peaks -- for one sentence pitch listing
def HLPeaks(pitch_listing):
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

				incr = not incr
				new = {"avg": None, "points":[p2]}
				trends.append(new)

				slopes = []


		# calculate final avg slope
		if i == len(pitch_listing) - 1:
			if len(slopes) == 0:
					trends[-1]["avg"] = None
			else:
				avg_slope = np.mean(np.array(slopes))
				trends[-1]["avg"] = avg_slope

		p1 = p2

	return trends


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

 	if len(slopes) > 0:
 		all_trends[-1]["avg"] = np.mean(np.array(slopes))


# Step 5: Clean trends
def cleanTrends(trends, cutoff, timecutoff, debug=False):
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

		if debug:
			print avg, points

		# if prev too low! absorb him
		# made this "< timecutoff instead of <.04" -- who knows.
		if (prev_points[-1][0] - prev_points[0][0] < timecutoff+.001) or (prev_avg is not None and abs(prev_avg) < cutoff):
		#if (((prev_points[-1][0] - prev_points[0][0]) * abs(prev_avg)) < (.06*cutoff)):
			absorb(new_trends, trend)
			
			if debug:
				print "absorbed previous", (prev_points[-1][0] - prev_points[0][0]), (prev_avg), cutoff

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

				newtime = new_points[0][0]
	 			oldtime = prev_points[-1][0]
	 			time_diff = newtime - oldtime
				
				if debug:
					print "comp", dist_to_old, dist_to_new, time_diff

				if (dist_to_new+10 < dist_to_old) or ((dist_to_new+5 < dist_to_old) and time_diff > .06):
					new_trends.append(trend)
				
					if debug:
						print "left alone"

					i += 1
					continue

			absorb(new_trends, trend)
			if debug:
				print "absorbed old"


		elif abs(avg) < cutoff:
			absorb(new_trends, trend)
			if debug:
				print "low slope"


		# if too short duration
		# .05 seems magic!
		elif (points[-1][0] - points[0][0]) < .05:
			absorb(new_trends, trend)
			if debug:
				print "too short"


		# if two slopes same, check the jump
		elif (avg >= 0 and prev_avg >= 0) or (avg < 0 and prev_avg < 0):
			pitch_jump = abs(prev_points[-1][1] - points[0][1])
			if pitch_jump < 15:
				absorb(new_trends, trend)
				if debug:
					print "low jump"
			else:
				new_trends.append(trend)

		else:
			new_trends.append(trend)

		i += 1

	return new_trends


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
		f = lambda x, y: x > y
		label = "H"
	else:
		f = lambda x, y: x < y
		label = "L"
	peakpoint = peak(points, f)
 	time = peakpoint[0]
 	return {"label":label, "point":peakpoint}





def generateTones(trends):
	tones = {}
	for i in range(len(trends)):
		trend = trends[i]
	 	points = trend["points"]
	 	avg = trend["avg"]

	 	# time will be at min/max 
	 	minv = getPeak("min", points)
	 	maxv = getPeak("max", points)

	 	mintime = minv["point"][0]
	 	maxtime = maxv["point"][0]

	 	# both = (((abs(minv["point"][0] - maxv["point"][0]) > .1 and 
	 	# 	abs(minv["point"][1] - maxv["point"][1]) > 15)) or 
			# abs(minv["point"][1] - maxv["point"][1]) > 25)
		both = ((abs(minv["point"][0] - maxv["point"][0]) > .1 and 
	 		abs(minv["point"][1] - maxv["point"][1]) > 15))

	 	if i > 0:
	 		prev_avg = trends[i-1]["avg"]
	 		if avg >= 0:
	 			if prev_avg >= 0:
	 				tones[mintime] = minv
	 			tones[maxtime] = maxv
	 		else:
	 			if prev_avg < 0:
	 				tones[maxtime] = maxv
	 			tones[mintime] = minv
	 	else:
	 		if avg >= 0:
	 			if both:
	 				tones[mintime] = minv
	 			tones[maxtime] = maxv
	 		else:
	 			if both:
	 				tones[maxtime] = maxv
	 			tones[mintime] = minv
	
	return tones


# normalize, out of 100
# def normalize(data):
# 	norms = []
# 	for metric in data:

# 		min_val = min(metric)
# 		max_val = max(metric)
# 		range_val = float(max_val - min_val)

# 		norm = []
# 		for value in metric:
# 			if range_val != 0:
# 				norm.append(((value - min_val)/range_val)*100)
# 			else:
# 				norm.append(100)

# 		#print norm
# 		norms.append(norm)
# 	return norms



# 1. a pitch contour with a sequence of level tones is less macro-rhythmic 
# than a contour with a sequence of rising or falling tones (HHHH < HLHLL)
#		weigh by time? -- i think this means  ** more **  h/l alternations
# 		div by time
def metric1(contour):
	# number of alternations div by time.
	tones = contour["tones"]
	trends = contour["trends"]
	tonekeys = sorted(tones.iterkeys())

	high = (tones[tonekeys[0]]["label"] == "H") 
	alts = 0
	for i in range(1, len(tones)):
		key = tonekeys[i]
		if (tones[key]["label"] == "H") != high:
			alts += 1
		high = (tones[key]["label"] == "H")

	start = trends[0]["points"][0][0]
	end = trends[-1]["points"][-1][0]

	if (end-start) == 0:
		return 0
	return (alts / float(end-start))

	#should be low for monotonic things.


# 2. a pitch contour with a sequence of similar sub-tonal units is more macro-rhythmic 
# than that with less similar ones. (you want your rise-fall hills to be similar to each other)
def metric2(contour):
	tones = contour["tones"]
	trends = contour["trends"]
	tonekeys = sorted(tones.iterkeys())

	rising = []
	falling = []

	start = tones[tonekeys[0]]["point"][0]
	for i in range(1,len(tonekeys)):
		key = tonekeys[i]
		end = tones[key]["point"][0]

		ps = []
		for tr in trends:
			points = tr["points"]
			for p in points:
				if (p[0] >= start and p[0] <= end):
					ps.append(p)

		if tones[key]["label"] == "H":
			rising.append(ps)
		else:
			falling.append(ps)
		start = end


	# sd of rising slope (l->h)
	ms = []
	for curve in rising:
		slope = slopeOfList(curve)
		if slope is not None:
			ms.append(slope)
	if len(ms) == 0:
		r = 0
		scaled_SDr = 0
	else:
		r = np.mean(np.array(ms))
		SDr = np.std(np.array(ms))
		scaled_SDr = abs(SDr / r)


	# sd of falling slope
	ms = []
	for curve in falling:
		slope = slopeOfList(curve)
		if slope is not None:
			ms.append(slope)
	if len(ms) == 0:
		f = 0
		scaled_SDf = 0
	else:
		f = np.mean(np.array(ms))
		SDf = np.std(np.array(ms))
		scaled_SDf = abs(SDf / f)

	return (r, f, scaled_SDr, scaled_SDf)


	# doesnt take into account ... how many ... 
	# can't just straight add. -- normalize
	# i dont think normalizing is good. artificially stretches std
	# oops i normalized wrong
	# need to also include freq!!!! bc low std error
	# dum dum, scale it.



# 3. a pitch contour with a regular interval of sub-tonal unit is more macro-rhythmic 
# than that of irregular intervals (regular timing or interval of sub-tonal unit matters) 
#	i think this means *regularity of* h/l alternations (time)
def metric3(contour):
	tones = contour["tones"]	
	tonekeys = sorted(tones.iterkeys())

	# sd of peak-to-peak interval
	times = []
	for k in tonekeys:
		t = tones[k]
		if t["label"] == "H":
			times.append(t["point"][0])
	intervals = []
	for i in range(1,len(times)):
		intervals.append(times[i]-times[i-1])
	
	if len(intervals) == 0:
		p = 0
		scaled_SDp = 0
	else:
		p = np.mean(np.array(intervals))
		SDp = np.std(np.array(intervals))
		scaled_SDp = abs(SDp / p)


	# sd of valley-to-valley interval 
	times = []
	for k in tonekeys:
		t = tones[k]
		if t["label"] == "L":
			times.append(t["point"][0])
	intervals = []
	for i in range(1,len(times)):
		intervals.append(times[i]-times[i-1])
	
	if len(intervals) == 0:
		v = 0
		scaled_SDv = 0
	else:
		v = np.mean(np.array(intervals))
		SDv = np.std(np.array(intervals))
		scaled_SDv = abs(SDv / v)

	return (p, v, scaled_SDp, scaled_SDv)



def metric4(contour):
	tones = contour["tones"]	
	tonekeys = sorted(tones.iterkeys())

	pitchranges = []

	# abs pitch change from point to point
	for i in range(1,len(tonekeys)):
		t1 = tones[tonekeys[i-1]]
		t2 = tones[tonekeys[i]]
		dt = t2["point"][0]-t1["point"][0]
		dx = t2["point"][1]-t1["point"][1]
		# sanity check:
		if abs(dx/dt) > 350:
			#print "slope too high:", abs(dx/dt)
			pass
		else:
			pitchranges.append(abs(dx/dt))
	
	if len(pitchranges) == 0:
		p = 0
	else:
		p = np.mean(np.array(pitchranges))

	# print "avg pitch change", p
	# print "pitch slopes", pitchranges
	return p






#Turn list of words into textgrid
def toTextGrid(stressed):
	save_path = "macro_files/"
	complete_name = os.path.join(save_path, "words.TextGrid")
	f = open(complete_name, "w")

	header = "File type = \"ooTextFile\"" + "\n" + "Object class = \"TextGrid\"\n"
	f.write(header)

	start = stressed[0]["phones"][0]["start"]
	i = len(stressed)
	while i >= 0:
		try:
			end = stressed[i]["phones"][-1]["end"]+.2
			break
		except:
			i -= 1

	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")
	f.write("tiers? <exists>" + "\n")
	f.write("size = 1" + "\n")
	f.write("item []:" + "\n")
	
	f.write("item [1]:" + "\n")
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



# Turn list of tones into textgrid
def toTonesGrid(stressed, tones, trends):
	save_path = "macro_files/"
	complete_name = os.path.join(save_path, "tones.TextGrid")
	f = open(complete_name, "w")

	header = "File type = \"ooTextFile\"" + "\n" + "Object class = \"TextGrid\"\n"
	f.write(header)

	try:
		start = stressed[0]["phones"][0]["start"]
	except:
		print stressed

	i = len(stressed)
	while i >= 0:
		try:
			end = stressed[i]["phones"][-1]["end"]+.2
			break
		except:
			i -= 1

	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")
	f.write("tiers? <exists>" + "\n")
	f.write("size = 3" + "\n")
	f.write("item []:" + "\n")
	
	sortkeys = sorted(tones.iterkeys())
	first = sortkeys[0]
	last = sortkeys[-1]

	start = tones[first]["point"][0]
	end = tones[last]["point"][0]


	f.write("item [1]:" + "\n")
	f.write("class = \"TextTier\"" + "\n")
	f.write("name = \"tones\"" + "\n")
	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")

	f.write("points: size = " + str(len(tones)) + "\n")

	i = 1
	for key in sortkeys:
		tone = tones[key]

		time = tone["point"][0]
		label = tone["label"]

		f.write("points [" + str(i) + "]\n")
		f.write("number = " + str(time) + "\n")
		f.write("mark = \"" + label + "\"\n")

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


	


	start = trends[0]["points"][0][0]
	end = trends[-1]["points"][-1][0]

	f.write("item [3]:" + "\n")
	f.write("class = \"IntervalTier\"" + "\n")
	f.write("name = \"slopes\"" + "\n")
	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")

	f.write("intervals: size = " + str(len(trends)) + "\n")

	i = 1
	for trend in trends:
		points = trend["points"]
		avg = trend["avg"]

		start = points[0][0]
		end = points[-1][0]

		f.write("intervals [" + str(i) + "]\n")
			
		f.write("xmin = " + str(start) + "\n")
		f.write("xmax = " + str(end) + "\n")
			
		f.write("text = \"" + str(avg) + "\"\n")

		i += 1

	f.close()




