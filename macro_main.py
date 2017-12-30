import os
import numpy as np 
import matplotlib.pyplot as plt

from macro_by_sentence import macroBySentence
from prettytable import PrettyTable



# # find macro
genres = ["poetry","academic","prose"]
colors = {"academic":"blue","poetry":"green","prose":"red"}
x = []
y = []
c = []
labels = []

path = "texts/"

t = PrettyTable(['Name', 'Genre', 'Within', 'Stdstd' ,'Across'])


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
			data = macroBySentence(os.path.join(folder, file), debug=False)
		except:
		 	print filename + " failed."
		 	continue

		x.append(data[0])
		y.append(data[1])
		c.append(colors[genre])
		labels.append(filename)

		row = [filename, genre, float(format(data[0], '.4f')), float(format(data[1], '.4f')), float(format(data[2], '.4f'))]
		t.add_row(row)


print t
plt.scatter(x, y, color=c)

for i,txt in enumerate(labels):
	plt.annotate(txt, (x[i],y[i]))

plt.show()







