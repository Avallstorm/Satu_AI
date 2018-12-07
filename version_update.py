from src.AI_class import AI

data = "src/config.json"

Satu = AI(data)

message = ""
inc_t	= ""

api  = Satu.get_api()

Satu.version_update(message,inc_t,api)

