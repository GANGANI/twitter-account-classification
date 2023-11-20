import json
import csv
import sys
import gzip

from bloc.generator import add_bloc_sequences
from bloc.util import conv_tf_matrix_to_json_compliant
from bloc.util import get_bloc_doc_lst
from bloc.util import get_bloc_variant_tf_matrix
from bloc.util import get_default_symbols

csv.field_size_limit(sys.maxsize)

bloc_model = {
    'name': 'm1: bigram',
    'ngram': 2,
    'token_pattern': '[^ |()*]',
    'tf_matrix_norm': 'l1',  # set to '' if tf_matrices['tf_matrix_normalized'] not needed
    'keep_tf_matrix': True,
    'set_top_ngrams': True,
    # set to False if tf_matrices['top_ngrams']['per_doc'] not needed. If True, keep_tf_matrix must be True
    'top_ngrams_add_all_docs': True,
    # set to False if tf_matrices['top_ngrams']['all_docs'] not needed. If True, keep_tf_matrix must be True
    'bloc_variant': None,
    'bloc_alphabets': ['action', 'content_syntactic']
}

bloc_collection = []
all_bloc_symbols = get_default_symbols()

with open('grouped_tweets_data.json.csv', 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)

    for row in csv_reader:
        user_id, tweets_str = row
        user_tweets = eval(tweets_str)
        u_bloc = add_bloc_sequences(
            user_tweets,
            all_bloc_symbols=all_bloc_symbols,
            bloc_alphabets=bloc_model['bloc_alphabets'],
            sort_action_words=bloc_model.get('sort_action_words', False))
        bloc_collection.append(u_bloc)

bloc_doc_lst = get_bloc_doc_lst(bloc_collection, bloc_model['bloc_alphabets'], src='IU', src_class='human')
tf_matrix = get_bloc_variant_tf_matrix(bloc_doc_lst,
                                       tf_matrix_norm=bloc_model['tf_matrix_norm'],
                                       keep_tf_matrix=bloc_model['keep_tf_matrix'],
                                       min_df=2,
                                       ngram=bloc_model['ngram'],
                                       token_pattern=bloc_model['token_pattern'],
                                       bloc_variant=bloc_model['bloc_variant'],
                                       set_top_ngrams=bloc_model.get('set_top_ngrams', False),
                                       top_ngrams_add_all_docs=bloc_model.get('top_ngrams_add_all_docs', False))

with gzip.open('results/tf_idf_matrices.json.gz', 'wt', encoding='utf-8') as json_gz_file:
    json.dump(conv_tf_matrix_to_json_compliant(tf_matrix), json_gz_file, indent=2)

csv_file_path = 'results/features.csv'

with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    header = ['user_id', 'class'] + [f'tf_vector_{i}' for i in range(len(tf_matrix['tf_matrix_normalized'][0]['tf_vector']))]
    writer.writerow(header)

    for entry in tf_matrix['tf_matrix_normalized']:
        row = [entry['user_id'], entry['class']] + entry['tf_vector']
        writer.writerow(row)
