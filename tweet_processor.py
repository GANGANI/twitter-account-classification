import csv
import logging
import re

logger = logging.getLogger('twitter.account.classification')

def get_tweet_object(csv_entry, header):

    tweet = {}
    for i in range(len(csv_entry)):
        tweet[header[i]] = csv_entry[i].strip()

    user = {'id': tweet['user_id'],
            'name': tweet['name'],
            'screen_name': tweet['screen_name'],
            'created_at': tweet['created_at_y'],
            'friends_count': tweet['friends_count'],
            'followers_count': tweet['followers_count'],
            'favourites_count': int(tweet['favourites_count'])}

    text = tweet['text']

    hashtags = [word.strip("#") for word in text.split() if word.startswith("#")]
    hashtags_entities = [{"text": hashtag, "indices": [text.find(hashtag), text.find(hashtag) + len(hashtag)]}
                         for hashtag in hashtags]

    user_mentions = [word.strip("@") for word in text.split() if word.startswith("@")]
    user_mentions_entities = [{"screen_name": user_mention, "indices": [text.find(user_mention),
                                                                        text.find(user_mention) + len(user_mention)]}
                              for user_mention in user_mentions]

    url_pattern = re.compile(r'https?://\S+')
    urls = [{"expanded_url": match.group(), "indices": [match.start(), match.end()]}
            for match in re.finditer(url_pattern, text)]

    entities = {"hashtags": hashtags_entities,
                "user_mentions": user_mentions_entities,
                "symbols": [],
                "urls": urls}

    payload = {
        'id': tweet['tweetid'],
        'full_text': tweet['text'],
        'source': '',
        'lang': tweet['lang'],
        'user': user,
        'geo': tweet['geo'],
        'coordinates': None,
        'in_reply_to_status_id':
            None if (tweet['in_reply_to_status_id'] == '' or tweet['in_reply_to_status_id'] == "0")
            else tweet['in_reply_to_status_id'],
        'in_reply_to_user_id':
            None if (tweet['in_reply_to_user_id'] == '' or tweet['in_reply_to_user_id'] == "0")
            else tweet['in_reply_to_user_id'],
        'retweeted_status_id':
            None if tweet['retweeted_status_id'] == '' else tweet['retweeted_status_id'],
        'created_at': tweet['created_at_x'],
        'entities': entities
    }
    return payload

all_tweets = []
with open('data/output.csv', 'r', newline='', encoding='utf-8') as infile:

    csvObj = csv.reader(infile)
    header = next(csvObj)
    hmap = {}
    [hmap.update({h[1]: h[0]}) for h in enumerate(header)]

    while True:

        row = ''
        try:
            row = next(csvObj)
        except StopIteration:
            break
        except:
            logger.info('\nError occurred file reading through lines of csv')

        if (len(row) == 0):
            continue

        tweet = get_tweet_object(row, header)
        all_tweets.append(tweet)

user_tweets_dict = {}

for tweet in all_tweets:
    user_id = tweet['user']['id']

    # Check if user_id is already in the dictionary
    if user_id in user_tweets_dict:
        # If yes, append the entire tweet JSON to the existing list
        user_tweets_dict[user_id].append(tweet)
    else:
        # If no, create a new entry with the user_id and tweet JSON as a list
        user_tweets_dict[user_id] = [tweet]

with open('grouped_tweets_data.json.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['user_id', 'tweets'])

    for user_id, tweet_list in user_tweets_dict.items():
        tweet_json_str = str(tweet_list)
        csv_writer.writerow([user_id, tweet_json_str])