from src.AI_class import AI

data = "src/config.json"

Satu = AI(data)

api  = Satu.get_api()

Satu.like_followers_posts(api,1)
