import mattermostdriver.exceptions

import mattermost_client
from config import config
from mattermost_client import ChannelApi, MMApi


def send_message(file_info, message):
    channel_id = file_info["originating_mm_post_channel_id"]
    post_id = file_info["originating_mm_post_id"]

    # TODO Comment below line, this is for testing purposes
    # channel_id = MMApi().get_channel_id("bestuur-dev")
    channel = ChannelApi(
        channel_id=channel_id,
        user=mattermost_client.users[config["mattermost"]["selected_user"]],
    )

    try:
        channel.create_threaded_post(
            post_id,
            f"{message}",
        )
    except mattermostdriver.exceptions.InvalidOrMissingParameters as e:
        # This will occur when we try to react to a file in a channel that is not the same as the originating channel.
        unique_post_url = f"{config['mattermost']['server_url']}/pl/{post_id}"
        channel.create_post(
            f"{unique_post_url}\n\n{message}",
        )


def report_newly_found_file(file_info):
    git_url = f"https://{config['gitea']['server_url']}/{config['gitea']['remote_org']}/{config['gitea']['remote_repo']}"
    message = f"I found a new CodiMD file in this post! Making work of putting it on git :)\n - Requested location in the [drive]({git_url}): {file_info['metadata']['sync-to']}"
    send_message(file_info, message)


def report_newly_found_but_invalid_file(file_info):
    message = """Hi there! :wave: 
I'm your friendly neighbourhood document sync bot.
I could synchronize this CodiMD file automatically to our Git DRIVE for safekeeping, but the necessary metadata block is not present.
You can easily add the correct info and I will do the rest of the work for you!

Just add the following lines to your file, the location in your file is not important but at the top would be my recommendation.

```
:::spoiler git drive sync
- sync-to: <a valid path on the DRIVE, for ex.: verslagen/21-22/2022-05-13.md>
:::
```"""
    send_message(file_info, message)


send_message(
    {
        "originating_mm_post_channel_id": "dm1abp4wfidezmig1yqyu53mmy",
        "originating_mm_post_id": "dm1abp4wfidezmig1yqyu53mmy"
    },
    "this is a test message"
)
