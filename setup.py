import pickle

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

keys = [consumer_key,consumer_secret,access_token,access_token_secret]

rejects = [	"the strongest people aren't always the people who win, but the people who don't give up when they lose.",
				"",
				]

prefixes = ["the","my","how","ok","so","this","love","what","why","where","hehe","i","help","there's","today","good","wow","you","not","bad","did","say","but"]

prefixes = [pre + " " for pre in prefixes]

with open('keyfile', 'wb') as fp:
    pickle.dump(keys, fp)

with open('prefixes', 'wb') as fp:
    pickle.dump(prefixes, fp)

with open('rejects', 'wb') as fp:
	pickle.dump(rejects, fp)
