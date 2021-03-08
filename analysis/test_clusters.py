import pandas as pd
import statsmodels.api as sm

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils.path import makedir
from utils.tables import write_csv


def test_transition_clusters(data_trial):

    print('Testing transition clusters in a regression model...')
    data_cluster = data_trial.dropna(
        subset=[
            'trans_type_0',
            'trans_type_aLLtLL', 'trans_type_tLLaSS', 'trans_type_aLLaSS',
            'trans_type_aSStSS', 'trans_type_tLLtSS'],
        how='all')

    data_cluster.loc[:, [
        'trans_type_0',
        'trans_type_aLLtLL', 'trans_type_tLLaSS', 'trans_type_aLLaSS',
        'trans_type_aSStSS', 'trans_type_tLLtSS']].isnull().any()

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data_cluster.loc[
       :,
       ['trans_type_0',
        'trans_type_aLLtLL', 'trans_type_tLLaSS', 'trans_type_aLLaSS',
        'trans_type_aSStSS', 'trans_type_tLLtSS']
       ]
       )


    output = []
    X = data_cluster[["run_id"]]  # , "withinTaskIndex"]]
    X_ = sm.add_constant(X)
    y = 1 - data_cluster[["choseLL"]]
    log_reg = sm.Logit(y, X_).fit()
    output.append([0, log_reg.bic, log_reg.aic])

    for n_cluster in range(2, 5):
        data_cluster['cluster' + str(n_cluster)] = \
            clusters(n_cluster, scaled_features)
        X = data_cluster[["run_id", 'cluster' + str(n_cluster)]]
        X_ = sm.add_constant(X)
        y = 1 - data_cluster[["choseLL"]]
        log_reg = sm.Logit(y, X_).fit()
        output.append([n_cluster, log_reg.bic, log_reg.aic])

    output = pd.DataFrame(output, columns=['n_clusters', 'BIC', 'AIC']) \
        .set_index('n_clusters')

    print(
        f"""\n"""
        f"""Comparison of transition clusters: \n"""
        f"""{output} \n"""
    )

    makedir('results', 'tables', 'transitions')
    write_csv(
        output,
        'transition_clusters.csv',
        'results', 'tables', 'transitions')


def clusters(n_clusters, scaled_features):
    kmeans = KMeans(
        init="random",
        n_clusters=n_clusters,
        n_init=10,
        max_iter=300,
        random_state=42
    )
    kmeans.fit(scaled_features)

    #     https://realpython.com/k-means-clustering-python/
    #     print(kmeans.inertia_)
    #     print(kmeans.cluster_centers_)
    #     print(kmeans.n_iter_)

    return kmeans.labels_
