def positiveValues(a):
	# Your code goes here
	pass

def printArray(a):
	for n in a:
		print n

N = int(raw_input())
s = raw_input()
a = [int(c) for c in s.split(' ')]
ans = positiveValues(a)
printArray(ans)