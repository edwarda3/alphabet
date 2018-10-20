#!/usr/bin/env python

import re
import random
import sys

alphabet = 'abcdefghijklmnopqrstuvwxyz'

iters = 10000
divider = iters//100

# Read the data from a file, and only keep alpha characters.
def getFileStr(filepath):
	data = None
	print("Reading file... ", end = '')
	try:
		myfile = open(filepath,'r')
	except IOError:
		print("Failed to read file!")
		sys.exit()
	with myfile:
		data=myfile.read().lower()
	data= ''.join(c for c in data if c in alphabet)
	print('DONE')
	return data

# adding a certain value to the dictionary (takes care of incrementing)
def addToDict (dict,key,val):
	if(not key in dict):
		dict[key] = 0
	dict[key]+=val

# Takes any string and counts each pair moving forward.
# For instance, the string 'hello' would have pairs:
# 	(h,e), (e,l), (l,l), (l,o)
def classify(string):
	print("Classifying pairs... ", end = '')
	dict = {}
	for i in range(len(string)-1):
		addToDict(dict, (string[i], string[i+1]),1)
	print('DONE')
	return dict

# pretty print a dictionary
def printDict(dict):
	for key in dict.keys():
		print(str(key) + ': ' +str(dict[key]))

# Takes the dictionary and makes it into a 2-d array of tuples, such that:
#  [[(a,a,?)...(a,z,?)],
# 	[(b,a,?)...(b,z,?)].
# 	.
# 	.
# 	.
# 	[(z,a,?)...(z,z,?)]]
# Where a-z are their respective characters and ? represents their counter.
def sortByLeadLetter(dict):
	print("Sorting pairs... ", end = '')
	arr = []
	for c in  alphabet:
		letter = []
		for d in  alphabet:
			if((c,d) in dict):
				letter.append((c,d,dict[(c,d)]))
		letter.sort(key=lambda x: x[2],reverse=True)
		arr.append(letter)
	print('DONE')
	return arr

def printarr(arr):
	i = 0
	for a in arr:
		print(alphabet[i])
		for b in a:
			print('\t'+str(b))
		i+=1

# Tries a greedy arrangement, taking the most common pairing, then using the second letter to make the next pairing, etc.
# Start with:
# (e,a) #The highest from e's
#    v
#	(a,t) # highest from a's with unused letters
#      v
#	  (t,?)
#			......
def makeArrangement(arr):
	largestTuple = ('a','a',0)
	for a in arr:
		for b in a:
			if(b[2] > largestTuple[2]):
				largestTuple = b
	usedAlpha = ''
	usedAlpha += largestTuple[0]
	currentchar = largestTuple[1]
	while (not ''.join(sorted(usedAlpha)) == alphabet):
		usedAlpha += currentchar
		letter = arr[alphabet.index(currentchar)]
		found= False
		for pair in letter:
			if(not pair[1] in usedAlpha):
				currentchar = pair[1]
				found = True
				break		
		if(not found):
			for c in alphabet:
				if( not c in usedAlpha):
					currentchar = c
	return usedAlpha

# Makes some number of augmentations to the string supplied to it, returns an array of those augmented strings.
# Augments the string given to it by swapping two random indexes a random number of times.
def makeAugs(string,attempts):
	maxswaps = 10
	candidates = []
	for _ in range(attempts):
		cand = list(string)
		swaps = random.randint(1,maxswaps)
		for i in range(swaps):
			first = random.randint(0,len(cand)-1)
			second = random.randint(0,len(cand)-1)
			while(second == first):
				second = random.randint(0,len(cand)-1)
			cand[first], cand[second] = cand[second], cand[first] 
		candidates.append(''.join(cand))
	return candidates

# Gets the cost of the string passed to it.
# The cost is the total value (number of occurences) that each pair of letters appeared in the original training set.
# Higher is better
def getCost(string,dict):
	cost = 0
	for i in range(len(string)-1):
		if(not (string[i],string[i+1]) in dict):
			cost+=0
		else:
			cost += dict[(string[i],string[i+1])]
	#print(string + ",\tcost: "+str(cost))
	return cost

# Returns a more readable "score"
# This is pretty much arbitrary, but a value from 0-10 should be the range.
def getReadableCost(string,dict):
	cost = getCost(string,dict)
	totalpossiblepairs = 0
	for key in dict:
		totalpossiblepairs += dict[key]
	return round(50*cost/totalpossiblepairs,2)

# Selects the best string from the list of strings, using its cost function.
def getBest(strings,dict):
	bestidx = 0
	bestcost = 0
	for i in range(len(strings)):
		if(getCost(strings[i],dict) > bestcost):
			bestidx = i
			bestcost = getCost(strings[i],dict)
	return strings[bestidx]

def printLoadingBar(progress):
	percent = progress//divider
	string = '['
	i=0
	while(i<100):
		if(percent > i):
			string += '>'
		else:
			string += '-'
		i+=2
	string += ']('+str(percent)+'/100)'
	print(string, end='\r')

# Runs through the generations $iters number of times. Every time, we also add some random shuffled arrangement in case we get lucky and escape some local maxima.
def findBest(arr,dict):
	print('Finding Best Arrangement...')
	best = makeArrangement(arr)
	for i in range(iters):
		augmentations = makeAugs(best,50)
		augmentations.append(best)
		augmentations.append(''.join(random.sample(best,len(best))))
		augmentations.append(''.join(random.sample(best,len(best))))
		augmentations.append(''.join(random.sample(best,len(best))))
		augmentations.append(''.join(random.sample(best,len(best))))
		augmentations.append(''.join(random.sample(best,len(best))))
		augmentations.append(''.join(random.sample(best,len(best))))
		best = getBest(augmentations,dict)
		printLoadingBar(i)
	print('\nDONE')
	return best

if __name__ == "__main__":
	if(len(sys.argv) != 2):
		print("Need Input file! \n classify.py <example.txt>")
		sys.exit()
	file = sys.argv[1]
	filestr = getFileStr(file)
	data = classify(filestr)
	olist = sortByLeadLetter(data)
	#printarr(olist)

	best = findBest(olist,data)
	cost = getReadableCost(best,data)
	print('--')
	print('Found: '+best+"\tscore: " + str(cost))
