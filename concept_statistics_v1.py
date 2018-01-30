# -*- coding:utf-8 -*-
#@time: 2018/01/29
#Usage: preview big data to temp.txt
from __future__ import print_function
import os
import sys
import re
import ast
import urllib2
import requests
import json
import numpy
import time
import argparse
import cPickle as pickle
import string

''' Statistics Need to Deal:
1.concept numbers:
2.instance numbers: 
3.relations numbers:
4.each concept's instances sets: {concept: list[(instance,relation)]} ?? each instance's concept
5.each instance's topK concept distribution. (Get by Conceptualization API)
	score functions: BLC \ smoothed P(e|c) \ P(c|e) \ MI \ NPMI \ PMI^K 
'''

# FILE_PATH = "./data/data-concept-instance-relations.txt"
FILE_PATH = "./temp.txt"
ARGS = None
LOG_FILE = None

class ConceptGraph(object):
	"""docstring for ConceptGraph"""
	def __init__(self):
		self.concepts = {} # concept:count
		self.instances = {} # instance:count
		self.e2c = {} # instance:[concept]
		self.c2e = {} # concept:[instance]
		self.record_count = 0
		self.sort_instances = {}
	def count_instance(self, c_e):
		if len(c_e) == 2:
			c = c_e[0]
			e = c_e[1]
			self.record_count += 1
			if c not in self.concepts:
				self.concepts[c] = 1
				self.c2e[c] = list()
				self.c2e[c].append(e)
			else:
				self.concepts[c] += 1
				self.c2e[c].append(e)
			if e not in self.instances:
				self.instances[e] = 1
				self.e2c[e] = list()
				self.e2c[e].append(c)
			else:
				self.instances[e] += 1
				self.e2c[e].append(c)

# class ConceptsStat(object):
# 	def __init__(self):
# 		self.concepts = {}
# 		self.c2e = {}

# class InstancesStat(object):
# 	def __init__(self):
# 		self.instances = {}
# 		self.e2c = {}
# 		self.e2c_w_r = {} # with relations
# 		self.e2c_w_p = {} # with prob

class InstancesBlock(object):
	def __init__(self, name, prob_len):
		self.name = str(name)
		self.block_list = []
		self.e2c2p = {} # instance:prob_list
		self.block_count = 0
		self.block_prob_len = prob_len
	def conceptual(self, e, prob_list):
		# if e not in self.e2c2p:
		# self.e2c2p[e] = list()
		# self.e2c2p[e].append(prob_list)
		self.e2c2p[e] = prefix_list
		self.block_list.append(e)
		self.block_count += 1

def log_in(log_str):
	log_str = str(log_str)
	print(log_str)
	LOG_FILE.write(log_str + "\n")

def prepara_concept_graph():
	start_time = time.time()
	cg = ConceptGraph()
	with open(ARGS.input, 'r') as file_in:
		count = 0
		line = file_in.readline() # or readlines() --Memory Question
		while line:
			count += 1
			# file_out.write(line)
			tokens = line.strip().split("\t")
			c_and_e = tokens[:2]
			cg.count_instance(c_and_e)
			line = file_in.readline()
			if count % 1000 == 0:
				print("%d lines." % count)
	log_in("Build Concept Graph: using time %.4f sec." % (time.time()-start_time))
	log_in("Total %d lines." % count)
	log_in("Total record: %d." % cg.record_count)
	log_in("Total Concepts numbers: %d" % len(cg.concepts))
	log_in("Total Instances numbers: %d" % len(cg.instances))
	# print(cg.concepts["metal"])
	# print(cg.c2e["metal"])
	time2 = time.time()
	log_in("Sort Instances: ")
	sort_instances = sorted(cg.instances.items(), key=lambda item: item[0])
	prefix_list = []
	nums = []
	for i in range(0,26):
		alphabet = chr(ord("a") + i)
		prefix_list.append(alphabet)
		cg.sort_instances[alphabet] = list()
	for i in range(0,10):
		nums.append(str(i))
	prefix_list.append(nums)
	cg.sort_instances["nums"] = list()
	for (e,n) in sort_instances:
		if e[0] in prefix_list[-1]:
			cg.sort_instances["nums"].append((e,n))
		else:
			prefix_list_index = prefix_list.index(e[0])
			cg.sort_instances[prefix_list[prefix_list_index]].append((e,n))
	# a_instances = [(e,n) for (e,n) in sort_instances if e.startswith(prefix_list[0])]
	# num_instances = [(e,n) for (e,n) in sort_instances if e[0] in prefix_list[-1]]
	log_in("\tSort Instances DONE! Using %.4f sec." % (time.time()-time2))
	return cg, prefix_list

def get_prob(entity):
	'''get topk prob of entity
	REF:https://concept.research.microsoft.com/help/index#!/Concept/Concept_ScoreByCross
	URL TEMPLATE: "https://concept.research.microsoft.com/api/Concept/ScoreByCross?instance=%s&topK=%d&pmiK=%d&smooth=%d" % (str(entity), topk, pmik, smooth)
	Arguments:
		entity {str}
		topk {int}
	Returns:
		list -- sorted topk prob of entity
	'''
	url_template = "https://concept.research.microsoft.com/api/Concept/ScoreBy%s" % ARGS.prob # no "?" char
	if ARGS.prob in ["Cross","PMIK","NPMI","Typi","MI"]:
		url_params = {"instance":entity,"topk":ARGS.topk,"smooth":ARGS.smooth}
	else:
		url_params = {"instance":entity,"topk":ARGS.topk}
	start_time = time.time()
	req = requests.get(url=url_template, params=url_params)
	response = req.content
	get_prob = ast.literal_eval(response) # get_prob = json.loads(response_content)
	float_formatter = lambda x: "%.10f" % x
	for k,v in get_prob.items():
		v = float_formatter(v)
		get_prob[k] = v
	sort_prob = sorted(get_prob.items(), key = lambda item:item[1], reverse = True) # list
	# print(sort_prob)
	log_in("Get [%s] %d :\tUsing time %.4f sec." % (entity, len(get_prob), (time.time() - start_time)))
	return sort_prob

def build_prob(cg,prefix_list):
	## version V1 ##
	count0 = 0
	start_time = time.time()
	for prefix, instances_list in cg.sort_instances.items():
		i_block = InstancesBlock(prefix, ARGS.topk)
		time1 = time.time()
		count1 = 0
		for (e,n) in instances_list:
			prob_list = get_prob(str(e))
			i_block.conceptual(e, prob_list)
			count1 += 1
			count0 += 1
			if count0 % 100 == 0:
				log_in("%d Instances DONE. Using %.4f sec." % (count0, (time.time()-start_time)))
				start_time = time.time()
			if count0 % 2 == 0:
				break
		log_in("Prefix[%s]: %d Instances DONE. Using %.4f sec." % (count1, str(prefix), (time.time()-time1)))
		dump_prob(i_block, prefix)



def test_args():
	print(ARGS.probpkl % "a")

def dump_obj(cg):
	start_time = time.time()
	with open(ARGS.objpkl,'w') as f:
		pickle.dump(cg, f, True)
	log_in("OBJ Pickle process DONE! %.5f sec." % (time.time()-start_time))

def dump_prob(prob_obj, pkl_name):
	start_time =time.time()
	file_path = ARGS.probpkl % (str(ARGS.prob), str(pkl_name))
	with open(file_path, 'w') as f:
		pickle.dump(prob_obj, f, True)
	log_in("Prob Prefix[%s] Pickle process DONE! %.5f sec." % (pkl_name, time.time()-start_time))

def load_pkl(load_file_path):
	start_time = time.time()
	with open(load_file_path, 'r') as f:
		content = pickle.load(f)
	print("Load pick DONE! %.5f sec." % (time.time()-start_time))
	return content

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Concepts Statistics Version 1")
	parser.add_argument("--input", default="./temp.txt", type=str, help="file in path")
	parser.add_argument("--output", default="./temp_prob_blc.txt", type=str, help="file out path")
	parser.add_argument("--log", default="./concept_blc.log", type=str, help="log file path")
	parser.add_argument("--prob", default="Cross", type=str, help="Conceptualization API:https://concept.research.microsoft.com/help/")
	parser.add_argument("--topk", default=10, type=int, help="score topk")
	parser.add_argument("--smooth", default=0, type=int, help="score smooth")
	parser.add_argument("--objpkl", default="./ConceptGraph.pkl", type=str, help="file path to save ConceptGraph")
	parser.add_argument("--probpkl", default="./prob/prob_%s_%s.pkl", type=str, help="file path to save prob as pickle")
	ARGS = parser.parse_args()
	LOG_FILE = open(ARGS.log,'w')
	#### run ####
	cg, prefix_list = prepara_concept_graph()
	dump_obj(cg)
	build_prob(cg, prefix_list)
	#### test
	# ib = load_pkl(ARGS.probpkl % (str(ARGS.prob), 'a'))
	# print(ib.name)
	# print(ib.e2c2p["abb"])
	# print(ib.block_list)
	# print(ib.block_count)
	# print(ib.block_prob_len)
	# test_args()
	# print(get_prob_BLC("14 c"))
	# test_pickle(cg)
	###########
	LOG_FILE.close()