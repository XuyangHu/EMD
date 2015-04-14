'''
Created on 11/04/2015

@author: Andrew Chalmers
'''

import numpy as np
import scipy.optimize

def flow(f, D):
    f = np.reshape(f, D.shape)
    return (f * D).sum()

def groundDistance(x1, x2, norm = 2):
    return np.linalg.norm(x1-x2, norm)

def getDistMatrix(s1, s2, norm = 2):
    # rows = s1 feature length
    # cols = s2 feature length
    numFeats1 = s1[0].shape[0]
    numFeats2 = s2[0].shape[0]
    distMatrix = np.zeros((numFeats1, numFeats2))

    for i in range(0, numFeats1):
        for j in range(0, numFeats2):
            distMatrix[i,j] = groundDistance(s1[0][i], s2[0][j], norm)
    
    return distMatrix
    
# Constraints
def positivity(f):
    return f 

def fromSrc(f, wp, i, shape):
    fr = np.reshape(f, shape)
    f_sumColi = np.sum(fr[i,:])
    return wp[i] - f_sumColi

def toTgt(f, wq, j, shape):
    fr = np.reshape(f, shape)
    f_sumRowj = np.sum(fr[:,j])
    return wq[j] - f_sumRowj

def maximiseTotalFlow(f, wp, wq): 
    return f.sum() - np.minimum(wp.sum(), wq.sum())

# EMD formula, normalised by the flow
def EMD(F, D):  
    return (F * D).sum() / F.sum()
    
# 
def getEMD(P,Q, norm = 2):  
    """
    EMD computes the Earth Mover's Distance between
    the distributions P and Q
    
    P and Q are of shape (2,N)
    
    Where the first row are the set of N features
    The second row are the corresponding set of N weights
    
    The norm defines the L-norm for the ground distance
    Default is the Euclidean norm (norm = 2)
    """  
    
    D = getDistMatrix(P, Q, norm)
    
    numFeats1 = P[0].shape[0]
    numFeats2 = Q[0].shape[0]
    shape = (numFeats1, numFeats2)
    
    # Constraints  
    cons1 = [{'type':'ineq', 'fun' : positivity},
             {'type':'eq', 'fun' : maximiseTotalFlow, 'args': (P[1], Q[1],)}]
    
    cons2 = [{'type':'ineq', 'fun' : fromSrc, 'args': (P[1], i, shape,)} for i in range(numFeats1)]
    cons3 = [{'type':'ineq', 'fun' : toTgt, 'args': (Q[1], j, shape,)} for j in range(numFeats2)]
    
    cons = cons1 + cons2 + cons3
    

    # Solve for F (solve transportation problem) 
    F_guess = np.zeros(D.shape)
    F = scipy.optimize.minimize(flow, F_guess, args=(D,), constraints=cons)
    F = np.reshape(F.x, (numFeats1,numFeats2))
    
    return EMD(F, D)
    
# returns: signature1[features][weights], signature2[features, weights]
def getExampleSignatures():
    features1 = np.array([ np.array([100, 40, 22]), 
                          np.array([ 211, 20, 2 ]), 
                          np.array([ 32, 190, 150 ]), 
                          np.array([ 2, 100, 100 ]) ])
    weights1 = np.array([ 0.4, 0.3, 0.2, 0.1 ])

    features2 = np.array([ np.array([ 0, 0, 0 ]), 
                          np.array([ 50, 100, 80 ]), 
                          np.array([ 255, 255, 255 ]) ])
    weights2 = np.array([ 0.5, 0.3, 0.2 ])
    
    signature1 = np.array([features1, weights1])
    signature2 = np.array([features2, weights2])
    
    return signature1, signature2

if __name__ == '__main__':
    print 'EMD'
    
    # Setup
    P, Q = getExampleSignatures()
        
    # Get EMD
    emd = getEMD(P, Q)
    
    print emd, '== 160.54277'
    
    print 'Success'
    
    