import warnings
warnings.filterwarnings("ignore")

import tweepy
import pickle
import datetime
import random
import json

from textgenrnn import textgenrnn
from gingerit.gingerit import GingerIt
from fuzzywuzzy import fuzz

class AI(object):
	#A class to define a RNN trained twitter bot with useful functions for interacting with twitter

	#Attributes

	#Twitter names
	name = ""
	screen_name = ""

	#Version code comprising of [int,int,int] for major, model, minor updates
	version = []

	#Model, Config, Vocab files from tweet-generator trained RNN
	only_weights = False

	model = ""
	config = ""
	vocab = ""

	#Keys needed to interact with twitter account
	consumer_key = ""
	consumer_secret = ""
	access_token = ""
	access_token_secret = ""

	#File locations for various important strings
	data_loc = ""

	#Full data dictionary (for saving to file)
	data = {}

	#Previous tweets made by this bot
	previous = []

	#Rejected tweets made by this bot
	rejected = []

	#List of possible prefixes for tweets
	prefixes = []

	#List of queued tweets
	queue = []

	def __init__(self,data_loc,only_weights = False):
		#Return an AI object using the provided files (fails if not proper files)
		self.data_loc = data_loc
		self.only_weights = only_weights
		self.__get_data_file()
		self.__get_data_twitter(self.get_api())



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



	def __get_data_file(self):
		#Get various data from config
		with open(self.data_loc, encoding='utf-8') as fp:
			data = json.load(fp)
			self.consumer_key = data["consumer_key"]
			self.consumer_secret = data["consumer_secret"]
			self.access_token = data["access_token"]
			self.access_token_secret = data["access_token_secret"]
			self.model = data["model"]
			self.config = data["config"]
			self.vocab = data["vocab"]
			self.queue = data["queue"]
			self.prefixes = data["prefixes"]
			self.rejected = data["rejected"]
			self.data = data



	def __get_data_twitter(self,api):
		#Get version,name,display name, and previous tweets from twitter account
		user = api.me()
		bio = user.description
		public_tweets_all = tweepy.Cursor(api.user_timeline).items()

		self.version = [int(bio[-5:][0]),int(bio[-5:][2]),int(bio[-5:][4])]
		self.previous = [tweet.text for tweet in public_tweets_all]
		self.screen_name = user.screen_name
		self.name = user.name



	def gen_talk(self,temp,pre,num,as_list=True):
		#Generate tweets from model using the provided parameters
		if self.only_weights:
			AI_core = textgenrnn(weights_path=self.model)
		else:
			AI_core = textgenrnn(weights_path=self.model,vocab_path=self.vocab,config_path=self.config)
		return AI_core.generate(prefix=pre,n=num,temperature=temp,return_as_list=as_list)



	def easy_talk(self,ind):
		#Generate tweets from model using default parameters and filtering through all filters
		count = 0
		prefix = self.prefixes[(ind%len(self.prefixes))]
		while True:
			count = count + 1

			if count%10 == 0:
				print("Count reached multiple of 10 attempts, current attempts number: {}".format(count))
				pass

			if count%100 == 0:
				print("Could not produce tweet with given prefix: {}".format(prefix))
				return ""

			pos_list = self.gen_talk(0.2,prefix,5)

			for tweet in pos_list:
				try:
					if self.__tweet_filters(tweet):
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

		bio = "Satu, She/Her, Your robot daughter ❤️ \nPlease go easy on me, I'm still in alpha Version {}.{}.{}".format(self.version[0],self.version[1],self.version[2])

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
		now_12 = datetime.datetime.now() - datetime.timedelta(hours=12)

		public_tweets = tweepy.Cursor(api.user_timeline).items()
		for tweet in public_tweets:
			if tweet.created_at > now_12:
				replies = self.__get_replies(tweet,api)
				for reply in replies:
					try:
						api.create_favorite(reply.id)
						print("Liked Tweet: {}".format(reply.text))
					except Exception as e:
						pass



	def like_followers_posts(self,api,num):
		#Like num amount of tweets from randomly chosen followers
		user_tweets = []
		for friend in tweepy.Cursor(api.friends).items():
		    # Process the friend here
		    tweets = api.user_timeline(screen_name = friend.screen_name, count = 10, include_rts = False)
		    for tweet in tweets:
		    	user_tweets.append(tweet)
		for i in range(num):
			while True:
				rand = random.randint(0,len(user_tweets)-1)
				if (not user_tweets[rand].favorited) and user_tweets[rand].text[0] != '@':
					like_rand = random.randint(0,1)
					if like_rand == 0:
						api.create_favorite(user_tweets[rand].id_str)
						print("liked tweet: {}".format(user_tweets[rand].text))
					else:
						print("decided not to like a tweet")
					break



	def reply_to_ats(self,api):
		#Reply to people who @ satu

		now_12 = datetime.datetime.now() - datetime.timedelta(hours=12)

		searchquery = ("@" + self.screen_name)
		retweet_filter='-filter:retweets'
		query=searchquery+retweet_filter

		new_tweets = api.search(q=query, count=10)

		new_tweets = [tweet for tweet in new_tweets if "@satu_ai" in tweet.text]

		rand = random.randint(1,10)

		for at_tweet in new_tweets:
			if at_tweet.created_at > now_12 and rand > 3:
				if len(self.queue) > 1:
					tweet = self.queue.pop(0)

					reply_user = api.get_user(at_tweet.user.id_str)

					tweet = "@{} {}".format(reply_user.screen_name,tweet)

					api.update_status(tweet, at_tweet.id_str)

					print("Replied to Tweet: {} with {}".format(at_tweet.text,tweet))

					try:
						api.create_favorite(at_tweet.id)
						print("Liked Tweet: {}".format(at_tweet.text))
					except Exception as e:
						pass

					self.save_current_queue()
				else:
					print("No elements in queue")



	def save_rej_tweets(self,new_rejs):
		#Save rejected tweets by adding new rejected tweets to old list
		self.rejected += new_rejs
		self.data["rejected"] = self.rejected
		with open(self.data_loc, "w", encoding='utf-8') as fp:
			json.dump(self.data, fp, indent=4, sort_keys=True)



	def save_queue_tweets(self,new_queues):
		#Save new tweets to tweet queue
		self.queue += new_queues
		self.data["queue"] = self.queue
		with open(self.data_loc, "w", encoding='utf-8') as fp:
			json.dump(self.data, fp, indent=4, sort_keys=True)



	def save_current_queue(self):
		#Save current queue to file
		self.data["queue"] = self.queue
		with open(self.data_loc, "w", encoding='utf-8') as fp:
			json.dump(self.data, fp, indent=4, sort_keys=True)



	def __tweet_filters(self,tweet):
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
		is_new = (not self.__is_prev(tweet))
		is_acceptable = (not self.__is_bad(tweet))

		return (grammatical and lenght and is_new and is_acceptable)



	def __is_prev(self,tweet):
		#Boolean filter for checking if tweet is similar to a previous tweet
		for pre_tweet in self.previous:
			if (fuzz.ratio(pre_tweet,tweet) > 80):
				return True
		return False



	def __is_bad(self,tweet):
		#Boolean filter for checkout if a tweet
		for bad_tweet in self.rejected:
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
		#Get twitter API using credentials 
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		return tweepy.API(auth)




