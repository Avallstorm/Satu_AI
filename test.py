from src.AI_class import AI

data = "src/config.json"

Satu = AI(data, only_weights=True)

print(Satu.name)
print(Satu.screen_name)

print(Satu.version)
print(Satu.model)

print(Satu.prefixes)
