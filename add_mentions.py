from AI_class import AI

data = "config.json"

Satu = AI(data)

api  = Satu.get_api()

Satu.get_interacts(api,2000)

Satu.recommend_followers(api,2)