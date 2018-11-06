import warnings
warnings.filterwarnings("ignore")

import tweepy
import pickle
import datetime

from textgenrnn import textgenrnn
from gingerit.gingerit import GingerIt
from fuzzywuzzy import fuzz

class AI(object):
	#A class to define a RNN trained twitter bot with useful functions for interacting with twitter

	#Attributed 

	#Version code comprising of [int,int,int] for major, model, minor updates
	version = []

	#Model, Config, Vocab files from tweet-generator trained RNN
	model = ""
	config = ""
	vocab = ""

	#Keys needed to interact with twitter account
	consumer_key = ""
	consumer_secret = ""
	access_token = ""
	access_token_secret = ""

	#File locations for various important strings
	key_loc = ""

	#Previous tweets made by this bot
	prev_tweets = []

	#Rejected tweets made by this bot
	rej_tweet_loc = ""
	rej_tweets = []

	#List of possible prefixes for tweets
	pref_loc = ""
	pref = []

	#List of queued tweets
	queue_loc = ""
	queue = []

	def __init__(self,model_loc,config_loc,vocab_loc,key_loc,rej_tweets_loc,pref_loc,queue_loc):
		#Return an AI object using the provided files (fails if not proper files)
		self.model = model_loc
		self.config = config_loc
		self.vocab = vocab_loc
		self.key_loc = key_loc
		self.rej_tweets_loc = rej_tweets_loc
		self.pref_loc = pref_loc
		self.queue_loc = queue_loc
		self.get_keys()
		self.get_data(self.get_api())



	def tweet_from_queue(self,api):
		#Tweet out from queue if tweets exist
		if len(self.queue) > 0:
			tweet = self.queue.pop(0)
			try:
				api.update_status(tweet)
				self.save_current_queue()
			except Exception as e:
				print("==================== {} ====================".format(e))
		else:
			print("No elements in queue")



	def get_keys(self):
		#Get various twitter keys from given will formatted file
		with open(self.key_loc, "rb") as fp:
			itemlist = pickle.load(fp)
			self.consumer_key = itemlist[0]
			self.consumer_secret = itemlist[1]
			self.access_token = itemlist[2]
			self.access_token_secret = itemlist[3]



	def get_data(self,api):
		#Get current version from twitter bio, get previous tweets from twitter, get rejected tweets from file

		bio = api.get_user("Satu_AI").description
		self.version = [int(bio[-5:][0]),int(bio[-5:][2]),int(bio[-5:][4])]

		public_tweets_all = tweepy.Cursor(api.user_timeline).items()
		self.prev_tweets = [tweet.text for tweet in public_tweets_all]

		with open (self.rej_tweets_loc, 'rb') as fp:
			self.rej_tweets = pickle.load(fp)

		with open (self.pref_loc, 'rb') as fp:
			self.pref = pickle.load(fp)

		with open (self.queue_loc, 'rb') as fp:
			self.queue = pickle.load(fp)



	def gen_talk(self,temp,pre,num,as_list=True):
		#Generate tweets from model using the provided parameters
		AI_core = textgenrnn(weights_path=self.model,vocab_path=self.vocab,config_path=self.config)
		return AI_core.generate(prefix=pre,n=num,temperature=temp,return_as_list=as_list)



	def easy_talk(self,ind):
		#Generate tweets from model using default parameters and filtering through all filters
		count = 0
		prefix = self.pref[(ind%len(self.pref))]
		while True:
			count = count + 1

			if count%10 == 0:
				print("Count reached multiple of 10 attempts, current attempts number: {}".format(count))
				pass

			if count%100 == 0:
				print("Could not produce tweet with given prefix: {}".format(prefix))
				raise Exception

			pos_list = self.gen_talk(0.2,prefix,5)

			for tweet in pos_list:
				try:
					if self.tweet_filters(tweet):
						return tweet
				except Exception as e:
					print("==================== {} ====================".format(e))
					pass



	def version_update(self, message, inc_type, api):
		#Update version in bio and make update tweet based on provided message and increment class

		if inc_type == "Major":
			self.version[0] += self.version[0]
		elif inc_type == "Model":
			self.version[1] += self.version[1]
		elif inc_type == "Minor":
			self.version[2] += self.version[2]
		else:
			print("Error no correct increment type given")
			raise Exception # Define proper exceptions later

		bio = "Please go easy on me, I'm still in alpha Version {}.{}.{}".format(self.version[0],self.version[1],self.version[2])

		status = 'Update! Current version is {}.{}.{}! \n"{}"'.format(self.version[0],self.version[1],self.version[2],message)

		if len(status) < 180:
			api.update_profile(description=bio)
			print("updated bio")
			api.update_status(status)
			print("tweeted version number")
		else:
			print("Status too long")
			raise Exception



	def like_replies(self,api):
		#Like replies to tweets the bot has made in the last _ amount of time
		now_7 = datetime.datetime.now() - datetime.timedelta(hours=7)

		public_tweets = tweepy.Cursor(api.user_timeline).items()
		for tweet in public_tweets:
			if tweet.created_at > now_7:
				replies = self.__get_replies(tweet,api)
				for reply in replies:
					try:
						api.create_favorite(reply.id)
						print("Liked Tweet: {}".format(reply.text))
					except Exception as e:
						print("==================== {} ====================".format(e))
						pass



	def reply_to_ats(self,api):
		#Reply to people who @ satu

		now_7 = datetime.datetime.now() - datetime.timedelta(hours=7)

		searchquery = "@Satu_AI"
		retweet_filter='-filter:retweets'
		q=searchquery+retweet_filter

		new_tweets = api.search(q=searchQuery, count=tweetsPerQry)

		for tweet in new_tweets:
			print(tweet.text)

		"""for at_tweet in new_tweets:
			if at_tweet.created_at > now_7:
				if len(self.queue) > 1:
				tweet = self.queue.pop(0)
				api.update_status(tweet, in_reply_to_status_id = at_tweet.id_str)
				self.save_current_queue()"""



	def save_rej_tweets(self,new_rejs):
		#Save rejected tweets by adding new rejected tweets to old list
		self.rej_tweets += new_rejs
		with open(self.rej_tweet_loc, 'wb') as fp:
			pickle.dump(self.rej_tweets, fp)



	def save_queue_tweets(self,new_queues):
		#Save new tweets to tweet queue
		self.queue += new_queues
		with open(self.queue_loc, 'wb') as fp:
			pickle.dump(self.queue, fp)



	def save_current_queue(self):
		#Save current queue to file
		with open(self.queue_loc, 'wb') as fp:
			pickle.dump(self.queue, fp)



	def tweet_filters(self,tweet):
		#Boolean filter for outputs from generated tweets
                parser = GingerIt()
                grammatical = False
                
                while tweet[-1] == "'":
                    tweet = tweet[:-1]

		try:
			parsed = parser.parse(tweet)
			if "corrections" in parsed:
				grammatical = (len(parser.parse(tweet)["corrections"]) < 2)
                                
		except Exception as e:
			pass

		lenght = (len(tweet) < 160)
		is_new = (not self.is_prev(tweet))
		is_acceptable = (not self.is_bad(tweet))

		return (grammatical and lenght and is_new and is_acceptable)



	def is_prev(self,tweet):
		#Boolean filter for checking if tweet is similar to a previous tweet
		for pre_tweet in self.prev_tweets:
			if (fuzz.ratio(pre_tweet,tweet) > 80):
				return True
		return False



	def is_bad(self,tweet):
		#Boolean filter for checkout if a tweet
		for bad_tweet in self.rej_tweets:
			if (fuzz.ratio(bad_tweet,tweet) > 80):
				return True
		return False



	def __get_replies(self,tweet,api):
		#Gets all replies to tweets
		replies=[]
		user = tweet.user.screen_name
		tweet_id = tweet.id_str
		max_id = None
		for reply in tweepy.Cursor(api.search,q='to:{}'.format(user), since_id=992433028155654144, result_type='recent',timeout=999999).items(1000):
			if hasattr(reply, 'in_reply_to_status_id_str') and reply.in_reply_to_status_id_str == tweet_id:
				replies.append(reply)
		return replies



	def get_api(self):
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		return tweepy.API(auth)




