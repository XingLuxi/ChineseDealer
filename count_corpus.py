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
# import jieba
# import thulac
import time
# import nltk
import numpy as np
import random
from matplotlib import pyplot as plt


def count_max_length(file_path):
	with codecs.open(file_path, 'r', 'utf-8') as file_in:
		read_in = file_in.readlines()
		idx = 0
		len_num_dict = {} # key = length , value = num
		for each_line in read_in:
			line_len = len(each_line.split())
			if line_len not in len_num_dict:
				len_num_dict[line_len] = 1
			else:
				len_num_dict[line_len] += 1
			idx += 1
			print("id: %d \t ==> %d " %(idx, line_len))
		print(len_num_dict)
	return len_num_dict

def draw_graph(len_num_dict):
	# d = {1:2,4:5,10:8,2:7}
	d = len_num_dict
	for i,key in enumerate(d):
		plt.bar(key, d[key], color="r", width=0.3)
	
	# max_length = 10000000
	len_list = [d[key] for key in d]
	print(max(len_list), min(len_list))
	plt.xticks(d.keys())
	plt.yticks(np.arange(0,max(len_list)+100, len(d.values())))
	# plt.grid(True)
	plt.xlabel("tokens length")
	plt.ylabel("counts")
	plt.show()
	return

def draw_hist(len_num_dict, title):
	d = len_num_dict
	# num_list = [d[k] for k in d]
	num_list = d.values()
	max_num = max(num_list)
	len_list = d.keys()
	max_len = max(len_list)
	# print(title)
	print("max len = %d" % int(max_len))
	print("max num = %d" % int(max_num))
	for i,k in enumerate(d):
		plt.bar(k, d[k], color="blue", width=0.3)
		plt.text(k, d[k], d[k], color='red', horizontalalignment='center', fontsize=6)
	xwidth = int(len(len_list) / (int(len(len_list) / 100)))
	ywidth = int(len(num_list) / (int(len(num_list) / 50)))
	plt.xticks(np.arange(0, int(max_len)+10, 50))
	plt.yticks(np.arange(0, int(max_num)+20, 20000))
	plt.title(title)
	plt.xlabel("sentences tokens length")
	plt.ylabel("counts")
	plt.show()
	return

def main(args):
	file_name = args[0]
	file_path = os.path.join("E:\PyProject\CorpusDealer\data", str(file_name))
	print(args)
	dicts = count_max_length(file_path)
	draw_hist(dicts, str(file_name))
	return

if __name__ == "__main__":
	start_time = time.time()
	main(sys.argv[1:])
	end_time = time.time() - start_time
	print("using time: %0.3f sec" % end_time)