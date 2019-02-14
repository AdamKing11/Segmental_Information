import os, re, sys
import csv, math

from pprint import pprint
from tqdm import tqdm
from collections import Counter, defaultdict

def neg_log2(p):
	return -math.log(p) / math.log(2)

def match_upper(m):
	return m.group(1).upper()

def read_j(f = 'jpn/lex/ja_lex.v02', min_count = 5):

	j = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for l in reader:
			word = l[2]
			#word = re.sub('tts', 'Ծ', word)
			word = re.sub('ts', 'ծ', word)
			#word = re.sub('ssh','%', word)
			word = re.sub('sh','$', word)
			#word = re.sub('cch','C', word)
			word = re.sub('ch','c', word)
			#word = re.sub(r'([szptkbdgmnaeiou])\1', match_upper, word)
			word = re.sub(r'ai', '@', word)
			word = re.sub(r'ou', '0', word)
			word = re.sub(r'ei', '3', word)
			count = int(l[5])
			if count >= min_count:	
				j[word] = (word, count)
	return j



def read_a(f = 'ara/lex/ar_lex.v07', min_count = 5):
	a = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for l in reader:
			word = l[0]
			#word = re.sub(r'([lwysz])\1', match_upper, word)
			count = sum([int(c) for c in l[5:7]])
			if count >= min_count:
				a[word] = (word, count)
	return a

sys.path.append("../")
from SegInfo import SegInfo


if __name__ == '__main__':
	j = read_j()
	a = read_a()

	uf = True
	print(1)
	ara = SegInfo(a, use_freq = uf)
	ara.save('ara.txt')
	ara.save_lexicon('../lexicons/' + 'ara.lex.txt')
	rev_ara = SegInfo(a, use_freq = uf, reverse = True)
	rev_ara.save('rev_ara.txt')

	print(2)
	jpn = SegInfo(j, use_freq = uf)
	jpn.save('jpn.txt')
	jpn.save_lexicon('../lexicons/' + 'jpn.lex.txt')
	rev_jpn = SegInfo(j, use_freq = uf, reverse = True)
	rev_jpn.save('rev_jpn.txt')		
		
	if False:
		for i in tqdm(range(100)):
			random_si = SegInfo(a, use_freq = uf, exclude_word_freq = True, scramble_freqs = True)
			random_si.save('randos/ara/{0}.txt'.format(i))

			random_si = SegInfo(j, use_freq = uf, exclude_word_freq = True, scramble_freqs = True)
			random_si.save('randos/jpn/{0}.txt'.format(i))