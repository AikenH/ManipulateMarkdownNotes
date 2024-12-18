# FIXME: 重建Github仓库，基于GPT重写README;
# TODO: 自动触发发布任务：
# * 1. Publish文件有改动的时候定期触发发布任务，发布到指定的hugo文件夹中，随后自动commit并更新github
# * 2. Linklog文件夹随着Publish的改动同步更新，同样用.env or sql 存储对应的文件夹数据，当发生改动的时候将新增的文件publish出去

from curses import meta
from datetime import datetime
import os
import re
import random
import logging
import frontmatter
from glob import glob

# * consider setup logger by .env file

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s ', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.WARNING)
logger = logging.getLogger("post_process")

# FIXME: 根据不同平台自适应获取创建时间的函数
# FIXME: 完善异常处理逻辑，不要直接终止流程，而是提示错误的文件
# FIXME: 考虑是否支持仅针对错误文件重新提取（从自己的log中找文件名或者给定之类）
def get_create_time(file_path):
    # Get the status of the file
    file_stat = os.stat(file_path)
    # Return the birth time (creation time)
    return file_stat.st_birthtime

# TODO: 是否要考虑同个category的Post使用同一个Cover
# TODO: 基于这次的脚本来重建仓库，考虑操作文件位置等
# IDEA: 考虑是否要支持基本的UI

class PostsIterator:
    DEFAULT_TYPE = ['default', 'newest', 'new']
    MODIFY_TYPE = ['modify']
    INIT_TYPE = ['init', 'initial', 'all']
    def __init__(self, post_path:str, pub_type:str="default", nums:int=1, depth:int=2) -> None:
        self.post_dir_path = post_path
        self.pub_type = pub_type
        self.search_depth = depth
        self.nums = nums

        self.all_post_list = self._get_all_post_list()
        self.valid_posts = self.get_valid_posts_list(self.all_post_list)
        return
    
    def get_valid_posts_list(self, post_list) -> list:
        # sort post by mod, then select post.
        if (self.pub_type.lower() in self.DEFAULT_TYPE):
            # * sort by create time. 
            sorted_posts = self._get_sort_by_ctime(post_list)
            valid_posts = [post["pth"] for post in sorted_posts]
            return valid_posts
        
        elif (self.pub_type.lower() in self.MODIFY_TYPE):
            # * sort by modify time 
            return
        elif (self.pub_type.lower() in self.INIT_TYPE):
            logger.warning("[get_valid_posts_list] initial, using all post from src dir")
            return self.all_post_list
        
        else:
            logger.error("[get_valid_posts_list] failed, check initial type")

        return None
    
    def _get_all_post_list(self):
        all_post_list = []

        for i in range(self.search_depth):
            all_post_list += glob(
                os.path.join(self.post_dir_path, "*/"*i+"*.md")
            )
        return all_post_list

    def _get_sort_by_ctime(self, post_list:list, verbose:bool=True) -> list:
        file_data_list = [
            {"pth": post, "ctime": get_create_time(post)}
            for post in post_list if os.path.isfile(post)
        ]
        sort_file_list = sorted(file_data_list, key=lambda x: x["ctime"])
        if (verbose):
            for post in sort_file_list:
                print(f"{post['pth']} - {datetime.fromtimestamp(post['ctime'])}")
        return sort_file_list

    def _get_sort_by_mtime(self, post_list:list) -> list:

        return 
    

    def __getitem__(self, index):
        return self.valid_post_list[index]


class PostManipulator:
    HEXO_TYPE = ['icarus', 'hexo']
    HUGO_TYPE = ['papermod', 'hugo']
    def __init__(self, pub_type:str, pub_path:str = "./") -> None:

        # base attr setting
        self.cover_base_path = "/cover/cover{}.jpeg"
        self.cover_list = None # none will not assign cover if cover-mod is none.
        self.cover_nums = 0 

        self.pub_type = pub_type
        self.pub_path = pub_path
        
        return

    def publish(self, post_path) -> bool:
        if (self.pub_type.lower() not in self.HEXO_TYPE and self.pub_type not in self.HUGO_TYPE):
            logger.warning("[publish] publish type not support, check your publish type")
            return False
        
        # * file_path or list
        if (isinstance(post_path, list)):
           for post in post_path:
               res = self._publish(post)
               self._record_fail_log(res, post)
        
        elif(isinstance(post_path, str)):
            res = self._publish(post_path)
            self._record_fail_log(res=res, post_path=post_path)

        else:
            logger.warning("[publish] the post type seems wrong, do not carry out publish")
        return True
    
    def store_by_categories(self, post_path) -> bool:
         # * file_path or list
        if (isinstance(post_path, list)):
           for post in post_path:
               res = self._move_file_by_categories(post)
               self._record_fail_log(res, post)
        
        elif(isinstance(post_path, str)):
            res = self._move_file_by_categories(post_path)
            self._record_fail_log(res=res, post_path=post_path)

        else:
            logger.warning("[publish] the post type seems wrong, do not carry out publish")
        pass

    def _move_file_by_categories(self, post_path:str) -> bool:
        post_info = frontmatter.load(post_path)
        meta_info = post_info.metadata

        try:
            category = meta_info["categories"][0]
            category = category.replace(" ", "_")
            category = category.replace("/", "|")
        except:
            print(post_path)
            return False

        post_name = os.path.basename(post_path)
        final_dir_path = os.path.join(self.pub_path, category)
        
        if not os.path.exists(final_dir_path):
            os.mkdir(final_dir_path)
        final_post_path = os.path.join(final_dir_path, post_name)
        # print(final_post_path)
        frontmatter.dump(post_info, final_post_path)

        return True

    
    def _publish(self, post_path:str) -> bool:
        if (self.pub_type.lower() in self.HEXO_TYPE):            
            res = self.publish_hexo(post_path)

        elif (self.pub_type.lower() in self.HUGO_TYPE):
            res = self.publish_hugo(post_path)

        if(not res):
            return False
        
        return True

    def publish_hexo(self, post:str)->bool:
        post_info = frontmatter.load(post)
        meta_info = post_info.metadata

        # * the dict will pass the obj directly.
        res = self._modify_hexo_metadata(meta_info)
        
        # 
        return res

    def publish_hugo(self, post:str)->bool:
        post_info = frontmatter.load(post)
        meta_info = post_info.metadata
        
        # * get encrypt params
        encrypt = None
        if "password" in meta_info:
            encrypt = meta_info["password"]

        # * the dict will pass the obj directly.
        res = self._modify_hugo_metadata(meta_info=meta_info)
        post_info.content = self._modify_hugo_content(post_info.content, encrypt)

        # * get the filename & assign it to the new path
        post_name = os.path.basename(post)
        final_post_path = os.path.join(self.pub_path, post_name)
        frontmatter.dump(post_info, final_post_path)
        return res

    def _modify_hexo_metadata(self, meta_info:dict) -> bool:
        # * catch the exception, if something wrong happen return false.
        # maybe pass the exception info as well

        return True

    def _modify_hugo_metadata(self, meta_info:dict) -> bool:
        # * catch the exception, if something wrong happen return false.
        # maybe pass the exception info as well

        # * 1. delete the tag and make it tags.
        if "tag" in meta_info:
            meta_info["tags"] = meta_info.pop("tag")
        
        # *2. change the cover' attr's style. now support same idx.
        if "cover" in meta_info and  isinstance(meta_info['cover'], str):
            src = meta_info.pop("cover")
            
            # get the final num in the file name.
            idx = re.findall(r"\d+", src.split("/")[-1])[-1]
            # FIXME: tmp usage, get the real num after.
            if int(idx) > 27: 
                idx = str(int(idx) % 27)
            idx = random.randint(0, 26)
            # print(idx)
            src = self.cover_base_path.format(idx)
            meta_info["cover"] = {"image": src}

        # * 3. using description replace subtitle
        if "subtitle" in meta_info:
            meta_info["description"] = meta_info.pop("subtitle")

        return True
    
    
    def _modify_hugo_content(self, post_content, encrypt=None) -> str:
        # modify those special display.
        # * 1. update latex display by surround by <span></span> or <div></div>
        post_content = self._surround_latex_by_tag(post_content)

        # * 2. update gallery formate.
        post_content = self._update_gallery_to_hugo(post_content)

        # * 3. del more-tag in file.
        post_content = self._del_more_tag(content=post_content)
    
        # * 4. update for password article
        if (encrypt is None): 
            return post_content
        post_content = self._encrypt_hugo_content(post_content, encrypt)
        
        return post_content
    
    def _record_fail_log(self, res:bool, post_path:str):
        if (not res):    
            logger.error("[Publish] {} failed, check what happen".format(post_path))

        return

    def _update_gallery_to_hugo(self, content:str) -> str:

        div_pattern = re.compile(r'(<div class="justified-gallery">.*?</div>)', re.DOTALL)
        div_match = div_pattern.search(content)

        if (not div_match):
            return content
        
        logger.error("[_update_gallery_to_hugo] execute")

        new_gallery = "{{< galleries >}} \n"
        gallery_content = div_match.group(1)
        img_pattern = re.compile(r'<img\s+src="([^"]+)"(?:\s+alt="([^"]+)")?\s*\/?>')

        for match in img_pattern.finditer(gallery_content):
            img_src = match.group(1).strip()
            img_alt = match.group(2).strip() if match.group(2) else ""

            if img_alt:
                new_gallery += f'{{{{<gallery src="{img_src}" title="{img_alt}" >}}}}\n'
            else:
                new_gallery += f'{{{{<gallery src="{img_src}" >}}}}\n'
        new_gallery += "{{< /galleries >}}"

        new_content = div_pattern.sub(new_gallery, content)
        return new_content
    
    def _del_more_tag(self, content:str) -> str:
        more_pattern = re.compile(r'<!--\s*more\s*-->')
        if not more_pattern:
            return content
        
        logger.error("[_del more tag for hugo] execute")
        
        new_content = more_pattern.sub('',content)
        return new_content

    def _encrypt_hugo_content(self, content:str, encrypt:str) -> str:
        logger.error("[_encrypt_hugo_content] {}".format(encrypt))

        encrypt_content = '{{{{% hugo-encryptor "{}" %}}}} \n'.format(encrypt)
        encrypt_content += content
        encrypt_content += "\n{{% /hugo-encryptor %}}"
        return encrypt_content
        
    def _surround_latex_by_tag(self, content:str) -> str:
        # *. need to match those inline latex & block latex & ignore those $ in ``` block
        # 1. read code block and ignore it.
        # 非贪婪匹配
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        preserved_code_blocks = {}
        for i, match in enumerate(code_block_pattern.finditer(content)):
            placeholder = f"__CODE_BLOCK_{i}__"
            preserved_code_blocks[placeholder] = match.group(0)
            content = content.replace(match.group(0), placeholder)

        # 2. add space surround the inline latex sentence
        inline_latex_pattern = re.compile(r'(?<!\$)(\$.*?\$)(?!\$)')
        
        content = inline_latex_pattern.sub(lambda match: self._latex_add_space_inline(match, content), content)

        # 3. add newline between the $$ block or $$$ block 
        block_latex_pattern = re.compile(r'(?<!\S)(\$\$.*?\$\$|(?<!\S)\$\$\$.*?\$\$\$)(?!\S)', re.DOTALL)

        content = block_latex_pattern.sub(lambda match: self._latex_add_div_tags(match, content), content)

        # 4. restore the code block
        for placeholder, code_block in preserved_code_blocks.items():
            content = content.replace(placeholder, code_block)
            
        return content
    
    def _latex_add_space_inline(self, match, content):
        match_expr = match.group(1)
        start_index = match.start()
        end_index = match.end()

        # check it there is a space before
        if start_index > 0 and content[start_index -1] != ' ':
            match_expr = ' ' + match_expr
        
        if end_index < len(content) and content[end_index] != ' ':
            match_expr = match_expr + ' '

        return match_expr

    def _latex_add_div_tags(self, match, content):
        latex_block = match.group(1).strip()
        # Check if the block is already wrapped in <div> tags
        if not re.search(r'<div>\s*' + re.escape(latex_block) + r'\s*</div>', content):
            # Check for unmatched <div> tags before the LaTeX block
            #                 
            if content[:match.start()].rstrip().endswith('<div>'):
                # Only add </div> after the LaTeX block
                return f"{latex_block}\n</div>\n"
            elif content[match.end():].lstrip().startswith('</div>'):
                # Only add <div> before the LaTeX block
                return f"<div>\n{latex_block}"
            else:
                # No unmatched <div>, wrap the block
                return f"\n<div>\n{latex_block}\n</div>\n"
        return latex_block  # Return the original block if already wrapped


if __name__ == "__main__":
    post_list = glob("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档/Published发布/修改hugo主题的markdown渲染.md")
    post_manager = PostManipulator(pub_type='hugo', pub_path='/Users/aikenhong/workspace/hugo-theme/content/posts')
    post_manager.publish(post_path=post_list)

    # metadata = frontmatter.load("./test.md")
    # logger.warning("[metadata]"+str(metadata.metadata))

    # posts = PostsIterator("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档")

    # post_manager.store_by_categories(post_list)