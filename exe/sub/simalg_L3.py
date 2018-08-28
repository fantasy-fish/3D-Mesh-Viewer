'''
filename: simalg_L3.py
version: 0.21
description: simplification algorithms (Level 3)
Version 0.1: delete nodes and beams
by Jongmoo Choi (jongmooc@usc.edu)
'''
# simplifications

import numpy as np
import ssgtools

#############################################################
#
# Detele R4.999: Remove each node that has the 'TBDELETED' marker
#
#############################################################
def deletenode_marked(SS): # delete each node that has the 'TBDELETED' marker
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            CHECKEDALL = 1
            while(CHECKEDALL):
                CHECKEDALL = 0
                for m in range(len(SS[h][k])): # each node
                    if SS[h][k][m].TBDELETED:
                        SS[h][k].pop(m)
                        CHECKEDALL = 1
                        break    
    return SS

#############################################################
#
# 3D simplification -- delete isolated nodes (Remove nodes with no vertical connections)
#
#############################################################
def sim_rule_L31(SS, PARA):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if not(SS[h][k][m].PPP) and len(SS[h][k][m].PJP) == 0 and not(SS[h][k][m].LPP) and len(SS[h][k][m].LJP) == 0:
                    SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                    SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                    SS[h][k][m].TBDELETED = True
                    
    deletenode_marked(SS)
    return SS
    
#############################################################
#
# 3D simplification -- delete isolated contours (DONE)
#
#############################################################
def sim_rule_L32_v1(SS, PARA):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            FLAG = True
            for m in SS[h][k]: # each node
                # no connections
                if m.PPP or len(m.PJP)>0 or m.LPP or len(m.LJP)>0:
                    FLAG = False
                    break
            if FLAG:
                for m in SS[h][k]: # each node
                    m.TBDELETED = True
                    
    deletenode_marked(SS)
    return SS

def sim_rule_L32(SS, PARA):
    #dlist = []
    for h in range(len(SS)): # each slices
        if len(SS[h])>1: # at least one
            for k in range(len(SS[h])): # each contour
                FLAG = True
                for m in SS[h][k]: # each node
                    # no connections
                    if m.PPP or len(m.PJP)>0 or m.LPP or len(m.LJP)>0:
                        FLAG = False
                        break
                if FLAG:
                    for m in SS[h][k]: # each node
                        m.LBP = None
                        m.RBP = None
    deletenode_marked(SS)
    return SS



#############################################################
#
# 3D simplification -- delete snap node = align beams and delete the (pillar) nodes (DONE)
#
#############################################################
def sim_rule_L33(SS, PARA):
    SS = ssgtools.clearTBDmarker(SS)    
        
    nodelist = []
    
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                x1 = SS[h][k][m].x
                y1 = SS[h][k][m].y
                x2 = SS[h][k][m].RBP.x
                y2 = SS[h][k][m].RBP.y
                x0 = SS[h][k][m].LBP.x
                y0 = SS[h][k][m].LBP.y

                p1 = np.array([x1, y1])
                p2 = np.array([x2, y2])
                p0 = np.array([x0, y0])
                
                v2 = p2 - p1
                v1 = p0 - p1
                                   
                theta = ssgtools.angleoftwovectors(v1, v2)
                
                # store the measure 
                SS[h][k][m].angle2 = theta

                if abs(theta) > (90.0 + 90.0/2.0 + 90.0/2.0/2.0):
                    a = p2 - p0
                    b = p1 - p0 #-v1
                    
                    unitvec = a / np.linalg.norm(a)
                    s = np.dot(b, unitvec)
                    q = p0 + s * unitvec

                    SS[h][k][m].x = q[0]
                    SS[h][k][m].y = q[1]
                    # insert into the stack
                    nodelist.append(SS[h][k][m])
                    SS[h][k][m].TBDELETED = True
                    #SS[h][k][m].DEBUG = True
    
    for i in nodelist:
        if len(i.LJP)>0 or len(i.PJP)>0:
            i.TBDELETED = False
        else:
            if i.PPP:
                i.PPP.LPP = None
            if i.LPP:
                i.LPP.PPP = None
            i.LBP.RBP = i.RBP
            i.RBP.LBP = i.LBP
        
    deletenode_marked(SS)    
    return SS


#############################################################
#
# 3D simplification -- delete short edges
#
#############################################################
def sim_rule_L34(SS, PARA):
    SS = ssgtools.clearTBDmarker(SS)
    SS = ssgtools.find_terminal_nodes(SS)
        
    # for short pillars
    if 1:
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if 0 and SS[h][k][m].LPP:
                        #SS[h][k][m].DEBUG = True                    
                        pass
                    if 0 and SS[h][k][m].start:
                        #SS[h][k][m].DEBUG = True
                        pass
                    if 1 and ( SS[h][k][m].start and len(SS[h][k][m].LJP)==0 and 
                            SS[h][k][m].LPP.end and len(SS[h][k][m].LPP.PJP)==0):
                        #SS[h][k][m].TBDELETED = True
                        #SS[h][k][m].LPP.TBDELETED = True  # DO NOT DELETE! it can be a corner 
                        
                        #SS[h][k][m].DEBUG = True
                        #SS[h][k][m].LPP.DEBUG = True                    
    
                        SS[h][k][m].start = None
                        SS[h][k][m].LPP.end = None
                        SS[h][k][m].LPP.PPP = None                    
                        SS[h][k][m].LPP = None
        #deletenode_marked(SS)    

    # for short joists                    
    if 1:
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if ( SS[h][k][m].start and len(SS[h][k][m].LJP)==1 and 
                            SS[h][k][m].LJP[0].end and len(SS[h][k][m].LJP[0].PJP)==1):
                        #SS[h][k][m].TBDELETED = True
                        #SS[h][k][m].LPP.TBDELETED = True  # DO NOT DELETE! it can be a corner 
                        
                        #SS[h][k][m].DEBUG = True
                        #SS[h][k][m].LJP[0].DEBUG = True                    
    
                        SS[h][k][m].start = None
                        SS[h][k][m].LJP[0].end = None
                        SS[h][k][m].LJP[0].PJP = []                    
                        SS[h][k][m].LJP = []
    return SS


#############################################################
#
# 3D simplification -- delete pan joist nodes
#
#############################################################
def sim_rule_L35(SS, PARA):
    SS = ssgtools.clearTBDmarker(SS)    
        
    nodelist = []
    
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if len(SS[h][k][m].PJP) > 1:
                    nodelist.append(SS[h][k][m])

    
    for i in nodelist:
        # visit all leaves
        stacklist = [i] # per node
        winnerlist = []
        looserlist = []
        history = []

        while len(stacklist)>0:
            newstacklist = []
            for n in stacklist:
                history.append(n)
                if len(n.PJP)>0: # has parents
                    for j in n.PJP:
                        newstacklist.append(j) # insert all parents
                        #j.DEBUG = True
            stacklist = newstacklist

            if len(stacklist)>0: # because the lastest stack contains the longer joists
                winnerlist = stacklist
        
        # find the winner
        if len(winnerlist)==1:
            #winnerlist[0].DEBUG = True
            Bestnode = winnerlist[0]
        else: # find the shortest one
            Bestdist = 999999
            Bestnode = None
            for candi in winnerlist:
                dist = ssgtools.L2dist(i, candi)
                if dist < Bestdist:
                    Bestdist = dist
                    Bestnode = candi
            #Bestnode.DEBUG = True
        #i.DEBUG = True        

        for n in history:
            if n == i:
                #print 'a'
                pass
            elif n == Bestnode:
                #print 'b'
                pass
            else:
                #n.DEBUG = True
                if len(j.PJP)==0 and len(j.LJP)>0:
                    index = j.LJP[0].PJP.index(j)
                    j.LJP[0].PJP.pop(index)
                    j.LJP = []

    return SS

