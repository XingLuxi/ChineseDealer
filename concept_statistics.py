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

''' Statistics Need to Deal:
1.concept numbers:
2.instance numbers: 
3.relations numbers:
4.each concept's instances sets: {concept: list[(instance,relation)]} ?? each instance's concept
5.each instance's topK concept distribution. (Get by Conceptualization API)
	score functions: BLC \ smoothed P(e|c) \ P(c|e) \ MI \ NPMI \ PMI^K 
'''

# FILE_PATH = "./data-concept/data-concept-instance-relations.txt"
# FILE_PATH = "./temp.txt"
FILE_PATH = ".\data-concept\data-concept-instance-relations.txt"
LOG_FILE = open(".\concept-blc.log",'w')

class ConceptGraph(object):
	"""docstring for ConceptGraph"""
	def __init__(self):
		self.concepts = {} # concept:count
		self.instances = {} # instance:count
		self.e2c = {} # instance:[concept]
		self.c2e = {} # concept:[instance]
		self.record_count = 0
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

class ConceptsStat(object):
	def __init__(self):
		self.concepts = {}
		self.c2e = {}

class InstancesStat(object):
	def __init__(self):
		self.instances = {}
		self.e2c = {}
		self.e2c_w_r = {} # with relations
		self.e2c_w_p = {} # with prob

class Entity(object):
	def __init__(self, name):
		self.name = name
		self.e2c_p = {}
	def conceptual(self, api_get):
		# TODO
		pass

def prepara_concept_graph():
	start_time = time.time()
	cg = ConceptGraph()
	with open(FILE_PATH, 'r') as file_in:
		count = 0
		line = file_in.readline()
		while line: # add count line and print
			count += 1
			# file_out.write(line)
			tokens = line.strip().split("\t")
			c_and_e = tokens[:2]
			cg.count_instance(c_and_e)
			line = file_in.readline()
			if count % 1000 == 0:
				print("%d lines." % count)
	print("Total %d lines." % count)
	LOG_FILE.write("Total %d lines.\n" % count)
	print("Total record: %d." % cg.record_count)
	LOG_FILE.write("Total record: %d.\n" % cg.record_count)
	print("Total Concepts numbers: %d." % len(cg.concepts))
	LOG_FILE.write("Total Concepts numbers: %d.\n" % len(cg.concepts))
	print("Total Instances numbers: %d" % len(cg.instances))
	LOG_FILE.write("Total Instances numbers: %d.\n" % len(cg.instances))
	# print(cg.concepts["metal"])
	# print(cg.c2e["metal"])
	log_build_cg = "Build Concept Graph: using time %.4f sec." % (time.time()-start_time)
	print(log_build_cg)
	LOG_FILE.write(log_build_cg+"\n")
	return cg

def get_prob_BLC(entity, topk):
	'''get topk prob of entity
	REF:https://concept.research.microsoft.com/help/index#!/Concept/Concept_ScoreByCross
	URL TEMPLATE: "https://concept.research.microsoft.com/api/Concept/ScoreByCross?instance=%s&topK=%d&pmiK=%d&smooth=%d" % (str(entity), topk, pmik, smooth)
	Arguments:
		entity {str}
		topk {int}
	Returns:
		list -- sorted topk prob of entity
	'''
	url_template = "https://concept.research.microsoft.com/api/Concept/ScoreByCross" # no "?" char
	url_params = {"instance":entity,"topk":topk,"pmik":10,"smooth":0}
	start_time = time.time()
	req = requests.get(url=url_template, params=url_params)
	response = req.content
	get_prob = ast.literal_eval(response) # get_prob = json.loads(response_content)
	float_formatter = lambda x: "%.10f" % x
	for k,v in get_prob.items():
		v = float_formatter(v)
		get_prob[k] = v
	sort_prob = sorted(get_prob.items(), key = lambda item:item[1], reverse = True) # list
	# print(type(sort_prob[0])) # tuple
	log_str = "Get [%s] %d :\tUsing time %.4f sec." % (entity, len(get_prob), (time.time() - start_time))
	print(log_str)
	LOG_FILE.write(log_str+'\n')
	return sort_prob

def build_prob(cg):
	prob_file_path = "./instance-concept-blc-20.txt"
	prob_file_in = open(prob_file_path, 'w')
	count = 0
	start_time = time.time()
	for e,nums in cg.instances.items():
		prob_list = get_prob_BLC(str(e),20)
		for (c,p) in prob_list:
			prob_record = "%s\t|%s:\t\t\t\t%s" % (e,c,p)
			prob_file_in.write(prob_record + '\n')
		count += 1
		if count % 100 == 0:
			log_str = "%d Instances DONE. Using %.5f sec." % (count, time.time()-start_time)
			print(log_str)
			LOG_FILE.write(log_str+"\n")
		# if count % 200 == 0:
		# 	return



if __name__ == '__main__':
	cg = prepara_concept_graph()
	# get_prob_BLC("age",10)
	build_prob(cg)