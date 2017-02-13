
import os
#import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.backends.backend_pdf import PdfPages

import logging
log = logging.getLogger('prospecting.plot')


def plot_distribution(x, num_bins=20, normed=1, log=False):
    mu = x.mean()
    sigma = x.std()
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(x, num_bins, normed=normed, log=log)
    y = mlab.normpdf(bins, mu, sigma)
    ax.plot(bins, y, '-')
    ax.set_xlabel(x.name)
    ax.set_ylabel('Probability density')
    ax.set_title('Histogram of ' + x.name + ':\n$\mu=' + str(mu) + '$, $\sigma=' + str(sigma) + '$')
    fig.tight_layout()
    plt.show()


def boxplot(x, labels=None):
    fig, ax = plt.subplots()
    ax.boxplot(x, labels=labels, showmeans=True, meanline=True)
    ax.set_title('showmeans=True,\nmeanline=True')
    fig.tight_layout()
    plt.show()


def plot_pca_expvar_to_pdf(modelsession, directory, filename='pca_explained_variance.pdf'):
    # pass in list of pca's, as well as dataset name so modelsession is not required
    log.info('Creating PDF of PCA explained variance plots...')
    file_path = os.path.join(directory, filename)
    pp = PdfPages(file_path)
    plot_pca_expvar(modelsession.pca, modelsession.dataset_name, expvar=1, ratio=1)
    plot_pca_expvar(modelsession.pca_std, modelsession.dataset_name, expvar=1, ratio=1)
    plot_pca_expvar(modelsession.pca_mms, modelsession.dataset_name, expvar=1, ratio=1)
    pp.savefig()
    plt.close()
    plot_pca_expvar(modelsession.pca, modelsession.dataset_name, expvar=1, ratio=0)
    plot_pca_expvar(modelsession.pca_std, modelsession.dataset_name, expvar=1, ratio=0)
    plot_pca_expvar(modelsession.pca_mms, modelsession.dataset_name, expvar=1, ratio=0)
    pp.savefig()
    plt.close()
    plot_pca_expvar(modelsession.pca, modelsession.dataset_name, expvar=0, ratio=1)
    plot_pca_expvar(modelsession.pca_std, modelsession.dataset_name, expvar=0, ratio=1)
    plot_pca_expvar(modelsession.pca_mms, modelsession.dataset_name, expvar=0, ratio=1)
    pp.savefig()
    plt.close()
    pp.close()
    log.info('PDF saved to: {0}'.format(file_path))


def plot_pca_expvar(pca, dataset, expvar=1, ratio=1):
    dataset_name = os.path.splitext(os.path.basename(dataset))[0]
    with plt.style.context('ggplot'):
        if expvar is 1 and ratio is 1:
            plt.figure(1, figsize=(10, 6))
            plt.plot(pca.explained_variance_, linewidth=2, label=str(pca.train_set))
            plt.plot(pca.explained_variance_ratio_.cumsum() * 100, linewidth=1, label=(str(pca.train_set)) + " cume")
            plt.suptitle('PCA Explained Variance', fontsize=18)
            plt.title('Dataset: ' + (str(dataset_name)), y=1.01, fontsize=10, loc='right')
            plt.ylabel('Explained variance')
            plt.xlabel('Principal Components')
            plt.legend(loc='best')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
        elif expvar is 1:
            plt.figure(1, figsize=(10, 6))
            plt.plot(pca.explained_variance_, linewidth=2, label=str(pca.train_set))
            plt.suptitle('pca.explained_variance_', fontsize=18)
            plt.title('Dataset: ' + (str(dataset_name)), y=1.01, fontsize=10, loc='right')
            plt.ylabel('Explained variance')
            plt.xlabel('Principal Components')
            plt.legend(loc='best')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
        elif ratio is 1:
            plt.figure(1, figsize=(10, 6))
            plt.plot(pca.explained_variance_ratio_.cumsum() * 100, linewidth=1, label=(str(pca.train_set)) + " cume")
            plt.suptitle('pca.explained_variance_ratio_.cumsum()*100', fontsize=18)
            plt.title('Dataset: ' + (str(dataset_name)), y=1.01, fontsize=10, loc='right')
            plt.ylabel('Explained variance Ratio')
            plt.xlabel('Principal Components')
            plt.legend(loc='best')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
        else:
            log.warning("Neither expvar or ratio were set. No PCA plot created.")