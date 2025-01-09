#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USING replace of $$->abcde,$->$$,abcde->$$ also
WARNING：This will be overwrite the origin file，make bak before
Author: @AikenHong 2021
Purpose:
    Format the inLine Tex in md to blogs(gitbook)
Example:
    $tex$ -> $$tex$$
"""
import glob
import os
import time

# define a match fuction to replace the $
def ezsyntaxMatch(lines):
    """
    match '\' as skiper
    match '$' and '$$'
    """
    resfile = []
    for line in lines:
        index = 0
        listline = list(line)

        while(index < len(listline)):
            if listline[index] == "\\":
                index += 1
            elif listline[index] == '$' and listline[index+1] != '$' :
                listline.insert(index+1,'$')
                index += 1
            elif listline[index] == '$' and listline[index+1] == '$':
                index += 1
            index += 1
        line = ''.join(listline)
        resfile.append(line)
        # print(line)
    # print(resfile)
    return resfile

def writebakfile(name, resfile):
    with open(name, "w") as f:
        f.writelines(resfile)
    print('finish writing the file : {}'.format(name))

def process():
    # get all the md files in the dir
    targetdir = r'.'
    filelist = glob.glob(os.path.join(targetdir,'*.md'))
    assert len(filelist) != 0, 'there is not file in this dir'
    print("those file we will modify {} ".format(filelist))

    # read lines of markdown files
    for file in filelist:
        with open(file) as f:
            lines = f.readlines()
        # read data, we will keep the \n in the end of line.
        lines = [i for i in lines]
        # print(lines)
        resfile = ezsyntaxMatch(lines)
        writebakfile(file, resfile)

if __name__ == '__main__':
    print(__doc__)
    starttime = time.time()
    process()
    print('it spend {}'.format(time.time()-starttime))


