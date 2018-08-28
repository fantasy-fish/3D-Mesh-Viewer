'''
filename: sim_x.py
version: 0.34
description: simplification module for the viewer
Version 0.1: contains R2.1a only
Version 0.2: include multiple algorithms
Version 0.21: the ID and name of each rule has been changed
version 0.3: new simplification algorithms, parameters for real data
version: 0.34: batch simplifications (D1, D2, D3, D4)

Input: (1) *.csv (SSG file), (2) meta.txt
    meta.txt -----------------------
    inputfilename without extension (ex: in1)
    outputfilename without extension (ex: out1)
    id (integer representing the simplification algorithm)
    No (integer representing the number of selected nodes; selected ALL iff No==-1)
    n1 (1st node if not empty)
    n2 (2nd node if not empty)
    ...
    nm (m-th node)
Output: 3D skeleton consists of nodes, beams, pillars, and joists

* how to install opencv 3.4
    https://docs.opencv.org/3.3.1/d5/de5/tutorial_py_setup_in_windows.html
    Installing OpenCV from prebuilt binaries
        1) install numpy (newest version)
        2) copy cv2.pyd into C:/Python27/lib/site-packages

by Jongmoo Choi (jongmooc@usc.edu)
'''

import ssgtools
import simalg
import simalg_L3
import os, sys

def simplify(ID, SS, PARA):
    if ID == 11: # Rule L1.1 (connect joists)
        print 'Rule L1.1'
        SS = simalg.sim_rule_L11(SS, PARA)
    elif ID == 12: # Rule L1.2 (connect Butterfly Js)
        print 'Rule L1.2'
        SS = simalg.sim_rule_L12(SS, PARA)
    elif ID == 131: # Rule L1.3a (align Js, line fit)
        print 'Rule L1.3a'
        SS = simalg.sim_rule_L13a(SS, PARA)
    elif ID == 132: # Rule L1.3b (align Js, S/E nodes)
        print 'Rule L1.3b'
        SS = simalg.sim_rule_L13b(SS, PARA)
    elif ID == 14: # align Ps
        print 'Rule L1.4'
        SS = simalg.sim_rule_L14(SS, PARA)
    elif ID == 15: # align Bs
        print 'Rule L1.5'
        SS = simalg.sim_rule_L15(SS, PARA)
    elif ID == 111: # SIM_GROUP_PILLARS (P -- J -- P)
        print 'Rule L111'
        SS = simalg.sim_rule_L111(SS, PARA)
    elif ID == 16: # ALIGN_JPJPJP
        print 'Rule L16'
        SS = simalg.sim_rule_L16(SS, PARA)
    #elif ID == 31: # DELETE_ISOLATED_NODES:
    #    print 'Rule L3.1'
    #    SS = simalg_L3.sim_rule_L31(SS, PARA)
    #elif ID == 32: # DELETE_ISOLATED_CONTOURS
    #    print 'Rule L3.2'
    #    SS = simalg_L3.sim_rule_L32(SS, PARA)
    elif ID == 33: # DELETE_SNAP_NODES
        print 'Rule L3.3'
        SS = simalg_L3.sim_rule_L33(SS, PARA)
    elif ID == 35: # DELETE_PAN_JOIST_NODES
        print 'Rule L3.5'
        for j in range(3):
            SS = simalg_L3.sim_rule_L35(SS, PARA)
    elif ID == 34: # DELETE_SHORT_EDGES
        print 'Rule L3.4'
        for j in range(3):
            SS = simalg_L3.sim_rule_L34(SS, PARA)
    elif ID == 151: # AGGRESSIVE_ALIGN_BEAMS
        print 'Rule L1.51'
        for j in range(5):
            PARA.beamsnap180 = (90.0 + 90.0/2.0)
            SS = simalg.sim_rule_L15(SS, PARA)
    elif ID == 41: # batch simplifications D1
        print 'Batch simplifications D1'
        SS = simalg.sim_rule_L18tbd(SS, PARA)
        SS = simalg_L3.sim_rule_L35(SS, PARA) # delete panjoists
        SS = simalg_L3.sim_rule_L33(SS, PARA) # delete snap nodes
        SS = simalg_L3.sim_rule_L34(SS, PARA) # delete short edges
        SS = simalg_L3.sim_rule_L35(SS, PARA) # delete panjoists
        SS = simalg_L3.sim_rule_L35(SS, PARA) # delete panjoists
        SS = simalg.sim_rule_L17(SS, PARA) # beam snapping with the confidence
        SS = simalg_L3.sim_rule_L34(SS, PARA) # delete short edges    
    elif ID == 42: # batch simplifications D2
        print 'Batch simplifications D2'
        SS = simalg.sim_rule_L11(SS, PARA) # connect joists
        SS = simalg.sim_rule_L111(SS, PARA) # connect JPJ
        SS = simalg.sim_rule_L14(SS, PARA) # align posts
        SS = simalg.sim_rule_L15(SS, PARA) # align beams 
        SS = simalg_L3.sim_rule_L33(SS, PARA) # delete snap nodes
        SS = simalg_L3.sim_rule_L34(SS, PARA) # delete short edges        
    elif ID == 43: # batch simplifications D3
        print 'Batch simplifications D3'
        for k in range(10):
            print 'multiple alignment', k
            SS = simalg.sim_rule_L11(SS, PARA) # connect joists
            SS = simalg.sim_rule_L111(SS, PARA) # connect JPJ
            SS = simalg.sim_rule_L14(SS, PARA) # align posts
            SS = simalg.sim_rule_L15(SS, PARA) # align beams 
            SS = simalg.sim_rule_L16(SS, PARA) # align PJPJP
            SS = simalg_L3.sim_rule_L33(SS, PARA) # delete snap nodes
            for j in range(3):
                SS = simalg_L3.sim_rule_L35(SS, PARA) # delete panjoists
            for j in range(3):
                SS = simalg_L3.sim_rule_L34(SS, PARA) # delete short edges
            for j in range(10):
                PARA.beamsnap180 = (90.0 + 90.0/2.0)
                SS = simalg.sim_rule_L15(SS, PARA) # aggressive 
            SS = simalg.sim_rule_L14(SS, PARA) # align posts
            SS = simalg.sim_rule_L16(SS, PARA) # align PJPJP        
    elif ID == 44: # batch simplifications D4
        print 'Batch simplifications D4'
        SS = simalg.sim_rule_L11(SS, PARA) # connect joists
        SS = simalg.sim_rule_L111(SS, PARA) # connect JPJ
        SS = simalg.sim_rule_L16(SS, PARA) # align PJPJP
        SS = simalg_L3.sim_rule_L34(SS, PARA) # delete short edges        
    else:
        print 'Unknown ID'
    return SS

def main():
    BOOL_SYNTHETICDATA = False

    if BOOL_SYNTHETICDATA:
        PARA = ssgtools.CMeta( 0.05 )
        PARA.joist_dist = 15.0
        PARA.pillar_dist = 1.0
        PARA.CONTOUR_SIMPLIFICATION = 0.005   
    else:
        HightResolution = 0.5
        PARA = ssgtools.CMeta(HightResolution)
        PARA.joist_dist = HightResolution * 3.0
        PARA.pillar_dist = HightResolution  
        PARA.beamsnap180 = (90.0 + 90.0/2.0 + 90.0/2.0/2.0)
        PARA.L0_SHORT_BEAM = 3.0 #?2
        PARA.minnumberofcontours = 2
        PARA.mincontourlength = 30 # 30 for D3, 
        #CONTOUR_SIMPLIFICATION = 0.002 # for GT Yasu 
        PARA.CONTOUR_SIMPLIFICATION = 0.005    
    
    PARA.minnumberofcontours = 0
    PARA.mincontourlength = 30.0    
       
    print sys.argv
    fid = open(sys.argv[0] + 'sub/meta.txt','r')
    meta = fid.readlines()
    fid.close()
    print 'done 2'

    INFILE = meta[0].replace('\n','')
    OUTFILE = meta[1].replace('\n','')
    SIM_ID = int(meta[2].replace('\n',''))

    SS = ssgtools.readssgcsv(INFILE+".csv")
    SS = simplify(SIM_ID, SS, PARA)
    ssgtools.writessgcsv(OUTFILE+".csv", SS)

    print 'Simplification Complete'
