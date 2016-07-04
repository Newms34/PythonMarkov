import numpy as np 
import datetime
import sys
import random
import os
import re
from PIL import Image
mark_obj = {}
def markov_make(inp,splitter):
	#make a markov chain object
	global mark_obj
	if(len(mark_obj)<1):
		mark_obj = {}
	if type(inp) is str:
		#if our input is a string, split it
		if not (splitter==''):
			inp=inp.split(splitter)
		else:
			inp = inp.split()
	elif type(inp) is not list:
		raise TypeError('Input to markov object creator must be a string or list!')
		return
	for wrd in range (0,len(inp)-1):
		the_wrd = inp[wrd].lower()
		#word obj doesnt exist yet. Create it.
		if the_wrd not in mark_obj:
			mark_obj[the_wrd]={}
		# print(the_wrd,inp[wrd+1],inp[wrd+1] in mark_obj.get(the_wrd, {}).keys())
		if inp[wrd+1].lower() in mark_obj.get(the_wrd, {}).keys():
			#this follower already recorded. Increment freq
			mark_obj[the_wrd][inp[wrd+1].lower()]+=1
		else:
			#this follower not recorded. Set initial val = 1
			mark_obj[the_wrd][inp[wrd+1].lower()]=1
	

def gen_mark_str (obj,the_len):
	global group_size
	true_len = int(the_len/group_size)
	#take a markov obj (from above) and spit out a string 
	#note the default values in our fn above
	print('desired length:'+str(true_len))
	seed = random.choice(list(obj.keys()))
	if type(obj) is not dict:
		raise TypeError('Input to markov string generator must be a dict!')
		return
	end_str = ''
	good_bad = [0,0]
	for i in range(0,true_len):
		end_str+= ' '+seed
		prob_arr=[]
		#if the seed is not found, choose a random word instead.
		if seed not in obj:
			good_bad[1]+=1
			seed = random.choice(list(obj.keys()))
		else:
			good_bad[0]+=1
		seed_folls = obj.get(seed,{}).keys()
		for j in seed_folls:
			for k in range(0,obj[seed][j]):
				prob_arr.append(j)
		seed = random.choice(prob_arr)
	print('GOOD/BAD RATIO ([good,bad]):'+str(good_bad)+' FOR LEN: '+str(len(end_str))+str(end_str[0:200]))
	return end_str

def invert_im(im_name):
	#let's just see if we can invert an image!
	im = Image.open(im_name) #Can be many different formats.
	pix = im.load()
	print (im.size[0]) #Get the width and hight of the image for iterating over
	global w
	w = im.size[0]
	global h
	h = im.size[1]
	for i in range (0,w):
		for j in range(0,h):
			new_r = 255-pix[i,j][0]
			new_g = 255-pix[i,j][1]
			new_b = 255-pix[i,j][2] 
			pix[i,j] = (new_r,new_g,new_b) # Set the RGBA Value of the image (tuple)
	im.save('test2.jpg')

# invert_im('test.jpg')

def rediffy(im_name):
	#change the image to red, and only red
	im = Image.open(im_name) #Can be many different formats.
	pix = im.load()
	print (im.size[0]) #Get the width and hight of the image for iterating over
	global w
	w = im.size[0]
	global h
	h = im.size[1]
	for i in range (0,w):
		for j in range(0,h):
			brite_pic = 0
			if  pix[i,j][0] > pix[i,j][1] and pix[i,j][0] > pix[i,j][2]:
				brite_pic = pix[i,j][0]
			elif  pix[i,j][1] > pix[i,j][0] and pix[i,j][1] > pix[i,j][2]:
				brite_pic = pix[i,j][1]
			else: 
				brite_pic = pix[i,j][2]
			# first, get the brightest pic
			
			pix[i,j] = (brite_pic,0,0) # Set the RGBA Value of the image (tuple)
	im.save('test3.jpg')

def draw_mark_im(img_dat):
	img_dat_arr = img_dat.split(' ')
	#we now have an array of all the mark objs we made. we need to convert this into a list of rgb tuples
	im = Image.new('RGB',(w,h))
	pix = im.load()
	print('length:'+str(len(img_dat)))
	all_pxs = [] 
	print(img_dat_arr[4][0:len(img_dat_arr[4])-1].split('|'))
	#these loops should just de-code the img markov string to rgb tuples
	for i in range (0,len(img_dat_arr)-1):
		new_pxs = img_dat_arr[i][0:len(img_dat_arr[i])-1].split('|')
		for j in range(0,len(new_pxs)):
			rgb_lets = new_pxs[j].split('_')
			if(len(rgb_lets)>2):
				one_rgb = (int(rgb_lets[0]) or 0,int(rgb_lets[1]) or 0,int(rgb_lets[2]) or 0)
				all_pxs.append(one_rgb)
	# convert 'flat' list of pxls to rows
	dimmed_pic_arr = []
	for m in range(0,len(all_pxs),w):
		pic_row = all_pxs[m:m+w]
		dimmed_pic_arr.append(pic_row)
	# At this point, i'm basically logging out the pixel array to let me know that SOMETHING is happening()
	for o in range(0,len(dimmed_pic_arr)):
		for p in range(0,len(dimmed_pic_arr[o])):
			try:
				pix[o,p]=dimmed_pic_arr[o][p]
			except:
				print('img out of range at '+str(o)+','+str(p))
	im.save('mark1.jpg')


def prep_im(im_name,el_sz):
	#prepare image for feeding to the markov chain generator
	#el_sz is the number of pixels in each sample
	im_arr = []
	im_str = ''
	im = Image.open(im_name) #Can be many different formats.
	pix = im.load()
	global w
	w = im.size[0]
	global h
	h = im.size[1]
	print(w,h)
	#first, we need to convert the im to a 1-d array. 
	for x in range (0,w):
		for y in range(0,h):
			im_arr.append(pix[x,y])

	# print(im_arr)
	for i in range(0,len(im_arr),el_sz):
		new_el = '@'
		for k in range(0,el_sz):
			try:
				new_el+=str(int(im_arr[i+k][0]/10)*10)+'_'+str(int(im_arr[i+k][1]/10)*10)+'_'+str(int(im_arr[i+k][2]/10)*10)+'|'
			except:
				new_el+=''
		im_str+=new_el
	return im_str

files = os.listdir();
name = input("Tell me the base file name!")
group_size = int(input("How big should the groups be? Recommend btwn 3 and 9"))
picked_files = []
for n in range(0,len(files)):
	if (re.match(name+'\d{1,}\.jpg',files[n])):
		picked_files.append(files[n])
# got all files, run analyses on em all!
for q in range (0,len(picked_files)):
	im_data = prep_im(picked_files[q],group_size)
	markov_make(im_data,'@')
	print('Done with '+str(picked_files[q]))


# im_data = prep_im('dog1.jpg',group_size)
# markov_make(im_data,'@')
# print('Done with pic number 1')
# im_data = prep_im('dog3.jpg',group_size)
# markov_make(im_data,'@')
# print('Done with pic number 3')
# im_data = prep_im('dog4.jpg',group_size)
# markov_make(im_data,'@')
# print('Done with pic number group_size')
# im_data = prep_im('dog5.jpg',group_size)
# markov_make(im_data,'@')
# print('Done with pic number 5')
# im_data = prep_im('dog6.jpg',group_size)
# markov_make(im_data,'@')
# print('Done with pic number 6')
im_marky = gen_mark_str(mark_obj,w*h)
draw_mark_im(im_marky)


	