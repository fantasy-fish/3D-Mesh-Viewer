'''
filename: line3dfit.py
version: 0.1
description: 3d line fit to joists
by Jongmoo Choi (jongmooc@usc.edu)
'''
# https://www.codefull.org/2015/06/3d-line-fitting/
# https://stackoverflow.com/questions/2298390/fitting-a-line-in-3d

import numpy as np

def fit(data):
    # Calculate the mean of the points, i.e. the 'center' of the cloud
    datamean = data.mean(axis=0)
    
    # Do an SVD on the mean-centered data.
    try:
        uu, dd, vv = np.linalg.svd(data - datamean)
    except:
        print data
        print datamean
        assert(0)
    return datamean, vv[0] 

def move(data):
     mean, vv = fit(data)

     unitvec = vv / np.linalg.norm(vv)

     new = []
     for p in data:
         s = np.dot(p - mean, unitvec)
         #print s
         q = mean + s * vv
         new.append(q)       
     return np.array(new)

def movencheck(data):
     mean, vv = fit(data)

     unitvec = vv / np.linalg.norm(vv)

     new = []
     maxdelta = 0
     for p in data:
         s = np.dot(p - mean, unitvec)
         #print s
         q = mean + s * vv
         new.append(q)
         delta = np.linalg.norm(p - q)
         if delta > maxdelta:
             maxdelta = delta
     return np.array(new), maxdelta

# simple method using two fixed points
def movencheck_fixedheight(data):
     vv = data[-1] - data[0]
     anchor = data[0]

     unitvec = vv / np.linalg.norm(vv)
     
     new = []
     maxdelta = 0
     for p in data:
         s = np.dot(p - anchor, unitvec)
         #print s
         q = anchor + s * vv

         if vv[2]==0.0:
             vv[2] = 0.000001
         
         # m.z + alpha vv.z = p.z
         alpha = (p[2] - anchor[2]) / vv[2]
         q = anchor + alpha * vv
         
         new.append(q)
         delta = np.linalg.norm(p - q)
         if delta > maxdelta:
             maxdelta = delta
     return np.array(new), maxdelta

# fit a 3D line to the data
def movencheck_fixedheight_linefit(data):
    mean, vv = fit(data)

    unitvec = vv / np.linalg.norm(vv)
     
    new = []
    maxdelta = 0
    for p in data:
        s = np.dot(p - mean, unitvec)
        #print s
        q = mean + s * vv
        
        if vv[2]==0.0:
            vv[2] = 0.000001
        
        # m.z + alpha vv.z = p.z
        alpha = (p[2] - mean[2]) / vv[2]
        q = mean + alpha * vv
         
        new.append(q)
        delta = np.linalg.norm(p - q)
        if delta > maxdelta:
            maxdelta = delta
    '''      
    # check
    if not(np.isnan(new)):
        return np.array(new), maxdelta
    else:
        return data, 0
    '''
    return np.array(new), maxdelta