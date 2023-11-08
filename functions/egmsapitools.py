# -*- coding: iso-8859-1 -*-

# Part of EMGStoolkit.py:

import sys

################################################################################
## Function to create the extention for the release
################################################################################
def check_release(inputrelease): 
    if inputrelease == '2015_2021': 
        ext_release = ''
    elif inputrelease == '2018_2022':
        ext_release = '_2018_2022_1'
    else: 
        sys.exit('ERROR: bad release')

    release_para = [inputrelease, ext_release]

    return release_para

################################################################################
## Function to define the release for the name file
################################################################################
def check_release_fromfile(namefile): 
    
    ni = namefile.split('.')
    ni = ni[0].split('VV')
    
    if '_2018_2022_1' in ni[-1]: 
        inputrelease = '2018_2022'
        ext_release = '_2018_2022_1'
    else: 
        inputrelease = '2015_2021'
        ext_release = ''
    
    release_para = [inputrelease, ext_release]

    return release_para