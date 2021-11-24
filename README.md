# Generic Twitter Image Poster
With such an exciting, descriptive name, the fact that this script posts a random image to a Twitter account should not come as a surprise.


# Installation

From the root of the project, create a virtual envrionment for the install and activate it:

`python3 -m venv venv`

then

`. ./venv/bin/activate`

## Install the requirements:

`pip install -r requirements.txt`

## Setup your secrets in the config

1. Copy `config.json` and `metadata.json` from `/_samples` to the root of the project.

2. Modify `config.json` to include your credentials as provided by the developer
   dashboard for your account.

3. Optionally modify `metadata.json` with whatever follow-up details you want replied
   to the image tweet. If `metadata_file` or the file it points to is missing, this
   step will be skipped.

## Extracting your media (an example)

This ia a big one. You have to supply your own content. This script was designed to pull from a pool of images ripped from TV show episodes. How you make it work for your use case is up to you, but I'll provide an example of how *I* use it.

First, I take a single TV episode... let's say, I'm posting screens from my MKV rips of _The Addams Family_.

I'll need ffmpeg installed. Ask `apt` or whoever you like.

Given `addams-family-1x01.mkv`, I'll do this:

    ffmpeg -i addams-family-1x01.mkv -r 1 "frames/frame_1x01_Pilot-Episode_%04d.jpg"

This rips one frame of video a second, putting it into the `frames` directory, using a pattern that results in:
- `frame_1x01_Pilot-Episode_0000.jpg`
- `frame_1x01_Pilot-Episode_0001.jpg`
- `frame_1x01_Pilot-Episode_0002.jpg`
- etc...

### Patterns
That output filename pattern is important if you're taking advantage of metadata lookups (see the _Metadata_ section).

`frame_EPISODEID_title-of-the-show_FRAMENUM.jpg`

Ignored are `frame` and the `title` portions -- these are mostly just to keep the listings clean and easily organized.

The `EPISODEID` is whatever makes sense -- just be consistent. Quite common is the `01x23` format of season/episode number, but `S1E2` is just as valid.

And `FRAMENUM` is provided as a potential metadata token, but in practice `ffmpeg` will handle that part.

### Metadata
The `metadata.json` file looks like this:
```json
{
    "template": "From ep {{id}}: {{title}} (First aired: {{aired}}, Frame #{{frame_id}})",
    "entries": {
        "0x00": {
            "title": "Max Headroom: 20 Minutes Into the Future (TV Movie)",
            "imdb": "https://www.imdb.com/title/tt0089568/",
            "aired": "1985-Apr-04"
        },
        "1x01": {
            "title": "Blipverts",
            "imdb": "https://www.imdb.com/title/tt0644551/",
            "aired": "1987-Mar-31"
        },
        ...
```

If you provide it, extra data for an episode will be extracted from this for use in a follow-up post to give context for the posted frame.

The `template` key provides the formatted string used in the reply, with the `{{VALUE}}` tokens replaced with the value inside the matching `enrties` entry.

You can create whatever metadata keys you want and add them to the template. `imdb` and `aired` are here just as examples.

Just look at it. Should make sense.

_NOTE: If you don't provide a `template` string, it defaults to `{{title}}` which is required._

## Test it

Run `post.sh` to give it a go. On failure, it'll python-barf, otherwise it will be silent on success. The `post.sh` wrapper script takes care of setting up the virtual environment, and ensuring the script is run from it's own directory.

If you already have the venv activated, calling `post-frame.py` directly should work just as well.

## Add to your crontab, or whatever makes sense for your lifestyle

Under *nix, you'll want to add an entry to your crontab to run the bot script on a regular interval.

Here's an example that posts every 15 minutes:

```
0,15,30,45 * * * * my_username /opt/bot-twitterimage/post.sh
```

And another that posts on the hour:
```
0 * * * * my_username /opt/bot-twitterimage/post.sh
```

# Important note regarding API access

While Twitter is pressing for folks to use the v2 API, as of this writing, the ability to post images requires v1.x API access with 'elevated' features. This is as easy as simply applying for it on the dashboard.









