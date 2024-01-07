"""
Signature auto created by nvim
@Author: AikenHong
@Desc: add more and meta data for markdown files
"""

import numpy as np
import glob
import os

# we add <!-- more --> to a spcific location
def get_all_blogs(directory, verbose = False):
    # get all blog path
    blogs = glob.glob(directory + '/*.md')
    if verbose:
        print(len(blogs))
        for blog in blogs:
            print(blog + '\n')
    return blogs 

# using dict to save all the metadata we want
# using loop to generate it. and add it on. may be better.
# tryit and must faster.
def add_metadata(blog, loc = 3, info='toc'):
    lines = []
    with open(blog,'r', encoding='UTF-8') as f:
        lines = f.readlines()
    
    if info == 'toc':
        lines.insert(loc, 'toc: true\n')
        with open(blog,'w', encoding='UTF-8') as f:
            contents = "".join(lines)
            f.write(contents)

    return True


# using grep to checkout and locate section.
# using sed can easily add <!--more--> for those file
# make this part script, but on windows. maybe python still.
def add_more_lines_spec_loc(blog, locs=45):
    # get the counts of this file
    counts = 0
    lines = []
    with open(blog, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        counts = len(lines)
    
    # ...
    if counts < locs: return False
    else:
        # add this one.
        lines.insert(locs,"<!-- more -->\n")
        with open(blog,'w', encoding='UTF-8') as f:
            contents = "".join(lines)
            f.write(contents)
    return True

if __name__ == '__main__':

    # this line is for linux sys, you can set it to windows pattern
    blog_path = '/mnt/g/WorkSpaceLocal/Hexo_Blog_Test/source/_posts'
    blogs =  get_all_blogs(blog_path,True)

    for blog in blogs:
    #     add_more_lines_spec_loc(blog, 45)
        add_metadata(blog, loc=3, info='toc')

    print('done')
