# -*- coding:utf-8 -*-
import os
import re
import sys
import codecs

reload(sys)
sys.setdefaultencoding("utf-8")

DIR = "E:\PyProject\CorpusDealer\data"
FOLDER = "Colings"

FILE_PATH = os.path.join(DIR, FOLDER)

files = [f for f in os.listdir(FILE_PATH) if os.path.isfile(os.path.join(FILE_PATH,f))]
file_name = []
print len(files)

output = "out.txt"
output_path = os.path.join(DIR, output)
print output_path

for each in files:
	file_name.append(each)
	# print each.__class__ # str
print file_name
with codecs.open(output_path,'w') as out:
	for each in file_name:
		out.write(each+"\n")

str = "我是"
print unicode(str).encode("utf-8")
print str.__class__