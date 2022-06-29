import json
from paper import Paper


# _json = {
#     "layout-sizes": {
#         "A4": {"size": "A4", "width": 210, "height": 297},
#         "A3": {"size": "A3", "width": 297, "height": 420},
#         "Rolo": {"size": "Rolo", "width": 914, "height": 2000},
#     }
# }

# with open("config.json", "w") as f:
#     json.dump(papers, f, sort_keys=True, indent=4)

config = json.load(open("config.json", "r"))
layout_sizes = [{k: v} for k, v in config["layout-sizes"].items()]
layouts = config["layout-sizes"]

print(layout_sizes)
print(layouts)


# for k, v in _json.items():
#     print(_json[k])
#     for i, j in _json[k].items():
#         print(i, j)
