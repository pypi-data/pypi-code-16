l = [1,2,3,4,5]# create a list
sume = lambda a, b: a+b #create a lambda function
print reduce(sume,l)

#from Fahrenheit to Celsius
f2C = lambda F: F * 5.0/9.0 - 32 * 5.0/9.0

#from Celsius to Fahrenheit 
C2f = lambda C: 32 + (9.0/5.0) * C

#map function
Tc = [1.6, 2.2, 4.9, 8.3, 12.8, 15.7, 17.2, 17.1, 14.2, 10.4, 5.6, 2.8, 9.4]

print map(C2f,Tc)

#Improve the previous function to make it return ”bigger”, ”smaller” and ”equal”

bigOsmall = lambda a,b: "bigger" if a > b else ("equal" if a==b else "smaller")  

print bigOsmall(5,8)

#Write a lambda function and print the elements 
#passed as an argument inside the standard output (use the sys module)

print reduce(lambda a: sys.argv(a),[1]) 
