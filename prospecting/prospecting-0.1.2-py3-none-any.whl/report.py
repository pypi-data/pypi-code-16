

import time
from collections import OrderedDict
import pandas as pd


# report
from sklearn.metrics import confusion_matrix          # (y_true, y_pred[, ...])
#from sklearn.metrics import classification_report     # (y_true, y_pred)
from sklearn.metrics import precision_score           # (y_true, y_pred[, ...])
from sklearn.metrics import recall_score              # (y_true, y_pred[, ...])
from sklearn.metrics import accuracy_score            # (y_true, y_pred[, ...])
from sklearn.metrics import f1_score                  # (y_true, y_pred[, labels, ...])
from sklearn.metrics import roc_auc_score             # (y_true, y_score[, ...])
#from sklearn.metrics import auc                       # (x, y[, reorder])
#from sklearn.metrics import roc_curve                 # (y_true, y_score[, ...])

import logging
log = logging.getLogger('prospecting.report')


def create_description(dataframe):
    log.info('Creating description for {0}'.format(dataframe.__name__))
    tmp_df = pd.DataFrame(dataframe.describe(include='all').transpose())
    # --------------
    # create column for 'column_name' and reset index
    if 'column_name' not in tmp_df.columns:
        tmp_df.insert(0, 'column_name', tmp_df.index)
        tmp_df.reset_index(drop=True, inplace=True)
        log.info('Success! "column_name" added to description at column position [0]')
    else:
        log.info('Column_name has already been added')
    # --------------
    # create column for dtype
    if 'dtype' not in tmp_df.columns:
        tmp_df.insert(1, 'dtype',
                      [str(dataframe[col].dtype)for col in tmp_df['column_name']]
                      )
        log.info('Success! "dtype" added to description at column position [1]')
    else:
        log.info('Column "dtype" has already been added')
    # --------------
    # add 'missing_count' column
    if 'missing_count' not in tmp_df.columns:
        tmp_df.insert(2, 'missing_count',
                      #[str(dataframe.shape[0]-dataframe[col].count()) for col in tmp_df['column_name']]
                      [(dataframe.shape[0] - dataframe[col].count()) for col in tmp_df['column_name']]
                      )
        log.info('Success! "missing_count" added to description at column position [4]')
    else:
        log.info('Column "missing_count" has already been added')

    for col in tmp_df.columns:
        tmp_df[col] = tmp_df[col].astype(str)

    log.info('Description created for {0}'.format(dataframe.__name__))
    return tmp_df


def cv_results_to_df(modelsession, gsclf):
    df_cv_results = pd.DataFrame.from_dict(gsclf.cv_results_)
    objectcols = df_cv_results.select_dtypes(include=['object']).columns
    df_cv_results[objectcols] = df_cv_results.select_dtypes(include=['object']).astype('str')
    col_list = [col for col in df_cv_results.columns.tolist() if not col.startswith('param_')]
    rank_score = [col for col in col_list if col.startswith('rank_test')]
    params_col = [col for col in col_list if col.startswith('params')]
    fit_time_cols = [col for col in col_list if col.endswith('fit_time')]
    score_time_cols = [col for col in col_list if col.endswith('score_time')]
    train_score_cols = [col for col in col_list if not col.startswith('split') and
                        not col.startswith('rank') and
                        col.endswith('train_score')]
    test_score_cols = [col for col in col_list if not col.startswith('split') and
                       not col.startswith('rank') and
                       col.endswith('test_score')]
    split_cols = [col for col in col_list if col.startswith('split')]
    column_order = (rank_score +
                    params_col +
                    fit_time_cols +
                    score_time_cols +
                    train_score_cols +
                    test_score_cols +
                    split_cols
                    )
    df_cv_results = df_cv_results[column_order]
    df_cv_results.insert(0, 'session_id', modelsession.session_id)
    df_cv_results.insert(1, 'timestamp', gsclf.model_start_time)
    df_cv_results.insert(8, 'scoring_type', gsclf.score_type)
    return (df_cv_results)


def add_cv_results_to_ss(modelsession, gsclf):
    df_cv_results = cv_results_to_df(modelsession, gsclf)
    if hasattr(modelsession.ss.sheets['cv_results'], 'columns'):
        log.info('Appending df_cv_results to cv_results tab in spreadsheet.')
        modelsession.ss.append(df_cv_results, 'cv_results')
    else:
        log.info('Updating cv_results tab in spreadsheet with df_cv_results.')
        modelsession.ss.update(df_cv_results, 'cv_results')


def session_report(modelsession, clf, ytrue, ypred, yprobs):
    report_start_timestamp = time.time()
    y_true_count = ytrue.sum()
    y_pred_count = ypred.sum()
    tpr, fpr, fnr, tnr = confusion_matrix(ytrue, ypred).flatten()
    rocauc_score = roc_auc_score(ytrue, yprobs)
    acc_score = accuracy_score(ytrue, ypred)
    prec_score = precision_score(ytrue, ypred)
    rec_score = recall_score(ytrue, ypred)
    f1 = f1_score(ytrue, ypred)
    if not hasattr(clf, "score_type"):
        clf.score_type = "N/A"
    if hasattr(clf, "best_estimator_"):
        pipe_steps = {i: (t) for i, t in enumerate([(t[0], type(t[1])) for t in clf.best_estimator_.steps])}
        pipeline = "_".join([pipe_steps[step][0] for step in pipe_steps])
        best_score = "{:0.4f}".format(clf.best_score_)
        best_params_full = {str(param_k): str(param_v) for param_k, param_v in sorted(clf.best_estimator_.get_params().items())}
        tunedparams = clf.tunedparams
        best_parameters = {str(param_name): str(best_params_full[param_name]) for param_name in sorted(tunedparams.keys())}
    else:
        pipe_steps = None
        pipeline = [name for name, model in modelsession.lookup_model_types.items() if model == str(type(clf))][0]
        best_score = None
        best_params_full = clf.get_params()
        best_parameters = None

    sessionreport = [('session_id', [modelsession.session_id]),
                     ('timestamp', [clf.model_start_time]),
                     ('dataset', [modelsession.dataset_name]),
                     ('n_rows', [modelsession.dataset.shape[0]]),
                     ('n_cols', [modelsession.dataset.shape[1]]),
                     ('test_size', [modelsession.test_size]),
                     ('X_train_shape', [str(modelsession.X_train.shape)]),
                     ('X_test_shape', [str(modelsession.X_test.shape)]),
                     ('y_train_shape', [str(modelsession.y_train.shape)]),
                     ('y_test_shape', [str(modelsession.y_test.shape)]),
                     ('fit_time', [((clf.end_time - clf.fit_start_time) / 60)]),
                     ('training_set', [(clf.training_set)]),
                     ('pipeline', [(pipeline)]),
                     ('y_true_count', [y_true_count]),
                     ('y_pred_count', [y_pred_count]),
                     ('tpr', [tpr]),
                     ('fpr', [fpr]),
                     ('fnr', [fnr]),
                     ('tnr', [tnr]),
                     ('roc_auc_score', [rocauc_score]),
                     ('accuracy_score', [acc_score]),
                     ('precision_score', [prec_score]),
                     ('recall_score', [rec_score]),
                     ('f1_score', [f1]),
                     ('scoring_type', [clf.score_type]),
                     ('best_score', [float(best_score)]),
                     ('best_params_tuned', [str(best_parameters)]),
                     ('best_params_all', [str(best_params_full)]),
                     ('pipe_steps', [str(pipe_steps)]),
                     ]
    df_session_report = pd.DataFrame.from_dict(OrderedDict(sessionreport))
    modelsession.ss.append(df_session_report, 'session_report')
    log.info("Report complete in {0} seconds".format((time.time() - report_start_timestamp)))
    return(df_session_report)
