import pandas as pd
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils.path import makedir
from utils.save_data import write_csv
from sklearn.cluster import AgglomerativeClustering
from tqdm import tqdm
import numpy as np


def hierarchical_clusters(data, transition_columns, max_clusters):

    for n_cluster in tqdm(range(2, max_clusters + 1),
                          desc='Agglomerative clustering for transitions: '):

        model = AgglomerativeClustering(n_clusters=n_cluster,
                                        linkage='average')

        # fit model and predict clusters
        data['cluster' + str(n_cluster)] = pd.Series(
            model.fit_predict(data[transition_columns]))

        grouped = data.groupby('cluster' + str(n_cluster), as_index=False).agg(
            n=('trial_index', 'count'))

        print(f"""Cluster solution with {n_cluster} clusters: \n"""
              f"""{grouped} \n""")

    return data


def clusters(n_clusters, scaled_features):
    k_means = KMeans(
        init="random",
        n_clusters=n_clusters,
        n_init=10,
        max_iter=300,
        random_state=42
    )
    k_means.fit(scaled_features)

    #     https://realpython.com/k-means-clustering-python/
    #     print(k_means.inertia_)
    #     print(k_means.cluster_centers_)
    #     print(k_means.n_iter_)

    return k_means.labels_


def add_k_means_clusters(data, transition_columns, subject_level, path_tables):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data[transition_columns])

    if np.invert(subject_level):
        output = []
        x = data[["run_id"]]
        x_ = sm.add_constant(x)
        y = 1 - data[["choseLL"]]
        log_reg = sm.Logit(y, x_).fit()
        output.append([0, log_reg.bic, log_reg.aic])

    for n_cluster in range(2, 5):
        data['cluster' + str(n_cluster)] = clusters(n_cluster, scaled_features)

        if np.invert(subject_level):
            x = data[["run_id", 'cluster' + str(n_cluster)]]
            x_ = sm.add_constant(x)
            y = 1 - data[["choseLL"]]
            log_reg = sm.Logit(y, x_).fit()
            output.append([n_cluster, log_reg.bic, log_reg.aic])

    if np.invert(subject_level):
        output = pd.DataFrame(output, columns=['n_clusters', 'BIC', 'AIC']) \
            .set_index('n_clusters')

        print(f"""Comparison of transition clusters: \n"""
              f"""{output} \n""")

        write_csv(data=output,
                  file_name='transition_clusters.csv',
                  path=path_tables)

    return data


def add_transition_clusters(data_trial, data_subject, path_tables,
                            undirected_transitions=False,
                            subject_level=True):

    if undirected_transitions:
        data_trial['trans_type_aLLtLL'] = data_trial['trans_type_aLLtLL'] + \
                                          data_trial['trans_type_tLLaLL']
        data_trial['trans_type_tLLaSS'] = data_trial['trans_type_tLLaSS'] + \
                                          data_trial['trans_type_aSStLL']
        data_trial['trans_type_aLLaSS'] = data_trial['trans_type_aLLaSS'] + \
                                          data_trial['trans_type_aSSaLL']
        data_trial['trans_type_aSStSS'] = data_trial['trans_type_aSStSS'] + \
                                          data_trial['trans_type_tSSaSS']
        data_trial['trans_type_tLLtSS'] = data_trial['trans_type_tLLtSS'] + \
                                          data_trial['trans_type_tSStLL']
        data_trial['trans_type_aLLtSS'] = data_trial['trans_type_aLLtSS'] + \
                                          data_trial['trans_type_tSSaLL']

        transition_columns = data_trial.columns.intersection([
            'trans_type_0',
            'trans_type_aLLtLL',
            'trans_type_tLLaSS',
            'trans_type_aLLaSS',
            'trans_type_aLLtSS',
            'trans_type_aSStSS',
            'trans_type_tLLtSS'])

    else:
        transition_columns = data_trial.columns.intersection([
            'trans_type_0',
            'trans_type_aLLtSS', 'trans_type_tSSaLL',
            'trans_type_aLLtLL', 'trans_type_tLLaLL',
            'trans_type_tLLaSS', 'trans_type_aSStLL',
            'trans_type_aLLaSS', 'trans_type_aSSaLL',
            'trans_type_aSStSS', 'trans_type_tSSaSS',
            'trans_type_tLLtSS', 'trans_type_tSStLL'])

    if subject_level:
        data_cluster = data_trial \
            .dropna(subset=transition_columns, how='all') \
            .groupby(['run_id'], as_index=False) \
            [transition_columns].mean()
    else:
        data_cluster = data_trial.dropna(subset=transition_columns, how='all')

    data_cluster = add_k_means_clusters(data=data_cluster,
                                        subject_level=subject_level,
                                        transition_columns=transition_columns,
                                        path_tables=path_tables)

    if subject_level:
        data_subject = data_subject.merge(
            data_cluster[['run_id',
                          'trans_type_aLLtSS',
                          'trans_type_aLLtLL',
                          'trans_type_tLLaSS',
                          'trans_type_aLLaSS',
                          'trans_type_aSStSS',
                          'trans_type_tLLtSS',
                          'cluster2', 'cluster3', 'cluster4']],
            on=['run_id'],
            how='left')

        data_trial = data_trial.merge(
            data_cluster[['run_id', 'cluster2', 'cluster3',
                          'cluster4']],
            on=['run_id'],
            how='left')

        print(data_subject[['run_id', 'cluster2', 'cluster3', 'cluster4']])

        return data_subject, data_trial
    else:
        data_trial = data_trial.merge(
            data_cluster[['run_id', 'trial_index', 'cluster2', 'cluster3',
                          'cluster4']],
            on=['run_id', 'trial_index'],
            how='left')
        print(data_trial[['run_id', 'trial_index',
                         'cluster2', 'cluster3', 'cluster4']])
        return data_subject, data_trial

