# -*- coding:utf-8 -*-
#@author: 	Xingluxi
#@time:		2017/9/14/10:20

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import sys
import codecs
import jieba
import thulac
import time
import nltk

reload(sys)
sys.setdefaultencoding("utf-8")

DIR = "E:\PyProject\CorpusDealer\data"
FILE_NAME = ""
FILE_PATH = os.path.join(DIR, FILE_NAME)

_WORD_SPILT = re.compile(b"([.,!?\";:)(])")
_DIGIT_RE = re.compile(br"\d")
_SPECIAL_PUN = re.compile(b"\.\.")

thu = thulac.thulac(seg_only=True)

def maybe_load(dircectory, filename):
	if not os.path.exists(dircectory):
		print("Directory: %s not exists!" % dircectory)
		return
	filepath = os.path.join(dircectory, filename)
	return filepath

def en_tokenizer(sentence):
	# words = []
	words_out = []
	# find_str = "'"
	# for word in sentence.strip().split():
	# 	if bool(_DIGIT_RE.search(word)):
	# 		if word.find(","):
	# 			word = word.replace(",","")
	# 		words.append(word)
	# 	else:
	# 		words.extend(_WORD_SPILT.split(word))
	# for each in words:
	# 	each = each.decode("utf-8")
	# 	ind = each.find(find_str)
	# 	if ind != -1:
	# 		out = [each[:ind], each[ind:]]
	# 		words_out.extend(out)
	# 	else:
	# 		words_out.append(each)
	# print(type(sentence)) # unicode
	words = nltk.tokenize.word_tokenize(sentence)
	for word in words:
		if bool(_DIGIT_RE.search(word)):
			if word.find(","):
				word = word.replace(",","")
		words_out.append(word)
	return [w for w in words_out if w]


def dealer(raw_file_path, out_file_path, language = None):
	out_file = open(out_file_path,"w")
	with codecs.open(raw_file_path, 'r', 'utf-8') as in_file:
		readin = in_file.readlines()
		count = 0
		for each_line in readin:
			each_line = each_line.strip()
			if language == "en":
				tokens = en_tokenizer(each_line)
			elif language == "zh":
				tokens = zh_char_tokenizer(each_line)
			else:
				print("Invalid LANGUAGE!")
				return
			out_file.write(" ".join([str(tok) for tok in tokens]) + "\n")
			count += 1
			print("line %d done!" % count)

def main(args):
	file_in = os.path.join("E:\PyProject\CorpusDealer\data", str(args[0]))
	FILE_OUT_NAME = str(args[1])
	FILE_OUT_PATH = os.path.join(DIR, FILE_OUT_NAME)
	print(args[0])
	print(args[1])
	dealer(file_in, FILE_OUT_PATH, language="en")
	return

if __name__ == "__main__":
	start_time = time.time()
	main(sys.argv[1:])
	end_time = time.time() - start_time
	print("using time: %0.3f sec." % end_time)