"""
此函数可以迭代打印嵌套多层的列表中的数据项
"""
"""
这是“printapp”模块，提供了一个名为printapp()的函数，
这个函数的作用就是打印列表，其中有可能包含（也可能不包含）嵌套列表
"""
def print_app (the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_app(each_item)
        else:
            print(each_item)
fav_movies = [
    '赌神',['十里埋伏','刘德华'],['栀子花开',['李易峰','张慧雯'],'何炅','20150710'],'阳光照常升起','私人定制','夏洛特烦恼']

print_app(fav_movies)
