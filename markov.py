import numpy as np 
import datetime
import sys
import ast
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

#'murica
sample_text = "When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separate and equal station to which the Laws of Nature and of Nature's God entitle them, a decent respect to the opinions of mankind requires that they should declare the causes which impel them to the separation.We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.--That to secure these rights, Governments are instituted among Men, deriving their just powers from the consent of the governed, --That whenever any Form of Government becomes destructive of these ends, it is the Right of the People to alter or to abolish it, and to institute new Government, laying its foundation on such principles and organizing its powers in such form, as to them shall seem most likely to effect their Safety and Happiness. Prudence, indeed, will dictate that Governments long established should not be changed for light and transient causes; and accordingly all experience hath shewn, that mankind are more disposed to suffer, while evils are sufferable, than to right themselves by abolishing the forms to which they are accustomed. But when a long train of abuses and usurpations, pursuing invariably the same Object evinces a design to reduce them under absolute Despotism, it is their right, it is their duty, to throw off such Government, and to provide new Guards for their future security.--Such has been the patient sufferance of these Colonies; and such is now the necessity which constrains them to alter their former Systems of Government. The history of the present King of Great Britain is a history of repeated injuries and usurpations, all having in direct object the establishment of an absolute Tyranny over these States. To prove this, let Facts be submitted to a candid world.He has refused his Assent to Laws, the most wholesome and necessary for the public good.He has forbidden his Governors to pass Laws of immediate and pressing importance, unless suspended in their operation till his Assent should be obtained; and when so suspended, he has utterly neglected to attend to them.He has refused to pass other Laws for the accommodation of large districts of people, unless those people would relinquish the right of Representation in the Legislature, a right inestimable to them and formidable to tyrants only. He has called together legislative bodies at places unusual, uncomfortable, and distant from the depository of their public Records, for the sole purpose of fatiguing them into compliance with his measures. He has dissolved Representative Houses repeatedly, for opposing with manly firmness his invasions on the rights of the people.He has refused for a long time, after such dissolutions, to cause others to be elected; whereby the Legislative powers, incapable of Annihilation, have returned to the People at large for their exercise; the State remaining in the mean time exposed to all the dangers of invasion from without, and convulsions within.He has endeavoured to prevent the population of these States; for that purpose obstructing the Laws for Naturalization of Foreigners; refusing to pass others to encourage their migrations hither, and raising the conditions of new Appropriations of Lands.He has obstructed the Administration of Justice, by refusing his Assent to Laws for establishing Judiciary powers.He has made Judges dependent on his Will alone, for the tenure of their offices, and the amount and payment of their salaries.He has erected a multitude of New Offices, and sent hither swarms of Officers to harrass our people, and eat out their substance.He has kept among us, in times of peace, Standing Armies without the Consent of our legislatures.He has affected to render the Military independent of and superior to the Civil power.He has combined with others to subject us to a jurisdiction foreign to our constitution, and unacknowledged by our laws; giving his Assent to their Acts of pretended Legislation:For Quartering large bodies of armed troops among us:For protecting them, by a mock Trial, from punishment for any Murders which they should commit on the Inhabitants of these States:For cutting off our Trade with all parts of the world:For imposing Taxes on us without our Consent: For depriving us in many cases, of the benefits of Trial by Jury:For transporting us beyond Seas to be tried for pretended offencesFor abolishing the free System of English Laws in a neighbouring Province, establishing therein an Arbitrary government, and enlarging its Boundaries so as to render it at once an example and fit instrument for introducing the same absolute rule into these Colonies:For taking away our Charters, abolishing our most valuable Laws, and altering fundamentally the Forms of our Governments:For suspending our own Legislatures, and declaring themselves invested with power to legislate for us in all cases whatsoever.He has abdicated Government here, by declaring us out of his Protection and waging War against us.He has plundered our seas, ravaged our Coasts, burnt our towns, and destroyed the lives of our people.He is at this time transporting large Armies of foreign Mercenaries to compleat the works of death, desolation and tyranny, already begun with circumstances of Cruelty & perfidy scarcely paralleled in the most barbarous ages, and totally unworthy the Head of a civilized nation.He has constrained our fellow Citizens taken Captive on the high Seas to bear Arms against their Country, to become the executioners of their friends and Brethren, or to fall themselves by their Hands. He has excited domestic insurrections amongst us, and has endeavoured to bring on the inhabitants of our frontiers, the merciless Indian Savages, whose known rule of warfare, is an undistinguished destruction of all ages, sexes and conditions.In every stage of these Oppressions We have Petitioned for Redress in the most humble terms: Our repeated Petitions have been answered only by repeated injury. A Prince whose character is thus marked by every act which may define a Tyrant, is unfit to be the ruler of a free people.Nor have We been wanting in attentions to our Brittish brethren. We have warned them from time to time of attempts by their legislature to extend an unwarrantable jurisdiction over us. We have reminded them of the circumstances of our emigration and settlement here. We have appealed to their native justice and magnanimity, and we have conjured them by the ties of our common kindred to disavow these usurpations, which, would inevitably interrupt our connections and correspondence. They too have been deaf to the voice of justice and of consanguinity. We must, therefore, acquiesce in the necessity, which denounces our Separation, and hold them, as we hold the rest of mankind, Enemies in War, in Peace Friends.We, therefore, the Representatives of the united States of America, in General Congress, Assembled, appealing to the Supreme Judge of the world for the rectitude of our intentions, do, in the Name, and by Authority of the good People of these Colonies, solemnly publish and declare, That these United Colonies are, and of Right ought to be Free and Independent States; that they are Absolved from all Allegiance to the British Crown, and that all political connection between them and the State of Great Britain, is and ought to be totally dissolved; and that as Free and Independent States, they have full Power to levy War, conclude Peace, contract Alliances, establish Commerce, and to do all other Acts and Things which Independent States may of right do. And for the support of this Declaration, with a firm reliance on the protection of divine Providence, we mutually pledge to each other our Lives, our Fortunes and our sacred Honor."

def markov_make(inp):
	#make a markov chain object
	mark_obj = {}
	if type(inp) is str:
		#if our input is a string, split it
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
	return mark_obj

def gen_mark_str (obj,seed='the',the_len=100):
	#take a markov obj (from above) and spit out a string 
	#note the default values in our fn above
	if type(obj) is not dict:
		raise TypeError('Input to markov string generator must be a dict!')
		return
	end_str = ''
	good_bad = [0,0]
	for i in range(0,the_len):
		end_str+= ' '+seed
		prob_arr=[]
		#if the seed is not found, choose a random word instead.
		if seed not in obj:
			good_bad[1]+=1
			seed = random.choice(obj.keys())
		else:
			good_bad[0]+=1
		seed_folls = obj.get(seed,{}).keys()
		for j in seed_folls:
			for k in range(0,obj[seed][j]):
				prob_arr.append(j)
		seed = random.choice(prob_arr)
	print('GOOD/BAD RATIO ([good,bad]):'+str(good_bad))
	return end_str

def indp():
	print('------Markov Sample with Declaration of Independence------\n')
	print(cap_em(gen_mark_str(markov_make(sample_text),'of')))

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

def get_threds():
	print('------4chan Markov Experiment------\nNOTE: These posts are from an online forum, and as such\nare NOT censored. Use at your own risk!')
	which_thred = input("Please input the thread symbol (e.g., sci, g, or vg): ")
	thred_nums = json.loads(requests.get('https://a.4cdn.org/'+which_thred+'/threads.json').text)
	num_th = 0
	all_threads = []
	for q in thred_nums:
		num_th +=1
		for r in q['threads']:
			all_threads.append(r['no'])
	thred_base = 'https://a.4cdn.org/'+which_thred+'/thread/'
	# this has somthing to do with a concept called 'deferred' ('promises' in JS).
	# Put simply, it has to wait for ALL the approx. 150 or so responses to
	# return before it can continue. We basically create an array of http reqs
	# with the line below, and then say "wait till they all get back" with 
	# grequests.map(reqs)
	reqs = (grequests.get(thred_base+str(url)+'.json') for url in all_threads)
	rez = grequests.map(reqs)
	txt = ''
	for r in rez:
		try:
			coms = json.loads(r.text)['posts']
			for n in coms:
				try:
					txt+=n['com']
				except:
					txt+=''
		except: txt+=''
	# got all txt. Now clean it!
	clean_txt = clean(txt)
	no_html_txt  = strip_tags(clean_txt)
	no_quote_txt = reg.sub('&gt;&gt;\d{4,}|&gt;+|>>\d{4,}',' ',no_html_txt)
	go_ahead = input("Are you sure you want to continue? 'y' to continue!")
	if go_ahead == 'y':
		print('Beginning Markov Chain analysis!')
		print(gen_mark_str(markov_make(no_quote_txt)))
	else:
		print('Stopped!')

# get_threds()

def prep_shake():
	# shake_obj = json.loads(requests.get(os.path.join(sys.path[0], "will_play_text.json")).text)
	shake_obj = open('will_play_text.json').read()
	shake_dict = ast.literal_eval(shake_obj)
	all_shake = ''
	print(shake_dict[0])
	for t in range (0,len(shake_dict)):
		print('Adding line '+str(t)+' of '+str(len(shake_dict))+ '('+str(int(100*t/len(shake_dict)))+'%)')
		all_shake+=shake_dict[t]['text_entry']+' '
	shake_mark = markov_make(all_shake)
	rand_shake = gen_mark_str(shake_mark);
	#now capitalize for easier reading
	

	rand_shake = cap_em(rand_shake)
	print(rand_shake)

def cap_em(txt):
	puncs = ['.','!','?']
	str_len = len(txt)
	txt_arr=list(txt)
	for p in range(0,len(puncs)):
		index = 0
		found_arr = []
		#find all instances of this punctuation
		while index < str_len:
			index = txt.find(puncs[p], index)
			if index == -1:
				break
			found_arr.append(index)
			index += 1
		for c in range (0,len(found_arr)):
			if str_len-2 > int(found_arr[c]):
				if txt_arr[found_arr[c]+1] == " ":
					txt_arr[found_arr[c]+2] =  str(txt_arr[found_arr[c]+2]).upper()
				else: 
					txt_arr[found_arr[c]+1] =  str(txt_arr[found_arr[c]+1]).upper()
	return "".join(txt_arr)

def choice_me():
	print('Which text source do you wanna use? Enter the corresponding number:\n----------------------------------------------------\n1: Declaration of Independence\n2: 4chan post data\n3: The works of William Shakespeare\nx: Cancel')
	chc = input("Choice: ")
	while chc is not "1" and chc is not "2" and chc is not "3" and chc is not "x":
		print(chc)
		print("Invalid choice!\n1: Declaration of Independence\n2: 4chan post data\n3: The works of William Shakespeare\nx: Cancel'")
		chc = input("Choice: ")
	if chc == "1":
		indp()
	elif chc == "2":
		get_threds()
	elif chc == "3":
		prep_shake()
	elif chc == "x":
		print("Okay, bye!")
	else:
		print("Something went wrong!")
	print('----------------------------------------------------')
	rep = input("Again?\n1: Yes\n2: No\nChoice: ")
	if rep == "1":
		choice_me()

choice_me()