import os, re, sys, csv
from tqdm import tqdm
from pprint import pprint

sys.path.append("../")
from SegInfo import SegInfo

def read_french(f = 'FrenchLexiqueLemmaCorpusWCats.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for word, count, pos in reader:
			count = float(count)
			if count > 0:
				d[word] = (word, count)
	return d

def read_korean(f = 'korean_lexicon_stage_9_unix.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = ' ')
		for word, count, pos in reader:
			word = re.sub(r'\.', '', word)
			count = float(count)
			if count > 0:
				d[word] = (word, count)
	return d

def read_slovak(f = 'SlovakLemmaListOut.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for word, count in reader:
			count = float(count)
			if count > 0:
				d[word] = (word, count)
	return d

def read_spanish(f = 'SpanishLemmaCorpus.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for word, pos, _, count in reader:
			count = float(count)
			if count > 0:
				d[word] = (word, count)
	return d


def read_turkish(f = 'TurkishLemmaCorpusND.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for line in reader:
			word = line[0]
			count = line[1]
			count = float(count)
			if count > 0:
				d[word] = (word, count)
	return d


if __name__ == '__main__':
	fr = read_french()
	kr = read_korean()
	sl = read_slovak()
	sp = read_spanish()
	tr = read_turkish()

	langs = [fr, kr, sl, sp, tr]
	langs_outputs = ['fr', 'kr', 'sl', 'sp', 'tr']
	
	for i, (l, lf) in enumerate(zip(langs, langs_outputs)):
		print(i, lf)
		si = SegInfo(l, exclude_word_freq = True)
		si.save(lf + '.txt')
		if True:
			for j in tqdm(range(50)):
				random_si = SegInfo(l, scramble_freqs = True, exclude_word_freq = True)
				random_si.save('randos/{0}/{1}.txt'.format(lf, j))