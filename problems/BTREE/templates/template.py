def isTree(tree):
	# Your code goes here
	pass

N = int(raw_input())
for T in range(N):
	s = raw_input()
	tree = [int(c) for c in s.split(' ')]
	ans = isTree(tree)
	if ans:
		print 'YES'
	else:
		print 'NO'