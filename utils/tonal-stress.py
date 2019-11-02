# Thou art more lovely and more temperate
import numpy as np 

# by sentence!

def scores(d):
	d = [
	["Thou_EH1", 		[171.10, 74.34, .15]],
	["Art_AA1", 		[171.10, 71.39, .01]],
	["More_AO1", 		[157.20, 73.89, .08]],
	["Lovely_AH1", 		[183.51, 73.29, .07]],
	["Lovely_IY0", 		[140.08, 72.34, .08]],
	["And_AE0", 		[136.50, 70.20, .04]],
	["More_AO1", 		[154.54, 73.29, .07]],
	["Temperate_EH1", 	[139.40, 73.44, .09]],
	["Temperate_AH0", 	[126.49, 71.02, .10]],
	]

	# normalization
	pitches = []
	ints = []
	durs = []
	for item in d:
		key = item[0]
		val = item[1]

		pitch, intensity, duration = val[0], val[1], val[2]

		pitches.append(pitch)
		ints.append(intensity)
		durs.append(duration)
		

	data = [pitches, ints, durs]
	norms = []
	for metric in data:

		min_val = min(metric)
		max_val = max(metric)
		range_val = max_val - min_val

		norm = []
		for value in metric:
			norm.append((value - min_val)/float(range_val))

		print norm
		norms.append(norm)


	# d = [
	# ["Thou_EH1", 		[171.10, 74.34, .15]],
	# ["Art_AA1", 		[171.10, 71.39, .01]],
	# ["More_AO1", 		[157.20, 73.89, .08]],
	# ["Lovely_AH1", 		[183.51, 73.29, .07]],
	# ["Lovely_IY0", 		[140.08, 72.34, .08]],
	# ["And_AE0", 		[136.50, 70.20, .04]],
	# ["More_AO1", 		[154.54, 73.29, .07]],
	# ["Temperate_EH1", 	[139.40, 73.44, .09]],
	# ["Temperate_AH0", 	[126.49, 71.02, .10]],]

	i = 0
	norm_d = []
	for item in d:
		name = item[0]
		vals = []
		entry = [name, [norms[0][i], norms[1][i], norms[2][i]]]
		norm_d.append(entry)
		i+=1

	# for item in norm_d:
	# 	print item

	# ['Thou_EH1', 		[0.782357, 1.0, 	 1.0]]
	# ['Art_AA1', 		[0.782357, 0.287439, 0.0]]
	# ['More_AO1', 		[0.538582, 0.891304, 0.50000]]
	# ['Lovely_AH1', 	[1.0, 	   0.746376, 0.42857]]
	# ['Lovely_IY0', 	[0.238337, 0.516908, 0.50000]]
	# ['And_AE0', 		[0.175552, 0.0, 	 0.21428]]
	# ['More_AO1', 		[0.491932, 0.746376, 0.42857]]
	# ['Temperate_EH1', [0.226411, 0.782608, 0.57142]]
	# ['Temperate_AH0', [0.0, 	   0.198067, 0.642857]]

	s = []

	for item in norm_d:
		key = item[0]
		val = item[1]

		pitch, intensity, duration = val[0], val[1], val[2]
		
		score = .15*(pitch)+ .10*(intensity) + .75*(duration)# + .10*(intensity)

		s.append(score)

		print key, "\t", score

	print "\n"
	print "mean:", np.mean(np.array(s))
	print "std:", np.std(np.array(s))

scores("hi")
