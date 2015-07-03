#!/usr/bin/python

import sys, getopt
import codecs

def main(argv):
	inputfile = ''
	outputfile = ''

	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print_help(2)

	for opt, arg in opts:
		if opt == '-h':
			print_help(0)
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
        		outputfile = arg

	with codecs.open(inputfile, 'r', 'utf-8') as orig:
		with codecs.open(outputfile, 'w', 'windows-1252') as copy:
			for line in orig:
				copy.write(line)
		

def print_help(code):
	print 'unidecodejson.py -i <inputfile> -o <outputfile>'
	sys.exit(code)

if __name__ == "__main__":
	main(sys.argv[1:])
