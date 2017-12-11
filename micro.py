import nltk
import gentleScript

arpabet = nltk.corpus.cmudict.dict()

file = "source.txt"
words = open(file).read().split(" ")

for word in words:
	print word, "\t\t", " ".join(arpabet[word.lower()][0])

