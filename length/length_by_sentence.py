import re
import numpy as np

def lengthBySentence(source, debug=True):
	# Step 1: read text file
	source_text = open(source).read()
	
	sentences = re.split('\. |\! |\? |\n', source_text)

	lengths = []
	for sentence in sentences:
		length = len(sentence)
		lengths.append(length)
			
	# MEASUREMENTS
	avg = np.mean(np.array(lengths))
	std = np.std(np.array(lengths)) / avg

	return ([avg, std])

