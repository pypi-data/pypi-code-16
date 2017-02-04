import os
from flask import url_for
class Mgr(object):

        def __init__(self,path):
                self.path = path
                self.name = 'theme_static'
        def dir(self):
                return self.path
        def tree_dict(self):    
                return self.tree(self.dir())
        def tree(self,path,relative_path=''):
                '''
                        Return a recursively nested dict of files under root path
                '''
                L={}
                content=os.listdir(path)
                for each in content:
                        each_path = path+os.sep+each                                    
                        record = relative_path + each + os.sep
                        #except
                        if each[0]=='.' or 'pycache' in each or 'build' in each or 'fonts' in each:
                                continue 
                        ##this line is for numeric folder (articleimg)
                        if each.isdigit():
                                each = int(each)
                        else:
                                each = str(each)
                        if os.path.isdir(each_path):
                                L[each]=self.tree(path=each_path,relative_path=record)
                        else:
                                L[each.split('.',1)[0]] = relative_path+each
                return L
        def target(self,target,dirs=None,key='',relative=True):
                '''
                        find and return a specific file dict by name under root path
                        target: specific dir name
                        url:
                                True: url_for with relative path
                                False: relative path
                                None: Nothing change
                '''
                if not dirs:dirs = self.tree_dict()
                for k,v in dirs.items():
                        if isinstance(v,dict):
                                hold = self.target(target,key=k,dirs=v)
                                if hold:return hold 
                        elif relative:
                                dirs[k]=dirs[k].split(target+os.sep,1)[-1]
                        else:
                                pass
                                #relative = dirs[k].split(target+os.sep,1)[-1]
                                #dirs[k] = url_for('static',filename=relative)
                return dirs if key == target else None

        def url_builder(self,dicts):
                for k,v in dicts.items():
                        if isinstance(v,dict):
                                self.url_builder(v)
                        else:
                                
                                dicts[k] = url_for('static',filename=v)
                                 
                return dicts


















                                           
