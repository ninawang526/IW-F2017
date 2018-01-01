########################################################
# NAME: Stress-analysis.praat                               
# Tae-Jin Yoon (UVic)
# March 3, 2008
########################################################


inputdir$ = "/Users/ninawang/iw/macro_files/"
tier_number = 1
outdir$ = "/Users/ninawang/iw/macro_files/"


# Read the list of files
;Read Strings from raw text file... 'inputdir$'/'listfile$'
Create Strings as file list... list 'inputdir$'/*.wav
end = Get number of strings

for filecounter from 1 to end

   select Strings list
   file$ = Get string... filecounter

   Read from file... 'inputdir$'/'file$'

   To Pitch... 0.01 75 500

	numberOfFrames = Get number of frames

	iframe = 1
	while iframe < numberOfFrames
    	time = Get time from frame: iframe
    	pitch = Get value in frame: iframe, "Hertz"
    	if pitch = undefined
      		appendInfoLine: fixed$ (time, 3)
   		else
       		appendInfoLine: fixed$ (time, 3), " ", fixed$ (pitch, 3)
    	endif
		iframe = iframe + 3
	endwhile

endfor

select all
Remove
