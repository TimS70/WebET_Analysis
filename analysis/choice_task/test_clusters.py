import pandas as pd
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils.path import makedir
from utils.save_data import write_csv


def add_transition_clusters(data_trial, path_tables,
                            undirected_transitions=False):
    print('Testing transition clusters in a regression model...')

    if undirected_transitions:
        data_trial['trans_type_aLLtLL'] = data_trial['trans_type_aLLtLL'] + data_trial['trans_type_tLLaLL']
        data_trial['trans_type_tLLaSS'] = data_trial['trans_type_tLLaSS'] + data_trial['trans_type_aSStLL']
        data_trial['trans_type_aLLaSS'] = data_trial['trans_type_aLLaSS'] + data_trial['trans_type_aSSaLL']
        data_trial['trans_type_aSStSS'] = data_trial['trans_type_aSStSS'] + data_trial['trans_type_tSSaSS']
        data_trial['trans_type_tLLtSS'] = data_trial['trans_type_tLLtSS'] + data_trial['trans_type_tSStLL']

        transition_columns = data_trial.columns.intersection([
            'trans_type_0',
            'trans_type_aLLtLL',
            'trans_type_tLLaSS',
            'trans_type_aLLaSS',
            'trans_type_aSStSS',
            'trans_type_tLLtSS'])

    else:
        transition_columns = data_trial.columns.intersection([
            'trans_type_0',
            'trans_type_aLLtLL', 'trans_type_tLLaLL',
            'trans_type_tLLaSS', 'trans_type_aSStLL',
            'trans_type_aLLaSS', 'trans_type_aSSaLL',
            'trans_type_aSStSS', 'trans_type_tSSaSS',
            'trans_type_tLLtSS', 'trans_type_tSStLL'])

    data_cluster = data_trial.dropna(subset=transition_columns, how='all')

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(
        data_cluster[transition_columns])

    output = []
    x = data_cluster[["run_id"]]
    x_ = sm.add_constant(x)
    y = 1 - data_cluster[["choseLL"]]
    log_reg = sm.Logit(y, x_).fit()
    output.append([0, log_reg.bic, log_reg.aic])

    for n_cluster in range(2, 5):
        data_cluster['cluster' + str(n_cluster)] = \
            clusters(n_cluster, scaled_features)
        x = data_cluster[["run_id", 'cluster' + str(n_cluster)]]
        x_ = sm.add_constant(x)
        y = 1 - data_cluster[["choseLL"]]
        log_reg = sm.Logit(y, x_).fit()
        output.append([n_cluster, log_reg.bic, log_reg.aic])

    output = pd.DataFrame(output, columns=['n_clusters', 'BIC', 'AIC']) \
        .set_index('n_clusters')

    print(f"""Comparison of transition clusters: \n"""
          f"""{output} \n""")

    write_csv(data=output,
              file_name='transition_clusters.csv',
              path=path_tables)

    data_trial = data_trial.merge(
        data_cluster[['run_id', 'trial_index',
                      'cluster2', 'cluster3', 'cluster4']],
        on=['run_id', 'trial_index'],
        how='left')

    return data_trial


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
