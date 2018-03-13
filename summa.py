from flask import Flask, request
import json
import threading
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib.request
from bs4 import BeautifulSoup
from flask import Flask
import json
import threading
from random import random
from flask_cors import CORS, cross_origin
from gensim.summarization import keywords

app = Flask(__name__,static_url_path="")
CORS(app)
	
class FrequencySummarizer:
	def __init__(self, min_cut=0.1, max_cut=0.9):
		self._min_cut = min_cut
		self._max_cut = max_cut 
		self._stopwords = set(stopwords.words('english') + list(punctuation))
	def _compute_frequencies(self, word_sent):
		freq = defaultdict(int)
		for s in word_sent:
			for word in s:
				if word not in self._stopwords:
					freq[word] += 1
		m = float(max(freq.values()))
		for w in list(freq):
			freq[w] = freq[w]/m
			if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
				del freq[w]
		return freq
    
	def summarize(self, text, n):
		sents = sent_tokenize(text)
		assert n <= len(sents)
		word_sent = [word_tokenize(s.lower()) for s in sents]
		self._freq = self._compute_frequencies(word_sent)
		ranking = defaultdict(int)
		for i,sent in enumerate(word_sent):
			for w in sent:
				if w in self._freq:
					ranking[i] += self._freq[w]
		sents_idx = self._rank(ranking, n)    
		return [sents[j] for j in sents_idx]
		
	def _rank(self, ranking, n):
		return nlargest(n, ranking, key=ranking.get)
		
def get_only_text(url):
	if url[:36]=='https://timesofindia.indiatimes.com/':
		page = urllib.request.urlopen(url).read().decode('utf8')
		soup = BeautifulSoup(page,"html.parser")
		text = ' '.join(map(lambda p: p.text, soup.find_all('div',attrs={'class': 'Normal'})))
		return soup.title.text, text
	if url[:24]=='https://www.nytimes.com/':
		page = urllib.request.urlopen(url).read().decode('utf8')
		soup = BeautifulSoup(page,"lxml")
		text = ' '.join(map(lambda p: p.text, soup.find_all('p',attrs={'class': "story-body-text story-content"})))
		return soup.title.text, text
	page = urllib.request.urlopen(url).read().decode('utf8')
	soup = BeautifulSoup(page,"html.parser")
	text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
	return soup.title.text, text

@app.route("/abridge", methods=['GET','POST'])
def func():
	try:
		data=request.data
		print(data)
		print("Hello here")
		data=data.decode('ascii')
		url,lines = data.split('&')
		n = int(lines)
		#feed_xml = urllib.request.urlopen('https://www.nytimes.com/').read()
		#print('--------------------------------FEED_XML-------------------------------')
		#print(feed_xml)
		#print('--------------------------------FEED-------------------------------')
		#feed = BeautifulSoup(feed_xml.decode('utf8'),"html.parser")
		#print(feed)
		#print('--------------------------------TO SUMMARIZE-------------------------------')
		#to_summarize = list(map(lambda p: p.text, feed.find_all('a',href=True)))
		to_summarize=[url]
		#for i in feed.find_all('a',href=True):
		#	if '#' not in i['href']:
		#			to_summarize.append(i['href'])
		print(to_summarize)
		fs = FrequencySummarizer()
		print('HereAAS')
		#to_summarize=['https://domypapers.com/blog/syrian-refugees/']
		if url=='https://www.nytimes.com/':
			print('ADSDS')
			feed_xml = urllib.request.urlopen('https://www.nytimes.com/').read()
			print('--------------------------------FEED_XML-------------------------------')
			print(feed_xml)
			print('--------------------------------FEED-------------------------------')
			feed = BeautifulSoup(feed_xml.decode('utf8'),"lxml")
			print(feed)
			print('--------------------------------TO SUMMARIZE-------------------------------')
			to_summarize=[]
			print(type(feed))
			temp=[]
			temp = list(map(lambda p: p.a, feed.find_all('h2',attrs={'class': 'story-heading'})))
			for i in range(5):
				to_summarize.append(str(temp[i]['href']))
			print(to_summarize[0])
			
		if url=='https://timesofindia.indiatimes.com/':
			print('ADSDS')
			feed_xml = urllib.request.urlopen('https://timesofindia.indiatimes.com/').read()
			print('--------------------------------FEED_XML-------------------------------')
			#print(feed_xml)
			print('--------------------------------FEED-------------------------------')
			feed = BeautifulSoup(feed_xml.decode('utf8'),"lxml")
			print(feed)
			print('--------------------------------TO SUMMARIZE-------------------------------')
			to_summarize=[]
			print(type(feed))
			temp=[]
			for ia in range(1,6):
				temp.extend(list(map(lambda p: p, feed.find_all('a',attrs={'pg': 'new_#Story_View-'+str(ia)+'-geturl~Top_Story_Section'}))))
			for i in range(5):
				to_summarize.append('https://timesofindia.indiatimes.com/'+str(temp[i]['href']))
			print(to_summarize[0])

			
		#to_summarize=['https://domypapers.com/blog/syrian-refugees/']
		xx='<html><head><link href="https://fonts.googleapis.com/css?family=Poiret+One|Sanchez" rel="stylesheet"> <link rel="stylesheet" type="text/css" href="window.css"></head><body>'
		for article_url in to_summarize:
			
			title, text = get_only_text(article_url)
			print('----------------------------------')
			print(title)
			xx+='<h1>'+title+'</h1>'
			for s in fs.summarize(text, n):
				xx+="<p> * "+s+"</p>"
				print ('*',s)
			xx+="</body></html>"	
		return str(xx)
	except urllib.request.URLError:
		return '<html><head><link href="https://fonts.googleapis.com/css?family=Poiret+One|Sanchez" rel="stylesheet"> <link rel="stylesheet" type="text/css" href="window.css"></head><body><p>This url cannot be summarized</p></body></html>'
	except Exception as e:
		return '<html><head><link href="https://fonts.googleapis.com/css?family=Poiret+One|Sanchez" rel="stylesheet"> <link rel="stylesheet" type="text/css" href="window.css"></head><body><p>'+str(e)+'</p></body></html>'

@app.route("/abridge/android", methods=['POST'])
def func_android():
	try:
		data=request.data
		print(data)
		data=data.decode('ascii')
		x=json.loads(data)
		#print(x)
		#print(data.url)
		#print(data.lines)
		url = x['url']
		n= int(x['number'])
		#url,lines = data.split('&')
		#n = int(lines)
		#feed_xml = urllib.request.urlopen('https://www.nytimes.com/').read()
		#print('--------------------------------FEED_XML-------------------------------')
		#print(feed_xml)
		#print('--------------------------------FEED-------------------------------')
		#feed = BeautifulSoup(feed_xml.decode('utf8'),"html.parser")
		#print(feed)
		#print('--------------------------------TO SUMMARIZE-------------------------------')
		#to_summarize = list(map(lambda p: p.text, feed.find_all('a',href=True)))
		to_summarize=[url]
		#for i in feed.find_all('a',href=True):
		#	if '#' not in i['href']:
		#			to_summarize.append(i['href'])
		print(to_summarize)
		fs = FrequencySummarizer()
		#to_summarize=['https://domypapers.com/blog/syrian-refugees/']
		for article_url in to_summarize:
			xx="\t\t"
			title, text = get_only_text(article_url)
			print('----------------------------------')
			print(title)
			
			for s in fs.summarize(text, n):
				xx+=s
				print ('*',s)
		jsons={}
		jsons['title']=title
		jsons['datas']=xx
		a=str(keywords(text))
		s=a.split('\n')
		print(s)
		jsons['keywords']='\n'.join(s[:10])
		
		x=json.dumps(jsons)
		print('--------------------------------------------------------------------------------------------------------------',x)
		obj = json.loads(x)
		return x
	except (urllib.request.URLError,ValueError):
		jsons={}
		jsons['title']="Invalid URL"
		jsons['datas']="Cannot abridge URL"
		jsons['keywords']="Invalids don't have KEYWORDS"
		x=json.dumps(jsons)
		print('--------------------------------------------------------------------------------------------------------------',x)
		obj = json.loads(x)
		return x

if __name__=="__main__":
	app.run(host='192.168.43.252',debug=True)