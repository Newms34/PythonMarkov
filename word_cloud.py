import numpy as np 
import datetime
import sys
import random
import requests
import json
import grequests
from html.parser import HTMLParser
import string
import re as reg 

#some of 4chan's text input is not 'clean'. No, I dont mean it's not fit for children (tho it isnt).
#I mean some of the unicode chars are non-standard, which makes python unhappy.
clean = lambda dirty: ''.join(filter(string.printable.__contains__, dirty))

class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.strict = False
		self.convert_charrefs= True
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)

def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()
com_wrds=['the','be','to','of','and','a','in','that','have','i','it','for','not','on','with','he','as','you','do','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like','time','no','just','him','know','take','people','into','year','your','good','some','could','them','see','other','than','then','now','look','only','come','its','over','think','also','back','after','use','two','how','our','work','first','well','way','even','new','want','because','any','these','give','day','most','us','is','was','are']
def search(arr,name):
	for p in range(0,len(arr)):
		if arr[p]['name'] == name:
			return p
	return None

def draw_graf(arr,e):
	e= int(e)
	if e > len(arr):
		e=len(arr)
	for n in range (0,e):
		displ = (40 - len(arr[n]['name'])) if (40 - len(arr[n]['name']))>0 else 0
		displ_str = " "*int(displ)
		print('Word: '+str(arr[n]['name'])+displ_str+'| Frequency: '+str(arr[n]['count']))

def count_words(txt):
	txt_arr = txt.split(' ')
	word_names = []
	max_count = 0
	print('Counting words!')
	for t in range(0,len(txt_arr)):
		if txt_arr[t] not in com_wrds and txt_arr[t] is not '':
			already_there = search(word_names,txt_arr[t])
			if not already_there:
				#word not yet recorded
				word_names.append({'name':txt_arr[t],'count':1})
			else:
				word_names[already_there]['count']+=1
			print('Doing word '+str(t)+' of '+str(len(txt_arr))+'('+str(int(100*t/len(txt_arr)))+'%)')
	final_list = sorted(word_names, key=lambda k: k['count'],reverse=True)
	end = input("There are "+str(len(final_list))+" different words in this sample. How many do you wanna include? (rec: 10-50)")
	draw_graf(final_list,end)

def exception_handler(req,ex):
	print('There seems to be something wrong with either this script or 4chan. Probly this script tbh fam')
	print('The request: '+str(req)+' failed with exception '+str(ex))

def get_threds():
	#get the threds of a particular board
	print('------4chan Word Frequency Experiment------\nNOTE: These posts are from an online forum, and as such\nare NOT censored. Use at your own risk!\n---What This Is---\nThis script counts the number of occurances of any particular\nword in a board on 4chan, and returns a descending list\nof those word frequencies. It currently ignores some\n(but not all!) common words.')
	which_thred = input("Please input the thread symbol (e.g., sci, g, or vg): ")
	thred_nums = json.loads(requests.get('https://a.4cdn.org/'+which_thred+'/threads.json').text)
	num_th = 0
	all_threads = []
	for q in thred_nums:
		num_th +=1
		for r in q['threads']:
			all_threads.append(r['no'])
	thred_base = 'https://a.4cdn.org/'+which_thred+'/thread/'
	print(str(all_threads))
	# this has somthing to do with a concept called 'deferred' ('promises' in JS).
	# Put simply, it has to wait for ALL the approx. 150 or so responses to
	# return before it can continue. We basically create an array of http reqs
	# with the line below, and then say "wait till they all get back" with 
	# grequests.map(reqs)
	reqs = (grequests.get(thred_base+str(url)+'.json',timeout=10) for url in all_threads)
	rez = grequests.imap(reqs,exception_handler=exception_handler)
	txt = ''
	thred_count = 0
	print('Beginning thread concatenization')
	for r in rez:
		thred_count += 1
		try:
			coms = json.loads(r.text)['posts']
			for n in coms:
				try:
					txt+=n['com']
				except:
					txt+=''
		except: 
			txt+=''
		print('Done thread #'+str(thred_count))
	# got all txt. Now clean it!
	clean_txt = clean(txt) #clean the text to remove unprintable chars
	no_html_txt  = strip_tags(clean_txt) #remove HTML tags, since those are not part of the posted data
	no_link_txt = reg.sub(r'^https?:\/\/.*[\r\n]*', '', no_html_txt)#remove links (mostly)
	no_quote_txt = reg.sub('&gt;&gt;\d{4,}|&gt;+|>>\d{4,}',' ',no_link_txt) #remove 4chan 'quotes', such as >>blahblah
	unwanted_symbs = [">","&gt;","[^a-zA-Z0-9']"]
	for q in range(0,len(unwanted_symbs)):
		no_quote_txt = reg.sub(unwanted_symbs[q],' ',no_quote_txt) 
	count_words(no_quote_txt.lower())

get_threds()

