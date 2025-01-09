"""
Signature auto created by nvim
@Author: AikenHong
@Mail: h.aiken.970@gmail.com
@Date: 2022-06-28 00:46:38
@Desc:
    the script to convert normal markdown to hexo_blogs(icarus)
    include those function:
        1. add meta data for a blog(beside the subtitle)
        2. add tag <!--more--> for blog, which make the home page clean.
        3. regenerate the cover and thumbnail index, which avoid repetition
    TODO: finish those fucntion and reorganize this script, make it better.
"""
import os
import sys
import glob
from tqdm import tqdm
import random
import datetime


def get_all_blogs(directory, verbose=False):
    blogs = glob.glob(directory + "/*.md")
    blogs = sorted(blogs, key=lambda x: os.path.getctime(x))
    print(blogs)
    blogs = filter_by_date(blogs)
    print(blogs)
    if verbose:
        print(
            "this dir {} have {} blog, we will work for those".format(
                directory, len(blogs)
            )
        )
        for blog in blogs:
            print(blog)
    return blogs


def filter_by_date(xs):
    new_res = []
    for x in xs:
        timetag = os.path.getctime(x)
        # print(timetag)
        filter_time = datetime.datetime(2023, 10, 31, 9, 34, 0)
        # print(filter_time.timestamp())
        if (timetag > filter_time.timestamp()):
            new_res.append(x)
    return new_res

# FIXME: metadata is finish in another script, we should move it here

# def add_metadata(blog, loc = 3, info='toc'):
#     lines = []
#     with open(blog,'r', encoding='UTF-8') as f:
#         lines = f.readlines()
#
#     if info == 'toc':
#         lines.insert(loc, 'toc: true\n')
#         with open(blog,'w', encoding='UTF-8') as f:
#             contents = "".join(lines)
#             f.write(contents)
#
#     return True


def add_more_lines_spec_loc(blog, locs=45):
    # get the counts of this file
    counts = 0
    lines = []
    with open(blog, "r", encoding="UTF-8") as f:
        lines = f.readlines()
        counts = len(lines)
    # ...
    if counts < locs:
        return False
    # add this one.
    lines.insert(locs, "<!-- more -->\n")
    with open(blog, "w", encoding="UTF-8") as f:
        contents = "".join(lines)
        f.write(contents)
    return True


def reindex_img_of_blog(blogs, num_of_pic, israndom=False):
    # using index to regenerate the pic num.
    basic_path = "{}: /img/header_img/lml_bg{}.jpg\n"
    for index, blog in enumerate(tqdm(blogs)):
        print(blog, index)
        contexts = []
        meta = 2
        # get and modify origin file.
        with open(blog, "r", encoding="UTF-8") as reader:
            for line in reader:
                if "---" in line:
                    meta -= 1
                if "cover:" in line and meta > 0:
                    order = get_random(index, num_of_pic, israndom)
                    contexts.append(basic_path.format("cover", order))
                    print("modify")
                elif "thumbnail:" in line and meta > 0:
                    order = get_random(index, num_of_pic, israndom)
                    contexts.append(basic_path.format("thumbnail", order))
                else:
                    contexts.append(line)
        # note down the new file.
        with open(blog, "w", encoding="UTF-8") as writer:
            new_file = "".join(contexts)
            writer.write(new_file)

    return True


def get_random(index, nums, israndom=False):

    if israndom:
        return random.randint(0, nums)
    new_order = index % nums

    return new_order


if __name__ == "__main__":
    # this line is for linux sys, you can set it to windows pattern
    blog_path = sys.argv[1]
    blogs = get_all_blogs(blog_path, False)
    # reindex_img_of_blog(blogs, 44, False)

    # test the
    print("done")
