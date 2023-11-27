import gzip

from bloc.generator import add_bloc_sequences
from bloc.subcommands import run_subcommands
from bloc.util import dumpJsonToFile
from bloc.util import get_bloc_params
from bloc.util import get_default_symbols
from bloc.util import getDictFromJson
from tqdm import tqdm

bot_dataset_files = [
    # {'src': 'astroturf', 'classes': ['political_Bot']},
    {'src': 'botwiki', 'classes': ['bot']}
    # {'src': 'caverlee', 'classes': ['bot']}
    # {'src': 'cresci-17', 'classes': ['bot-socialspam', 'bot-traditionspam', 'bot-fakefollower']},
    # {'src': 'gilani-17', 'classes': ['bot']},
    # {'src': 'gregory_purchased', 'classes': ['bot']},
    # {'src': 'josh_political', 'classes': ['bot']},
    # {'src': 'kevin_feedback', 'classes': ['bot']},
    # {'src': 'pronbots', 'classes': ['bot']},
    # {'src': 'rtbust', 'classes': ['bot']},
    # {'src': 'stock', 'classes': ['bot']},
    # {'src': 'varol-icwsm', 'classes': ['bot']}
]

human_dataset_files = [
    {'src': 'caverlee', 'classes': ['human']},
    {'src': 'cresci-17', 'classes': ['human']},
    {'src': 'gilani-17', 'classes': ['human']},
    {'src': 'kevin_feedback', 'classes': ['human']},
    {'src': 'rtbust', 'classes': ['human']},
    {'src': 'stock', 'classes': ['human']},
    {'src': 'varol-icwsm', 'classes': ['human']},
    {'src': 'verified', 'classes': ['human']},
    {'src': 'midterm-2018', 'classes': ['human']},
    {'src': 'zoher-organization', 'classes': ['human', 'organization']}
]


def get_user_id_class_map(file_path):
    user_id_class_map = {}
    all_classes = set()

    with open(file_path, 'r') as fd:
        for line in fd:
            parts = line.strip().split()
            if len(parts) >= 2:
                user_id, user_class = parts[0], parts[1]
                user_id_class_map[user_id] = user_class
                all_classes.add(user_class)

    return user_id_class_map, all_classes

def process_dataset(dataset_files, result_file_path):
    bloc_payload = []
    dataset_path = '../dataset/'
    for file in tqdm(dataset_files):
        tweets_file_path = dataset_path + file['src'] + '/tweets.jsons.gz'
        userid_file_path = dataset_path + file['src'] + '/userIds.txt'
        user_id_class_map, all_classes = get_user_id_class_map(userid_file_path)

        with gzip.open(tweets_file_path, 'rt', encoding='windows-1252') as infile:
            for line in tqdm(infile):
                line = line.split('\t')
                if user_id_class_map.get(line[0], '') in file['classes']:
                    #print(line[0])
                    tweets = getDictFromJson(line[1])
                    u_bloc = add_bloc_sequences(tweets, all_bloc_symbols=all_bloc_symbols, **gen_bloc_params)
                    bloc_payload.append(u_bloc)

    pairwise_sim_report = run_subcommands(gen_bloc_args, 'sim', bloc_payload)
    dumpJsonToFile(result_file_path, pairwise_sim_report, indentFlag=True)

all_bloc_symbols = get_default_symbols()
gen_bloc_params, gen_bloc_args = get_bloc_params([], '',
                                                 sort_action_words=True, keep_bloc_segments=True,
                                                 tweet_order='noop')

bot_result_file = 'results/pairwise_sim_report_bot.json'
# human_result_file = 'results/pairwise_sim_report_human.json'

process_dataset(bot_dataset_files, bot_result_file)
# process_dataset(human_dataset_files, human_result_file)

