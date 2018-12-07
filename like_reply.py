from src.AI_class import AI

data = "src/config.json"

Satu = AI(data)

api  = Satu.get_api()

Satu.like_replies(api)

