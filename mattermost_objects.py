from typing import Dict, List, NamedTuple


class MMUser(NamedTuple):
    id: str
    create_at: int
    update_at: int
    delete_at: int
    username: str
    first_name: str
    last_name: str
    nickname: str
    email: str
    auth_data: str
    auth_service: str
    roles: str
    locale: str
    timezone: dict
    position: any

    is_bot: bool = None
    bot_description: str = None
    email_verified: bool = None
    notify_props: dict = None
    last_password_update: int = None
    failed_attempts: int = None
    mfa_active: bool = False
    terms_of_service_id: str = None
    terms_of_service_create_at: int = None
    props: dict = {}
    last_picture_update: int = None

    @staticmethod
    def load(data):
        try:
            return MMUser(**data)
        except TypeError as e:
            print("[ERROR] Could not load dict into MMUser namedtuple")
            print(str(e))


class MMPostProps(NamedTuple):
    from_webhook: str = False
    override_icon_url: str = None
    override_username: str = None
    webhook_display_name: str = None

    channel_mentions: Dict = None
    matterircd_krcggydky38kdcuubsc7fddc7w: str = None
    matterircd_s4ptwhx7wfnx7qwexp1khorh7e: str = None
    username: str = None
    userId: str = None
    old_header: str = None
    new_header: str = None
    old_purpose: str = None
    new_purpose: str = None
    old_displayname: str = None
    new_displayname: str = None
    remove_link_preview: str = None
    removedUserId: str = None
    addedUserId: str = None
    removedUsername: str = None
    addedUsername: str = None
    message: str = None
    attachments: str = None
    from_bot: str = False
    disable_group_highlight: str = None


class MMPost(NamedTuple):
    channel_id: str
    create_at: int
    delete_at: int
    edit_at: int
    hashtags: str
    id: str
    is_pinned: bool
    message: str
    metadata: Dict
    original_id: str
    pending_post_id: str
    root_id: str
    type: str
    update_at: int
    user_id: str
    parent_id: str = None
    message_source: str = None
    has_reactions: bool = None
    file_ids: List[str] = None
    props: MMPostProps = None
    reply_count: int = None
    last_reply_at: str = None
    participants: any = None

    def from_human(self):
        return self.props is None or (
            self.props.from_webhook is False and self.props.from_bot is False
        )

    @staticmethod
    def load(data):
        try:
            props = None
            if "props" in data:
                try:
                    props: MMPostProps = MMPostProps(**data["props"])
                except TypeError as e:
                    print("[ERROR] Could not load dict into MMPostProps namedtuple")
                    print(str(e))
            del data["props"]
            return MMPost(props=props, **data)
        except TypeError as e:
            print("[ERROR] Could not load dict into MMPost namedtuple")
            print(str(e))


class MMChannelPosts(NamedTuple):
    prev_post_id: str
    next_post_id: str
    order: List[str]
    posts: Dict[str, MMPost]
    has_next: any
    first_inaccessible_post_time: any
    reply_count: any = None
    disable_group_highlight: any = None

    @staticmethod
    def load(data):
        try:
            posts: Dict[str, MMPost] = {
                k: MMPost.load(v) for (k, v) in data["posts"].items()
            }
            del data["posts"]
            return MMChannelPosts(posts=posts, **data)
        except TypeError as e:
            print("[ERROR] Could not load dict into MMUser namedtuple")
            print(str(e))
