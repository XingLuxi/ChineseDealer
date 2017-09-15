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
from itertools import groupby

reload(sys)
sys.setdefaultencoding("utf-8")

DIR = "E:\PyProject\CorpusDealer\data"
FILE_NAME = ""
FILE_PATH = os.path.join(DIR, FILE_NAME)

_WORD_SPILT = re.compile(b"([.,!?\";:)(：；。，！？‘’“”])")
_DIGIT_RE = re.compile(br"\d")
_SPECIAL_PUN = re.compile(b"\.\.")
_ENG_CHAR = re.compile(b"\w")

thu = thulac.thulac(seg_only=True)

def maybe_load(dircectory, filename):
	if not os.path.exists(dircectory):
		print("Directory: %s not exists!" % dircectory)
		return
	filepath = os.path.join(dircectory, filename)
	return filepath

def zh_char_tokenizer(sentence):
	"""Comments:
		1.spilt chinese sentence char by char and punctuation;
		2.continuous number do not spilt;
		3.
	"""
	words_out = []
	seg_list = thu.cut(sentence, text=True)
	seg_list = seg_list.split()
	# print(seg_list)
	for each_seg in seg_list:
		each_seg = each_seg.decode("utf-8")
		# print(each_seg)
		if bool(_DIGIT_RE.search(each_seg)):
			# words_out.append(each_seg)
			split_num_char = ["".join(list(g)) for k,g in groupby(each_seg, key=lambda x: x.isdigit() or (x==".") or (x==":"))]
			# 
			words_out.extend(split_num_char)
		elif bool(_SPECIAL_PUN.search(each_seg)):
			words_out.append(each_seg)
		elif bool(_ENG_CHAR.search(each_seg)):
			words_out.append(each_seg)
		else:
			each_seg = list(each_seg)
			words_out.extend(each_seg)
	return [w for w in words_out if w]

def dealer(raw_file_path, out_file_path):
	out_file = open(out_file_path,"w")
	with codecs.open(raw_file_path, 'r', 'utf-8') as in_file:
		readin = in_file.readlines()
		count = 0
		for each_line in readin:
			each_line = each_line.strip()
			tokens = zh_char_tokenizer(each_line)
			out_file.write(" ".join([str(tok) for tok in tokens]) + "\n")
			count += 1
			print("line %d done!" % count)

def main(args):
	file_in = os.path.join("E:\PyProject\CorpusDealer\data", str(args[0]))
	FILE_OUT_NAME = str(args[1])
	FILE_OUT_PATH = os.path.join(DIR, FILE_OUT_NAME)
	print(args[0])
	print(args[1])
	dealer(file_in, FILE_OUT_PATH)
	return

if __name__ == "__main__":
	start_time = time.time()
	main(sys.argv[1:])
	end_time = time.time() - start_time
	print("using time: %0.3f sec." % end_time)