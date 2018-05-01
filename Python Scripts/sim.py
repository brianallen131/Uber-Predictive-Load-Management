import copy
import random
import numpy
import matplotlib.pyplot as plt

def zero_one(prob):
    if(random.random()<prob):
        return 1
    else:
        return 0

def arrivals_two(time,rate1,rate2):
    list1 = numpy.cumsum(numpy.random.exponential(scale = 1/rate1,size = int(rate1)))
    list2 = numpy.cumsum(numpy.random.exponential(scale = 1/rate2,size = int(rate2)))
    zeros = numpy.zeros(int(rate1),dtype=int)
    ones = numpy.ones(int(rate2),dtype=int)
    dict1 = dict(zip(list1,zeros))
    dict2 = dict(zip(list2,ones))
    finaldict = {**dict1,**dict2}

    ret = []
    for time in sorted(finaldict):
        ret.append(finaldict[time])

    return ret

def simulate(arrivals,N,x):
    '''
    arrivals is a list of arrival orders with 0 being the most central area
    n is an array where n[i] is the number of cars in area i
    x is the probability array: x[i][j] is the prob that customer in area i takes Uber if other car is in area j
    '''
    stacks = copy.deepcopy(N)

    y = [0]*len(N)
    for request in arrivals:
        src = request
        while(src<len(N) and stacks[src]==0):
            src += 1

        if src != len(N):
            stacks[src] -= 1

        if(zero_one(x[request][src]) == 1):
            y[request] += 1
            #print('customer from',request,'accepted a ride from',src)
        else:
            pass
            #print('customer from',request,'rejected a ride from',src)
        #print('remaining cars in locations:',stacks)
    return y, stacks[0]

def best_n(D):
    max_N = 50
    max_prof = 0
    for N in range(50,130):
        ret = [0,0,0]
        simsize = 100
        for i in range(simsize):
            arr, stack = simulate(arrivals_two(60.0,D,20.0),[N,43],[[0.99,0.68,0.17],[0.68,0.99,0.54]])
            ret[0] += arr[0]
            ret[1] += arr[1]
            ret[2] += stack

        prof = 1.5*9.03*(ret[0]+ret[1])/simsize-8*(N-5)
        if(ret[2]/simsize > 5):
            prof -= 25*(ret[2]/simsize-5)
        if prof>max_prof:
            max_prof = prof
            max_N = N
    return max_N, max_prof

f = open('out_3.csv','w')
for D in range(80,120):
    N, prof = best_n(D)
    f.write(str(D)+','+str(prof)+'\n')
f.close()

Sensitivity = []
f = open('out_4.csv','w')

for D in range(80,120):
    #N, OptProfit = best_n(D)
      # find optimal profit for the current actual demand D
    ret = [0,0,0]

    simsize = 10000
    for i in range(simsize):
        arr, stack = simulate(arrivals_two(60.0,D,20.0),[85,43],[[0.99,0.68,0.17],[0.68,0.99,0.54]])  # N = 82 because we believe D=100
        ret[0] += arr[0]
        ret[1] += arr[1]
        ret[2] += stack

    prof = 1.5*9.03*(ret[0]+ret[1])/simsize-8*(85-5)
    if(ret[2]/simsize > 5):
        prof -= 25*(ret[2]/simsize-5)
    #diffInProf = prof-OptProfit
    #Sensitivity.append((D,diffInProf))
    f.write(str(D)+','+str(prof)+'\n')
f.close()

