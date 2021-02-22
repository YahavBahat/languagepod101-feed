import argparse
import logging
import backend


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


def logging_setup():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y '
                                                                                    '%H:%M:%S',
                        filename="languagepod101-feed.log", filemode="w")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    args = argparse_setup().parse_args()
    logging_setup()
    backend.languagepod101(args)


if __name__ == "__main__":
    main()
