#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

# Part of EMGStoolkit.py:

import os 
import sys
import wget
import zipfile
import numpy as np
import glob
import warnings
import shutil
import time

from functions import egmsapitools

timeerror462 = 5

################################################################################
## Creation of a class to manage the Sentinel-1 burst ID map
################################################################################
class egmsdownloader:

    ################################################################################
    ## Initialistion of the class
    ################################################################################
    def __init__(self):
        self.listL2a = []
        self.listL2alink = []
        self.listL2b = []
        self.listL2blink = []
        self.listL3UD = []
        self.listL3UDlink = []
        self.listL3EW = []
        self.listL3EWlink = []
        self.token = 'XXXXXXX--XXXXXXX'
       
        self.verbose = True

    ################################################################################
    ## Check parameters
    ################################################################################
    def checkparameter(self):
        if (self.token == 'XXXXXXX--XXXXXXX'):
            print('Error: The user token parameter is not correct (in EGMSdownloaderapi.py)')
        
    ################################################################################
    ## Function to print the attributes
    ################################################################################
    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

    ################################################################################
    ## Function to create the ROI file
    ################################################################################
    def updatelist(self,**kwargs): 

        if self.verbose:
            print('EMGStoolkit.py => EGMSdownloaderapi: update the list(s) of files')

        infoS1ROIparameter = kwargs['infoS1ROIparameter']

        release_para = egmsapitools.check_release(infoS1ROIparameter.release)

        if infoS1ROIparameter.egmsL3component == 'UD': 
            ext_3D = 'U'
        elif infoS1ROIparameter.egmsL3component == 'EW': 
            ext_3D = 'E'
        
        if infoS1ROIparameter.Data: 
            if infoS1ROIparameter.egmslevel == 'L2a' or infoS1ROIparameter.egmslevel == 'L2b': 
                for tracki in infoS1ROIparameter.Data:
                    for idx in ['1','2','3']: 
                        for iwi in infoS1ROIparameter.Data[tracki]['IW%s' %(idx)]:
                            name_zip = 'EGMS_%s_%03d_%04d_IW%s_VV%s.zip' % (infoS1ROIparameter.egmslevel,iwi['relative_orbit_number'],iwi['egms_burst_id'],idx,release_para[1])
                            link_zip = 'https://egms.land.copernicus.eu/insar-api/archive/download/%s' % (name_zip)
                            if infoS1ROIparameter.egmslevel == 'L2a':
                                self.listL2a.append(name_zip)
                                self.listL2alink.append(link_zip)
                            elif infoS1ROIparameter.egmslevel == 'L2b':
                                self.listL2b.append(name_zip)
                                self.listL2blink.append(link_zip)

        if infoS1ROIparameter.DataL3:
            if infoS1ROIparameter.egmslevel == 'L3':
                for tilei in infoS1ROIparameter.DataL3['polyL3']:
                
                    x = tilei.exterior.coords.xy[0].tolist()[0]/100000
                    y = tilei.exterior.coords.xy[1].tolist()[0]/100000

                    name_zip = 'EGMS_L3_E%2dN%2d_100km_%s%s.zip' % (y,x,ext_3D,release_para[1])
                    link_zip = 'https://egms.land.copernicus.eu/insar-api/archive/download/%s' % (name_zip)

                    if infoS1ROIparameter.egmsL3component == 'UD':
                        self.listL3UD.append(name_zip)
                        self.listL3UDlink.append(link_zip)
                    elif infoS1ROIparameter.egmsL3component == 'EW':
                        self.listL3EW.append(name_zip)
                        self.listL3EWlink.append(link_zip)

        self.listL2a = np.unique(self.listL2a).tolist()
        self.listL2alink = np.unique(self.listL2alink).tolist()
        self.listL2b = np.unique(self.listL2b).tolist()
        self.listL2blink = np.unique(self.listL2blink).tolist()
        self.listL3UD = np.unique(self.listL3UD).tolist()
        self.listL3UDlink = np.unique(self.listL3UDlink).tolist()
        self.listL3EW = np.unique(self.listL3EW).tolist()
        self.listL3EWlink = np.unique(self.listL3EWlink).tolist()

        if self.verbose:
            print('\tPrint the list using the printlist method')
            self.printlist()

    ################################################################################
    ## Function to print the list(s) of files
    ################################################################################
    def printlist(self): 

        if self.verbose:
            print('EMGStoolkit.py => EGMSdownloaderapi: print the list(s) of files')

        for type in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            datatmp = eval('self.list%s' % (type))
            datatmplink = eval('self.list%slink' % (type))
        
            if datatmp: 
                print('For the EGMS data: %s' % (type))
                for idx in np.arange(len(datatmp)): 
                    release_para = egmsapitools.check_release_fromfile(datatmp[idx])
                    # print('\t File %d: %s stored to %s (Release %s)' % (idx+1,datatmp[idx],datatmplink[idx],release_para[0]))
                    print('\t File %d: %s (Release %s)' % (idx+1,datatmp[idx],release_para[0]))

    ################################################################################
    ## Function to download the files
    ################################################################################
    def download(self,**kwargs): 

        self.checkparameter()

        if self.verbose:
            print('EMGStoolkit.py => EGMSdownloaderapi: download the files')

        if not "outputdir" in kwargs:
            outputdir = './Output'
        else: 
            outputdir = kwargs['outputdir']

        if not "unzip" in kwargs:
            unzipmode = False
        else: 
            unzipmode = kwargs['unzip']

        if not "clean" in kwargs:
            cleanmode = False
        else: 
            cleanmode = kwargs['clean']

        if not os.path.isdir(outputdir): 
            os.mkdir(outputdir)

        total_len = len(self.listL2a) + len(self.listL2b) + len(self.listL3UD) + len(self.listL3EW)

        h = 1
        for type in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            datatmp = eval('self.list%s' % (type))
            datatmplink = eval('self.list%slink' % (type))
        
            if datatmp: 
                if not os.path.isdir('%s/%s' % (outputdir,type)):
                    os.mkdir('%s/%s' % (outputdir,type))

                for idx in np.arange(len(datatmp)): 
                    if self.verbose:
                        print('%d / %d files: Download the file: %s' % (h,total_len,datatmp[idx]))

                    release_para = egmsapitools.check_release_fromfile(datatmp[idx])

                    if not os.path.isdir('%s/%s/%s' % (outputdir,type,release_para[0])):
                        os.mkdir('%s/%s/%s' % (outputdir,type,release_para[0]))
                    pathdir = '%s/%s/%s' % (outputdir,type,release_para[0])

                    if not os.path.isfile('%s/%s' % (pathdir,datatmp[idx])): 
                        try:
                            # Download the file
                            filename = wget.download('%s?id=%s' % (datatmplink[idx],self.token), out=pathdir)
                            if self.verbose:
                                print(f"\tFile downloaded: {filename}")
                        except Exception as e:
                            time.sleep(timeerror462)
                            if self.verbose:
                                print(f"An error occurred: {e}")
                    else: 
                        if self.verbose:
                            print('\tAlready downloaded')

                    h = h + 1

                    self.unzipfile(outputdir=outputdir,unzip=unzipmode,clean=cleanmode)

    ################################################################################
    ## Function to unzip the files
    ################################################################################
    def unzipfile(self,**kwargs): 

        if self.verbose:
            print('EMGStoolkit.py => EGMSdownloaderapi: unzip the files')

        if not "outputdir" in kwargs:
            outputdir = './Output'
        else: 
            outputdir = kwargs['outputdir']

        if not "unzip" in kwargs:
            unzipmode = True
        else: 
            unzipmode = kwargs['unzip']

        if not "clean" in kwargs:
            cleanmode = False
        else: 
            cleanmode = kwargs['clean']

        list_files = glob.glob('%s/*/*/*.zip' % (outputdir))
        
        if unzipmode:
            h = 1
            for fi in list_files: 
                pathsplit = fi.split('/')
                namefile = fi.split('/')[-1].split('.')[0]
                pathdirfile = ''
                for i1 in np.arange(len(pathsplit)-1):
                    if i1 == 0:
                        pathdirfile = pathsplit[i1] 
                    else:
                        pathdirfile = pathdirfile + '/' + pathsplit[i1] 
                if self.verbose:
                    print('%d / %d files: Unzip the file: %s' % (h,len(list_files),pathsplit[-1]))
                h = h + 1
                with zipfile.ZipFile("%s" %(fi), 'r') as zip_ref:
                    zip_ref.extractall('%s/%s' % (pathdirfile,namefile))

                if os.path.isdir('%s/%s' % (pathdirfile,namefile)) and (cleanmode): 
                    os.remove(fi)
        else: 
            if self.verbose:
                print('\tNo processing.')

    ################################################################################
    ## Function to clean the unused files
    ################################################################################
    def clean(self,**kwargs): 

        if self.verbose:
            print('EMGStoolkit.py => EGMSdownloaderapi: clean the unused files (based on the list(s))')

        if not "outputdir" in kwargs:
            outputdir = './Output'
        else: 
            outputdir = kwargs['outputdir']

        if not os.path.isdir(outputdir): 
            sys.exit('Error')

        listdirall = []
        listfileall = []
        for type in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            datatmp = eval('self.list%s' % (type))
            if datatmp: 
                for idx in np.arange(len(datatmp)): 
                    release_para = egmsapitools.check_release_fromfile(datatmp[idx])
                    listdirall.append('%s/%s/%s/%s' % (outputdir,type,release_para[0],datatmp[idx].split('.')[0]))
                    listfileall.append('%s/%s/%s/%s' % (outputdir,type,release_para[0],datatmp[idx]))

        liststored = glob.glob('%s/*/*/*' % (outputdir))
        liststoredDIR = []
        liststoredFILE = []
        for li in liststored: 
            if os.path.isfile(li):
                liststoredFILE.append(li)
            else: 
                liststoredDIR.append(li)

        for li in liststoredDIR: 
            if not li in listdirall:
                if self.verbose: 
                    print('The directory %s is not in the list(s), it will be removed...' % (li))
                shutil.rmtree(li)
            else:
                if self.verbose:
                    print('The directory %s is in the list(s), it will be kept...' % (li))

        for li in liststoredFILE: 
            if not li in listfileall: 
                if self.verbose:
                    print('The .zip file %s is not in the list(s), it will be removed...' % (li))
                os.remove(li)
            else:
                if self.verbose:
                    print('The .zip file %s is in the list(s), it will be kept...' % (li))

        #  Clean the empty directories 
        for i1 in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            for i2 in ['2015_2021', '2018_2022']:
                if os.path.isdir('%s/%s/%s' % (outputdir,i1,i2)):
                    if len(os.listdir('%s/%s/%s' % (outputdir,i1,i2))) == 0: 
                        shutil.rmtree('%s/%s/%s' % (outputdir,i1,i2))

            if os.path.isdir('%s/%s' % (outputdir,i1)):
                if len(os.listdir('%s/%s' % (outputdir,i1))) == 0: 
                    shutil.rmtree('%s/%s' % (outputdir,i1))



    
    
            


        
        

