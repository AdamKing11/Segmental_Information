import os, re, sys
import csv, math
from pprint import pprint
from collections import Counter, defaultdict

def neg_log2(p):
	return -math.log(p) / math.log(2)

def match_upper(m):
	return m.group(1).upper()

_f = 'jpn/lex/ja_lex.v02'
j = {}
with open(_f) as rf:
	reader = csv.reader(rf, delimiter = '\t')
	for l in reader:
		word = l[2]
		word = re.sub('sh','$', word)
		word = re.sub(r'([aeiou])\1', match_upper, word)
		count = int(l[5])
		if count >= 10:	
			j[word] = (word, count)




_f = 'ara/lex/ar_lex.v07'
a = {}
with open(_f) as rf:
	reader = csv.reader(rf, delimiter = '\t')
	for l in reader:
		word = l[0]
		count = sum([int(c) for c in l[5:7]])
		if count >= 10:
			a[word] = (word, count)

"""
class SegInfo(object):

	def __init__(self, d, use_freq = True):
		seqs = Counter()
		for word, count in d.items():
			if not use_freq:	count = 1
			for position in range(len(word)+1):
				seqs[word[:position]] += count
				
		lex_sum = sum(d.values())		
		
		self.si = {}
		for word, count in d.items():
			phone_probs = []
			p = seqs[word[:1]]/lex_sum
			phone_probs.append(neg_log2(p))
			for position in range(1, len(word)):
				p = seqs[word[:position+1]]/seqs[word[:position]]
				phone_probs.append(neg_log2(p))
			self.si[word] = (count, phone_probs)

	def save(self, f):
		with open(f, 'w') as wf:
			wf.write('{0}\n'.format('\t'.join(['WORD', 'FREQUENCY', 'POSITION', 'INFO'])))
			for w, t in sorted(self.si.items(), key = lambda x : x[1][0], reverse = True):
				count = str(t[0])
				for i, p in enumerate(t[1]):
					wf.write('{0}\n'.format('\t'.join([w, count, str(i+1), str(p)]))) 
"""

sys.path.append("../")
from SegInfo import SegInfo

uf = True
print(1)
ara = SegInfo(a, use_freq = uf)
print(2)
jpn = SegInfo(j, use_freq = uf)

print(3)
scr_ara = SegInfo(a, use_freq = uf, scramble = True)
print(4)
scr_jpn = SegInfo(j, use_freq = uf, scramble = True)
print(5)
rev_ara = SegInfo(a, use_freq = uf, reverse = True)
print(6)
rev_jpn = SegInfo(j, use_freq = uf, reverse = True)

ara.save('ara.txt')
jpn.save('jpn.txt')
scr_ara.save('scr_ara.txt')
scr_jpn.save('scr_jpn.txt')
rev_ara.save('rev_ara.txt')
rev_jpn.save('rev_jpn.txt')