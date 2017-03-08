"""Tool functions for manipulating data.
"""

import csv
import gzip
import glob
import itertools
import os
import scipy
import shutil
import sys

import numpy.random
import skimage
import skimage.transform

import cPickle as pickle
import numpy as np
import random as rand

# import cv2

scale_factor = 0.00390625


def get_project_dir():
  """Get DeepModels root dir.

  Returns:
    root dir path.
  """
  full_path = os.path.realpath(__file__)
  cur_dir = os.path.dirname(full_path)
  proj_dir = os.path.join(cur_dir, "../../")
  return proj_dir


def remove_dir(target_dir, verbose=True):
  """Remove the target directory recursively.

  Args:
    target_dir (string): the directory and all its subdirectories to be removed.
    verbose (boolean):
  """
  if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
    if verbose:
      print("removed {}".format(target_dir))


def make_dir(target_dir, verbose=True, delete_exist=True):
  """Create directory recursively.

  Args:
    target_dir (string): the directory to be created.
    verbose (boolean): print out on creation.
    delete_exist (boolean): delete target_dir first if it exists.
  """
  create_dir = True
  # check if target_dir exists
  if os.path.exists(target_dir):
    if delete_exist:
      remove_dir(target_dir, verbose)
    else:
      # target_dir exists and was not deleted
      create_dir = False
  # target_dir did not exist or has been deleted
  if create_dir:
    os.makedirs(target_dir)
    if verbose:
      print("created {}".format(target_dir))


''' label organization '''


def map_labels(input_labels):
  """Build a mapper to modify labels to unique continous labels.

  Args:
    input_labels: arbitrary label id list.
  Returns:
    a dictionary takes original label as key and map to a new label starts from 0.
  """
  label_mapper = {}
  new_label = 0
  unique_labels = set(input_labels)
  # build mapper.
  for cur_label in unique_labels:
    label_mapper[cur_label] = new_label
    new_label += 1
  # map labels.
  mapped_labels = []
  for cur_label in input_labels:
    mapped_labels.append(label_mapper[cur_label])
  return mapped_labels, label_mapper


# fetch all infos about images under each category folder
def form_metadata_from_folder_dictlabels(train_dir,
                                         img_ext,
                                         dictlabels,
                                         max_num_per_cate=None):
  print('forming metadata from: ' + train_dir)
  cate_names = os.listdir(train_dir)
  img_fns = []
  labels = []
  kept_cate_names = []
  skipped_cate = 0
  for i in range(len(cate_names)):
    if cate_names[i] in dictlabels:
      cur_dir = train_dir + cate_names[i] + '/'
      cur_cate_imgs = glob.glob(cur_dir + '*.' + img_ext)
      if not max_num_per_cate:
        one_max_num_per_cate = len(cur_cate_imgs)
      else:
        one_max_num_per_cate = max_num_per_cate
      for j in range(min(len(cur_cate_imgs), one_max_num_per_cate)):
        img_fns.append(cur_cate_imgs[j])
        labels.append(i - skipped_cate)
      kept_cate_names.append(cate_names[i])
      print('category {}/{} loaded.'.format(i + 1 - skipped_cate,
                                            len(dictlabels)))
    else:
      skipped_cate += 1

  return (img_fns, labels, kept_cate_names)


# fetch all infos about images under each category folder
def form_metadata_from_folder(train_dir, img_ext, max_num_per_cate=None):
  print('forming metadata from: ' + train_dir)
  cate_names = os.listdir(train_dir)
  img_fns = []
  labels = []
  for i in range(len(cate_names)):
    cur_dir = train_dir + cate_names[i] + '/'
    cur_cate_imgs = glob.glob(cur_dir + '*.' + img_ext)
    if not max_num_per_cate:
      one_max_num_per_cate = len(cur_cate_imgs)
    else:
      one_max_num_per_cate = max_num_per_cate
    for j in range(min(len(cur_cate_imgs), one_max_num_per_cate)):
      img_fns.append(cur_cate_imgs[j])
      labels.append(i)
    print('category {}/{} loaded.'.format(i + 1, len(cate_names)))

  return (img_fns, labels, cate_names)


def form_metadata_from_folders(train_dir, test_dir, img_ext, max_num_per_cate):
  (train_img_fns, train_labels, train_cate_names) = form_metadata_from_folder(
      train_dir, img_ext, max_num_per_cate)
  (test_img_fns, test_labels, test_cate_names) = form_metadata_from_folder(
      test_dir, img_ext, max_num_per_cate)
  return (train_img_fns, train_labels, test_img_fns, test_labels,
          train_cate_names)


# divide samples based on labels
def split_train_val_test(labels, train_ratio, val_ratio, test_ratio):
  assert (train_ratio + val_ratio + test_ratio == 1
          ), 'percentages must add up to 1'
  train_ids = []
  val_ids = []
  test_ids = []
  # split for each class fairly
  unique_labels = set(labels)
  for label in unique_labels:
    indices = [i for i, v in enumerate(labels) if v == label]
    num = len(indices)
    train_num = int(num * train_ratio)
    val_num = int(num * val_ratio)
    test_num = num - val_num - train_num
    all_ids = range(num)
    rand.shuffle(all_ids)
    train_ids += [indices[all_ids[id]] for id in range(train_num)]
    val_ids += [
        indices[all_ids[id]] for id in range(train_num, train_num + val_num)
    ]
    test_ids += [
        indices[all_ids[id]] for id in range(train_num + val_num, len(all_ids))
    ]
  return (train_ids, val_ids, test_ids)


def form_set_data(labels, max_num, verbose=False):
  """Generate label sets from sample labels.

  For each sample, generate a set by random sampling within the same class.
  Set is a tensor
  """
  # group sample ids based on label.
  label_ids = {}
  for idx in range(labels.size):
    if labels[idx] not in label_ids:
      label_ids[labels[idx]] = []
    label_ids[labels[idx]].append(idx)
  set_ids = {}
  for idx in range(labels.size):
    samp_ids = label_ids[labels[idx]][:]
    samp_num = min(max_num, len(samp_ids))
    set_ids[idx] = rand.sample(samp_ids, samp_num)
    if verbose:
      print "set {} formed.".format(idx)
  return set_ids


def form_sets(samples, labels, max_num, verbose=False):
  """Form sample and label sets.
  """
  # form training set data
  set_ids = form_set_data(labels, max_num, verbose)
  set_data = []
  set_labels = []
  print "forming set samples"
  sys.stdout.flush()
  count = 0
  for key, ids in set_ids.iteritems():
    # ignore small sets
    if len(ids) < max_num:
      continue
    set_data.append(samples[ids])
    set_labels.append(labels[key])
    count += 1
    if np.mod(count, 500) == 0:
      sys.stdout.write(".")
      #sys.stdout.write(".{}-{}".format(key,train_labels[key]))
  sys.stdout.write("\n")
  return set_data, set_labels, set_ids


def gen_pairs(labels, num, pos_ratio):
  """Create label pairs with the same label (positive)
  and different labels (negative).
  """
  N = len(labels)
  max_pair_num = N * (N - 1) / 2
  assert max_pair_num >= num and num < 1000, \
  'requested pair number can not exceed maximum num or num is larger than 1000'
  # generate all possible pairs (only feasible for small batch)
  same_cls_pairs = []
  diff_cls_pairs = []
  for id1 in range(len(labels)):
    for id2 in range(id1 + 1, len(labels)):
      if labels[id1] == labels[id2]:
        same_cls_pairs.append((id1, id2))
      else:
        diff_cls_pairs.append((id1, id2))
  # select pairs from both groups
  pos_num = min(int(num * pos_ratio), len(same_cls_pairs))
  neg_num = num - pos_num
  pos_ids = range(len(same_cls_pairs))
  neg_ids = range(len(diff_cls_pairs))
  rand.shuffle(pos_ids)
  sel_pos_ids = pos_ids[:pos_num]
  rand.shuffle(neg_ids)
  sel_neg_ids = neg_ids[:neg_num]
  sel_pos_pairs = [same_cls_pairs[idx] for idx in sel_pos_ids]
  sel_neg_pairs = [diff_cls_pairs[idx] for idx in sel_neg_ids]
  return sel_pos_pairs, sel_neg_pairs


def gen_cls_labels(labels):
  """Group labels.

  Args:
    labels: a list of labels.
  Returns:
    a dictionary mapping label to a list of ids.
  """
  unique_labels = list(set(labels))
  cls_labels = {}
  for one_label in unique_labels:
    cls_labels[one_label] = (np.where(labels == one_label))[0]
  return cls_labels


def gen_cls_combs(labels):
  """Generate exhaustive label pairs.

  Args:
    labels: a set of labels.
  Returns:
    a list of unique label pairs.
  """
  unique_labels = list(set(labels))
  # generate class combinations to cover all classes at least once
  cls_combs = []
  for idx in range(len(unique_labels)):
    cls1 = unique_labels[idx]
    for id2 in range(idx + 1, len(unique_labels)):
      cls2 = unique_labels[id2]
      cls_combs.append((cls1, cls2))
  return cls_combs


def gen_rand_cls_combs(labels, max_pairs_one_class=8):
  """Generate random label pairs.

  Args:
    labels: array of labels.
    max_pairs_one_class: maximum number of pairs with one class as first item.
  Returns:
    list of tuple of class pairs.
  """
  unique_labels = list(set(labels))
  # generate class combinations
  cls_combs = []
  cl1_range = range(len(unique_labels))
  for idx in cl1_range:
    cls1 = unique_labels[idx]
    cls1_pairs = 0
    # shuffle here some we take randomly the second item of the pair
    cls2_range = range(len(unique_labels))
    np.random.shuffle(cls2_range)
    for id2 in cls2_range:
      cls2 = unique_labels[id2]
      if cls1 != cls2:
        cls_combs.append((cls1, cls2))
        cls1_pairs += 1
      # at most `max_pairs_one_class` with one class in first position
      if cls1_pairs == max_pairs_one_class:
        break
  return cls_combs


def gen_triplet_from_cls_combs(cls_combs,
                               samples_labels,
                               max_triplet_per_pair=8):
  ''' Generate triplets (anchor, positive, negative) from all the provided pairs of classes.

    :param cls_combs: list of pairs of classes
    :param samples_labels: all the samples labels
    :return: triplets generated from these classes pairs
    '''
  triplets = []
  # for all class pairs
  for clp in cls_combs:
    c1_pos = np.where(samples_labels == clp[0])[0]
    c2_pos = np.where(samples_labels == clp[1])[0]
    if c1_pos.shape[0] == 0 or c2_pos.shape[0] == 0:
      print(
          '[gen_triplet_from_cls_combs: warning] Could not find samples for class pair {}-{}.'.
          format(clp[0], clp[1]))
      continue
    # build anchor, positive
    # jiefeng: this takes very long time to compute for large cls_combs
    ap = [p for p in itertools.combinations(c1_pos, 2)]
    # print "ap done"
    np.random.shuffle(c2_pos)
    # push triplets
    for i in range(min(len(ap), max_triplet_per_pair, len(c2_pos))):
      triplets.append([ap[i][0], ap[i][1], c2_pos[i]])
  return triplets


# generate samples from a class pair, return ids
def gen_samps_from_cls(labels, cls_pair, max_num_per_cls):
  cls1_ids = []
  cls2_ids = []
  N = len(labels)
  for id in range(N):
    if labels[id] == cls_pair[0]:
      cls1_ids.append(id)
    if labels[id] == cls_pair[1]:
      cls2_ids.append(id)
  samp_ids = []
  samp_ids.append(rand.sample(cls1_ids, min(max_num_per_cls, len(cls1_ids))))
  samp_ids.append(rand.sample(cls2_ids, min(max_num_per_cls, len(cls2_ids))))
  return samp_ids


# input: sample labels; number of triplets
def gen_random_triplets(labels, num):
  N = len(labels)
  unique_labels = list(set(labels))
  max_triplet_num = N * N * N
  assert max_triplet_num >= num and num < 10000000, \
  'requested triplet number can not exceed maximum num or num is larger than 10000000'
  # divide samples into classes
  cls_labels = {}
  for id in range(N):
    label = labels[id]
    if label not in cls_labels:
      cls_labels[label] = []
    cls_labels[label].append(id)

  # randomly sample
  triplet_ids = []
  # generate all possible pairs (only feasible for small batch)
  i = 0
  trials = 0
  while i < num and trials < 10 * num:
    trials = trials + 1
    anchor_id = rand.sample(range(N), 1)[0]
    sim_pool = cls_labels[labels[anchor_id]][:]
    sim_pool.remove(anchor_id)
    if len(sim_pool) == 0:
      i = i - 1
      continue
    sim_id = rand.sample(sim_pool, 1)[0]
    cls_pool = unique_labels[:]
    cls_pool.remove(labels[anchor_id])
    dis_cls = rand.sample(cls_pool, 1)[0]
    dis_id = rand.sample(cls_labels[dis_cls], 1)[0]
    triplet_ids.append([anchor_id, sim_id, dis_id])
    i = i + 1
  print "Random triplets created."
  return np.asarray(triplet_ids)


# generate triplets that have low intra-class similarity and large inter-class similarity
def gen_hard_triplets(feats, labels, num):
  # divide samples into classes
  unique_labels = list(set(labels))
  N = len(labels)
  cls_labels = {}
  for id in range(N):
    label = labels[id]
    if label not in cls_labels:
      cls_labels[label] = []
    cls_labels[label].append(id)

  # randomly sample anchors
  triplet_ids = []
  # generate all possible pairs (only feasible for small batch)
  for i in range(num):
    anchor_id = rand.sample(range(N), 1)[0]
    sim_pool = cls_labels[labels[anchor_id]][:]
    sim_pool.remove(anchor_id)
    # find hard positives
    Y = scipy.spatial.distance.cdist(
        np.matrix(feats[anchor_id]), feats[sim_pool], 'euclidean')
    sorted_ids = np.argsort(Y)[0][::-1]
    sorted_ids = np.asarray(sim_pool)[sorted_ids]
    # select one from first half
    sim_id = rand.sample(sorted_ids[:len(sorted_ids) / 2], 1)[0]
    # sample ids from other classes
    dis_pool = []
    for j in unique_labels:
      if j == labels[anchor_id]:
        continue
      dis_pool += cls_labels[j]
    # find hard negatives
    Y = scipy.spatial.distance.cdist(
        np.matrix(feats[anchor_id]), feats[dis_pool], 'euclidean')
    sorted_ids = np.argsort(Y)[0]
    sorted_ids = np.asarray(dis_pool)[sorted_ids]
    # select one from first half
    dis_id = rand.sample(sorted_ids[:len(sorted_ids) / 2], 1)[0]
    triplet_ids.append([anchor_id, sim_id, dis_id])

  # veritify triplet correctness
  for triplet in triplet_ids:
    assert labels[triplet[0]] == labels[triplet[1]] and labels[triplet[
        0]] != labels[triplet[2]]
  return np.asarray(triplet_ids)


''' image tools '''


# resize and crop to make sure image fits the model input
def prepare_img_for_test(im, mean_img):
  # Resize so smallest dim = 256, preserving aspect ratio
  h, w, _ = im.shape
  if h < w:
    im = skimage.transform.resize(im, (256, w * 256 / h), preserve_range=True)
  else:
    im = skimage.transform.resize(im, (h * 256 / w, 256), preserve_range=True)
  # Central crop to 224x224
  h, w, _ = im.shape
  im = im[h // 2 - 112:h // 2 + 112, w // 2 - 112:w // 2 + 112]
  # backup
  rawimg = np.copy(im).astype('uint8')
  print im.shape
  # Shuffle axes to c01, MXNX3 -> 3XMXN
  im = np.swapaxes(np.swapaxes(im, 1, 2), 0, 1)
  print im.shape
  # Convert to BGR
  im = im[::-1, :, :]
  # subtract mean
  if mean_img is not None:
    im = im - mean_img
  else:
    im = im - np.array([103.939, 116.779, 123.68])

  print('image prepared.')
  return rawimg, np.floatX(im[np.newaxis])


def get_meanimg(database='casia', size=(100, 100), nb_channels=1):
  mean_img_path = "data/" + database + "/mean_" + str(size[0]) + "x" + str(
      size[1]) + "_" + str(nb_channels) + "c.npy"
  mean_img = np.load(mean_img_path)
  mean_img = np.squeeze(mean_img)
  return mean_img


# load images into a numpy array
# if all images have same size or img_sz is provided, output NXHXWXC
# otherwise, an array of image objects with different dims
# img_fns is a numpy array with strings
def load_cv_imgs(img_fns, img_sz=(256, 256), use_bgr=True):
  nb_channels = 3
  if not use_bgr:
    nb_channels = 1

  imgs = [
  ]  #np.ndarray((len(img_fns), img_sz[0], img_sz[1], nb_channels), np.float32)
  for i in range(len(img_fns)):
    try:
      im = cv2.imread(img_fns[i])
      if im is None:
        print 'cannot read image {}'.format(img_fns[i])
        continue
      if img_sz is not None:
        im = cv2.resize(im, img_sz)
      if use_bgr:
        imgs.append(im)
      else:
        # keep same dim
        curimg = np.ndarray((im.shape[0], im.shape[1], 1), np.uint8)
        curimg[:, :, 0] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        imgs.append(curimg)
    except cv2.error as e:
      print 'img error: {}, {}'.format(img_fns[i], e.message)

  #print 'loaded {} cv images'.format(len(imgs))
  if len(imgs) == 0:
    print img_fns
  return np.asarray(imgs)


# img_fns is a numpy array with strings
def load_scipy_imgs(img_fns, img_sz=(256, 256), use_bgr=True):
  nb_channels = 3
  if not use_bgr:
    nb_channels = 1

  imgs = [
  ]  #np.ndarray((len(img_fns), img_sz[0], img_sz[1], nb_channels), np.float32)
  for i in range(len(img_fns)):
    try:
      #im = cv2.imread(img_fns[i])
      import scipy.ndimage as sni
      im = sni.imread(img_fns[i])
      if im is None:
        continue
      if img_sz is not None:
        im = cv2.resize(im, img_sz)
      if use_bgr:
        imgs.append(im)
      else:
        # keep same dim
        curimg = np.ndarray((im.shape[0], im.shape[1], 1), np.uint8)
        curimg[:, :, 0] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        imgs.append(curimg)
    except cv2.error as e:
      print 'img error: {}, {}'.format(img_fns[i], e.message)
  #print 'loaded {} cv images'.format(len(imgs))
  return np.asarray(imgs)


# load images into a numpy array
def load_crop_imgs(img_fns, img_bboxes, img_sz, use_bgr=True):
  nb_channels = 3
  if not use_bgr:
    nb_channels = 1
  imgs = np.ndarray((len(img_fns), nb_channels, img_sz[0], img_sz[1]),
                    np.float32)
  print imgs.shape
  for i in range(len(img_fns)):
    im = cv2.imread(img_fns[i])
    imcrop = np.ndarray((img_sz[0], img_sz[1], nb_channels), np.float32)
    xs, ys, xe, ye = img_bboxes[i][0], img_bboxes[i][1], img_bboxes[i][
        0] + img_bboxes[i][2], img_bboxes[i][1] + img_bboxes[i][3]
    # Check if im is bgr or grayscale here?
    if use_bgr:
      imcrop = im[xs:xe, ys:ye, :]
    else:
      imcrop = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
      im = imcrop[xs:xe, ys:ye]
    im = cv2.resize(imcrop, img_sz)
    if use_bgr:
      imgs[i, :, :, :] = im
    else:
      imgs[i, 0, :, :] = im
  return imgs


# load images into a numpy array
def load_crop_imgs_sets(img_fns_sets, img_bboxes_sets, img_sz, use_bgr=True):
  all_imgs = []
  for i in range(len(img_fns_sets)):
    all_imgs.append(
        load_crop_imgs(img_fns_sets[i], img_bboxes_sets[i], img_sz, use_bgr))
  return all_imgs


def prepare_face_img(test_img, mean_img, nb_channels=1):
  if nb_channels == 1 and test_img.shape[2] == 3:
    test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
  test_img = np.float32(test_img)
  input_img = (test_img - mean_img) * scale_factor
  if nb_channels == 1:
    input_arr = np.array([[input_img]])
  else:
    input_arr = np.array([np.transpose(input_img, (2, 0, 1))])
  return input_arr


# imgs are bgr format
def batch_prepare_imgs(imgs, mean_img):
  for img in imgs:
    #img = img - mean_img
    img = prepare_face_img(img, mean_img)
  return imgs


# visualize image in cnn format: num x ch x height x width
def vis_cnn_imgs(imgs):
  cv_imgs = cnn_to_cvimg(imgs)
  vis_cv_imgs(cv_imgs)


def vis_cv_imgs(imgs):
  for i in range(imgs.shape[0]):
    cv2.imshow('img', imgs[i])
    cv2.waitKey(0)


def vis_cv_imgfns(img_fns):
  cv_imgs = load_cv_imgs(img_fns, None)
  vis_cv_imgs(cv_imgs)


# convert opencv image to theano tensor format, color channel order needs to be handled outside
# N x H x W x CH -> N x CH x H x W
def cvimg_to_tensor_old(imgs):
  cnn_imgs = np.transpose(imgs, (
      0, 3, 1, 2))  #np.swapaxes(np.swapaxes(imgs, 2, 3), 1, 2) #
  return cnn_imgs


def cvimg_to_tensor(imgs):
  cnn_imgs = np.swapaxes(imgs, 1, 3)  #np.transpose(imgs, (0, 3, 1, 2))
  return cnn_imgs


# N x CH x H x W -> N x H x W x CH
def tensor_to_cvimg(imgs):
  cv_imgs = np.swapaxes(np.swapaxes(imgs, 1, 2), 2,
                        3)  #np.transpose(imgs, (0, 2, 3, 1))
  if cv_imgs.shape[-1] == 3:
    # change to bgr
    cv_imgs = cv_imgs[:, :, :, ::-1]
  return cv_imgs


''' 
preprocessing 
http://ufldl.stanford.edu/wiki/index.php/Data_Preprocessing
'''


# normalize to 0 mean and 1 std
# imgs_arr is numpy array in cnn format
def normalize_imgs(imgs_arr, mean, std):
  if mean is None:
    mean = np.mean(imgs_arr, 0)
  if std is None:
    std = np.std(imgs_arr, 0).clip(min=1)
  imgs_arr = (imgs_arr - mean) / std
  return imgs_arr, mean, std


def compute_mean_img(img_fns, img_sz):
  mean = None
  count = len(img_fns)
  for i in range(len(img_fns)):
    cv_img = cv2.imread(img_fns[i])
    if cv_img is None:
      raise ValueError(img_fns[i] + ' image read error')
    new_img = cv2.resize(cv_img, img_sz)
    if mean is None:
      mean = new_img.astype(np.float32)
    else:
      mean += new_img
  mean = mean / count
  return mean.astype(np.uint8)


class AugmentType:
  Crop = 0,
  Rotate = 1,
  Flip = 2,
  ColorShuffle = 3  # rgb channel shuffle


# take filename as input, return cnn images
def augment_imgfn(img_fn, max_set_sz, num_per_type, augment_types):
  # load image
  cv_imgs = load_cv_imgs(img_fn, (256, 256))
  cnn_img = cvimg_to_cnn(cv_imgs)
  return augment_img(cnn_img, max_set_sz, num_per_type, augment_types)


def augment_img(cnn_img, max_set_sz, num_per_type, augment_types):

  cv_img = cnn_to_cvimg(cnn_img)
  #print cv_img.shape
  all_imgs = cnn_img
  for aug_type in augment_types:
    if aug_type == AugmentType.Crop:
      crop_perc = 0.9
      #cv2.imshow('input', cv_img[0]/255)
      #cv2.waitKey(0)
      roi_size = [
          int(cv_img.shape[1] * crop_perc), int(cv_img.shape[2] * crop_perc)
      ]
      roi_tl_x = [0, cv_img.shape[1] - roi_size[0]]
      roi_tl_y = [0, cv_img.shape[2] - roi_size[1]]
      for i in range(num_per_type):
        sel_x = np.random.randint(roi_tl_x[0], roi_tl_x[1])
        sel_y = np.random.randint(roi_tl_y[0], roi_tl_y[1])
        cur_roi = [sel_x, sel_y, sel_x + roi_size[0], sel_y + roi_size[1]]
        cur_img = cv_img[0, cur_roi[0]:cur_roi[2], cur_roi[1]:cur_roi[3], :]
        cur_img_rz = cv2.resize(cur_img, (cnn_img.shape[3], cnn_img.shape[2]))
        #cv2.imshow('new', cur_img_rz)
        #cv2.waitKey(0)
        cur_img_new = np.reshape(cur_img_rz, (
            1, cur_img_rz.shape[0], cur_img_rz.shape[1], cur_img.shape[2]))
        cur_img_cnn = cvimg_to_cnn(cur_img_new)
        all_imgs = np.vstack((all_imgs, cur_img_cnn))
    if aug_type == AugmentType.Flip:
      # horizontal flip
      new_img = cv2.flip(cv_img[0], 1)
      new_img = cvimg_to_cnn([new_img])
      all_imgs = np.vstack((all_imgs, new_img))
      # vertical flip
      new_img = cv2.flip(cv_img[0], 0)
      new_img = cvimg_to_cnn([new_img])
      all_imgs = np.vstack((all_imgs, new_img))
      # all flip
      new_img = cv2.flip(cv_img[0], -1)
      new_img = cvimg_to_cnn([new_img])
      all_imgs = np.vstack((all_imgs, new_img))
    if aug_type == AugmentType.Rotate:
      # generate random angles
      (h, w) = cv_img[0].shape[:2]
      center = (w / 2, h / 2)
      angles = np.random.sample(num_per_type) * 360
      for angle in angles:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(cv_img[0], M, (w, h))
        new_img = cvimg_to_cnn([rotated])
        all_imgs = np.vstack((all_imgs, new_img))
    if aug_type == AugmentType.ColorShuffle:
      cur_img = cv_img[0, :, :, ::-1]
      new_img = cvimg_to_cnn([cur_img])
      all_imgs = np.vstack((all_imgs, new_img))

  # random sample max number of samples
  all_imgs = rand.sample(all_imgs, max_set_sz)
  return np.asarray(all_imgs)


''' common dataset manager '''


def load_mnist(data_fn, for_cnn=True, use_validset=True):
  print('loading mnist data from {}'.format(data_fn))
  with gzip.open(data_fn, 'rb') as f:
    data = pickle.load(f)  # encoding='latin-1'

  # The MNIST dataset we have here consists of six numpy arrays:
  # Inputs and targets for the training set, validation set and test set.
  X_train, y_train = data[0]
  X_val, y_val = data[1]
  X_test, y_test = data[2]

  if for_cnn == True:
    # The inputs come as vectors, we reshape them to monochrome 2D images,
    # according to the shape convention: (examples, channels, rows, columns)
    X_train = X_train.reshape((-1, 1, 28, 28))
    X_val = X_val.reshape((-1, 1, 28, 28))
    X_test = X_test.reshape((-1, 1, 28, 28))

  # The targets are int64, we cast them to int8 for GPU compatibility.
  y_train = y_train.astype(np.uint8)
  #y_train = np.reshape(y_train, (y_train.shape[0],1))
  y_val = y_val.astype(np.uint8)
  #y_val = np.reshape(y_val, (y_val.shape[0],1))
  y_test = y_test.astype(np.uint8)
  #y_test = np.reshape(y_test, (y_test.shape[0],1))

  if use_validset == False:
    # combine validation with train
    X_train = np.vstack((X_train, X_val))
    y_train = np.vstack((y_train, y_val))
    print('mnist data prepared. train size: {}; test size: {}'.format(
        X_train.shape[0], X_test.shape[0]))
    return X_train, y_train, X_test, y_test
  else:
    print('mnist data prepared. train size: {}; val size: {}; test size: {}'.
          format(X_train.shape[0], X_val.shape[0], X_test.shape[0]))
    return X_train, y_train, X_val, y_val, X_test, y_test


def load_cifar10(data_dir, for_cnn=True):
  print('loading cifar-10 data from {}'.format(data_dir))
  fns = {
      'train': [
          'data_batch_1', 'data_batch_2', 'data_batch_3', 'data_batch_4',
          'data_batch_5'
      ],
      'test': 'test_batch',
      'meta': 'batches.meta'
  }

  # data is a 2D numpy array, each row is a sample
  def format_data_for_cnn(data):
    cnn_data = data.reshape((-1, 3, 32, 32))
    return cnn_data

  def load_one_fn(data_fn):
    with open(data_fn, 'rb') as f:
      dict = pickle.load(f)
      # dict['data'] is a 2d numpy array; data['labels'] is a list
    return dict

  # training data
  train_data = []
  train_labels = []
  for fn in fns['train']:
    data = load_one_fn(data_dir + fn)
    train_labels += data['labels']
    train_data.append(format_data_for_cnn(data['data']))
  train_data = np.concatenate(train_data).astype(np.float32)
  train_labels = np.asarray(train_labels, dtype=np.int32)
  # test data
  data = load_one_fn(data_dir + fns['test'])
  test_data = format_data_for_cnn(data['data']).astype(np.float32)
  test_labels = np.asarray(data['labels'], dtype=np.int32)
  # normalize
  train_data, mean, std = normalize_imgs(train_data, None, None)
  test_data, _, _ = normalize_imgs(test_data, mean, std)
  print 'cifar10 loaded.'
  return train_data, train_labels, test_data, test_labels


if __name__ == '__main__':
  #Example CIFAR
  cifar10_dir = 'E:/Projects/Github/deeplearning/Data/cifar-10-python/'
  train_data, train_labels, test_data, test_labels = load_cifar10(cifar10_dir)
  #
  # cls = [1,1,1,2,2,3,3,4,4,5,5,6,6,7,7,7]
  # trips = gen_triplets(cls, 4)
  # print trips

  #(img_fns, labels, label_names) = form_metadata_from_folder('N:/product_data/EyeStyle/ShopStyle1/Images/')
  #print('total samples: {}\n category names: {}'.format(len(labels), label_names))
