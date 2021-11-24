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


def format_with_template(template_str: str, entry: dict):
    '''
    Given a template string, it looks to see what tokens are
    present (in "{{token_name}}" format) and replaces them with
    that value from the `entry` object.
    '''
    formatted = template_str

    # get tokens (e.g. `{{token_name}}`)
    tokens = re.findall(r"({{(\w*)}})", template_str)

    # use token name as key in entry data
    for tok in tokens:
        formatted = formatted.replace(tok[0], entry.get(tok[1], "???"))

    return formatted


def get_meta_from_filename(filename: str):
    '''
    Try to break down a filename to get an ID leading to
    expanded metadata for the frame. Returns formatted string
    ready for posting if successful, otherwise 'None'.
    '''
    metadata_file = config.get('metadata_file', None)

    if not metadata_file or not os.path.exists(metadata_file):
        return None

    try:
        # e.g. "frame_1x01_episode-title_01234.jpg"
        (_, ep_num, _, frame_id) = filename.split("_")
        if ep_num:
            with open(METADATA_FILE) as mdf:
                meta_json = json.load(mdf)

                template = meta_json.get('template', "{{title}}")

                entries = meta_json.get('entries', [])

                if ep_num in entries:
                    entry = entries.get(ep_num)
                    entry['id'] = ep_num
                    entry['frame_id'] = frame_id.split(".")[0]
                    return format_with_template(template, entries.get(ep_num))

                return None
    except:
        pass

    return None


def get_random_frame():
    frames_path = pathlib.Path(__file__).parent / config['frames_path']

    frames = os.listdir(frames_path)

    rand_frame = frames[random.randrange(0, len(frames))]

    meta = get_meta_from_filename(rand_frame)

    path = f"{frames_path}/{rand_frame}"

    return path, meta


def main():
    global config
    # load our config vars and creds
    if not os.path.exists(CONFIG_FILE):
        raise FileExistsError(f"Missing config file '{CONFIG_FILE}'")

    with open(CONFIG_FILE) as cf:
        config = json.load(cf)

    # setup the connection

    auth = tweepy.OAuthHandler(
        consumer_key=config['creds']['consumer_key'],
        consumer_secret=config['creds']['consumer_secret'],
    )

    auth.set_access_token(config['creds']['access_token'],
                          config['creds']['access_secret'])

    api = tweepy.API(auth)

    # fetch a random frame and any metadata available

    image_path, meta = get_random_frame()

    image_tweet = api.update_status_with_media("", image_path)

    # post a follow-up reply if there's metadata available
    if meta:
        reply_tweet = api.update_status(
            meta, in_reply_to_status_id=image_tweet.id_str)


if __name__ == "__main__":
    main()
