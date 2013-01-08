#!/usr/bin/python
import argparse

DEFAULT_PRECISION = 3

def compare(f1, f2, trim=True, floatCompare=False, precision=DEFAULT_PRECISION):
	success = True
	while True:
		line1 = f1.readline().strip() if trim else f1.readline()
		line2 = f2.readline().strip() if trim else f2.readline()

		if len(line1) + len(line2) == 0:
			break

		if floatCompare:
			line1 = float(line1)
			line1 = round(line1, precision)

			line2 = float(line2)
			line2 = round(line2, precision)
		
		if line1 != line2:
			success = False
			break

	return success

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file1", help="Name of the first file to compare")
	parser.add_argument("file2", help="Name of the second file to compare")
	parser.add_argument("-nt", "--noTrim", help="Don't trim each line of \
											whitespace before comparing them",
						action="store_true")
	parser.add_argument("-f", "--float", help="Parse each line as a float value",
						action="store_true")
	parser.add_argument("-p", "--precision", help="Precision to use when comparing \
						float values. Defaults to %d." % DEFAULT_PRECISION,
						type=int, default=DEFAULT_PRECISION)
	args = parser.parse_args()
	args.trim = not args.noTrim

	file1 = open(args.file1, 'r')
	file2 = open(args.file2, 'r')

	print compare(file1, file2, args.trim, args.float, args.precision)

	file1.close()
	file2.close()