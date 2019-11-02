#-------------------------------------------------------------------------------------------------#
#
# Tools for data analysis
#
#-------------------------------------------------------------------------------------------------#

import requests
import json
import nltk
import os



# HTTP POST request to Gentle to align transcript with aduio
def gentleAlign(audio, transcript):
	data = {"audio":open(audio, 'rb'), "transcript":transcript}
	payload = {"async":"false"}
	url = "http://localhost:8765/transcriptions"

	r = requests.post(url, files=data, params=payload)

	if r.status_code != 200:
		raise Exception("Could not align")

	return r.text


def alignPhones(timestamps):
	aligned_words = open("words.txt", "w")
	aligned_words_phones = []

	words = timestamps["words"]

	for wd in words:
		aligned_words_phones.append({"word":wd["word"],"phones":[]})

		if wd["case"] == "success":
			aligned_words.write(wd["word"] + " " + str(wd["start"]) + " " + str(wd["end"]))

			ph_start = wd["start"]

			for ph in wd["phones"]:
				s = ph["phone"].split("_")[0]

				duration = ph["duration"]
				info = {"str":s,"start":ph_start,"end":ph_start+duration,"stress":False,"syllable":False}
				aligned_words_phones[-1]["phones"].append(info)
				ph_start = ph_start + duration	

	return aligned_words_phones



def fillStress(transcript, aligned):
	arpabet = nltk.corpus.cmudict.dict()

	mismatch = 0
	total = 0

	for word in aligned:
		string = word["word"]
		try:
			found_phones = arpabet[string.lower()][0]
		except:
			print "Unable to find \"" + string.lower() + "\""
			continue

		phones = word["phones"]

		i = 0 
		while i < len(found_phones) and i < len(phones):
			if not found_phones[i][-1].isalpha():
				syllable = True
				stress = (found_phones[i][-1] != "0")
				found_ph = found_phones[i][:-1]
			else:
				syllable = False
				stress = False
				found_ph = found_phones[i]

			ph = phones[i]["str"].split("_")[0]

			if ph == "oov":
				break
			if ph.lower() != found_ph.lower():
				mismatch += 1

			# assume stress
			phones[i]["stress"] = stress
			phones[i]["syllable"] = syllable

			i += 1

		total += i

	#print "mismatch:", mismatch, "/", total, "=", mismatch/float(total)

	return aligned
