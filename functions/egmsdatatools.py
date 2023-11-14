# -*- coding: iso-8859-1 -*-

# Part of EMGStoolkit.py:

import sys

from functions import egmsapitools
import numpy as np
import glob
import pandas as pd 
import subprocess
import os
import fiona
from shapely.geometry import Polygon, mapping, shape, LineString, Point
import pyproj
import shutil

source_crs = 'epsg:4326'
target_crs = 'epsg:3035'

latlon_to_meter = pyproj.Transformer.from_crs(source_crs, target_crs)
meter_to_latlon = pyproj.Transformer.from_crs(target_crs,source_crs)

################################################################################
## Function to merge the datasets in csv format
################################################################################
def removerawdata(**kwargs): 
    
    ## Parameters
    if not "inputdir" in kwargs:
        inputdir = './Output'
    else: 
        inputdir = kwargs['inputdir']

    if not "force" in kwargs:
        forcemode = False
    else: 
        forcemode = kwargs['force']

    if not "verbose" in kwargs:
        verbose = True
    else: 
        verbose = kwargs['verbose']

    if not (verbose == True or verbose == False):
        sys.error('Error: bad parameter of the verbose parameter [True or False]')
    if not (os.path.isdir(inputdir)):
        sys.error('Error: the input directory %s is not a directory.' % (inputdir))

    if verbose:
        print('EMGStoolkit.py => egmsdatatools: remove the raw-data directories')
        print('\tInput Directory: %s' % (inputdir))

    if not forcemode:
        answer = input('Can you confirm the removal of raw-data directories? [y or n]?')
    else:
        answer = 'y'

    if answer in ['y','Y','yes','Yes','YES','1']:
        if verbose:
            print('Deleting...')

        for i1 in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            if os.path.isdir('%s/%s' % (inputdir,i1)):
                shutil.rmtree('%s/%s' % (inputdir,i1))

    li = glob.glob('bbox.*')
    if li:
        if not forcemode:
            answer = input('The bbox files have been detected. Can you confirm the removal of these files? [y or n]?')
        else:
            answer = 'yes'
        if answer in ['y','Y','yes','Yes','YES','1']:
            if verbose:
                print('Deleting...')

            for i1 in li:
                os.remove('%s' % (i1))


################################################################################
## Function to merge the datasets in csv format
################################################################################
def datamergingcsv(**kwargs): 
    
    ## Parameters
    if not "outputdir" in kwargs:
        outputdir = './Output'
    else: 
        outputdir = kwargs['outputdir']

    if not "inputdir" in kwargs:
        inputdir = './Output'
    else: 
        inputdir = kwargs['inputdir']

    if not "paratosave" in kwargs:
        paratosave = 'all'
    else: 
        paratosave = kwargs['paratosave']

    if not "mode" in kwargs:
        mode = 'onlist'
    else: 
        if kwargs['mode'] == 'onlist' or kwargs['mode'] == 'onfiles':
            mode = kwargs['mode']
        else:
            sys.exit('ERROR')

    if 'infoEGMSdownloader' in kwargs: 
        infoEGMSdownloader = kwargs['infoEGMSdownloader']
    else:
        if mode == 'onlist':
            sys.exit('The output of EGMSdownloaderapi function is required with the "onlist" mode.')

    if not "verbose" in kwargs:
        verbose = True
    else: 
        verbose = kwargs['verbose']

    if not (verbose == True or verbose == False):
        sys.error('Error: bad parameter of the verbose parameter [True or False]')
    if not (os.path.isdir(outputdir)):
        sys.error('Error: the output directory %s is not a directory.' % (outputdir))
    if not (os.path.isdir(inputdir)):
        sys.error('Error: the input directory %s is not a directory.' % (inputdir))

    if verbose:
        print('EMGStoolkit.py => egmsdatatools: merge the .csv files')
        print('\tOutput Directory: %s' % (outputdir))
        print('\tInput Directory: %s' % (inputdir))
        print('\tSelected parameters: %s' % (paratosave))
        print('\tMode: %s' % (mode))

    ## Creation of the list for merging
    if mode == 'onlist': # Based on the list
        listfiles = []
        for type in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            datatmp = eval('infoEGMSdownloader.list%s' % (type))
            if datatmp: 
                for idx in np.arange(len(datatmp)): 
                    release_para = egmsapitools.check_release_fromfile(datatmp[idx])
                    listfiles.append('%s/%s/%s/%s' % (inputdir,type,release_para[0],datatmp[idx].split('.')[0]))
    else: # Based on the files
        listfiles = glob.glob('%s/*/*/*/*.csv' % (inputdir))

    if not listfiles:
        sys.exit('Error: no files are detected.')

    filedict, release, level, track, L3compall = listtodictmerged(listfiles)
    
    for ri in release:
        for li in level:
            if not li == 'L3':
                for ti in track:
                    try:
                        file_list = filedict[ri][li][ti]['Files']
                        name_file = filedict[ri][li][ti]['Name']
                        if verbose:
                            print('Merging for %s...' % (name_file))
                        filemergingcsv(inputdir,outputdir,name_file,file_list,paratosave)
                    except:
                        a = 'dummy'
            else:
                for ci in L3compall:
                    try:
                        file_list = filedict[ri][li][ci]['Files']
                        name_file = filedict[ri][li][ci]['Name']
                        if verbose:
                            print('Merging for %s...' % (name_file))
                        filemergingcsv(inputdir,outputdir,name_file,file_list,paratosave)
                    except:
                        a = 'dummy'

################################################################################
## Function to merge the datasets
################################################################################
def datamergingtiff(**kwargs): 
    
     ## Parameters
    if not "outputdir" in kwargs:
        outputdir = './Output'
    else: 
        outputdir = kwargs['outputdir']

    if not "inputdir" in kwargs:
        inputdir = './Output'
    else: 
        inputdir = kwargs['inputdir']

    if not "mode" in kwargs:
        mode = 'onlist'
    else: 
        if kwargs['mode'] == 'onlist' or kwargs['mode'] == 'onfiles':
            mode = kwargs['mode']
        else:
            sys.exit('ERROR')

    if 'infoEGMSdownloader' in kwargs: 
        infoEGMSdownloader = kwargs['infoEGMSdownloader']
    else:
        if mode == 'onlist':
            sys.exit('The output of EGMSdownloaderapi function is required with the "onlist" mode.')

    if not "verbose" in kwargs:
        verbose = True
    else: 
        verbose = kwargs['verbose']

    if not (verbose == True or verbose == False):
        sys.error('Error: bad parameter of the verbose parameter [True or False]')
    if not (os.path.isdir(outputdir)):
        sys.error('Error: the output directory %s is not a directory.' % (outputdir))
    if not (os.path.isdir(inputdir)):
        sys.error('Error: the input directory %s is not a directory.' % (inputdir))

    if verbose:
        print('EMGStoolkit.py => egmsdatatools: merge the .tiff files (only for the L3 level)')
        print('\tOutput Directory: %s' % (outputdir))
        print('\tInput Directory: %s' % (inputdir))
        print('\tMode: %s' % (mode))

    ## Creation of the list for merging
    if mode == 'onlist': # Based on the list
        listfiles = []
        for type in ['L2a', 'L2b', 'L3UD', 'L3EW']:
            datatmp = eval('infoEGMSdownloader.list%s' % (type))
            if datatmp: 
                for idx in np.arange(len(datatmp)): 
                    release_para = egmsapitools.check_release_fromfile(datatmp[idx])
                    listfiles.append('%s/%s/%s/%s' % (inputdir,type,release_para[0],datatmp[idx].split('.')[0]))
    else: # Based on the files
        listfiles = glob.glob('%s/*/*/*/*.tiff' % (inputdir))
    
    if not listfiles:
        sys.exit('Error: no files are detected.')

    filedict, release, level, track, L3compall = listtodictmerged(listfiles)
    
    for ri in release:
        for li in level:
            if li == 'L3':
                for ci in L3compall:
                    try:

                        file_list = filedict[ri][li][ci]['Files']
                        name_file = filedict[ri][li][ci]['Name']

                        if verbose:
                            print('Merging for %s...' % (name_file))
                        filemergingtiff(inputdir,outputdir,name_file,file_list,verbose)
                    except:
                        a = 'dummy'

################################################################################
## Function to clip the data
################################################################################
def dataclipping(**kwargs): 
    
    if not "outputdir" in kwargs:
        outputdir = './Output'
    else: 
        outputdir = kwargs['outputdir']

    if not "inputdir" in kwargs:
        inputdir = './Output'
    else: 
        inputdir = kwargs['inputdir']

    if not "file" in kwargs:
        namefile = 'all'
    else: 
        namefile = kwargs['file']

    if not "shapefile" in kwargs:
        shapefile = 'bbox.shp'
    else: 
        shapefile = kwargs['shapefile']

    if not "verbose" in kwargs:
        verbose = True
    else: 
        verbose = kwargs['verbose']

    if verbose:
        print('EMGStoolkit.py => egmsdatatools: clip the files')
        if not namefile == 'all':
            print('\tThe file name is: %s' % (namefile))
        else:
            print('\tInput Directory: %s' % (inputdir))
            print('\tOutput Directory: %s' % (outputdir))
        print('\tShapefile: %s' % (shapefile))

    ## Create the list of files
    if namefile == 'all':
        list_file = glob.glob('%s/*.csv' %(outputdir)) + glob.glob('%s/*.tiff' %(outputdir))
    else:
        tmp = namefile.split(',')
        if not '/' in namefile:
            list_file = []
            for ni in tmp:
                list_file.append(inputdir+'/'+ni)
        else:
            list_file = [namefile]

    if not list_file:
        sys.exit('Error: the list of files is empty.')

    ## Cropping and clipping
    it = 1
    ittotal = 0
    for fi in list_file:
        if fi.split('.')[-1] == 'csv' and (not 'clipped' in fi):
            ittotal = ittotal+1
        elif fi.split('.')[-1] == 'tiff' and (not 'cropped' in fi):
            ittotal = ittotal+1

    for fi in list_file:
        
        if fi.split('.')[-1] == 'csv' and (not 'clipped' in fi):
            newname = fi[0:-4]+'_clipped.csv'

            if verbose:
                print('\t%d / %d file(s): Clip the file %s to %s...' % (it,ittotal,fi,newname))

            listROI = []
            listROIepsg3035 = []

            schema = {
                'geometry': 'Polygon',
                'properties' : {'id':'int'}
                }

            with fiona.open(shapefile,'r','ESRI Shapefile', schema) as shpfile:
                for feature in shpfile:
                    coordinates = []
                    Xcoord = []
                    Ycoord = []
                    line = shape(feature['geometry'])
                    if isinstance(line, LineString):
                        for index, point in enumerate(line.coords):
                            if index == 0:
                                first_pt = point
                            coordinates.append(point)
                            X, Y = latlon_to_meter.transform(point[1],point[0])
                            Xcoord.append(X)
                            Ycoord.append(Y)
                    if len(coordinates) >= 3:
                        listROI.append(Polygon(coordinates))
                        listROIepsg3035.append(Polygon(list(zip(Xcoord, Ycoord))))

            h = 0
            headerline = []
        
            outfile = open(newname,'w')
            outfile.close()
            with open(fi) as infile:
                for line in infile:
                    if h == 0:
                        headerline = line
                        headerline = headerline.split(';')
                        nx = np.where('easting' == np.array(headerline))[0]  
                        ny = np.where('northing' == np.array(headerline))[0]  
                        with open(newname,'a') as outfile:
                            outfile.write(line)
                    else:
                        linelist = line.split(';')
                        pti = Point(float(linelist[ny[0]]),float(linelist[nx[0]]))

                        for ROi in listROIepsg3035:
                            if ROi.contains(pti):
                                with open(newname,'a') as outfile:
                                    outfile.write(line)

                    h = h + 1
            
        elif fi.split('.')[-1] == 'tiff' and (not 'cropped' in fi):

            ## Create the polygon for cropping 
            name_bbox_clipping1 = '%s_forclipping1.GeoJSON' % (shapefile[0:-4])
            name_bbox_clipping2 = '%s_forclipping2.GeoJSON' % (shapefile[0:-4])
            schema = {
                'geometry': 'Polygon',
                'properties' : {'id':'int'}
                }
            cmdi = 'ogr2ogr -f "GeoJSON" -t_srs EPSG:3035 %s %s' % (name_bbox_clipping1,shapefile)
            os.system(cmdi)
            with fiona.open(name_bbox_clipping1) as in_file, fiona.open(name_bbox_clipping2, 'w', 'GeoJSON', schema) as out_file:
                for index, row in enumerate(in_file):
                    line = shape(row['geometry'])
                    hull = line.convex_hull
                    out_file.write({
                        'geometry': mapping(hull),
                        'properties': {'id': index},
                    })

            newname = fi[0:-5]+'_cropped.tiff'

            if verbose:
                print('\t%d / %d file(s): Crop the file %s to %s...' % (it,ittotal,fi,newname))

            cmdi = 'rio mask %s %s --crop --geojson-mask %s --overwrite' %(fi,newname,name_bbox_clipping2)
            os.system(cmdi)
    
            if os.path.isfile(name_bbox_clipping1):
                os.remove(name_bbox_clipping1)
            if os.path.isfile(name_bbox_clipping2):
                os.remove(name_bbox_clipping2)

        elif 'cropped' in fi or 'clipped' in fi:
            if verbose:
                print('\t%d / %d file(s): The file %s is already cropped/clipped...' % (it,ittotal,fi))
        else:
            if verbose:
                print('\t%d / %d file(s): The file %s has not been found...' % (it,ittotal,fi))

        it = it + 1
        
################################################################################
################################################################################
## SUBFUNCTIONS
################################################################################
################################################################################

################################################################################
## Sub-function to merge the .tiff files
################################################################################
def filemergingtiff(inputdir,outputdir,name,listfile,verbose):

    if os.path.isfile("%s/%s.tiff" % (outputdir,name)):
        os.remove("%s/%s.tiff" % (outputdir,name))

    cmdi= ["gdal_merge.py", "-o", "%s/%s.tiff" % (outputdir,name), "-n -9999 -a_nodata -9999"]
    for fi in listfile:
        pathfi = glob.glob('%s/*/*/*/%s.tiff' % (inputdir,fi))[0]
        cmdi.append(pathfi)
    
    cmdi = ' '.join(cmdi)
    if verbose:
        print('Used command: %s' % (cmdi))
        subprocess.call(cmdi,shell=True)  
    else:
        subprocess.call(cmdi,shell=True,stdout=open(os.devnull, 'wb'))  

################################################################################
## Sub-function to merge the .csv files
################################################################################
def filemergingcsv(inputdir,outputdir,name,listfile,paratosave):

    ## Detect the headers
    first_one = True
    date_ts = []
    for fi in listfile:

        # Detection of the file 
        pathfi = glob.glob('%s/*/*/*/%s.csv' % (inputdir,fi))[0]
        head = pd.read_csv(pathfi, index_col=0, nrows=0).columns.tolist()

        header_para = []
        header_ts = []
        for hi in head:
            if not '20' in hi:
                header_para.append(hi)
            else:
                header_ts.append(hi)
            
        date_ts = date_ts + header_ts

    date_ts = np.unique(date_ts)  

    header_final = header_para
    for ti in date_ts : 
        header_final.append(ti)

    ## Merge the files
    first_one = True
    for fi in listfile:
        # Detection of the file 
        pathfi = glob.glob('%s/*/*/*/%s.csv' % (inputdir,fi))[0]

        # Read the file
        datai = pd.read_csv(pathfi,index_col=0)
        # datai = pd.read_csv(pathfi,nrows=10,index_col=0)
        head = pd.read_csv(pathfi, index_col=0, nrows=0).columns.tolist()

        datamatrix = dict()
        if paratosave == 'all':
            for hi in header_final:
                datamatrix[hi] = []

        else:
            # Mandatory parameters
            mand_para = ['latitude', 'longitude', 'easting', 'northing', 'height', 'height_wgs84']
            for hi in mand_para:
                datamatrix[hi] = []
            # Selected parameters
            if isinstance(paratosave,list):
                for hi in paratosave:
                    datamatrix[hi] = []
            else:
                for hi in paratosave.split(','):
                    datamatrix[hi] = []

        # Merging 
        list_save = list(datamatrix.keys())
        for mi in list_save:
            ni = np.where(mi == np.array(head))[0]          
            if not len(ni) == 0:
                datamatrix[mi] = datai[head[ni[0]]]
            else: 
                datamatrix[mi] = datai[head[-1]]
                datamatrix[mi] = np.where(np.isnan(datamatrix[mi])==0, np.nan, datamatrix[mi])
            
        pdfdframetosave = pd.DataFrame(data=datamatrix)
        # print(pdfdframetosave)

        # Save the file 
        if first_one:
            pdfdframetosave.to_csv('%s/%s.csv' % (outputdir,name), mode='w', sep=';', index=True, header = True)
        else:
            pdfdframetosave.to_csv('%s/%s.csv' % (outputdir,name), mode='a', sep=';', index=True, header = False)

        first_one = False

################################################################################
## Sub-function to convert the list to a merged dictionary
################################################################################
def listtodictmerged(list):

    release = []
    level = []
    track = []
    L3compall = []
    filedict = {}

    ## Extraction of the parameters
    for fi in list:
        namei = fi.split('/')[-1].split('.')[0]
        ri = egmsapitools.check_release_fromfile(namei)

        if ri[1] == '':
            ri[1] = '_2015_2021'

        parai = namei.split('_')

        if '_U' in namei:
            L3comp = 'UD'
        elif '_E' in namei:
            L3comp = 'EW'
        else:
            L3comp = ''

        release.append(ri[0])
        level.append(parai[1])

        if not ri[0] in filedict:
            filedict[ri[0]] = {}
        if not parai[1] in filedict[ri[0]]:
                filedict[ri[0]][parai[1]] = {}
                   
        if not parai[1] == 'L3':
            if not parai[2] in filedict[ri[0]][parai[1]]:
                filedict[ri[0]][parai[1]][parai[2]] = {'Name': 'EGMS_%s_%s_VV%s' % (parai[1],parai[2],ri[1]),
                                                       'Files': []}
            filedict[ri[0]][parai[1]][parai[2]]['Files'].append(namei)    
            track.append(parai[2])
        else:
            if not L3comp in filedict[ri[0]][parai[1]]:
                filedict[ri[0]][parai[1]][L3comp] = {'Name': 'EGMS_%s%s_%s' % (parai[1],ri[1],L3comp),
                                                       'Files': []}
            filedict[ri[0]][parai[1]][L3comp]['Files'].append(namei)  
            L3compall.append(L3comp)

    release = np.unique(release)
    level = np.unique(level)
    track = np.unique(track)
    L3compall = np.unique(L3compall)

    return filedict, release, level, track, L3compall
