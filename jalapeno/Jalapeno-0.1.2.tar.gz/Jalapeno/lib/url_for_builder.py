from flask import url_for
def filename_url_builder(dicts):
        for k,v in dicts.items():
                if isinstance(v,dict):
                        filename_url_builder(v)
                else:
                        
                        dicts[k] = url_for('static',filename=v)
                         
        return dicts
def path_url_builder(dicts,endpoint):
        for k,v in dicts.items():
                if isinstance(v,dict):
                        path_url_builder(v,endpoint)
                else:
                        
                        dicts[k] = url_for(endpoint,path=v)
                         
        return dicts