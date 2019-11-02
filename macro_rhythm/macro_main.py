import os
import sys
import numpy as np 
import matplotlib.pyplot as plt

from macro_by_sentence import macroBySentence
from prettytable import PrettyTable

svmfile = None

# preload svm model, if one exists
# svmfile = open("macrosvm.t", 'w')

path = "classification_texts/"
genres = ["poetry","academic","prose"]
colors = {"academic":"blue","poetry":"green","prose":"red"}
x = []
y = []
c = []
labels = []


t = PrettyTable(['Index','Name', 'Genre', 'Within', 'Across'])

i = 1 
for genre in os.listdir(path):
	if genre not in genres:
		continue

	folder = os.path.join(path, genre)

	g = 0
	for file in os.listdir(folder):
		if not file.endswith("txt"):
			continue

		filename = file.split(".")[0]
		print filename

		try:
			data = macroBySentence(os.path.join(folder, file), debug=False)
		except:
		 	print filename + " failed."
		 	continue

		# within = float(format(data[0], '.4f'))
		# across = float(format(data[1], '.4f'))
		frequency, rf, pv, pitchranges = data

		# write svm file
		if svmfile is not None:
			svmfile.write("%d 1:%f 2:%f\n" % (genres.index(genre)+1, within, across))

		avgrf = np.mean(rf)
		stdrf = np.std(rf)/avgrf

		x.append(avgrf)
		y.append(stdrf)
		c.append(colors[genre])
		labels.append(str(i))

		row = [str(i), filename, genre, avgrf, stdrf]
		t.add_row(row)
		i += 1
		g += 1

		if g >= 10:
			break

if svmfile is not None:
	svmfile.close()

print t
plt.scatter(x, y, color=c)

for i,txt in enumerate(labels):
	plt.annotate(txt, (x[i],y[i]))

plt.show()







