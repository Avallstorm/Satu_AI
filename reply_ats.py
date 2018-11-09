from AI_class import AI

data = "config.json"

Satu = AI(data)

api  = Satu.get_api()

Satu.reply_to_ats(api)
