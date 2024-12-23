import tomllib
from pprint import pprint

with open("config.toml", mode="rb") as config_toml:
    config = tomllib.load(config_toml)


# pprint(config)
