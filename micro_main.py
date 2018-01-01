import os
import numpy as np 
import matplotlib.pyplot as plt

from micro_by_sentence import microBySentence
from prettytable import PrettyTable



# # find macro
genres = ["prose","poetry","academic"]
colors = {"academic":"blue","poetry":"green","prose":"red"}
x = []
y = []
c = []
labels = []

path = "texts/"

t = PrettyTable(['Index','Name', 'Genre', 'Within', 'Across'])

i = 0
for genre in os.listdir(path):
	if genre not in genres:
		continue

	folder = os.path.join(path, genre)

	for file in os.listdir(folder):
		if file ==".DS_Store":
			continue

		filename = file.split(".")[0]
		print filename

		try:
			data = microBySentence(os.path.join(folder, file), debug=False)
		except:
			print filename + " failed."
			continue

		x.append(data[1])
		y.append(data[2])
		c.append(colors[genre])
		labels.append(str(i))

		row = [str(i), filename, genre, float(format(data[1], '.4f')), float(format(data[2], '.4f'))]
		t.add_row(row)

		i += 1
		
	print "NEXT"


print t
plt.scatter(x, y, color=c)

for i,txt in enumerate(labels):
	plt.annotate(txt, (x[i],y[i]))

plt.show()







