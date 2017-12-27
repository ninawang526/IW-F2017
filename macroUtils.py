import os


# Turn list of words & phones into textgrid
# def toTextGrid(stressed):
# 	save_path = "macro_files/"
# 	complete_name = os.path.join(save_path, "audio.TextGrid")
# 	f = open(complete_name, "w")

# 	header = "File type = \"ooTextFile\"" + "\n" + "Object class = \"TextGrid\"\n"
# 	f.write(header)

# 	start = stressed[0]["phones"][0]["start"]
# 	i = len(stressed)
# 	while i >= 0:
# 		try:
# 			end = stressed[i]["phones"][-1]["end"]+.2
# 			break
# 		except:
# 			i -= 1

# 	f.write("xmin = " + str(start) + "\n")
# 	f.write("xmax = " + str(end) + "\n")
# 	f.write("tiers? <exists>" + "\n")
# 	f.write("size = 1" + "\n")
# 	f.write("item []:" + "\n")
	
# 	f.write("item [1]:" + "\n")
# 	f.write("class = \"IntervalTier\"" + "\n")
# 	f.write("name = \"words\"" + "\n")
# 	f.write("xmin = " + str(start) + "\n")
# 	f.write("xmax = " + str(end) + "\n")

# 	f.write("intervals: size = " + str(len(stressed)) + "\n")

# 	i = 1
# 	for wd in stressed:
# 		try:
# 			start = wd["phones"][0]["start"]
# 			end = wd["phones"][-1]["end"]
# 		except:
# 			start = 0
# 			end = 0

# 		f.write("intervals [" + str(i) + "]\n")
			
# 		f.write("xmin = " + str(start) + "\n")
# 		f.write("xmax = " + str(end) + "\n")
			
# 		f.write("text = \"" + wd["word"] + "\"\n")

# 		i += 1

# 	f.close()



# Turn list of words & phones into textgrid
def toTextGrid(trends, tones):
	save_path = "macro_files/"
	complete_name = os.path.join(save_path, "audio.TextGrid")
	f = open(complete_name, "w")

	header = "File type = \"ooTextFile\"" + "\n" + "Object class = \"TextGrid\"\n"
	f.write(header)

	start = trends[0]["points"][0][0]
	end = trends[-1]["points"][-1][0]

	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")
	f.write("tiers? <exists>" + "\n")
	f.write("size = 2" + "\n")
	f.write("item []:" + "\n")
	
	f.write("item [1]:" + "\n")
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


	start = tones[0]["time"]
	end = tones[-1]["time"]

	f.write("item [2]:" + "\n")
	f.write("class = \"TextTier\"" + "\n")
	f.write("name = \"tones\"" + "\n")
	f.write("xmin = " + str(start) + "\n")
	f.write("xmax = " + str(end) + "\n")

	f.write("points: size = " + str(len(tones)) + "\n")

	i = 1
	for tone in tones:
		time = tone["time"]
		label = tone["label"]

		f.write("points [" + str(i) + "]\n")
		f.write("number = " + str(time) + "\n")
		f.write("mark = \"" + label + "\"\n")

		i += 1




	f.close()



