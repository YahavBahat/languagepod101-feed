# Languagepod101-Feed

## About

Languagepod101's courses are produced and distributed by Innovative Language, who provides language learning courses from a selection of dozens of languages.
The feed's content vary based on the type of the feed and it can be used to watch and view the course's content offline.

LanguagePod101-feed is a Python-based downloader and viewer for languagepod101's feeds. The tool can download the content's feed onto your computer, making it possible to watch the courses offline.

The script works on any languagepod101 feed, e.g., japanesepod101.com, spanishpod101.com. For more information, [visit](https://www.innovativelanguage.com/online-language-courses)

You may find many other scripts to download a feed's content. However, this program offers a swift and comfortable user experience to view, watch, and traverse through the course content; It structures the downloaded content in an organized and efficient manner. Using LanguagePod101-feed's viewer, it is possible to watch every video, listen to every audio file, and view every document the course offers with ease.

## Usage

* [Python 3.9.x](python.org)
* Install required packages from requirements.txt using pip.
  ```
  pip install -r requirements.txt
  ```
* Languagepod101 feed file.

## Getting the feed

Overall, there are four types of feeds: Free, Basic, Premium feed, and My Feed. Their features can be seen here:

[Overview](https://www.japanesepod101.com/helpcenter/getstarted/how-to-save-lessons/)
[Free](https://www.japanesepod101.com/helpcenter/getstarted/how-to-save-lessons/#free)
[Premium and Basic](https://www.japanesepod101.com/helpcenter/getstarted/itunesfeeds)
[My Feed](https://www.japanesepod101.com/learningcenter/account/myfeed)

*Replace **'japanese'** with the language you want.


To find the feeds links scroll down and you will find two buttons: *Basic Feed* and *Premium Feed*. Once you spot them, choose one of them, right click the button, and click *Copy link address*.
For example, in japanesepod101.com, the link to the premium feed is this: itpc://www.japanesepod101.com/premium_feed/feed.xml.

Next, replace *itpc* at the start with *https*: https://www.japanesepod101.com/premium_feed/feed.xml.

Using wget download the feed file:

```
wget "https://www.japanesepod101.com/premium_feed/feed.xml" --user EMAIL --password PASSWORD
```

**NOTE: The *user* and *password* arguments are only required for the Basic, Premium feeds, and My Feed.**

# Example

Next, execute the script:

```
python3 CLI.py --root-url https://www.japanesepod101.com --download-path Japanesepod-101 --feed-path /Downloads/MyJapanesePremiumFeed.xml --content ALL --email EMAIL --password PASSWORD
```

An example downloading japanesepod101's premium feed to the folder *Japanesepod-101*. Downloads all types of content (Video, Audio, Document / PDF).


python3 CLI.py --help
```
usage: CLI.py [-h] [--content CONTENT [CONTENT ...]] [--email EMAIL] [--password PASSWORD] --feed-path FEED_PATH [--download-path DOWNLOAD_PATH]
                  --root-url ROOT_URL [--download-failed DOWNLOAD_FAILED]

Download languagepod101 Feed's content. For more information on feeds see: https://www.languagepod101.com/helpcenter/getstarted/how-to-save-lessons/#paid:
https://www.languagepod101.com/helpcenter/getstarted/itunesfeeds Replace 'language' with the language you want, e.g., japanese, spanish. How to use:
Download the feed to the computer using wget. For example, Premium feed: 'wget "https://www.japanesepod101.com/premium_feed/feed.xml" --user EMAIL
--password PASSWORD' Pass the download .xml file to the script.

optional arguments:
  -h, --help            show this help message and exit
  --content CONTENT [CONTENT ...]
                        What type of files to download. There are three types of content: Audio, Video, and finally, PDF / Document. If you want to download
                        all ofthem pass 'ALL'. If you want to choose one or more type of content simply type it and separate it from the other using
                        whitespace.For example if I would want to only download Audio and Video files I will pass in as an argument 'Audio Video'.NOTICE:
                        The email and password are only needed to to download PDF / Document files. This is because they are guarded behind a login form.
                        Defaults to ALL
  --email EMAIL         languagepod101's email address. Only required if user chooses to download PDF / Document files.
  --password PASSWORD   languagepod101's password. Only required if user chooses to download PDF / Document files.
  --feed-path FEED_PATH
                        File path to languagepod101 feed.
  --download-path DOWNLOAD_PATH
                        Path to which to download the content's feed.Defaults to current directory.
  --root-url ROOT_URL   URL to languagepod101 site, e.g., 'https://www.japanesepod101.com', 'https://www.spanishpod101.com'. Required.
  --download-failed DOWNLOAD_FAILED
                        What to do when the download fails.In case download fails, the program can either exit (0), skip the failed download (1) or retry at
                        the end of the program (2). Defaults to 2.
```

# TODO:
  - Create Languagepod101-feed's viewer.
  - Decide which entry's title parts are required and raise an error when they're not present
  - Get feed by URL https://feedparser.readthedocs.io/en/latest/http.html
