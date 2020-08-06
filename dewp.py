 
import sys
import numpy as np
 
# approximation valid for
# 0 degC < T < 60 degC
# 1% < RH < 100%
# 0 degC < Td < 50 degC 
 
# constants
a = 17.271
b = 237.7 # degC
 
# sys.argv[0] is program name
#T=float(sys.argv[1])
#RH=float(sys.argv[2])
 
 
def dewpoint_approximation(T,RH):
 
    Td = (b * gamma(T,RH)) / (a - gamma(T,RH))
 
    return Td
 
 
def gamma(T,RH):
 
    g = (a * T / (b + T)) + np.log(RH/100.0)
 
    return g
 
 
#Td = dewpoint_approximation(T,RH)
#print ('T, RH',T,RH)
#print ('Td=',Td)
