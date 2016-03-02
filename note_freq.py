# written from a code golf challenge - see http://codegolf.stackexchange.com/questions/69729/what-is-the-frequency-of-this-note

# This script takes a musical note and calculates its frequency.

import re
import sys
import math
import getopt
from collections import OrderedDict

# constants
SHARP = '#'	# character representing a musical sharp
FLAT = 'b'	# character representing a musical flat
A4 = 440.0	# frequency of A4
CENTS = 1.0	# initial value of cent multiplier for tuner
HERTZ = 0.0	# initial value of hertz adder for tuner
OUT_OF_TUNE_THRESH = 0.1	# number of cents out of tune that is acceptable
NOTE_FLAG = ['n:', '-n']	# info for the note command line flag
FREQ_FLAG = ['f:', '-f']	# info for the frequency command line flag
CENTS_FLAG = ['c:', '-c']	# info for the cents command line flag
HERTZ_FLAG = ['h:', '-h']	# info for the hertz command line flag
NOTE_DICT = OrderedDict([('C', 1), ('D', 3), ('E', 5), ('F', 6),\
					 ('G', 8), ('A', 10), ('B', 12)])
USAGE = "Usage: python note_freq.py [OPTIONS]\n"+\
	"--- OPTIONS ---\n"+\
	"   -n NOTE         formatted as LETTER ACCIDENTAL OCTAVE (F#3, Ab7, c4, etc.)\n"+\
	"   -f FREQUENCY    floating point number, frequency to convert to note value\n"+\
	"   -c TUNING       optional integer, tuning in cents (-3 = down 3 cents, etc)\n"+\
	"   -h TUNING       optional integer, tuning in Hertz (5 = up 5 Hertz, etc)\n\n"

# utility functions

def numToFreq(note_number):
	"Converts a note number (A0 is note 1) to a frequency"
	frequency = (note_number - 49) / 12.0
	frequency = 2 ** frequency
	frequency = frequency * A4 * CENTS
	return frequency + HERTZ

def freqToNum(note_frequency):
	"Converts a frequency to a note number (A0 is note 1)"
	number = note_frequency - HERTZ
	number = number / (A4 * CENTS)
	number = number * (2 ** (49.0 / 12.0))
	number = math.log(number, 2)
	return 12 * number

def noteToNum(note):
	"Converts a textual note (ex. F#5) to a note number (A0 is note 1)"
	# parse out letter, accidental, and octave number
	regex = '([a-gA-G])([' + SHARP + FLAT + ']?)(-?\d+).*'
	match = re.search(regex, options[NOTE_FLAG[1]])
	letter = match.group(1).upper()
	accidental = match.group(2)
	octave = int(match.group(3))
	# look up the base note
	number = NOTE_DICT[letter]
	if accidental == SHARP:
		number += 1
	elif accidental == FLAT:
		number -= 1
	# factor in the octave
	number += 12 * (octave - 1) + 3
	return number

def numToNote(number):
	"Converts a note number (A0 is note 1) to a textual note (ex. F#5)"
	note_integer = int(math.floor(number + 0.5))
	note_index = (note_integer % 12) - 3
	if note_index < 1:
		note_index += 12
	if note_index in NOTE_DICT.values():
		for i in NOTE_DICT.items():
			if note_index == i[1]:
				note = i[0]
				break
	else:
		note = ''
		for i in NOTE_DICT.items():
			if note_index - 1 == i[1]:
				note += i[0] + SHARP + '/'
			if note_index + 1 == i[1]:
				note += i[0] + FLAT
				break
	octave_number = int(math.floor(((note_integer - 4) / 12.0) + 1))
	return note + str(octave_number)

# main instruction set

# retrieve and parse command line arguments
try:
	options = dict(getopt.getopt(sys.argv[1:],\
		NOTE_FLAG[0] + FREQ_FLAG[0] + CENTS_FLAG[0] + HERTZ_FLAG[0])[0])
	if NOTE_FLAG[1] not in options.keys() and FREQ_FLAG[1] not in options.keys():
		raise getopt.GetoptError("no note or frequency supplied")
except getopt.GetoptError as e:
	sys.stderr.write("\nParse error: " + str(e) + '\n' + USAGE)
	sys.exit()

# adjust tuning if needed
try:
	if CENTS_FLAG[1] in options.keys():
		CENTS = 2 ** (int(options[CENTS_FLAG[1]]) / 1200.0)
	if HERTZ_FLAG[1] in options.keys():
		HERTZ = int(options[HERTZ_FLAG[1]])
except ValueError:
	sys.stderr.write("\nParse error: invalid input - check the tuning\n" + USAGE)
	sys.exit()

# do the note -> frequency conversion if the flag is present
try:
	if NOTE_FLAG[1] in options.keys():
		number = noteToNum(options[NOTE_FLAG[1]])
		frequency = numToFreq(number)
		sys.stdout.write("\nThe frequency of " + options[NOTE_FLAG[1]] +\
					" is " + str(frequency) + " Hz\n")
except AttributeError:
	sys.stderr.write("\nParse error: invalid input - check the note\n" + USAGE)
	sys.exit()

# do the frequency -> note conversion if the flag is present
try:
	if FREQ_FLAG[1] in options.keys():
		input_freq = float(options[FREQ_FLAG[1]])
		number = freqToNum(input_freq)
		note = numToNote(number)
		true_freq = numToFreq(int(math.floor(number + 0.5)))
		hertz_off = abs(input_freq - true_freq)
		cents_off = abs(1200 * math.log(input_freq / true_freq, 2))
		sys.stdout.write('\n' + str(input_freq) + " Hz is a")
		# determine whether the note is sharp, flat, or in tune
		if cents_off > OUT_OF_TUNE_THRESH:
			if float(options[FREQ_FLAG[1]]) > true_freq:
				sys.stdout.write(" sharp ")
			else:
				sys.stdout.write(" flat ")
			sys.stdout.write(note + " by " + str(hertz_off) + " Hz or "+\
						str(cents_off) + " cents\n")
		else:
			sys.stdout.write("n in-tune " + note + '\n')
except ValueError:
	sys.stderr.write("\nParse error: invalid input - check the frequency\n" + USAGE)
	sys.exit()

# output a final newline to ensure clean output and exit
sys.stdout.write('\n')
sys.exit()
