import os, sys, re
import csv, math, random

from pprint import pprint
from tqdm import tqdm
from collections import Counter, defaultdict

def neg_log2(p):
	return -math.log(p) / math.log(2)

def get_biphones(w):
	biphones = set()
	w = list(w)
	for i in range(len(w)-1):
		bp = ''.join(w[i:i+2])
		biphones.add(bp)
	return biphones


def as_prefix(prefix, as_str = True):
	if type(prefix) != str:	
		if as_str:
			prefix = ''.join(prefix)
		else:
			prefix = tuple(prefix)
	return prefix

# input type: orthography -> (phones, freq)
class SegInfo(object):

	def __init__(self, phone_d, nphone = 1, use_freq = True, reverse = False, scramble = False, scramble_freqs = False):
		"""
		arguments:
			`phone_d` : dictionary of tuples of phonetic transcription and frequency, e.g. 'dog' -> (['d', 'a', 'g'], 100)
						used to calculate the segmental info
			`nphone` : size of blocks for calculating segmental information. Right now, only monophones (1) and biphones (2)
			`use_freq` : to use frequency in calculation
			`reverse` : calculate segmental information on REVERSED lexicon
			`scrable` : scramble segments in words and calculate segmental information
			`scramble_freqs` : scramble the frequency scores between words 
		"""
		seqs = Counter()
		count_at_position = defaultdict(Counter)
		lex_sum = 0
		# in case we modify the dict, copy it so it doesn't affect the passed dictionary 
		d = phone_d.copy()
		
		if reverse:
			for ortho, (word, count) in d.items():
		
				d[ortho] = (word[::-1], count)
				
		if scramble:
			# lazy, but scramble the segments in the words but make sure every 2-phone sequence
			# in scrambled words is also in the original lexicon
			biphones = set()
			for _, (word, _) in d.items():
				biphones = biphones.union(get_biphones(word))

			for ortho, (word, count) in d.items():
				if len(word) > 1:
					original_word = word
					i = 0
					max_scrambles = math.factorial(len(word)) 
					while word == original_word or len(get_biphones(word).union(biphones)) > len(biphones):
						i += 1
						if i > max_scrambles:	
							word = original_word
							break
						word = list(word)
						random.shuffle(word)
						word = ''.join(word)
				
				d[ortho] = (word, count)

		# scramble the passed frequencies among words of the same length
		if scramble_freqs:
			length_to_counts = defaultdict(list)
			# get the frequencies for all words of a paricular length
			for _, (word, count) in d.items():
				wl = len(word)
				length_to_counts[wl].append(count)
			# now, randomly shuffle each list
			for wl in length_to_counts:
				random.shuffle(length_to_counts[wl])

			# now, loop back through the original data and replace frequency counts with counts of 
			# appropriate length, popping off the list
			for ortho, (word, _) in d.items():
				wl = len(word)
				new_count = length_to_counts[wl].pop(0)
				d[ortho] = (word, new_count)
		###
		# for n-phones
		if nphone not in [1, 2]:	nphone = 1
		for ortho, (word, count) in d.items():
			
			word_as_list = list(word)
			if nphone == 2:
				word_as_list = [word[i] + word[i+1] for i in range(len(word)-1)]
			d[ortho] = (word_as_list, count)
		###
		self.ortho_to_phones = {}
		for ortho, (word, count) in d.items():
			self.ortho_to_phones[ortho] = word

			if not use_freq:	count = 1
			lex_sum += count

			for position in range(len(word)+1):
				prefix = as_prefix(word[:position])

				seqs[prefix] += count
				if position < len(word):
					count_at_position[position][word[position]] += count
		pos_ent_sums = {}
		
		for position in count_at_position:
			pos_ent_sums[position] = sum(count_at_position[position].values())

		self.si = {}
		self.pe = {}
		for ortho, (word, count) in d.items():
			phone_probs = []
			pos_ent = []
			
			for position in range(len(word)):
				if position == 0:
					p = seqs[as_prefix(word[:1])]/lex_sum
				else:
					p = seqs[as_prefix(word[:position+1])]/seqs[as_prefix(word[:position])]
				phone_probs.append(neg_log2(p))
				
				e = count_at_position[position][word[position]] / pos_ent_sums[position]
				pos_ent.append(neg_log2(e))

			self.si[ortho] = (count, phone_probs)
			self.pe[ortho] = pos_ent

	def save(self, f, mono = set()):
		with open(f, 'w') as wf:
			wf.write('{0}\n'.format('\t'.join(['WORD', 'FREQUENCY', 'LENGTH', 'POSITION', 'PHONE', 'SEQ_INFO', 'POSITION_INFO', 'MONOMORPHEME'])))
			for w, t in sorted(self.si.items(), key = lambda x : x[1][0], reverse = True):
				count = str(t[0])
				phones = self.ortho_to_phones[w]
				phone_len = len(t[1])
				# sometimes, phonetic transcription (esp. CELEX) are weird. skip words where there are way more phones than letters
				if len(w) < phone_len * .75:	continue
				pos_info = self.pe[w]

				for i, p in enumerate(t[1]):
					wf.write('{0}\n'.format('\t'.join([w, count, str(phone_len), str(i+1), 
						phones[i], str(p), str(pos_info[i]), 'T' if w in mono else 'F']))) 
					

