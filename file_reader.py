# -*- coding:utf-8 -*-

import codecs
import os


DIR = "E:\PyProject\CorpusDealer\data"
FILE_NAME = "train.test.zh"
FILE_PATH = os.path.join(DIR, FILE_NAME)

with codecs.open(FILE_PATH, 'r', "utf-8") as file_in:
	readin = file_in.readlines()
	for each in readin:
		print each