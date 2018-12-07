from src.AI_class import AI

data = "src/config.json"

Satu = AI(data,only_weights=True)

for i in range(100):
	print(Satu.easy_talk(i))
