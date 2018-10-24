import os, sys, re
import csv, math

from pprint import pprint
from tqdm import tqdm
from collections import Counter

def clean_phones(p):
	p = re.sub(r'\\.*$', '', p)
	p = re.sub(r'ts', 'ծ', p)
	p = re.sub(r'dZ', 'ջ', p)
	p = re.sub(r'[\[\],:*\.]', '', p)
	return p


def read_celex(lang, phone_index, min_freq = 1):
	morph_file = '../celex2/{0}/{1}ml/{1}ml.cd'.format(lang, lang[0])
	phono_file = '../celex2/{0}/{1}pl/{1}pl.cd'.format(lang, lang[0])
	
	non_az = re.compile(r'[-\. ]')
	freqs = Counter()
	monos = set()
	with open(morph_file) as rf:
		reader = csv.reader(rf, delimiter = '\\')
		for line in reader:
			# M or Z for monomorphemes
			# monomorpheme or zero-derivation
			word = line[1]
			if non_az.search(word):	
				continue
			freqs[word] += int(line[2])
			if line[3] in ('M', 'Z'): 
				monos.add(word) 

	phonos = {}
	with open(phono_file) as rf:
		reader = csv.reader(rf, delimiter = '\\')
		for line in reader:
			word = line[1]
			if non_az.search(word):	continue
			p = clean_phones(line[phone_index])
			if len(p) == 0:	continue
			phonos[word] = (p, freqs[word])

	for word, freq in freqs.items():
		if freq < min_freq:
			monos.discard(word)
			if word in phonos:
				del phonos[word]
	return phonos, monos

def read_newdict(monos, f = 'newdic.txt', min_freq = 1):
	phonos = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for line in reader:
			p = line[0]
			word = line[3]
			freq = int(line[4])
			if freq >= min_freq:
				phonos[word] = (p, freq)
	return phonos


def read_coca_freqs(f = 'coca_freqs.txt'):
	freqs = {}
	with open(f) as rf:
	 	for line in rf:
	 		token, freq = line.rstrip().split()
	 		for word in token.split('-'):
	 			word = re.sub(r'[^a-zA-Z]', '', word)
	 			freqs[word] = freqs.get(word, 0) + int(freq)
	return freqs

sys.path.append("../")
from SegInfo import SegInfo


if __name__ == '__main__':
	uf = True
	_, e_monos = read_celex('english', 7)
	e_f = read_newdict(e_monos)

	# use the frequency from COCA instead
	cf = read_coca_freqs()
	d = e_f.copy()
	e_f = {}
	for w, t in d.items():
		if w in cf:
			e_f[w] = (t[0], cf[w])
	
	# for regulard monophones, with frequency
	e_si = SegInfo(e_f, use_freq = uf)
	re_si = SegInfo(e_f, use_freq = uf, reverse = True)

	e_si.save('eng.txt', e_monos)
	re_si.save('rev-eng.txt', e_monos)
	
	# for biphones
	e_si = SegInfo(e_f, use_freq = uf, nphone = 2)
	re_si = SegInfo(e_f, use_freq = uf, reverse = True, nphone = 2)
	e_si.save('eng.2.txt', e_monos)
	re_si.save('rev-eng.2.txt', e_monos)

	# for type data
	e_si = SegInfo(e_f, use_freq = False)
	re_si = SegInfo(e_f, use_freq = False, reverse = True)
	e_si.save('eng.nf.txt', e_monos)
	re_si.save('rev-eng.nf.txt', e_monos)

	# for exluding the frequency of a particular word when calculating seg info
	e_si = SegInfo(e_f, exclude_word_freq = True)
	re_si = SegInfo(e_f, exclude_word_freq = True, reverse = True)
	e_si.save('eng.excluded.txt', e_monos)
	re_si.save('rev-eng.excluded.txt', e_monos)

	# for variant lexicons where the frequencies have been shuffled among words of the same length
	if True:
		for i in tqdm(range(200)):
			random_si = SegInfo(e_f, use_freq = uf, exclude_word_freq = False, scramble_freqs = True)
			random_si.save('randos/eng/{0}.txt'.format(i), e_monos)
			random_si = SegInfo(e_f, use_freq = uf, exclude_word_freq = True, scramble_freqs = True)
			random_si.save('randos/eng_exclude/{0}.txt'.format(i), e_monos)