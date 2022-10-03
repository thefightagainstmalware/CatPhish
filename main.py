from dotenv import load_dotenv
import tweepy, requests, re, os, time, random

TWITTER_LINK_RE = re.compile(r"https?://t\.co/\w{10}")
TWITTER_DM_RE = re.compile(
    r"(https?:\/\/)?twitter\.com\/messages\/compose\?\w+?recipient_id=\d+"
)
GOOGLE_FORM_RE = re.compile(
    r"https:\/\/docs\.google\.com\/forms\/d\/e\/[A-Za-z0-9_-]{56}\/\S+"
)
INSTAGRAM_USER_RE = re.compile(r"(https?:\/\/)?www\.instagram\.com\/\w+?\/?")
INSTAGRAM_USER_MENTION_RE = re.compile(r".+@(?!gmail)[(?=[A-Za-z\d.+_)]+")
REAL_INSTAGRAM_USER_MENTION_RE = re.compile(r"@(?!gmail)[(?=[A-Za-z\d.+_)]+")
EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
TO_FORMAT = "{my_tweet_id},{replier_user_id},{replier_tweet_id},{found_content},{found_content_type},yes\n"


def write_to_file(
    my_tweet_id, replier_user_id, replier_tweet_id, found_content, found_content_type, filehandle
):
    filehandle.write(
        TO_FORMAT.format(
            my_tweet_id=my_tweet_id,
            replier_user_id=replier_user_id,
            replier_tweet_id=replier_tweet_id,
            found_content=found_content,
            found_content_type=found_content_type,
        )
    )
    filehandle.flush()
    os.fsync(filehandle.fileno())


def resolve_url(url: str) -> str:
    req = requests.get(url, allow_redirects=True)
    return req.url


load_dotenv()

messages = [
    "Help! I can't login to my Coinbase wallet. ",
    "i can't find the funds in my coinbase wallet! ",
    "help i can't find my nfts in coinbase wallet. ",
    "Help all the funds are gone in my metamask wallet!",
    "I can't login to my youtube channel help!"
]

auth = tweepy.OAuth1UserHandler(
    os.getenv("CONSUMER_KEY"),
    os.getenv("CONSUMER_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET"),
)

v1api = tweepy.API(auth)
v2api = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
)
idx = 0
maxid = 0

while True:
    alreadyseentweets = set()
    tweet = v1api.update_status(messages[idx] + str(random.randint(0, 1_000_000_000)))
    tweet_id = tweet.id
    time.sleep(10)
    a = v2api.get_tweet(tweet_id, tweet_fields="conversation_id")
    try:
        conversation_id: int = a.data.conversation_id
    except AttributeError:
        continue
    for _ in range(180):
        handle = open('data.csv', 'a')
        if maxid != 0:
            b = v2api.search_recent_tweets(
                query="conversation_id:{}".format(conversation_id),
                tweet_fields="author_id",
                max_results=100,
                since_id=maxid,
            )
        else:
            b = v2api.search_recent_tweets(
                query="conversation_id:{}".format(conversation_id),
                tweet_fields="author_id",
                max_results=100,
            )
        rts = v1api.get_retweets(tweet_id, count=100)
        tweets = b.data or [] + rts or []
        for tweet in tweets:
            if tweet.id in alreadyseentweets:
                continue
            maxid = max(maxid, tweet.id)
            alreadyseentweets.add(tweet.id)
            for match in re.finditer(TWITTER_LINK_RE, tweet.text):
                url = resolve_url(match.group(0))
                if re.match(TWITTER_DM_RE, url):
                    write_to_file(
                        tweet_id, tweet.author_id, tweet.id, url, "twitter_dm", handle
                    )
                elif re.match(GOOGLE_FORM_RE, url):
                    write_to_file(
                        tweet_id, tweet.author_id, tweet.id, url, "google_form", handle
                    )
                elif re.match(INSTAGRAM_USER_RE, url):
                    write_to_file(
                        tweet_id, tweet.author_id, tweet.id, url, "instagram_user", handle
                    )
            for match in re.finditer(EMAIL_RE, tweet.text):
                write_to_file(tweet_id, tweet.author_id, tweet.id, match.group(0), "email", handle)
            for match in re.finditer(INSTAGRAM_USER_MENTION_RE, tweet.text):
                write_to_file(tweet_id, tweet.author_id, tweet.id, REAL_INSTAGRAM_USER_MENTION_RE.match(match.group(0)).group(0), "instagram_user_mention", handle)
        handle.close()
        time.sleep(20)
    idx += 1
    idx %= len(messages)
