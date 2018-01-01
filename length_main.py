import os
import sys
import numpy as np 
import matplotlib.pyplot as plt

from length_by_sentence import lengthBySentence
from prettytable import PrettyTable

svmfile = None


# svmfile = open("macrosvm", 'w')
path = "texts/"

# svmfile = open("macrosvm.t", 'w')
# path = "classification_texts/"

# path = "texts/"

#genres = []
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

	for file in os.listdir(folder):
		if file ==".DS_Store":
			continue

		filename = file.split(".")[0]
		print filename

		data = lengthBySentence(os.path.join(folder, file), debug=False)
		
		avg = float(format(data[0], '.4f'))
		std = float(format(data[1], '.4f'))

		# write svm file
		if svmfile is not None:
			svmfile.write("%d 1:%f 2:%f\n" % (genres.index(genre)+1, within, across))

		x.append(data[0])
		y.append(data[1])
		c.append(colors[genre])
		labels.append(str(i))

		row = [str(i), filename, genre, avg, std]
		t.add_row(row)
		i += 1

if svmfile is not None:
	svmfile.close()

print t
plt.scatter(x, y, color=c)

for i,txt in enumerate(labels):
	plt.annotate(txt, (x[i],y[i]))

plt.show()







