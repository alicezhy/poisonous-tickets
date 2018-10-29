# This code is in Python 3
import bs4, requests, sys
import html2text
from multiprocessing import Pool

def crawl(train):
	try:
		open("raw_data/raw_train_data/%s.txt" % train, "r")
	except:	
		data = requests.get("http://www.jt2345.com/huoche/checi/%s.htm" % train)
		data.raise_for_status()
		data.encoding = "GBK"
		pia = bs4.BeautifulSoup(data.text, "html.parser")
		s = (str(pia))
		c = html2text.html2text(s)
		with open("raw_train_data/%s.txt" % train, "w") as f:
			f.write(c)
		print ("Finish downloading data for %s" % train)

all_train = []
with open("raw_data/all_train.txt", "r") as f:
	for line in f:
		c = line.split()
		for train in c:
			all_train.append(train)

p = Pool(100)
p.map(crawl, all_train)

