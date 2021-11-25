#!/usr/bin/env python3
'''
This script pulls a random image from a directory and posts it via
the Twitter v1.1 API with an optional metadata follow-up reply.
'''

import os
import re
import json
import pathlib
import random
import tweepy

CONFIG_FILE = "config.json"
METADATA_FILE = "metadata.json"

config = {}
meta_json = {}


def format_with_template(template_str: str, entry: dict) -> str:
    '''
    Given a template string, it looks to see what tokens are
    present (in `{{token_name}}` format) and replaces them with
    that value from the `entry` object.
    '''
    formatted = template_str

    # get tokens (e.g. `{{token_name}}`)
    tokens = re.findall(r"({{(\w*)}})", template_str)

    # use token name as key in entry data
    for tok in tokens:
        formatted = formatted.replace(tok[0], entry.get(tok[1], "???"))

    return formatted


def get_meta_entry_from_filename(filename: str):
    '''
    Try to break down a filename to get an ID leading to
    expanded metadata for the frame.

    Returns specific entry dict, otherwise 'None'.
    '''
    global meta_json

    try:
        # e.g. "frame_1x01_episode-title_01234.jpg"
        (_, ep_num, _, frame_id) = filename.split("_")

        if ep_num:

            template = meta_json.get('alt_template', "{{title}}")

            entries = meta_json.get('entries', [])

            if ep_num in entries:
                entry = entries.get(ep_num)
                entry['id'] = ep_num
                entry['frame_id'] = frame_id.split(".")[0]
                # return format_with_template(template, entries.get(ep_num)), entry
                return entry

            return None
    except:
        pass

    return None


def get_random_frame():
    '''
    Returns a tuple containing (path, meta_entry)
    '''
    frames_path = pathlib.Path(__file__).parent / config['frames_path']

    frames = os.listdir(frames_path)

    rand_frame = frames[random.randrange(0, len(frames))]

    meta_entry = get_meta_entry_from_filename(rand_frame)

    path = f"{frames_path}/{rand_frame}"

    return path, meta_entry


def load_configs():
    '''
    Load the config and metadata files.
    Returns tuple of (config, meta_json)
    '''
    # load our config vars and creds
    if not os.path.exists(CONFIG_FILE):
        raise FileExistsError(f"Missing config file '{CONFIG_FILE}'")
    if not os.path.exists(METADATA_FILE):
        raise FileExistsError(f"Missing metadata file '{METADATA_FILE}'")

    with open(CONFIG_FILE) as cf:
        with open(METADATA_FILE) as mf:
            return json.load(cf), json.load(mf)


def upload_media(api, image_path, meta_entry) -> str:
    # upload the image frame
    media = api.simple_upload(image_path)

    # if we have metadata, attach our `alt_template`` to it
    if meta_entry:
        meta_text = meta_json.get('alt_template', None)

        if meta_text:
            meta_text = format_with_template(meta_text, meta_entry)
            api.create_media_metadata(media.media_id, meta_text)

    return media.media_id


def create_post(api: tweepy.API):
    '''
    Pull random image from the pool and create a new post.
    '''
    tweet_text = ""

    image_path, meta_entry = get_random_frame()

    media_id = upload_media(api, image_path, meta_entry)

    # process the `post_template`` if we have it
    tweet_text = meta_json.get('post_template', 'Nope')

    # pass in the templated variables from the entry, where applicable
    tweet_text = format_with_template(tweet_text, meta_entry)

    # post the primary image tweet
    image_tweet = api.update_status(tweet_text, media_ids=[media_id])

    # optionally post a follow-up reply with details if there's
    # metadata available
    if meta_entry and config.get('meta_reply', False):
        meta_reply_text = meta_json.get('reply_template',None)
        if meta_reply_text:
            api.update_status(
                format_with_template(meta_reply_text, meta_entry),
                in_reply_to_status_id=image_tweet.id_str
            )


def main():
    global config, meta_json

    config, meta_json = load_configs()

    # setup the connection
    auth = tweepy.OAuthHandler(
        consumer_key=config['creds']['consumer_key'],
        consumer_secret=config['creds']['consumer_secret'],
    )

    auth.set_access_token(config['creds']['access_token'],
                          config['creds']['access_secret'])

    api = tweepy.API(auth)

    create_post(api)


if __name__ == "__main__":
    main()
