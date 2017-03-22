import numpy as np
import sys
import json
import bhtsne

import logging
logging.basicConfig()
log = logging.getLogger("rnns:tsne")
log.setLevel(logging.INFO)

def cmd():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("model_file")
    parser.add_argument("voc_file")
    parser.add_argument("output")
    parser.add_argument("--save_tsne_result")
    parser.add_argument("--webgl", default = False, action = "store_true")
    parser.add_argument("--threed", default = False, action = "store_true")
    
    parser.add_argument("--num_voc", default = 0, type = int)
    parser.add_argument("--max_nb_ex", type = int)
    
    parser.add_argument("--dpath", default = "dec/emb/W")
    parser.add_argument("--list_keys", default = False, action = "store_true")
    
    parser.add_argument('-d', '--no_dims', type=int,
                          default=bhtsne.DEFAULT_NO_DIMS)
    parser.add_argument('-p', '--perplexity', type=float,
            default=bhtsne.DEFAULT_PERPLEXITY)
    # 0.0 for theta is equivalent to vanilla t-SNE
    parser.add_argument('-t', '--theta', type=float, default=bhtsne.DEFAULT_THETA)
    parser.add_argument('-r', '--randseed', type=int, default=bhtsne.EMPTY_SEED)
    parser.add_argument('-n', '--initial_dims', type=int, default=bhtsne.INITIAL_DIMENSIONS)
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args()
    
    log.info("loading model %s" % args.model_file)
    model = np.load(args.model_file)
    
    if args.list_keys:
        for key in model.keys():
            print key, model[key].shape
        sys.exit(0)
        
    data = model[args.dpath][:args.max_nb_ex]
    
    log.info("performing bh-tsne")
    res_list = []
    for result in bhtsne.bh_tsne(data, no_dims=args.no_dims, perplexity=args.perplexity, theta=args.theta, randseed=args.randseed,
            verbose=args.verbose, initial_dims=args.initial_dims):
        res_list.append(result)
        
    log.info("done performing bh-tsne")
    sne = np.array(res_list)
    
    if args.save_tsne_result is not None:
        log.info("saving tsne data to %s" % args.save_tsne_result)
        np.save(args.save_tsne_result, sne)
        
    
    log.info("sne shape: %r"%(sne.shape,))
    
    log.info("loading voc %s  [%i]" % (args.voc_file, args.num_voc))
    voc = json.load(open(args.voc_file))[args.num_voc][:args.max_nb_ex]
        
        
    log.info("ploting in %s" % args.output)
    
    import plotly
    import plotly.graph_objs as go
    
    if args.threed:
        trace = go.Scatter3d(
            x = sne[:,0],
            y = sne[:,1],
            z = sne[:,2] if sne.shape[1] >2 else 0,
            mode = 'markers',
            marker = dict(
                opacity = 0.7,
                size = 1,
                colorscale='Viridis',
                showscale=True,
                color = sne[:,3] if sne.shape[1] >3 else "#990000"
#                 colorscale='Viridis',
#                 showscale=True,
#                 z = sne[:,2] if sne.shape[1] >2 else "#990000"
#                 line = dict(
#                     width = 1, 
#                     color = '#404040')
            ), 
            text = voc,
        )   
    elif args.webgl:
        trace = go.Scattergl(
            x = sne[:,0],
            y = sne[:,1],
            mode = 'markers',
            marker = dict(
                opacity = 0.7,
                colorscale='Viridis',
                showscale=True,
                color = sne[:,2] if sne.shape[1] >2 else "#990000"
#                 line = dict(
#                     width = 1, 
#                     color = '#404040')
            ), 
            text = voc,
        )
    else:
        trace = go.Scatter(
            x = sne[:,0],
            y = sne[:,1],
            mode = 'markers+text',
            marker = dict(
                opacity = 0.7,
                line = dict(
                    width = 1, 
                    color = '#404040')
            ), 
            text = voc,
            textposition='top right',
        )

    plotly.offline.plot([trace], filename=args.output)

    
    
if __name__ == '__main__':
    cmd()