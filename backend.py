import feedparser
import re
import argparse
from pathlib import Path
import requests
import pickle
from urllib.parse import urlparse
import os
import sys
from fake_useragent import UserAgent
import logging
import validators
import html

# TODO: Decide which entry's title parts are required and raise an error when they're not present
# TODO: Get feed by URL https://feedparser.readthedocs.io/en/latest/http.html


class LanguagePod101Feed:
    def __init__(self, args):
        self.args = args
        self.ua = UserAgent()
        self.m_session = requests.Session()
        self.FAKE_BROWSER_HEADERS = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3",
            "user-agent": self.ua.random,
            "accept-language": "en-US,en;q=0.9,ja;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-mode":
                "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        self.retry = []
        # Is root_url a valid URL?
        self.valid_url(self.args.root_url)
        # Authenticate
        self.authenticate(self.args.email, self.args.password)

    def analyzer(self, entry_title):
        """
        Analyzes an entry's title: checks what part names are in the title (see Structure.txt for an explanation),
        and based on that it executes the appropriate functions that creates the appropriate directories.
        :param entry_title: the entry's title
        :return: a dictionary containing the entry's title and its parts.
        """
        separator = " - "
        entry_title_split = entry_title.strip().replace("&#039;", "'").replace("&amp;", "&").split(separator)
        # Default Values
        lesson_number = ''
        type_name = ''
        part_name = ''
        # Parsing parts from entry_title and returning them in a dictionary
        re_lesson_name = re.search("#\d*", entry_title)
        if re_lesson_name is not None:
            lesson_number = re_lesson_name.group().strip()
        if entry_title.count(separator) > 1:
            type_name = entry_title_split[-1].strip()
            type_name = type_name.strip()
        re_part_name = re.search('Part.+?(?= - )', entry_title)
        if re_part_name is not None:
            part_name = re_part_name.group()
            part_name = part_name.strip()
        season_name_list = re.findall("(S\d|Season \d)", entry_title)
        if not season_name_list:
            season_name_list = re.findall("\d", entry_title_split[-1].replace(lesson_number, ""))
        level_name = entry_title_split[0].replace(lesson_number, "").strip()
        for season_name_ in season_name_list:
            level_name = level_name.replace(season_name_, "").strip()
        if ":" in level_name and not season_name_list:
            season_name_list.append(level_name[level_name.index(": ") + 2:])
            level_name = level_name[:level_name.index(":")].strip()
        lesson_name = f"{lesson_number} - {entry_title_split[len(entry_title_split) // 2].replace(part_name, '')}" \
            .strip()
        return {"entry_title": entry_title, "level_name": level_name, "season_name_list": season_name_list,
                "lesson_name": lesson_name, "part_name": part_name, "type_name": type_name}

    def retry_download(self):
        """
        Retrying failed downloads.
        :return:
        """
        logging.info("Retrying failed downloads.")
        for dict_ in self.retry:
            if dict_["document"]:
                self.download_document(dict_["url"], dict_["file_name"], self.args.email, self.args.password,
                                       dict_["path"])
            else:
                self.download(dict_["url"], dict_["file_name"], dict_["path"])

    def download_failed_manager(self, url, file_name, path, count='', document=False):
        """
        What to do when a download fails? Calls the appropriate function
        :param url: URL to remote file
        :param file_name: name of file
        :param path: path where the file will be downloaded
        :param count: number of times the function have been called. If count is bigger than one that means the
        download failed a second time, exit
        :param document: Is the file a document / PDF type or not?
        :return:
        """
        if self.args.download_failed == 0:
            sys.exit()
        elif self.args.download_failed == 2:
            self.retry.append({"url": url, "file_name": file_name, "path": path, "document": document})

    def save_file(self, resp, full_path):
        """
        Downloads a file to the given path.
        :param resp: resp
        :param full_path: path where the file will be downloaded to.
        :return:
        """
        total = int(resp.headers.get('content-length', 0))
        with open(str(full_path.absolute()), 'wb') as file:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)

    def download(self, url, file_name, path):
        """
        Downloads a file with a progress bar.
        :param url: URL to the file
        :param file_name: name of the file to be downloaded.
        :param path: path to the directory where the file will be downloaded
        :return:
        """
        full_path = path / file_name
        if not full_path.is_file():
            try:
                resp = requests.get(url, stream=True)
                self.save_file(resp, full_path)
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to download file. {e}")
                self.download_failed_manager(url, file_name, path, str(e))

    def download_document(self, url, file_name, email, password, path):
        """
        Downloads PDF files using wget.
        :param email: languagepod101's account email address
        :param password: languagepod101's account password
        :param url: URL of the remote PDF file
        :param file_name: File name
        :param path: path (directory) to download the file
        :return:
        """
        # downloading the PDF file to path
        full_path = path / file_name
        if not full_path.is_file():
            try:
                resp = self.m_session.get(url, auth=(email, password))
                if resp.status_code not in (200, 302):
                    logging.error(f"Failed to download document / PDF.")
                    self.download_failed_manager(url, file_name, path, document=True)
                self.save_file(resp, full_path)
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to download document / PDF. {e}")
                self.download_failed_manager(url, file_name, path, str(e), True)

    def discover_dirs(self, path):
        """
        Lists all directories.
        :param path: path to find directories
        :return: list with directories inside the path parameter
        """
        return [p for p in Path(path).iterdir() if p.is_dir()]

    def valid_path_checker(self, path):
        """
        Checks if a directory exists.
        :param path: path to check
        :return:
        """
        if not path.exists():
            logging.error(f"Failed to create path {path}")
            sys.exit()

    def makedir(self, name, path):
        """
        If directory does not exist safely create a directory.
        :param name: directory name
        :param path: path create the directory
        :return: path to the newly created directory
        """
        # Windows - removing illegal characters
        if os.name == "nt":
            name = "".join(i for i in name if i not in r'\/:*?"<>|.')
        path /= name
        if not path.exists():
            try:
                os.makedirs(str(path.absolute()))
            except Exception as e:
                logging.error(f"Could not create folder. {e}")
                sys.exit()
            self.valid_path_checker(path)
        return path

    def parse_url(self, url):
        """
        Returns the name of the file with its extension
        :param url: URL
        :return: name of the remote file
        """
        return urlparse(url).path.split("/")[-1]

    def match_url(self, keyword, entry_links):
        """
        Matches the type (keyword) with the entry_links, return a link to the remote file we want to download of
        content type keyword
        :param keyword: type name
        :param entry_links: entry_links
        :return:
        """
        url, file_type = '', ''
        for entry_link in entry_links:
            file_type = entry_link["type"]
            if keyword.lower() in file_type:
                url = entry_link["href"]
        return url, file_type

    def get_ext(self, url):
        """
        Get extension from URL (remote file)
        :param url: URL
        :return: remote file extension, str
        """
        return os.path.splitext(urlparse(url).path)[1]

    def download_type(self, file_type, url, path):
        """
        Based on the remote file's type (file_type), an appropriate function which downloads the file is called.
        Also checks if user chose to download the specific file type, and only downloads the file if he did.
        :param file_type: file_type, str
        :param url: URL
        :param path: path to the directory where the file will be downloaded
        :return:
        """
        # If file type is PDF / Document and user chose to either download PDF / Document type files.
        if "application" in file_type and self.args.content[0] == "ALL" or "PDF / Document" in self.args.content:
            self.download_document(url, self.parse_url(url), self.args.email, self.args.password, path)
        # If file type is Audio and user chose to download audio type files.
        elif "audio" in file_type and self.args.content[0] == "ALL" or "Audio" in self.args.content:
            self.download(url, self.parse_url(url), path)
        # If file type is Video and user chose to download video type files.
        elif "video" in file_type and self.args.content[0] == "ALL" or "Video" in self.args.content:
            self.download(url, self.parse_url(url), path)

    def download_manager(self, entry_links, path, type_name, entry_title, entry_count, entry_total, mode=0):
        """
        Manages Downloading files to their appropriate folders in two modes.
        mode 0 tells the function there is one content type in the entry, download it to the given path.
        mode 1 tells the function there is more than one content type in the entry, and inside the given path there is
        more than one folder. Match every folder with the correct content type and based on that, download the
        appropriate content to its suitable folder.
        :param entry_links: entry_links, a dictionary inside a list
        :param path: path to download/match the remote file/s into
        :param type_name: type name
        :param entry_title: entry title
        :param entry_count: how many entries have been download
        :param entry_total: how many entries there are
        :param mode: mode, an integer, explained above
        :return:
        """
        # TODO: Fix print statement
        print('\x1b[1K\r')
        print(f"\u27a4 Downloading entry {entry_title}... {entry_count} out of {entry_total}",
              flush=True)
        if mode == 0:
            # Parsing URL
            url = entry_links[0]["href"]
            file_type = entry_links[0]["type"]
            # Download the file
            self.download_type(file_type, url, path)
        else:
            content_types = ["Video", "Audio", "PDF / Document"]
            for directory in self.discover_dirs(path):
                url, file_type = '', ''
                # Match the folder's name with the content type and based on the content type find the appropriate
                # file link in entry_links, and download the file to its suitable folder.
                if directory == content_types[0]:
                    url, file_type = self.match_url(content_types[0], entry_links)
                if directory == content_types[1]:
                    url, file_type = self.match_url(content_types[1], entry_links)
                if directory == content_types[-1]:
                    url, file_type = self.match_url(content_types[-1], entry_links)
                full_path = Path(path) / directory
                # Download the file
                self.download_type(file_type, url, str(full_path.absolute()))

    # If the entry contains more than one type of content, e.g., (PDF, Video and Audio) without a type name in the
    # entry's title, we will create a directory for each type of content inside the entry folder
    # If the entry contains more than one type of content, e.g., (PDF, Video and Audio) with a type name in the title,
    # we will create a directory for each content's type inside the title's type directory.
    # If the entry does contain a type name in the title with only one type of content present, we will create a
    # directory for the title's type
    def type_manager(self, type_name, entry_title, path, entry_links, entry_count, entry_total):
        """
        Manages the creation of the type name folder/s and the process of downloading each content to its appropriate
        folder using download_manager
        :param type_name: type name
        :param entry_title: entry title
        :param entry_count: how many entries have been download
        :param entry_total: how many entries there are
        :param path: path to create the type name folder/s
        :param entry_links: entry_links
        :return:
        """
        content_types = ["Video", "Audio", "PDF / Document"]
        if len(entry_links) > 1:
            if type_name:
                path = self.makedir(type_name, path)
            for content_type in content_types:
                self.makedir(content_type, path)
            self.download_manager(entry_links, path, '', entry_title, entry_count, entry_total, mode=1)
        else:
            if not type_name:
                if "application" in entry_links[0]["type"]:
                    type_name = content_types[-1]
                elif "video" in entry_links[0]["type"]:
                    type_name = content_types[0]
                else:
                    type_name = content_types[1]
            path = self.makedir(type_name, path)
            self.download_manager(entry_links, path, type_name, entry_title, entry_count, entry_total, mode=0)

    def check_if_authenticated(self, response):
        """
        Checks if user is authenticated
        :param response: response
        :return:
        """
        returnValue = False
        try:
            response.raise_for_status()
        except Exception as e:
            logging.error(f'Could not reach site. Please check URL and internet connection. {e}')
            sys.exit()
        return 'X-Ill-Member' in response.headers

    def load_cookie(self):
        """
        Loads cookie from path
        :return:
        """
        cookiepath = Path(".")
        cookie_file = "lastsession"
        full_path = cookiepath / cookie_file
        if not full_path.exists():
            return None
        with open(str(full_path.absolute()), 'rb') as f:
            try:
                return pickle.load(f)
            except Exception as e:
                print(e)
        return None

    def place_cookie(self, session_cookie):
        """
        Saves cookie in cookiepath
        :param session_cookie: session_cookie
        :return:
        """
        cookiepath = Path(".")
        cookiepath_str = str(cookiepath.absolute())
        cookie_file = "lastsession"
        if not cookiepath.exists():
            os.mkdir(cookiepath_str)
        full_path = cookiepath / cookie_file
        with open(str(full_path.absolute()), 'wb') as f:
            pickle.dump(session_cookie, f)

    def valid_url(self, url):
        """
        checks if URL is valid
        :param url: URL
        :return:
        """
        # URL is not valid
        if isinstance(validators.url(url), validators.ValidationFailure):
            logging.error("URL is not valid. Please try again")
            sys.exit()

    def authenticate(self, username, password):
        """Logs in to the website via an old session or a new one"""
        logging.debug(f'Trying to log in to {self.args.root_url}')
        response = None
        login_url = f"{self.args.root_url}/member/login_new.php"
        cachedSession = False
        loadCookie = self.load_cookie()
        self.m_session.headers.update(self.FAKE_BROWSER_HEADERS)

        if loadCookie is not None:
            self.m_session.cookies.update(loadCookie)
            response = self.m_session.post(login_url)
            if self.check_if_authenticated(response):
                logging.info('Successfully logged in.')
                cachedSession = True
                return
        if not cachedSession:
            credentials = {'amember_login': username, 'amember_pass': password}
            response = self.m_session.post(login_url, data=credentials)
            self.place_cookie(self.m_session.cookies.get_dict())
            if self.check_if_authenticated(response):
                logging.info('Successfully logged in.')
                return
        if not self.check_if_authenticated(response):
            logging.error('Could not log in. Please check your credentials.')
            sys.exit()

    def executor(self, entry, entry_count, entry_total):
        """
        The main function.
        For each name part in the entry's title, executor creates for it a folder.
        :param entry: an entry object
        :param entry_count: how many entries have been download
        :param entry_total: how many entries there are
        """
        entry_title = entry.title
        path = self.args.download_path
        path_str = str(path)
        entry_dict = self.analyzer(entry_title)
        os.chdir(path_str)
        # Creating Level folder
        level_name = entry_dict["level_name"]  # REQUIRED
        path = self.makedir(level_name, path)
        # Creating Season folder (if exists)
        if entry_dict["season_name_list"]:  # OPTIONAL
            path = self.makedir(entry_dict["season_name_list"][0], path)
        # Creating Lesson folder (if exists)
        if entry_dict["lesson_name"]:  # OPTIONAL
            path = self.makedir(entry_dict["lesson_name"], path)
        # Creating Part folder (if exists)
        part_name = entry_dict["part_name"]  # OPTIONAL
        if part_name:  # OPTIONAL
            path = self.makedir(part_name, path)
        # Creating Type/s folder/s
        self.type_manager(entry_dict["type_name"], entry_title, path, entry.links, entry_count, entry_total)


def args_manager(args):
    content_types = ["Video", "Audio", "PDF / Document"]
    content = args.content
    if len(content) > 1:
        # Checking for invalid content types
        for content_type_chosen in content:
            if content_type_chosen not in content_types:
                logging.error(f"Invalid argument. {content_type_chosen} is not one of the content types available. "
                              f"Content types available: {content_types}")
                # Is download path a valid directory?
    if not args.download_path.is_dir():
        logging.error("Download path is not valid. Make sure the path is a valid directory.")
        sys.exit()
    # Is feed path a valid file?
    if not args.feed_path.is_file():
        logging.error("Feed path is not valid. Make sure the path is a valid file.")
        sys.exit()
    # If the user choose "ALL" but also another selected type of content
    if len(content) > 1 and "ALL" in content:
        logging.error("Invalid content type combination. ALL selects all content types but the user selected"
                      "another, additional content type which is unnecessary. Please remove the unnecessary content "
                      "type "
                      "to continue.")
        sys.exit()
    # If the user chose PDF / Document and the email and password arguments are unfilled raise an error
    if (len(content) == 1 and content[0] == "ALL" or content_types[-1] in content) and (
            not args.email or not args.password):
        logging.error("The email and password arguments are required in order to download PDF / Document files."
                      " Please fill the email and password arguments or do not choose to download PDF / Document files."
                      )
        sys.exit()


def logging_setup():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y '
                                                                                    '%H:%M:%S',
                        filename="languagepod101-feed.log", filemode="w")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def argparse_setup():
    parser = argparse.ArgumentParser(description='''
                            Download languagepod101 Feed's content. 
                            For more information on feeds see:
                            https://www.languagepod101.com/helpcenter/getstarted/how-to-save-lessons/#paid: 
                            https://www.languagepod101.com/helpcenter/getstarted/itunesfeeds
                            Replace 'language' with the language you want, e.g., japanese, spanish.
                            How to use:
                            Download the feed to the computer using wget. For example, Premium feed:
                            'wget "https://www.japanesepod101.com/premium_feed/feed.xml" --user EMAIL --password 
                            PASSWORD'
                            Pass the download .xml file to the script.
                            ''')

    # parser.add_argument('--feed-url', type=str, required=False, help='URL to languagepod101 feed.')
    parser.add_argument('--content', type=str, required=False, help="What type of files to download. There are "
                                                                    "three types of content: Audio, Video, and finally,"
                                                                    " PDF / Document. If you want to download all of"
                                                                    "them pass 'ALL'. If you want to choose one or "
                                                                    "more "
                                                                    "type of content simply type it and separate it "
                                                                    "from "
                                                                    " the other using whitespace."
                                                                    "For example if I would want to only download "
                                                                    "Audio and Video files I will pass in as"
                                                                    " an argument 'Audio Video'."
                                                                    "NOTICE: The email and password are only needed "
                                                                    "to to download PDF / Document files. This is "
                                                                    "because "
                                                                    "they are guarded behind a login form. Defaults "
                                                                    "to ALL",
                        nargs='+', default='ALL')
    parser.add_argument('--email', type=str, required=False,
                        help="languagepod101's email address. Only required if user"
                             " chooses to download PDF / Document files.", default='')
    parser.add_argument('--password', type=str, required=False, help="languagepod101's password. Only required if user"
                                                                     " chooses to download PDF / Document files.",
                        default='')
    parser.add_argument('--feed-path', type=str, required=True, help='File path to languagepod101 feed.')
    parser.add_argument('--download-path', type=str, required=False, default=".", help="Path to which to download the "
                                                                                       "content's feed."
                                                                                       "Defaults to current directory.")
    parser.add_argument('--root-url', type=str, required=True, help="URL to languagepod101 site, e.g., "
                                                                    "'https://www.japanesepod101.com', "
                                                                    "'https://www.spanishpod101.com'. Required.")
    parser.add_argument('--download-failed', type=int, required=False, help='What to do when the download fails.'
                                                                            'In case download fails, the program can '
                                                                            'either exit (0), skip the failed '
                                                                            'download ('
                                                                            '1) or '
                                                                            'retry at the end of the program (2). '
                                                                            'Defaults to 2.', default=2)
    return parser


def languagepod101(args):
    """
    The primary function of the program. Calls executor for each entry object.
    :param args: args
    :return:
    """
    args.download_path = Path(args.download_path)
    args.feed_path = Path(args.feed_path)

    args_manager(args)
    feed = feedparser.parse(str(args.feed_path.absolute()))

    languagepod101_feed = LanguagePod101Feed(args)
    entry_total = len(feed.entries)
    for entry_count, entry in enumerate(feed.entries):
        # Decoding HTML entities
        entry.title = html.unescape(entry.title)
        languagepod101_feed.executor(entry, entry_count, entry_total)

    # retrying failed downloads
    if args.download_failed == 2:
        languagepod101_feed.retry_download()

