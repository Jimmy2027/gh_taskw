


def get_url(notification_dict):
    url = ""
    if (
        "subject" in notification_dict
        and isinstance(notification_dict["subject"], dict)
        and "url" in notification_dict["subject"]
    ):
        url = notification_dict["subject"]["url"]
    elif "url" in notification_dict:
        url = notification_dict["url"]

    if url:
        url = (
            url.replace("api.", "").replace("/repos/", "/").replace("/pulls/", "/pull/")
        )
    return url


def get_reason(notification_dict):
    return notification_dict["reason"]


def get_subject(notification_dict):
    return notification_dict["subject"]["title"]


def get_repository(notification_dict):
    return notification_dict["repository"]["name"]


def get_owner(notification_dict):
    return notification_dict["repository"]["owner"]["login"]
