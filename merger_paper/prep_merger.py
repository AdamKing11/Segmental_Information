import os, re, sys, csv
from tqdm import tqdm
from pprint import pprint

sys.path.append("../")
from SegInfo import SegInfo

def upper_sub(match):
	return match.group(1).upper()

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

def read_finnish(f = 'FinnishLemmaList.txt'):
	d = {}
	with open(f) as rf:
		next(rf)
		for line in rf:
			line = re.sub(r' +', ' ', line.rstrip()).split()
			word = re.sub(r'(.)\1', upper_sub, line[3])
			count = int(line[1])
			if count > 0 and not re.search(r'[_-]', word):
				d[word] = (word, count)
	return d

def read_cantonese(f = 'CantoneseWordList.txt'):
	d = {}
	vowels = set(['i', 'e', 'a', 'u', 'o', 'A', 'V', 'O', 'y'])
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		for word, count, pos in reader:
			count = int(count)
			phones = []
			for p in word:
				if p in vowels:
					if len(phones) > 0 and phones[-1] in vowels:
						phones[-1] = phones[-1] + p
					else:
						phones.append(p)
				elif re.search(r'[0-9]', p):
					for i, q in enumerate(phones[::-1]):
						if q in vowels or len(q) == 2:
							phones[-i-1] = phones[-i-1] + p
							break
				else:
					phones.append(p)
			if count > 0:
				d[word] = (phones, count)
	return d

if __name__ == '__main__':
		
	fr = read_french()
	kr = read_korean()
	sl = read_slovak()
	sp = read_spanish()
	tr = read_turkish()
	fn = read_finnish()
	ca = read_cantonese()

	langs = [ca, fr, kr, sl, sp, tr, fn]
	langs_outputs = ['ca', 'fr', 'kr', 'sl', 'sp', 'tr', 'fn']

	langs = [tr]
	langs_outputs = ['tr']

	for i, (l, lf) in enumerate(zip(langs, langs_outputs)):
		print(i, lf)
		
		si = SegInfo(l, exclude_word_freq = True)
		si.save(lf + '.txt')
		si.save_lexicon('../lexicons/' + lf + '.lex.txt')
		if i == 0:
			for f in os.listdir('randos/{0}/'.format(lf)):
				os.remove('randos/{0}/'.format(lf) + f)
			for j in tqdm(range(100)):
				random_si = SegInfo(l, scramble_freqs = True, exclude_word_freq = True)
				random_si.save('randos/{0}/{1}.txt'.format(lf, j))