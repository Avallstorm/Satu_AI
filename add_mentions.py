from src.AI_class import AI

data = "src/config.json"

Satu = AI(data, only_weights=True)

api  = Satu.get_api()

Satu.get_interacts(api,12)

Satu.recommend_followers(api,2)