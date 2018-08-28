'''
filename: simalg.py
version: 0.21
description: simplification algorithms
Version 0.2: contains basic Level 1 simplification algorithms
by Jongmoo Choi (jongmooc@usc.edu)
'''
# simplifications

import numpy as np
import line3dfit
import ssgtools
#import checkcollision
import simalg_L3

#############################################################
#
# simplification codes
#
#############################################################

#############################################################
#
# 3D simplification -- connect joists/pillars
#
#############################################################
def sim_rule_L11(SS, PARA):
    print 'group joists/pillars'
    SS = ssgtools.find_terminal_nodes(SS)
    S_list = []
    E_list = []
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].start and not(SS[h][k][m].end):  # get isolated "start" nodes
                    S_list.append(SS[h][k][m])
                    SS[h][k][m].index_h = h
                    SS[h][k][m].index_k = k
                    SS[h][k][m].index_m = m
                if SS[h][k][m].end and not(SS[h][k][m].start):
                    E_list.append(SS[h][k][m])
                    SS[h][k][m].index_h = h
                    SS[h][k][m].index_k = k
                    SS[h][k][m].index_m = m
    
    for e in E_list:
        mindist = 999999 # max
        minnode = None
        for s in S_list:
            if s.index_h > e.index_h: # find it below slices
                dist = ssgtools.L2dist(e, s)
                if dist < mindist:
                    mindist = dist
                    minnode = s 
        if minnode and mindist < PARA.joist_dist: # 15
            if not(e.PPP): # joist type
                e.LJP.append(minnode)
                minnode.PJP.append(e)
                #e.end = False
                #minnode.start = False                    
            else: # pillar 
                e.LPP = minnode
                minnode.PPP = e
                #e.end = False
                #minnode.start = False
    return SS


def sim_rule_L111(SS, PARA):
    print 'group pillars only'
    SS = ssgtools.find_terminal_nodes(SS)
    S_list = []
    E_list = []
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].start and not(SS[h][k][m].end):  # get isolated "start" nodes
                    S_list.append(SS[h][k][m])
                if SS[h][k][m].end and not(SS[h][k][m].start):
                    E_list.append(SS[h][k][m])
    
    for e in E_list:
        mindist = 999999 # max
        minnode = None
        for s in S_list:
            if s.index_h > e.index_h: # find it below slices
                dist = ssgtools.L2dist(e, s)
                if dist < mindist:
                    mindist = dist
                    minnode = s 
        if minnode and mindist < PARA.group_pillar_dist: # 15
            if e.PPP and len(minnode.PJP)==0 and len(e.LJP)==0: # pillar
                e.LJP.append(minnode)
                minnode.PJP.append(e)
    return SS

            
#############################################################
#
# 3D simplification -- connect butterfly Js
#
#############################################################
def sim_rule_L12(SS, PARA):
    print 'group two end of joists'
    SS = ssgtools.find_terminal_nodes(SS)    
    S_list = []
    E_list = []
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].start and not(SS[h][k][m].end):  # get isolated "start" nodes
                    S_list.append(SS[h][k][m])
                    SS[h][k][m].index_h = h
                    SS[h][k][m].index_k = k
                    SS[h][k][m].index_m = m
                if SS[h][k][m].end and not(SS[h][k][m].start):
                    E_list.append(SS[h][k][m])
                    SS[h][k][m].index_h = h
                    SS[h][k][m].index_k = k
                    SS[h][k][m].index_m = m
    
    for e1 in E_list:
        mindist = 999999 # max
        minnode = None
        for e2 in E_list:
            if e1.index_h == e2.index_h and e1 != e2: # find it on the same slice
                dist = ssgtools.L2dist(e1, e2)
                if dist < mindist:
                    mindist = dist
                    minnode = e2
        if minnode and mindist < PARA.joist_dist:  
            if not(e1.PPP) and not(minnode.PPP): # joist type
                e1.x = (e1.x + minnode.x) / 2.0
                e1.y = (e1.y + minnode.y) / 2.0
                minnode.x = (e1.x + minnode.x) / 2.0
                minnode.y = (e1.y + minnode.y) / 2.0
                #e1.corner = 2
                #minnode.corner = 2
            else: # pillar 
                pass
    return SS


#############################################################
#
# 3D simplification -- align joists 
#
#############################################################
def sim_rule_L13a(SS, PARA):
    print 'aligning multi-angle joist'

    SS = ssgtools.clearTBDmarker(SS)

    joist_set = [] # contains lists each of that contains nodes in the contiguous joists
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if not(SS[h][k][m].TBD) and len(SS[h][k][m].LJP)>0:
                    LIST = []
                    pts = SS[h][k][m]
                    while(pts != None):
                        LIST.append(pts)
                        if len(pts.LJP)>0:
                            pts = pts.LJP[0]
                        else:
                            pts = None
                        if pts != None:
                            pts.TBD = True
    
                    data = []
                    for i in LIST:
                        data.append([i.x, i.y, i.z])
                    data2, margin = line3dfit.movencheck_fixedheight_linefit(np.array(data))
                    #print 'max residual', margin
                    if margin < (PARA.joist_dist / 3.0):  # ex: hexagonal gazebo
                        for idx in range(len(LIST)):
                            i = LIST[idx]
                            i.x = data2[idx][0]
                            i.y = data2[idx][1]
                        #LIST[0].start = True
                        #LIST[-1].end = True
                    else: # it detects the multi-angle joist
                        joist_set.append(LIST)
    
    # process rejected joists
    while len(joist_set) > 0:
        joist = joist_set.pop()
    
        if len(joist) < 3:
            pass # nothing.
        else:
            start_node = joist[0]
            end_node = joist[-1]
            #start_node.start = True
            #end_node.end = True
            
            # compute curvature
            curvature_list = []
            for n in joist[1:-1]:
                n.DEBUG = False
                curvature_list.append(ssgtools.computeanglefromnodes(n, start_node, end_node)) # or center, top, down
    
            # find 3D corner
            min_angle = min(curvature_list)
            minindex = curvature_list.index(min_angle)
            i = joist[minindex + 1]
            #i.corner = 2
            
            # break the joist into two edges
            listA = joist[:minindex + 1 + 1]
            listB = joist[minindex + 1:]

            # fit 3D line ---- A
            data = []
            for i in listA:
                data.append([i.x, i.y, i.z])
            #data2 = line3dfit.move(np.array(data))
            data2, margin = line3dfit.movencheck_fixedheight_linefit(np.array(data))
            if margin < 1:  # 5 is good for hexagonal gazebo
                for idx in range(len(listA)):
                    i = listA[idx]
                    i.x = data2[idx][0]
                    i.y = data2[idx][1]
            else: # it detects the multi-angle joists
                joist_set.append(listA)
    
            # fit 3D line ---- B
            data = []
            for i in listB:
                data.append([i.x, i.y, i.z])
            #data2 = line3dfit.move(np.array(data))
            data2, margin = line3dfit.movencheck_fixedheight_linefit(np.array(data))
            if margin < (PARA.joist_dist / 3.0):  # 5 is good for hexagonal gazebo
                for idx in range(len(listB)):
                    i = listB[idx]
                    i.x = data2[idx][0]
                    i.y = data2[idx][1]
            else: # it detects the multi-angle joists
                joist_set.append(listB)
    return SS


#############################################################
#
# 3D simplification -- align joists (DUPLICATED except the line fit function)
#
#############################################################
def sim_rule_L13b(SS, PARA):
    print 'aligning multi-angle joist'

    SS = ssgtools.clearTBDmarker(SS)

    joist_set = [] # contains lists each of that contains nodes in the contiguous joists
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if not(SS[h][k][m].TBD) and len(SS[h][k][m].LJP)>0:
                    LIST = []
                    pts = SS[h][k][m]
                    while(pts != None):
                        LIST.append(pts)
                        if len(pts.LJP)>0:
                            pts = pts.LJP[0]
                        else:
                            pts = None
                        if pts != None:
                            pts.TBD = True
    
                    data = []
                    for i in LIST:
                        data.append([i.x, i.y, i.z])
                    data2, margin = line3dfit.movencheck_fixedheight(np.array(data))
                    #print 'max residual', margin
                    if margin < (PARA.joist_dist / 3.0):  # ex: hexagonal gazebo
                        for idx in range(len(LIST)):
                            i = LIST[idx]
                            i.x = data2[idx][0]
                            i.y = data2[idx][1]
                        #LIST[0].start = True
                        #LIST[-1].end = True
                    else: # it detects the multi-angle joist
                        joist_set.append(LIST)
    
    # process rejected joists
    while len(joist_set) > 0:
        joist = joist_set.pop()
    
        if len(joist) < 3:
            pass # nothing.
        else:
            start_node = joist[0]
            end_node = joist[-1]
            #start_node.start = True
            #end_node.end = True
            
            # compute curvature
            curvature_list = []
            for n in joist[1:-1]:
                n.DEBUG = False
                curvature_list.append(ssgtools.computeanglefromnodes(n, start_node, end_node)) # or center, top, down
    
            # find 3D corner
            min_angle = min(curvature_list)
            minindex = curvature_list.index(min_angle)
            i = joist[minindex + 1]
            #i.corner = 2
            
            # break the joist into two edges
            listA = joist[:minindex + 1 + 1]
            listB = joist[minindex + 1:]

            # fit 3D line ---- A
            data = []
            for i in listA:
                data.append([i.x, i.y, i.z])
            #data2 = line3dfit.move(np.array(data))
            data2, margin = line3dfit.movencheck_fixedheight(np.array(data))
            if margin < 1:  # 5 is good for hexagonal gazebo
                for idx in range(len(listA)):
                    i = listA[idx]
                    i.x = data2[idx][0]
                    i.y = data2[idx][1]
            else: # it detects the multi-angle joists
                joist_set.append(listA)
    
            # fit 3D line ---- B
            data = []
            for i in listB:
                data.append([i.x, i.y, i.z])
            #data2 = line3dfit.move(np.array(data))
            data2, margin = line3dfit.movencheck_fixedheight(np.array(data))
            if margin < (PARA.joist_dist / 3.0):  # 5 is good for hexagonal gazebo
                for idx in range(len(listB)):
                    i = listB[idx]
                    i.x = data2[idx][0]
                    i.y = data2[idx][1]
            else: # it detects the multi-angle joists
                joist_set.append(listB)
    return SS



#############################################################
#
# 3D simplification -- align pillars
#
#############################################################
def sim_rule_L14(SS, PARA):
    print 'aligning posts'

    SS = ssgtools.clearTBDmarker(SS)

    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if not(SS[h][k][m].TBD) and not(SS[h][k][m].LPP == None):
                    LIST = []
                    pts = SS[h][k][m]
                    while(pts != None):
                        LIST.append(pts)
                        pts = pts.LPP
                        if pts != None:
                            pts.TBD = True
                    # compute AVG x,y
                    sum_x = 0.0
                    sum_y = 0.0
                    for i in LIST:
                        sum_x = sum_x + i.x
                        sum_y = sum_y + i.y
                    avg_x = sum_x / float(len(LIST))
                    avg_y = sum_y / float(len(LIST))
                    # replace x,y
                    for i in LIST:
                        i.x = avg_x
                        i.y = avg_y
    return SS

#############################################################
#
# 3D simplification -- align beams
#
#############################################################
def sim_rule_L15(SS, PARA):
    if PARA.beamsnap180 <= (90.0 + 90.0/2.0):
        print 'warning! the angle is', PARA.beamsnap180
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
                #theta = np.arccos( np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))) * 180 / 3.141592;
                
                # store the measure 
                SS[h][k][m].angle2 = theta

                if abs(theta) > PARA.beamsnap180: #(90.0 + 90.0/2.0 + 90.0/2.0/2.0):
                    a = p2 - p0
                    b = p1 - p0 #-v1
                    
                    unitvec = a / np.linalg.norm(a)
                    s = np.dot(b, unitvec)
                    q = p0 + s * unitvec

                    SS[h][k][m].x = q[0]
                    SS[h][k][m].y = q[1]
    return SS
    
#############################################################
#
# 3D simplification -- align multiple connected pillars and joists
#
#############################################################
def sim_rule_L16(SS, PARA):
    print 'aligning connected pillars and joists'

    SS = ssgtools.find_terminal_nodes(SS)
    S_list = []
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].start and not(SS[h][k][m].end):  # get isolated "start" nodes
                    S_list.append(SS[h][k][m])
                    #SS[h][k][m].DEBUG = True
    
    for e in S_list:
        LIST = []
        pts = e
        while(pts != None):
            LIST.append(pts)
            if pts.LPP:
                pts = pts.LPP
            elif len(pts.LJP)>0:
                pts = pts.LJP[0]
            else:
                pts = None
        
        # skip nodes if there are more than 2 joist at the starting points
        if 0 and len(LIST)>3:
            if len(LIST[0].LJP)>0 and len(LIST[1].LJP)>0:
                LIST.pop(0)
                LIST.pop(0)
                for t in range(len(LIST)): # find the first index of LPP
                    if LIST[t].LPP:
                        break
                for i in range(t):
                    LIST.pop(0)

        # compute AVG x,y
        sum_x = 0.0
        sum_y = 0.0
        for i in LIST:
            sum_x = sum_x + i.x
            sum_y = sum_y + i.y
        avg_x = sum_x / float(len(LIST))
        avg_y = sum_y / float(len(LIST))
        # replace x,y
        for i in LIST:
            i.x = avg_x
            i.y = avg_y
    return SS

#############################################################
#
# Simplification w/ confidence -- align beams with the confidence
#
#############################################################
def sim_rule_L17(SS, PARA):
    original_parameter = PARA.beamsnap180
        
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].TBD = None
                if SS[h][k][m].demconfidence <= 10:
                    SS[h][k][m].TBD = True

    for n in range(10):
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if SS[h][k][m].TBD:
                        x1 = SS[h][k][m].x
                        y1 = SS[h][k][m].y
                        x2 = SS[h][k][m].RBP.x
                        y2 = SS[h][k][m].RBP.y
                        x0 = SS[h][k][m].LBP.x
                        y0 = SS[h][k][m].LBP.y
        
                        p1 = np.array([x1, y1])
                        p2 = np.array([x2, y2])
                        p0 = np.array([x0, y0])
                        
                        # previous area of the triangle
                        #AreaOld = checkcollision.get_triangle_area((x1,y1), (x2,y2), (x0,y0))
                        
                        v2 = p2 - p1
                        v1 = p0 - p1
                        
                        theta = ssgtools.angleoftwovectors(v1, v2)
                        
                        # store the measure 
                        SS[h][k][m].angle2 = theta
        
                        PARA.beamsnap180 = (90.0 + 90.0/2.0)
                        PARA.beamsnap180 = 80.0
                        if abs(theta) > PARA.beamsnap180: #(90.0 + 90.0/2.0 + 90.0/2.0/2.0):
                            a = p2 - p0
                            b = p1 - p0 #-v1
                            
                            unitvec = a / np.linalg.norm(a)
                            s = np.dot(b, unitvec)
                            q = p0 + s * unitvec
        
                            SS[h][k][m].x = q[0]
                            SS[h][k][m].y = q[1]
                            
                            #AreaNew = checkcollision.get_triangle_area((x1,y1), (x2,y2), (x0,y0))
                            
    PARA.beamsnap180 = original_parameter

    return SS
#############################################################
#
# Simplification w/ confidence -- delete nodes
#
#############################################################
def sim_rule_L18(SS, PARA):
        
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].TBD = None
                if SS[h][k][m].demconfidence <= 10:
                    SS[h][k][m].TBD = True

    for n in range(1):
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if SS[h][k][m].TBD:
                        # no joists
                        if len(SS[h][k][m].LJP)==0 and len(SS[h][k][m].PJP)==0:
                            if SS[h][k][m].PPP:
                               SS[h][k][m].PPP.LPP = None
                               SS[h][k][m].PPP = None
                            if SS[h][k][m].LPP:
                               SS[h][k][m].LPP.PPP = None
                               SS[h][k][m].LPP = None
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True

                        # 1 joist only
                        if not(SS[h][k][m].LPP) and not(SS[h][k][m].PPP):
                            if len(SS[h][k][m].LJP)==1:
                               SS[h][k][m].LJP[0].PJP = []
                               SS[h][k][m].LJP = []
                            if len(SS[h][k][m].PJP)==1:
                               SS[h][k][m].PJP[0].LJP = []
                               SS[h][k][m].PJP = []
                            
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True

                        # isoloated
                        if not(SS[h][k][m].PPP) and len(SS[h][k][m].PJP) == 0 and not(SS[h][k][m].LPP) and len(SS[h][k][m].LJP) == 0:
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True
                    
        SS = simalg_L3.deletenode_marked(SS)    
    return SS

#############################################################
#
# Simplification w/ confidence -- delete nodes
#
#############################################################
def sim_rule_L18tbd(SS, PARA): # using saved file
    import cv2 as cv # to extract contours, display images

    import os.path
    if os.path.exists('c:/temp/confmap.png'):
        confmap = cv.imread('c:/temp/confmap.png', cv.IMREAD_GRAYSCALE)
    else:
        print 'no confidence file'
        return SS

    offsetX = 221
    offsetY = 54

    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                x = SS[h][k][m].x
                y = SS[h][k][m].y
                xx = int(round(x - offsetX))
                yy = int(round(y - offsetY))
                SS[h][k][m].demconfidence = confmap[yy, xx]
        
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                SS[h][k][m].TBD = None
                if SS[h][k][m].demconfidence <= 10:
                    SS[h][k][m].TBD = True

    for n in range(1):
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if SS[h][k][m].TBD:
                        # no joists
                        if len(SS[h][k][m].LJP)==0 and len(SS[h][k][m].PJP)==0:
                            if SS[h][k][m].PPP:
                               SS[h][k][m].PPP.LPP = None
                               SS[h][k][m].PPP = None
                            if SS[h][k][m].LPP:
                               SS[h][k][m].LPP.PPP = None
                               SS[h][k][m].LPP = None
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True

                        # 1 joist only
                        if not(SS[h][k][m].LPP) and not(SS[h][k][m].PPP):
                            if len(SS[h][k][m].LJP)==1:
                               SS[h][k][m].LJP[0].PJP = []
                               SS[h][k][m].LJP = []
                            if len(SS[h][k][m].PJP)==1:
                               SS[h][k][m].PJP[0].LJP = []
                               SS[h][k][m].PJP = []
                            
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True

                        # isoloated
                        if not(SS[h][k][m].PPP) and len(SS[h][k][m].PJP) == 0 and not(SS[h][k][m].LPP) and len(SS[h][k][m].LJP) == 0:
                            SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
                            SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
                            SS[h][k][m].TBDELETED = True
                    
        SS = simalg_L3.deletenode_marked(SS)    
    return SS


#############################################################
#
# Simplification w/ confidence -- display confidence
#
#############################################################
def sim_rule_L19(SS, PARA):
    for h in range(len(SS)): # each slices
        for k in range(len(SS[h])): # each contour
            for m in range(len(SS[h][k])): # each node
                if SS[h][k][m].demconfidence <= 10:
                    SS[h][k][m].DEBUG = True
                    SS[h][k][m].label = 'start'# doesn't work
                    SS[h][k][m].start = True

    for n in range(1):
        for h in range(len(SS)): # each slices
            for k in range(len(SS[h])): # each contour
                for m in range(len(SS[h][k])): # each node
                    if SS[h][k][m].TBD:
                        pass
    return SS


#==============================================================================
# #############################################################
# #
# # Simplification delete isolated nodes
# #
# #############################################################
# def sim_rule_L20(SS, PARA):
#     for h in range(len(SS)): # each slices
#         for k in range(len(SS[h])): # each contour
#             for m in range(len(SS[h][k])): # each node
#                 # isoloated
#                 if not(SS[h][k][m].PPP) and len(SS[h][k][m].PJP) == 0 and not(SS[h][k][m].LPP) and len(SS[h][k][m].LJP) == 0:
#                     SS[h][k][m].LBP.RBP = SS[h][k][m].RBP
#                     SS[h][k][m].RBP.LBP = SS[h][k][m].LBP
#                     SS[h][k][m].TBDELETED = True
#                     
#         SS = simalg_L3.deletenode_marked(SS)    
#     return SS
#==============================================================================
