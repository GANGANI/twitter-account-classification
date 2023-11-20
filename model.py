import gzip
import sys
import pandas as pd

from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier


def get_eval_metric_frm_conf_mat(conf_mat):
    if conf_mat.shape != (2, 2):
        return {}

    TP = conf_mat[0][0]
    TN = conf_mat[1][1]
    FP = conf_mat[0][1]
    FN = conf_mat[1][0]

    precision = TP / (TP + FP) if TP + FP != 0 else 0
    recall = TP / (TP + FN) if TP + FN != 0 else 0
    f1 = 2 * ((precision * recall) / (precision + recall)) if precision + recall != 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1-score': f1,
        'support': TP + TN + FP + FN
    }


def get_train_test_split(ds, n_splits=5):
    train_test_split_indices = []
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True)

    for train_index, test_index in skf.split(ds, y):
        train_test_split_indices.append((train_index, test_index))

    return train_test_split_indices

feature_df = pd.read_csv(features_path)
