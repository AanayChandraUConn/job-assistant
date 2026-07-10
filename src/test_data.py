# just checking the json file loads correctly and looks right before building on top of it
import json

with open("src/my_data.json") as f:
    data = json.load(f)

print("skills categories:", list(data["skills"].keys()))
print("\nnumber of projects:", len(data["projects"]))
print("\nfirst project name:", data["projects"][0]["name"])

