#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

# Part of EMGStoolkit.py:

import datetime 
import os 
import sys
import wget
import zipfile
import urllib.request  
import warnings

################################################################################
## Creation of a class to manage the Sentinel-1 burst ID map
################################################################################
class S1burstIDmap:

    ################################################################################
    ## Initialistion of the class
    ################################################################################
    def __init__(self):
        self.date_str_init = '29/05/2022'
        self.dirmap = os.environ.get('PATHS1BURSTIDMAP')+'/'
        self.pathIDmap = 'None'
        self.list_date = []
        self.verbose = True 

        self.verbose = False
        self.checkfile()
        self.verbose = True

    ################################################################################
    ## Function to print the attributes
    ################################################################################
    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

    ################################################################################
    ## Check the avaibility of the maps
    ################################################################################
    def checkfile(self):

        if self.verbose:
            print('EMGStoolkit.py => S1burstIDmap: check the avaibility of the stored S1 burst ID maps')

        ## Create the list of dates
        self.list_date = []; 
        datei = datetime.datetime.strptime(self.date_str_init, '%d/%m/%Y')

        while datei <=  datetime.datetime.now(): 
            datei = datei + datetime.timedelta(days=1)
            self.list_date.append(datei.strftime("%Y%m%d"))

        ## Check if the directory exists
        for i1 in self.list_date:
            if os.path.isdir("%s/S1_burstid_%s" %(self.dirmap,i1)):
                self.pathIDmap = "%s/S1_burstid_%s" %(self.dirmap,i1)

                if self.verbose:
                    print('\tDetection of the directory: %s' % (self.pathIDmap))

        if self.verbose and self.pathIDmap == 'None':
            warnings.warn('\tNo detection of the directory...\n\tPlease download the .zip file.') 

    ################################################################################
    ## Donwload the latest map
    ################################################################################
    def downloadfile(self): 

        if self.verbose:
            print('EMGStoolkit.py => S1burstIDmap: download the latest S1 burst ID maps')

        h = 0
        while self.pathIDmap == 'None':
            i1 = self.list_date[h]
            try:
                status = urllib.request.urlopen("https://sar-mpc.eu/files/S1_burstid_%s.zip" %(i1)).getcode()
                self.pathIDmap = "https://sar-mpc.eu/files/S1_burstid_%s.zip" %(i1)
                if self.verbose:
                    print("\tCheck the https://sar-mpc.eu/files/S1_burstid_%s.zip link ==> DETECTED" %(i1))
            except:
                print("\tCheck the https://sar-mpc.eu/files/S1_burstid_%s.zip link ==> NO DETECTED" %(i1))

            h = h + 1
            if h == len(self.list_date):
                sys.exit('ERROR: No detection of S1 burst ID map...')

            try:
                # Download the file
                filename = wget.download(self.pathIDmap, out=self.dirmap)
                print(f"File downloaded: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")

            if self.verbose:
                    print("\tUnzip the .zip file %s in %s" %(self.dirmap,i1))

            with zipfile.ZipFile("%s/S1_burstid_%s.zip" %(self.dirmap,i1), 'r') as zip_ref:
                zip_ref.extractall(self.dirmap)

            if self.verbose:
                    print("\tDelete the .zip file %s in %s" %(self.dirmap,i1))    
            os.remove("%s/S1_burstid_%s.zip" %(self.dirmap,i1))

        self.checkfile()







