#from selenium import webdriver
#browser = webdriver.Firefox()
#browser.get("http://localhost:8000")
#assert 'Django' in browser.title

print("hello")
#这是'print_List.py模块,提供了print_lol函数,用于打印嵌套列表

def print_lol(the_list,indent=Flase,level=0):
#这个函数取一个位置参数,名为this_list,这可以是任何一个python列表.所指定的列表中的每一项会
#(递归的)输出到屏幕上,各数据项各占一行
    for each_itme in the_list:
        if isinstance(each_itme,list):
            print_lol(each_itme,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t',end='')
            print(each_itme)
