# -*- coding:utf-8 -*-
#@time: 2018/01/26

from __future__ import print_function
import xml.etree.cElementTree as ET
# try:
# 	import xml.etree.cElementTree as ET
# except ImportError:
# 	import xml.etree.ElementTree as ET
import os
import time

# load file
dir_name = "./xml_data"
# file_name = 'wikicomp-2014_enzh.xml'
file_name ="10000.xml"
file_path = str(os.path.join(dir_name,file_name))
print(file_path)
# 
# 

def xml_dealer_failed():
	count = 0
	start_time = time.time()
	wiki_tree = ET.ElementTree(file_path)
	# wiki_tree = ET.iterparse(file_path)
	# wiki_tree = ET.parse(file_path)
	for elem in wiki_tree.iter():
		count += 1
		print(elem.tag, elem.attrib)

	for event, elem in ET.iterparse(file_path):
		if event == 'end':
			if elem.tag == 'articlePair':
				count += 1
		elem.clear()
	print(count)
	print("Using time: %.4f" % time.time()-start_time)

def xml_dealer():
	count = 0
	doc_tree = ET.iterparse(file_path)

	for event,elem in doc_tree:
		if elem.tag == 'articlePair':
			print(elem.attrib)
			articlePair_list = elem.getchildren()
			pairs = elem.getiterator("article")
			for each in pairs:
				print(each.attrib)
		elem.clear()


import lxml.html as HTML
import lxml.etree as etree
def xpath_dealer():
	f = open(file_path,'r')
	xml_txt = f.read()
	xdoc = HTML.fromstring(xml_txt)
	xtree = etree.ElementTree(xdoc)
	base_path = '/wikipediacomparable/articlepair'
	# for each in xdoc.iter():
	# 	path = xtree.getpath(each)
		# print(path)
		# print(each.tag)
	print(xdoc.xpath("//wikipediacomparable/articlepair/@id"))
	articles = xdoc.xpath("//wikipediacomparable/articlepair/article")
	categories = xdoc.xpath("//wikipediacomparable/articlepair/article/categories")
	contents = xdoc.xpath("//wikipediacomparable/articlepair/article/content")
	count=0
	for each in articles:
		count+=1
		print(count)
		print(xtree.getpath(each))
		print(each.attrib['lang'])
		# print(each.text_content())
	pairs_ID = xdoc.xpath("//wikipediacomparable/articlepair/@id")
	pairs_Lang = xdoc.xpath("//wikipediacomparable/articlepair/article/@lang")
	pairs_Lang = list(set(pairs_Lang))
	print(pairs_Lang)
	# print(xdoc.xpath("//wikipediacomparable/articlepair[@id='1']/article[@lang='zh']")[0].text_content())


def read_in():
	file_out = open("./xml_data/10000.txt",'w')
	with open(file_path,'r') as file_in:
		count = 0
		while count < 10000:
			line = file_in.readline().strip()
			file_out.write(line+"\n")
			count+=1
	file_out.close()

if __name__ == '__main__':
	# read_in()
	xpath_dealer()
