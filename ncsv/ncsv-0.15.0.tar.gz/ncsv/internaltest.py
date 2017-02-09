import numpy as np
import ncsv


y=[[-5,5,-5.03],[4,5,6],[7,8.43,3]]
print(ncsv.str_array(y))
y.insert(0,['one','two','three'])
print(ncsv.str_array(y,True, '--cf m -a a'))


x=np.random.gamma(10,size=(10,2))

print(ncsv.str_array(x,["first","second"],"-a a -s %0.2f --cf M"))


ld=[{'foo':1, 'faa':2},
   {'foo':False, 'faa':8.234},
   {'boo':00, 'faa':118.234},]
print(ncsv.str_list_dict(ld))


dl={
    'foob': [1,2,3,4,5,6,7],
    'geez': [4,6,2,5,10.0001]
   }
    
print(ncsv.str_dict_list(dl,options="--cf e"))


#ncsv.str_dict_list(dl,options="--cf e --iok")

print('End')
