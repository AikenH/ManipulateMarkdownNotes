"""
Signature auto created by nvim
@Author: AikenHong
@Desc: Generate hexo blogs's header for markdown files
"""

import os
import glob
import time

# define the path of saving and the target path.
# BlogPath = r"/mnt/d/OneDrive/Literature/"
# TargetPath = r"/mnt/e/WorkSpaceB/hexo_version_blog/source/_posts/en/"
BlogPath = 
TargetPath = 

def get_all_blogs(path):
    # get all blog path.
    dirs = os.listdir(BlogPath)
    blogs = []

    for blog_dir in dirs:
        if blog_dir not in ['.obsidian','_book', 'Day Planners', 'node_module', '毕业论文','Draft']:
            tmpdir = os.path.join(BlogPath, blog_dir)
            blogs += glob.glob(tmpdir + '/*.md')
    # del using _ replace space of filename.
    for blog in blogs:
        if ' ' in blog:
            blog = blog.replace(' ', '_')
            print(blog)

    return blogs

# TODO: get the basic info of each blog
# title(name of files) \ catalog: true \ data: create time \ subtitle: desc \ lang cn\en
# header-img: we can create a loop to generate this part.
# tags, categories, mathjax.
def change_realtime(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)

def get_attribute(blog, verbose=False):
    attr = {}
    # get timestamp.
    create_time = os.path.getctime(blog)
    modify_time = os.path.getmtime(blog)
    attr['data'] = change_realtime(create_time)
    attr['m_data'] = change_realtime(modify_time)

    # get tags and categories.
    tags = blog.split('\\')[-2]
    attr['tags'] = tags
    attr['categories'] = tags

    # get title.
    with open(blog, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        title = lines[0].strip().split('#')[1]
        attr['title'] = title

    # default attr
    attr['lang'] = 'cn'
    # verbose:
    if verbose: print(blog, '\n', attr)
    return attr

def cpy_files(blog,target):
    """cpy files to the target path"""
    filename = os.path.basename(blog)
    os.system('cp ' + blog + ' ' + target + filename)
    return target + filename

def add_header(blog,index=0,attr=None):
    """add default header for each files"""
    header_imgs = ["",1, 2, 3, 4,5]
    with open(blog, "r+", encoding='UTF-8') as f:
        old = f.read()
        f.seek(0)
        f.write("---\n")
        f.write("title: " + attr['title'] + "\n")
        f.write("catalog: true\n")
        f.write("date: " + attr['data'] + "\n")
        f.write("subtitle: \n")
        f.write("lang: " + attr['lang'] + "\n")
        f.write("header-img: " + '/img/header_img/lml_bg{}.jpg'.format(index%6) + "\n")
        f.write("tags: " + "\n")
        f.write("-  " + attr['tags'] + "\n")
        f.write("categories: " + "\n")
        f.write("-  " + attr['categories'] + "\n")
        f.write("---\n")
        f.write(old)
    return

def dir_process():
    blogs = get_all_blogs(BlogPath)
    for i,blog in enumerate(blogs):
        b_attr = get_attribute(blog)
        new_blog = cpy_files(blog, TargetPath)
        add_header(new_blog, index=i, attr=b_attr)

if __name__ == '__main__':
    dir_process()
    print('Done!')
