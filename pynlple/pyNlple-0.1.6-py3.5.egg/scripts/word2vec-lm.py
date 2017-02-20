# score_data = data
# score_data = FileDataSource.read_dataframe_from_folder(p.join(root_folder, mentions, mentions_key), '.tsv', fill_na_map=fill_na_map, encoding='utf8')
# score_data = FileDataSource.read_dataframe(p.join(root_folder, out_mentions, mentions_key, 'all.tsv'), fill_na_map=fill_na_map, encoding='utf8')
# chars = u'йцукенгшщзхъэждлорпавыфячсмитьбюЙЦУКЕНГШЩЗХЪЭЖДЛОРПАВЫФЯЧСМИТЬБЮ'
# score_data = score_data[score_data['deleted'] == True]
# score_data = score_data[score_data['text'] != fill_na_map['text']]
# score_data = score_data[score_data['text'].apply(lambda t: any([char in t for char in chars]) and len(t) > 10)]
# score_data['log_likelihood'] = model.score(score_data.loc[:,'text'], total_sentences=len(score_data.loc[:,'text']))
# max_log = numpy.max(score_data.loc[:,'log_likelihood'])
# min_log = numpy.min(score_data.loc[:,'log_likelihood'])
# score_data['text_len'] = score_data['text'].apply(lambda t: len(t.split()))
# max_length = numpy.max(score_data.loc[:,'text_len'])
# score_data['norm_log_lh'] = (score_data.loc[:,'log_likelihood'] - max_log)
# score_data['norm_likelihood'] = numpy.exp(score_data.loc[:,'norm_log_lh']) / score_data.loc[:, 'text_len']
# score_data['log_lh_length'] = score_data.loc[:,'log_likelihood'] / score_data.loc[:,'text_len']
# max_norm_log = numpy.max(score_data.loc[:,'log_lh_length'])
# min_norm_log = numpy.min(score_data.loc[:,'log_lh_length'])
# score_data.loc[:,'norm_log_lh'] = score_data.loc[:,'norm_log_lh'] - max_norm_log
# score_data.loc[:,'norm_log_lh'] = normalize_a_b(score_data.loc[:,'log_lh_length'], min_norm_log, max_norm_log, 0, 1)
# score_data['likelihood'] = numpy.exp(score_data.loc[:,'log_lh_length'])
# min_likelihood = numpy.min(score_data.loc[:,'likelihood'])
# max_likelihood = numpy.max(score_data.loc[:,'likelihood'])
# score_data['norm_likelihood'] = normalize_a_b(score_data.loc[:,'likelihood'],
#                                               min_likelihood,
#                                               max_likelihood,
#                                               -1,
#                                               1)
# score_data['probability'] = score_data.loc[:,'likelihood'] / (1 + score_data.loc[:,'likelihood'])
# outpath = p.join(root_folder, out_mentions, mentions_key, 'all.tsv')
# score_data.to_csv(outpath, sep='\t', encoding='utf8')
#