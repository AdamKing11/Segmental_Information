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


def read_celex(lang, phone_index, min_freq = 5):
	morph_file = '{0}/{1}ml/{1}ml.cd'.format(lang, lang[0])
	phono_file = '{0}/{1}pl/{1}pl.cd'.format(lang, lang[0])
	
	non_az = re.compile(r"[-\.' ]")
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

sys.path.append("../")
from SegInfo import SegInfo

if __name__ == '__main__':
	
	uf = True
	print(1)
	#e_f, e_monos = read_celex('english', 7)
	#e_si = SegInfo(e_f, use_freq = uf)
	#re_si = SegInfo(e_f, use_freq = uf, reverse = True)
	#e_si.save('eng.txt', e_monos)
	#re_si.save('rev-eng.txt', e_monos)
	
	print(2)
	g_f, g_monos = read_celex('german', 4)
	g_si = SegInfo(g_f, use_freq = uf, exclude_word_freq = True)
	rg_si = SegInfo(g_f, use_freq = uf, exclude_word_freq = True, reverse = True)
	g_si.save('german.txt', g_monos)
	g_si.save_lexicon('../lexicons/' + 'german.lex.txt')
	rg_si.save('rev-german.txt', g_monos)
	
	print(3)
	d_f, d_monos = read_celex('dutch', 5)	
	d_si = SegInfo(d_f, use_freq = uf, exclude_word_freq = True)
	rd_si = SegInfo(d_f, use_freq = uf, exclude_word_freq = True, reverse = True)
	d_si.save('dutch.txt', d_monos)
	d_si.save_lexicon('../lexicons/' + 'dutch.lex.txt')
	rd_si.save('rev-dutch.txt', d_monos)
	

	if False:
		for i in tqdm(range(100)):
			random_si = SegInfo(g_f, use_freq = uf, exclude_word_freq = True, scramble_freqs = True)
			random_si.save('randos/german/{0}.txt'.format(i), g_monos)

			random_si = SegInfo(d_f, use_freq = uf, exclude_word_freq = True, scramble_freqs = True)
			random_si.save('randos/dutch/{0}.txt'.format(i), d_monos)