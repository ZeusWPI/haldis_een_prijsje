#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint as pp
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict
from config import config

from colored import Style
from mattermostdriver import Driver

from mattermost_objects import MMChannelPosts
from utils import timer

pp = pp.PrettyPrinter(indent=2)


class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"


class User(ABC):
    @abstractmethod
    def credentials_dict(self) -> dict:
        pass

class TokenUser(User):
    def __init__(self, token):
        self.token = token

    def credentials_dict(self) -> dict:
        return {"token": self.token}

    def __repr__(self):
        return "TokenUser<token: {}>".format(self.token)


users: {str: [User]} = {}


def loadusers():
    usr = None
    for name, data in config["mattermost"]["users"].items():
        if "token" in data:
            usr = TokenUser(token=data["token"])
        else:
            print("Invalid user '{}' in toml file".format(name))
            exit(1)
        users[name] = usr


loadusers()


def merge_dict(a: dict, b: dict) -> dict:
    return {**a, **b}


class MMApi(Driver):
    def __init__(self, user: User = users["tyboro"]):
        print(f"Initializing MMApi client for user {user}")
        Driver.__init__(
            self,
            merge_dict(
                {
                    "url": "mattermost.zeus.gent",
                    "port": 443,
                    "debug": False,
                },
                user.credentials_dict(),
            ),
        )
        self.login()
        self.user_id = self.users.get_user(user_id="me")["id"]
        self.team_id = self.teams.get_team_by_name("zeus")["id"]
        print(" = Creating mattermost client")
        print(f" =  - User: {self.user_id}")
        print(f" =  - Team: {self.team_id}")

    @staticmethod
    def print_response(resp, title="Response"):
        print("--------")
        print(Style.BOLD + title + Style.RESET)
        pp.pprint(resp)

    def log(self, text: str, log_level: LogLevel = LogLevel.INFO):
        print(f"{Style.BOLD}[{log_level.value}]{Style.RESET} {text}")

    def get_channel_id(self, channel_name):
        resp = self.channels.get_channel_by_name(self.team_id, channel_name)
        id = resp["id"]
        self.log(f"Fetching channel id for {channel_name}: {id}")
        return id

    @timer
    def get_posts_for_channel(self, channel_id, since):
        print(f"Fetching posts for {channel_id} since {since}")
        page_size = 200
        page_i = 0
        data = {}
        more = True
        while more:
            resp = self.posts.get_posts_for_channel(
                channel_id,
                params={"page": page_i, "per_page": page_size, "since": since},
            )
            page_i += 1
            print(f"Fetching page {page_i}")
            # print("-", end=" ")

            paged_data = resp["posts"]
            paged_count = len(paged_data)

            if since != 0:
                # The mattermost api is absolutely retarted
                # If you add the since parameter and it's different then 0 it will give you 1000 posts max.
                # It will not respect you page_index or page_size.
                more = False
            else:
                if paged_count < page_size:
                    more = False

            # Transform the data into something more sensible or practical
            if type(paged_data) is list:
                paged_data = {item["id"]: item for item in paged_data}

            # Append the paged_data to our global data variable
            data = {**data, **paged_data}
        print()

        self.log(f"Post count: {len(data)}")
        return data


class ChannelApi(MMApi):
    def __init__(self, channel_name=None, channel_id=None, user=None):
        MMApi.__init__(self, user)
        assert channel_name is not None or channel_id != None

        if channel_name is not None:
            self.channel_id = self.get_channel_id(channel_name)
        if channel_id is not None:
            self.channel_id = channel_id

    def create_post(self, message: str, props: Dict = None) -> None:
        resp = self.posts.create_post(
            options={"channel_id": self.channel_id, "message": message, "props": props}
        )
        self.log(f'Message successfully created: "{message}"')

    def create_threaded_post(
        self, post_id: str, message: str, props: Dict = None
    ) -> None:
        resp = self.posts.create_post(
            options={
                "channel_id": self.channel_id,
                "message": message,
                "root_id": post_id,
                "props": props,
            }
        )
        self.log(f'Message successfully created: "{message}"')
        # print_response("Create post", resp)


if __name__ == "__main__":
    foo = MMApi(user=users["flynn"])

    # all_posts = foo.get_all_posts()

    channel = foo.channels.get_channel_by_name(
        foo.team_id,
        "bestuur",
    )
    channel_id = channel["id"]
    resp = foo.posts.get_posts_for_channel(channel_id, params={"per_page": 200})
    channel_posts: MMChannelPosts = MMChannelPosts.load(resp)
