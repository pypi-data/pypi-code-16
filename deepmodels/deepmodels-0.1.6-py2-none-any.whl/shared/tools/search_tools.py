# tools for retrieval related processing


import scipy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
import json

matplotlib.use("Agg")


class DistType:
  Hamming = 0
  L2 = 1
  L1 = 2


class ReduceType:
  MeanMin = 0,
  Min = 1


def comp_distmat(query_feats, db_feats, dist_type=DistType.Hamming):
  """Compute pair-wise distance matrix.

  Args:
    query_feats: query feature matrix, row major.
    db_feats: db feature matrix, row major.
    dist_type: distance type.
  Returns:
    distance matrix with shape: row(query_codes) x row(db_codes).
  """
#   if dist_type == DistType.L2:
#     # l2 normalization
#     query_norms = np.linalg.norm(query_feats, 2, axis=1, keepdims=True)
#     query_feats /= query_norms
#     if db_feats is not None:
#       db_norms = np.linalg.norm(db_feats, 2, axis=1, keepdims=True)
#       db_feats /= db_norms
  print "start matching..."
  if db_feats is None:
    db_feats = query_feats
  if dist_type == DistType.Hamming:
    dist_mat = scipy.spatial.distance.cdist(query_feats, db_feats, "hamming")
  if dist_type == DistType.L2:
    dist_mat = scipy.spatial.distance.cdist(query_feats, db_feats, "euclidean")
  if dist_type == DistType.L1:
    dist_mat = scipy.spatial.distance.cdist(query_feats, db_feats,
                                            "minkowski", 1)
  print "search done. distance matrix shape: {}".format(dist_mat.shape)
  return dist_mat


# return a reduced distance matrix with a single value for
def reduce_distmat(full_dist_mat, gal_templateids, probe_templateids, reduce_type=ReduceType.MeanMin):
    # Get unique template indices and there positions for keeping initial order
    #gal_tuids,gal_tuind=np.unique(gal_templateids,return_index=True)
    #probe_tuids,probe_tuind=np.unique(probe_templateids,return_index=True)
    gal_tuids,gal_tuind=np.unique([str(x) for x in gal_templateids],return_index=True)
    probe_tuids,probe_tuind=np.unique([str(x) for x in probe_templateids],return_index=True)
    red_dist_mat = np.zeros((len(gal_tuids),len(probe_tuids)))
    # Loop on gallery
    for g,gtupos in enumerate(gal_tuind):
        gutid = gal_templateids[gtupos]
        gt_pos = np.where(gal_templateids==gutid)[0]
        # Loop on probe
        for p,ptupos in enumerate(probe_tuind):
            putid = probe_templateids[ptupos]
            pt_pos = np.where(probe_templateids==putid)[0]
            # Get appropriate distance
            #print g,p
            dist_val = 0.0
            # TO BE FIXED
            if reduce_type==ReduceType.MeanMin:
                dist_val = np.mean(np.min(full_dist_mat[np.ix_(gt_pos,pt_pos)]))
            else:
                dist_val = np.amin(full_dist_mat[np.ix_(gt_pos,pt_pos)])
            red_dist_mat[g,p]=dist_val
    return red_dist_mat,gal_tuind,probe_tuind


class PtSetDist():
  Min = 0,
  Avg = 1,
  MeanMin = 2 # TO BE IMPLEMENTED


# compute distance between set pairs using point
# min point pair or avg point pair, distance matrix: query -> db
# input codes are list of tensors
def match_set_with_pts(db_set_feats, query_set_feats, dist_type, pt_set_dist_mode):
    print('start matching sets using points...')
    if query_set_feats is None:
        query_set_feats = db_set_feats
    dist_mat = np.empty((len(query_set_feats), len(db_set_feats)), dtype=np.float)
    for i in range(len(query_set_feats)):
        for j in range(len(db_set_feats)):
            if dist_type == DistType.Hamming:
                tmp_dist_mat = scipy.spatial.distance.cdist(query_set_feats[i], db_set_feats[j], 'hamming')
            if dist_type == DistType.L2:
                tmp_dist_mat = scipy.spatial.distance.cdist(query_set_feats[i], db_set_feats[j], 'euclidean')
            if pt_set_dist_mode == PtSetDist.Min:
                dist_mat[i,j] = np.amin(tmp_dist_mat)
            if pt_set_dist_mode == PtSetDist.Avg:
                dist_mat[i,j] = np.mean(tmp_dist_mat)
            if pt_set_dist_mode == PtSetDist.MeanMin:
                dist_mat[i,j] = np.mean(np.amin(tmp_dist_mat, axis=1))
    return dist_mat


def draw_pr_curves(plot_title, pr_curves, save_fn=''):
  """Plot pr curve.

  Args:
    plot_title: title name for plot.
    pr_curves: a set of pr curves.
    pr curve format: {'name', 'pre', 'recall', 'map'}
    save_fn: filename to save.
  """
  plt.figure()
  symbols = ['.', 'o', 'x', '+', 'd', 'v', '>', 's', 'p', '*', 'h']
  for i in range(len(pr_curves)):
    precision = pr_curves[i]['pre']
    recall = pr_curves[i]['recall']
    plt.plot(recall.tolist(), precision.tolist(), symbols[i]+'-', label=pr_curves[i]['name'])
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.title(plot_title)
  plt.xlim([0, 1])
  plt.ylim([0, 1.1])
  plt.legend(loc=4, fontsize=10)
  plt.grid()
  if save_fn != "":
    plt.savefig(save_fn)


def evaluate(plot_title, dist_mat, db_labels, query_labels, rank_num=100, save_fn_prefix=""):
  """Compute multiple performance metrics.

  Precision-recall curve, MAP, classification accu using NN.

  Args:
    plot_title: title of plot.
    dist_mat: computed distance matrix.
    db_labels: labels for db features.
    query_labels: labels for query features.
    rank_num: number of points to compute the pr curve.
    save_fn_prefix: prefix for filename.
  """
  print "start evaluation"
  query_num = dist_mat.shape[0]
  db_num = dist_mat.shape[1]
  top1_accu = float(0)
  # at least one is correct in top 5.
  top5_accu = float(0)
  # average precision and recall at each threshold point.
  precision = np.zeros(rank_num)
  recall = np.zeros(rank_num)
  MAP = 0
  valid_query_num = 0
  # check each query.
  for qid in range(len(query_labels)):
    sorted_db_ids = np.argsort(dist_mat[qid, :])
    sorted_db_labels = [db_labels[i] for i in sorted_db_ids]
    sorted_label_mask = (sorted_db_labels == query_labels[qid]).astype(np.int32)
    top1_accu += sorted_label_mask[0]
    top5_accu += sorted_label_mask[0:5].sum() > 0
    # total number of samples in the same category as query.
    total_cnt = sorted_label_mask.sum()
    # ignore nonexisting probe label
    if total_cnt == 0:
      continue
    # pr for current query.
    query_recall = np.zeros(rank_num)
    query_precision = np.zeros(rank_num)
    map_precision = np.zeros(rank_num)
    pos_id = 0
    for k in np.linspace(0, db_num, num=rank_num):
      corr_num = sorted_label_mask[0: k+1].sum() * 1.0
      cur_recall = corr_num / total_cnt
      cur_precision = corr_num / (k+1)
      query_precision[pos_id] = cur_precision
      query_recall[pos_id] = cur_recall
      if pos_id == 0:
        map_precision[pos_id] = cur_precision * query_recall[pos_id]
      else:
        map_precision[pos_id] = cur_precision * (query_recall[pos_id] - query_recall[pos_id-1])
      pos_id += 1
    precision += query_precision
    recall += query_recall
    MAP += np.sum(map_precision)
    print "finished {}/{}".format(qid, query_num)
    valid_query_num += 1

  MAP /= valid_query_num
  print "MAP: {}".format(MAP)
  top1_accu = top1_accu * 1.0 / valid_query_num
  top5_accu = top5_accu * 1.0 / valid_query_num
  print "top1 accuracy: {}".format(top1_accu)
  print "top5 accuracy: {}".format(top5_accu)

  precision /= valid_query_num
  recall /= valid_query_num
  pr_res = {}
  pr_res["name"] = plot_title
  pr_res["pre"] = precision
  pr_res["recall"] = recall
  pr_res["map"] = MAP
  pr_res["top1_accu"] = top1_accu
  pr_res["top5_accu"] = top5_accu

  prs = [pr_res]
  with open(save_fn_prefix + ".pr", "w") as f:
    pr_res["pre"] = np.array_str(precision)
    pr_res["recall"] = np.array_str(recall)
    json.dump(pr_res, f)
    print "pr curve saved to {}".format(save_fn_prefix + ".pr")

  draw_pr_curves(plot_title, prs, save_fn_prefix + ".png")

  #plt.show()
  #print('top1 accuracy: {:.3f}%, top5 accuracy: {:.3f}%'.format(top1*100, top5*100))
  #return top1, top5
