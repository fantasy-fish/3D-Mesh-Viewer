'''
filename: ssgtools.py
version: 0.21
description: SSG node definition and additional tools
by Jongmoo Choi (jongmooc@usc.edu)
'''
#############################################################
#
# Data Structure (Representation)
#
#############################################################

import numpy as np
import math

'''
CNode{ 
X, Y, Z - positions in global data coord system  (Z is redundant within a slice)
LBP - beam pointer to left neighbor node within a slice (looking into the structure)
RBP - beam pointer to right neighbor node within a slice (looking into the structure)
 
LJP - lower joist pointer list to nodes in lower slice (null terminate)
    - implement as a fixed length list of 5 (max) joists
    - null if LPP exists or current node is ground node

LPP - lower post pointer to node in lower slice
    - null if LJP exists or current node is ground node
 
PJP - parent joist pointer to node in upper slice
    - null if PPP exists or current node is top node

PPP - parent post pointer to node in upper slice
    - null if PJP exists or current node is top node
}
'''

class CMeta:
    def __init__(self, resolution = 1.0):
        self.resolution = resolution
        self.pillar_dist = 1.0
        self.joist_dist = resolution * 3.0
        self.group_pillar_dist = 5.0
        self.beamsnap180 = (90.0 + 90.0/2.0 + 90.0/2.0/2.0)
        self.beamsnap90 = 0
        self.L0_SHORT_BEAM = 0
        self.detectedchanges = []
        self.minnumberofcontours = 2
        self.mincontourlength = 30
        self.CONTOUR_SIMPLIFICATION = 0.005 # #CONTOUR_SIMPLIFICATION = 0.002 # for GT Yasu 


class CNode:
    def __init__(self, x, y, z):
        self.id = None
        self.label = None
        self.x = x
        self.y = y
        self.z = z
        self.LBP = None
        self.RBP = None
        self.LPP = None
        self.PPP = None
        self.LJP = []        
        self.PJP = []

        self.demconfidence = -1
        
        # to infer 3D corners
        self.corner = 0
        self.start = False
        self.end = False
        
        # slice, contour, node indices for the conversion (csv file <--> SSG)
        self.index_h = -1 # slice
        self.index_k = -1 # contour
        self.index_m = -1 # node

        self.angle2 = None
        #self.angle3 = None
        self.LBPlen = None
        self.RBPlen = None
        #self.LJPBlen = None
        #self.LPPlen = None

        #self.xx = x # updated?
        #self.yy = y
        self.simplification3D_post_aligned = False
        #self.angle3D_post_visited = False
        #self.weaknode = False
        #self.needmultiplejoists = False

        self.TBD = False
        self.TBDELETED = False 
        self.DEBUG = False # for visualization


def angleoftwovectors(v1, v2):
    # 
    # theta = np.arccos( np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))) * 180 / 3.141592
    #
    D = np.linalg.norm(v1) * np.linalg.norm(v2)
    if D < 0.0001:
        D = 0.0001

    component = np.dot(v1, v2) / D

    if component > 0.9999:
        component = 0.9999
    elif component < -0.9999:
        component = -0.9999
    else:
        pass
    return  np.arccos( component ) * 180 / 3.141592
    #return  np.arccos( np.dot(v1, v2) / D) * 180 / 3.141592

def L2dist(one, two):
    return math.sqrt((one.x - two.x)**2 + (one.y - two.y)**2 + (one.z - two.z)**2)

def computeangle(center, right, left): # or center, top, down
    p1 = center
    p2 = right
    p0 = left
    '''
    p1 = np.array([x1, y1, z1])
    p2 = np.array([x2, y2, z2])
    p0 = np.array([x0, y0, z0])
    '''
    v2 = p2 - p1
    v1 = p0 - p1
    return np.arccos( np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))) * 180 / 3.141592

def computeanglefromnodes(center, right, left): # or center, top, down
    p1 = np.array([center.x, center.y, center.z])
    p2 = np.array([right.x, right.y, right.z])
    p0 = np.array([left.x, left.y, left.z])
    
    return computeangle(p1, p2, p0)

def computeanglewrtvertical(top, down): # or center, top, down
    v1 = down - top  # heading to down
    v2 = np.array([0, 0, -1])
    return np.arccos( np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))) * 180 / 3.141592


def clearTBDmarker(SS):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].TBD = False
    return SS

def find_terminal_nodes(SS):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].label = None
                SS[h][k][m].start = None
                SS[h][k][m].end = None
                if SS[h][k][m].LPP and not(SS[h][k][m].PPP) and (len(SS[h][k][m].PJP)==0):
                    SS[h][k][m].start = True
                    SS[h][k][m].label = 'START'
                    continue
                if len(SS[h][k][m].LJP)>0 and not(SS[h][k][m].PPP) and (len(SS[h][k][m].PJP)==0):
                    SS[h][k][m].start = True
                    SS[h][k][m].label = 'START'                    
                    continue
                if SS[h][k][m].PPP and not(SS[h][k][m].LPP) and (len(SS[h][k][m].LJP)==0):
                    SS[h][k][m].end = True
                    SS[h][k][m].label = 'END'
                    continue
                if len(SS[h][k][m].PJP)>0 and not(SS[h][k][m].LPP) and (len(SS[h][k][m].LJP)==0):
                    SS[h][k][m].end = True
                    SS[h][k][m].label = 'END'
                    continue
    return SS

def find_corners_withH(SS, PARA):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if (SS[h][k][m].start == True):
                    if h in PARA.detectedchanges:
                        SS[h][k][m].corner = 1    
    return SS
        
#############################################################
#
# Read Data
#
#############################################################
def string2nodeid(n):
    h = int(n.split('_')[0])
    k = int(n.split('_')[1])
    m = int(n.split('_')[2])
    return h, k, m


def readssgcsv(INPUTFILE):
    import math    
    import csv
    
    SS = [] # SS graph that contains a list of slices
    S = [] # needs to be initialized at each slice
    C = [] # needs to be initialized at each contour

    # currnet pointer
    h = 0
    k = 0
    m = 0
    
    with open(INPUTFILE, 'rb') as csvfile:
        creader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for n in creader:
            if n[0][0] == '#':
                continue

            if math.isnan(float(n[2])):
                print h, k, m

            assert( not(math.isnan(float(n[2])) ))
            assert( not(math.isnan(float(n[3])) ))
            assert( not(math.isnan(float(n[4])) ))
        
            t = CNode(float(n[2]), float(n[3]), float(n[4]))
            t.id = n[0]
            t.label = n[1]

            t.LBP = n[5]
            t.RBP = n[6]
            t.LJP=n[7:12]
            t.LPP=n[12]
            t.PJP=n[13:18]
            t.PPP=n[18]
            
            th, tk, tm = string2nodeid(n[0])

            if th == h and tk == k and  tm >= 0: # adding a node on the contour
                C.append(t)
                #print t.id, 'C'
                m = tm
            elif th == h and tk == k + 1 and tm == 0: # adding a node on new contour
                S.append(C)
                C = []
                C.append(t)
                k = tk
                m = tm
                #print t.id, 'S'
            elif th == h + 1 and tk == 0 and tm == 0: # adding a slice
                S.append(C)
                SS.append(S)
                C = []
                S = []
                C.append(t)
                h = th
                k = tk
                m = tm
                #print t.id, 'SS'
            else:
                print 'error: 208'
                print 'id {} - th tk tm {} {} {} h k m {} {} {}\n'.format(t.id, th, tk, tm, h, k, m)
                assert(0)
                

        if len(C)>0:
            S.append(C)
            SS.append(S)

    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                #if SS[h][k][m].TBD:
                if 1:
                    t = SS[h][k][m]
                    
                    th, tk, tm = string2nodeid(t.LBP)
                    t.LBP = SS[th][tk][tm]
                    
                    th, tk, tm = string2nodeid(t.RBP)
                    t.RBP = SS[th][tk][tm]
                    
                    tmp = t.LJP
                    t.LJP = []
                    for i in tmp:
                        if i != 'None':
                            th, tk, tm = string2nodeid(i)
                            t.LJP.append(SS[th][tk][tm])
                        else:
                            break
                    
                    if t.LPP != 'None':
                        th, tk, tm = string2nodeid(t.LPP)
                        t.LPP = SS[th][tk][tm]
                        #print th, tk, tm, t.id
                    else:
                        t.LPP = None
                    
                    tmp = t.PJP
                    t.PJP = []
                    for i in tmp:
                        if i != 'None':
                            th, tk, tm = string2nodeid(i)
                            t.PJP.append(SS[th][tk][tm])
                        else:
                            break

                    if t.PPP != 'None':
                        th, tk, tm = string2nodeid(t.PPP)
                        t.PPP = SS[th][tk][tm]
                    else:
                        t.PPP = None
    return SS

#############################################################
#
# Write Data
#
#############################################################
def writessgcsv(OUTFILE, SS):
    # assign id
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].id = '{}_{}_{}'.format(h, k, m)

    # SS graph
    fid = open(OUTFILE,'w')
    fid.write('#id, label, x, y, z, LBP, RBP, LJP[0], LJP[1], LJP[2], LJP[3], LJP[4], LPP, PJP[0], PJP[1], PJP[2], PJP[3], PJP[4], PPP\n')
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                nodeid = SS[h][k][m].id
                label = SS[h][k][m].label
                x = SS[h][k][m].x
                y = SS[h][k][m].y
                z = SS[h][k][m].z
                
                if math.isnan(x) or math.isnan(y) or math.isnan(z):
                    print x, y, z
                
                LBP = 'None'
                RBP = 'None'

                LJP = ['None', 'None', 'None', 'None', 'None']
                LPP = 'None'

                PJP = ['None', 'None', 'None', 'None', 'None']
                PPP = 'None'
                
                if SS[h][k][m].LBP:
                    LBP = SS[h][k][m].LBP.id
                if SS[h][k][m].RBP:
                    RBP = SS[h][k][m].RBP.id
                if len(SS[h][k][m].LJP)>0:
                    for i in range(min(len(SS[h][k][m].LJP), 5)): # up to 5
                        LJP[i] = SS[h][k][m].LJP[i].id
                if SS[h][k][m].LPP:
                    LPP = SS[h][k][m].LPP.id
                if len(SS[h][k][m].PJP)>0:
                    for i in range(min(len(SS[h][k][m].PJP), 5)): # up to 5
                        PJP[i] = SS[h][k][m].PJP[i].id
                if SS[h][k][m].PPP:
                    PPP = SS[h][k][m].PPP.id
                tmp = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(nodeid, label, x, y, z, LBP, RBP, LJP[0], LJP[1], LJP[2], LJP[3], LJP[4], LPP, PJP[0], PJP[1], PJP[2], PJP[3], PJP[4], PPP)
                #print tmp
                fid.write(tmp)
    fid.close()
    
    # verify
    tmp = readssgcsv(OUTFILE)
   

def writessgnodesonly(OUTPATH):
    fid = open(OUTPATH,'w')
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].start == True:
                    x = SS[h][k][m].x
                    y = SS[h][k][m].y
                    z = SS[h][k][m].z
                    tmp = '{} {} {}\n'.format(x, y, z)
                    fid.write(tmp)
    fid.close()

def slicechangeindex1(histN):
    c1 = []
    for j in range(len(histN) - 1): # upto N-1
        #diff = (histN[j+1] - histN[j]) / ((histN[j+1] + histN[j]) / 2.0)
        diff = (histN[j+1] - histN[j]) / float(histN[j+1])
        c1.append(diff)
    c1[0] = 0

    # shift
    c1.insert(0,0)

    detections = []    
    for j in range(len(c1)):
        if c1[j] > 0.3:
            detections.append(j)
    
    return c1, detections


def contourchangeindex1(histN):
    c1 = []
    for j in range(len(histN) - 1): # upto N-1
        #diff = (histN[j+1] - histN[j]) / ((histN[j+1] + histN[j]) / 2.0)
        diff = (histN[j+1] - histN[j]) / float(histN[j+1])
        c1.append(diff)
    c1[0] = 0

    # shift
    # c1.insert(0,0)

    detections = []    
    for j in range(len(c1)):
        if abs(c1[j]) > 0.5:
            detections.append(j)
    
    return c1, detections

# test code    
if 0:
    infile = 'C:/Users/jongmooc/Dropbox/700 projects/cp.Core3D/GUI/v2_withSimplification/exe3/butterfly_out.csv'
    #infile = 'C:/Users/jongmooc/Dropbox/700 projects/cp.Core3D/GUI/v2_withSimplification/exe3/dormer_out.csv'
    SS = readssgcsv(infile)
    













