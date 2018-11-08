from AI_class import AI

data = "config.json"

Satu = AI(data)

api  = Satu.get_api()

Satu.like_replies(api)

