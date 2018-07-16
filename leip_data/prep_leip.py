import os, re, sys
from tqdm import tqdm
from pprint import pprint

def read_corpus(corpus_f, alphabet, min_freq = 50, skip_english = False):
	freqs = {}
	with open(corpus_f) as rf:
		for i, line in tqdm(enumerate(rf)):
			#if i > 10000:	break
			_, line = line.lower().rstrip().rsplit('\t')
			line = re.sub(r'\s+', ' ', line)
		
			for word in line.split():
				if re.search('[^{0} ]'.format(alphabet), word): continue
				if word in freqs:
					freqs[word] += 1
				else:
					freqs[word] = 1

	legit_words = {}
	for word, freq in freqs.items():
		if freq >= min_freq:
			legit_words[word] = freq

	if skip_english:
		from nltk.corpus import words
		english_words = set(words.words())

		for word in legit_words.copy():
			if len(word) > 2 and re.sub(r'e[rd]s?$', '', word) in english_words:
				del legit_words[word]

	return legit_words


def prepare_corpusfreq(cf, phone_transcript_f = lambda w : w):
	pcf = {}
	for word, freq in cf.items():
		pcf[word] = (phone_transcript_f(word), freq)
	return pcf






aybuben = 'աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆև'
def arm_t(w):
	# vo
	w = re.sub(r'^ո', 'վո', w)
	w = re.sub(r'օ', 'ո', w)
	# jE
	w = re.sub(r'^ե', 'յե', w)
	w = re.sub(r'է', 'ե', w)
	w = re.sub(r'և', 'եվ', w)
	return w

tag_alphabet = 'a-z'
def tag_t(w):
	# ng
	w = re.sub(r'ng', 'N', w)

	return w

turk_alphabet = r'a-zğçşıüö'


if __name__ == '__main__':
	sys.path.append("../")
	from SegInfo import SegInfo
	
	print(1)
	arm = read_corpus('hye/hye-am_web_2017_1M-sentences.txt', aybuben)
	arm = prepare_corpusfreq(arm, phone_transcript_f = arm_t)
	arm_si = SegInfo(arm)
	arm_si.save('hye.txt', ())
	scr_arm_si = SegInfo(arm, scramble = True)
	scr_arm_si.save('scr-hye.txt', ())
	rev_arm_si = SegInfo(arm, reverse = True)
	rev_arm_si.save('rev-hye.txt', ())

	print(2)
	turk = read_corpus('tur/tur-tr_web_2016_1M-sentences.txt', turk_alphabet)
	turk = prepare_corpusfreq(turk)
	turk_si = SegInfo(turk)
	turk_si.save('turk.txt')
	scr_turk_si = SegInfo(turk, scramble = True)
	scr_turk_si.save('scr-turk.txt', ())
	rev_turk_si = SegInfo(turk, reverse = True)
	rev_turk_si.save('rev-turk.txt', ())
	
	print(3)
	tag = read_corpus('tag/tgl_newscrwal_2011_300K-sentences.txt', tag_alphabet, skip_english = True)
	tag = prepare_corpusfreq(tag, phone_transcript_f = tag_t)
	tag_si = SegInfo(tag)
	tag_si.save('tag.txt')
	scr_tag_si = SegInfo(tag, scramble = True)
	scr_tag_si.save('scr-tag.txt', ())
	rev_tag_si = SegInfo(tag, reverse = True)
	rev_tag_si.save('rev-tag.txt', ())

