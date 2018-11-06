from AI_class import AI

model   = "models/model_0_2/Satu_0_2_weights.hdf5"
config  = "models/model_0_2/Satu_0_2_config.json"
vocab   = "models/model_0_2/Satu_0_2_vocab.json"
keys    = "keyfile"
rejects = "rejects"
prefs   = "prefixes"
queue   = "queue"

Satu = AI(model,config,vocab,keys,rejects,prefs,queue)
api  = Satu.get_api()

Satu.like_replies(api)

