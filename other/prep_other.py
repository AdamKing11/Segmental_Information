import os, re, sys, csv
import json
from tqdm import tqdm
from pprint import pprint
import unidecode

sys.path.append("../")
from SegInfo import SegInfo

def read_kaqchikel(f = 'kaqchikel.word.token.freq.May2016.txt'):

	from nltk.corpus import cess_esp
	spanish_words = set([w.lower() for w in cess_esp.words()])

	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		next(reader)
		# 
		for word, count in reader:
			# inconsistent accentation in the corpus, just strip all accents
			word = unidecode.unidecode(word)
			# remove characters that are not Mayan orthography
			if re.search(r"[dg]|c[^h]|[^t]z|b[^']", word) or re.search(r'([a-z])\1', word):
				continue
			phones = []
			last_ejective = ''
			for p in word:
				if len(phones) == 0:
					phones.append(p)
				elif p == "'":
					if phones[-1] in ['b', 't', 'k', 'q', 'ch', 'tz']:
						phones[-1] = phones[-1] + "'"
					else:
						phones.append(p)
				elif p == 'h':
					if phones[-1] == 'c':
						phones[-1] = 'ch'
					else:
						phones.append(p)					
				elif p == 'z':
					if phones[-1] == 't':
						phones[-1] = 'tz'
					else:
						phones.append(p)
				else:
					phones.append(p)
			
			phones = tuple(phones)
			count = int(count)
			if count >= 5 and len(phones) > 1:
				if word in d:
					d[word] = (phones, count + d[word][1])
				else:
					d[word] = (phones, count)

	return d

def read_swahili(f = 'swahili_vocab_nk.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		i = 0
		for line in reader:
			try:
				word, count, word_info = line
			except:
				continue
			if not re.search(r'[a-z][a-z]', word):	continue
			
			word_info = word_info.replace("'", '"')
			word_info = re.sub(r'\w"\w', "'", word_info)
			word_info = json.loads(word_info)
		
			if 'lemma' not in word_info:	continue

			count = int(count)
			lemma = word_info['lemma'].lower()
			phones = []
			for p in lemma:
				if len(phones) > 0 and ((p == 'h' and phones[-1] in ['c', 's', 't']) or (p in ['g', 'y'] and phones[-1] == 'n')):
					phones[-1] = phones[-1] + p
				else:
					phones.append(p)
			phones = tuple(phones)
			if count >= 5 and len(phones) > 1 and not re.search(r'[^a-z]', lemma):
				if lemma in d:
					d[lemma] = (phones, count + d[lemma][1])
				else:
					d[lemma] = (phones, count)
	return d


def read_mandarin(f = 'mandarin_char_uni.txt'):
	d = {}
	with open(f) as rf:
		reader = csv.reader(rf, delimiter = '\t')
		next(reader)
		for line in reader:
			word = line[0]
			count = int(line[1])
			###
			# vowel + tone
			vowel = line[3] + line[2]
			coda = line[5] if line[5] != 'NA' else ''
			rhyme_len = len(vowel) + len(coda)
			onset = word[:-rhyme_len]
			phones = [onset, vowel]
			if len(coda) > 0:
				phones.append(coda)
			phones = tuple(phones)
			d[word] = (phones, count)
		return d


if __name__ == '__main__':
	kaq = read_kaqchikel()
	swa = read_swahili()
	ma = read_mandarin()
	langs = [kaq, swa, ma]
	langs_outputs = ['kaq', 'swa', 'ma']

	for i, (l, lf) in enumerate(zip(langs, langs_outputs)):
		print(i, lf)
		
		si = SegInfo(l, exclude_word_freq = True)
		si.save(lf + '.txt')
		si.save_lexicon('../lexicons/' + lf + '.lex.txt')
		
		if i == 2:
			for f in os.listdir('randos/{0}/'.format(lf)):
				os.remove('randos/{0}/'.format(lf) + f)

			for j in tqdm(range(100)):
				random_si = SegInfo(l, scramble_freqs = True, exclude_word_freq = True)
				random_si.save('randos/{0}/{1}.txt'.format(lf, j))