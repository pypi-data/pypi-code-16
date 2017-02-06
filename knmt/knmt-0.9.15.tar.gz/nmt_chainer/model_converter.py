import numpy as np


old_paths = ['dec/attn_module/al_lin_h/W',
 'dec/attn_module/al_lin_h/b',
 'dec/attn_module/al_lin_o/W',
 'dec/attn_module/al_lin_s/W',
 'dec/bos_embeding',
 'dec/emb/W',
 
 'dec/gru/lateral/W',
 'dec/gru/upward/W',
 'dec/gru/upward/b',
 'dec/initial_cell',
 'dec/initial_state',
 
 'dec/lin_o/W',
 'dec/lin_o/b',
 'dec/maxo/linear/W',
 'dec/maxo/linear/b',
 'enc/emb/W',
 
 'enc/gru_b/lateral/W',
 'enc/gru_b/upward/W',
 'enc/gru_b/upward/b',
 'enc/initial_cell_b',
 'enc/initial_state_b',
 
 'enc/gru_f/lateral/W',
 'enc/gru_f/upward/W',
 'enc/gru_f/upward/b',
 'enc/initial_cell_f',
 'enc/initial_state_f']


new_paths = ['dec/attn_module/al_lin_h/W',
 'dec/attn_module/al_lin_h/b',
 'dec/attn_module/al_lin_o/W',
 'dec/attn_module/al_lin_s/W',
 'dec/bos_embeding',
 'dec/emb/W',
 
 'dec/gru/lstm/lateral/W',
 'dec/gru/lstm/upward/W',
 'dec/gru/lstm/upward/b',
 'dec/gru/initial_cell',
 'dec/gru/initial_state',
 
 'dec/lin_o/W',
 'dec/lin_o/b',
 'dec/maxo/linear/W',
 'dec/maxo/linear/b',
 'enc/emb/W',
 
 'enc/gru_b/lstm/lateral/W',
 'enc/gru_b/lstm/upward/W',
 'enc/gru_b/lstm/upward/b',
 'enc/gru_b/initial_cell',
 'enc/gru_b/initial_state',
 
 'enc/gru_f/lstm/lateral/W',
 'enc/gru_f/lstm/upward/W',
 'enc/gru_f/lstm/upward/b',
 'enc/gru_f/initial_cell',
 'enc/gru_f/initial_state',
 ]

assert len(old_paths) == len(new_paths)
conversion_dict = dict(zip(old_paths, new_paths))

def cmdline():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("original")
    parser.add_argument("new_file")
    args = parser.parse_args()
    
    model = np.load(args.original)
    
    dict_new_model = {}
    for k in model.keys():
        dict_new_model[conversion_dict[k]] = model[k]
        
    np.savez(args.new_file, **dict_new_model)

if __name__ == '__main__':
    cmdline()