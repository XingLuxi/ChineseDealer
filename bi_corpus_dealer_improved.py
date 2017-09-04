# -*- coding:utf-8 -*-
# @Time     : 2017/7/27 12:13
# @Author   : XingLuxi
# @File     : CorpusDealer/bi_corpus_dealer.py

import re
import os
import sys
import jieba
import codecs
import thulac
# import spacy
# import en_core_web_md

reload(sys)
sys.setdefaultencoding("utf-8")

DIR = "E:\PyProject\CorpusDealer\data"
# FILE_NAME = "Bi-Education.txt"
FILE_NAME = "Bi-Spoken.txt"
FILE_PATH = os.path.join(DIR, FILE_NAME)

ENG_OUT_NAME = FILE_NAME[:-4]+"-Eng.txt"
CH_OUT_NAME = FILE_NAME[:-4]+"-Ch.txt"
ENG_OUT_PATH = os.path.join(DIR, ENG_OUT_NAME)
CH_OUT_PATH = os.path.join(DIR, CH_OUT_NAME)
# print ENG_OUT_PATH
# print CH_OUT_PATH

_WORD_SPLIT = re.compile(b"([.,!?\":;)(])") # Problem of 's
_DIGIT_RE = re.compile(br"\d")
thu = thulac.thulac(seg_only=True)

def maybe_load(directory, filename):
	if not os.path.exists(DIR):
		print "Creating directory %s" % directory
		os.mkdir(directory)
	filepath = os.path.join(directory, filename)
	return filepath

def basic_tokenizer(sentence):
	words = []
	words_out = []
	find_str = "'"
	for seg in sentence.strip().split():
		words.extend(_WORD_SPLIT.split(seg))
	for each in words:
		indx = each.find(find_str)
		if indx != -1:
			out = [each[:indx],each[indx:]]
			words_out.extend(out)
		else:
			words_out.append(each)
	return [w for w in words_out if w]

def ch_tokenizer(sentence):
	words_out = []
	seg_list = thu.cut(sentence, text=True)
	seg_list = seg_list.split()
	words_out.extend(seg_list)
	return [w for w in words_out if w]

def dealer(raw, eng_out, ch_out):
	eng_file = open(eng_out,'w')
	ch_file = open(ch_out, 'w')
	with codecs.open(raw,'r',"utf-8") as file_in:
		readin = file_in.readlines()
		count = 0
		for line in readin:
			count = count+1
			if count % 2:
				line = line.strip()
				line = line.strip("\n")
				# eng_file.write(" ".join([str(tok) for tok in tokens]) + "\n")
				eng_file.write(line + "\n")
			else:
				# line = line.strip()
				# line = line.strip("\n")
				tokens = ch_tokenizer(line)
				ch_file.write(" ".join([str(tok) for tok in tokens]) + "\n")
			print "line %d deal Done!" % count

if __name__ == '__main__':
    # dealer(FILE_PATH, ENG_OUT_PATH, CH_OUT_PATH)
	file_e = os.path.join(DIR,"test_eng.txt")
	file_ch = os.path.join(DIR, "test_ch.txt")
	dealer(FILE_PATH, file_e, file_ch)
	pass