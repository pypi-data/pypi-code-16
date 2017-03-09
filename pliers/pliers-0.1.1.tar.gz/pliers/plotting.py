import matplotlib.pyplot as plt
# import seaborn as sns
import warnings


def plot_features(data, features=None, max_features=100):

    if isinstance(data, ExtractorResult):
        data = data.to_df()

    stim = data.pop('stim') if 'stim' in data.columns else None

    onset = data.pop('onset')
    duration = data.pop('duration')

    data = data.select_dtypes(include=[np.number])

    if features is None:
        features = data.columns.tolist()

    if max_features and len(features) > max_features:
        features = features[:max_features]
        warnings.warn("%d numeric features found; only displaying first %d." %
                      (len(features), max_features))

    n_features = len(features)

    fig, axes = plt.subplots(n_features, 1, figsize=(20, 0.4*n_features))

    for i in range(n_features):
        ax = axes[i]
        ax.plot(data[feature])
