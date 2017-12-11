# -*- coding: utf-8 -*-


import re
import inflect
import unicodedata


def cleanData (f):
	p = inflect.engine()
	numeric = re.compile('[0-9]+')
	words = f.split(" ")

	new_words = []
	for word in words:
		w = word
		if numeric.match(word):
			w = p.number_to_words(word)
		elif word == "dont":
			w = "don't"

		new_words.append(w)


	new_f = " ".join(new_words)

	removelist = "'"

	final_f = re.sub(r'[^\w+'+removelist+']', " ", new_f.replace("’","\'"))
	
	return final_f
