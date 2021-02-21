# LanguagePod101-Feed

## About

LanguagePod101-feed is a Python-based downloader and viewer for languagepod101's feed's content. The tool can download the content's feed onto your computer, making it possible to watch the courses offline.

The script works on any languagepod101 feed, e.g., japanesepod101.com, spanishpod101.com. For more information, visit:
https://www.innovativelanguage.com/online-language-courses

You may find many other scripts to download a feed's content. However, this program offers a swift and comfortable user experience to view, watch, and traverse through the course content; It structures the downloaded content in an organized and efficient manner. Using LanguagePod101-feed's viewer, it is possible to watch every video, listen to every audio file, and view every document the course offers with ease.

## Usage

* [Python 3.9.x](python.org)
* Install required packages from requirements.txt using pip.
  ```
  pip install -r requirements.txt
  ```
* Languagepod101 feed file.

### Getting the feed

Overall, there are four types of feeds: Free, Basic, Premium feed, and My Feed. which features can be seen here:

https://www.japanesepod101.com/helpcenter/getstarted/how-to-save-lessons/#myfeed
https://www.*language*pod101.com/helpcenter/getstarted/itunesfeeds

Replace *language* with your preferred language.

The Free feed link can be download here: https://www.japanesepod101.com/helpcenter/getstarted/how-to-save-lessons/#free
The Basic and Premium feeds can be found here (subscription required): https://www.hebrewpod101.com/helpcenter/getstarted/itunesfeeds

Scrolling down, you find Two buttons: *Basic Feed* and *Premium Feed*. Once you spot them, choose one of them, right click the button, and click *Copy link address*.
For example, in japanesepod101.com, the link to the premium feed is this: itpc://www.japanesepod101.com/premium_feed/feed.xml.

Next, replace *itpc* at the start with https: https://www.japanesepod101.com/premium_feed/feed.xml.

Download using wget download the feed file:

```
wget "https://www.japanesepod101.com/premium_feed/feed.xml" --user EMAIL --password PASSWORD
```

**NOTE: The *user* and *password* arguments are only required for the Basic, Premium feeds, and my Feed.**
