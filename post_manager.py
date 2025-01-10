# FIXME: 重建Github仓库，基于GPT重写README;
# TODO: 自动触发发布任务：
# * 2. Linklog文件夹随着Publish的改动同步更新，同样用.env or sql 存储对应的文件夹数据，当发生改动的时候将新增的文件publish出去

from datetime import datetime, timedelta
import hashlib
import shutil

import os
import re
import random
import logging
import frontmatter
from glob import glob
import logging.handlers
import platform
import sqlite3
import subprocess

# * consider setup logger by .env file
# Configure logging with file rotation and detailed format
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_format = '%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Create logger
logger = logging.getLogger("post_process")
logger.setLevel(logging.DEBUG)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join(log_dir, 'post_manager.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(log_format, date_format))
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format, date_format))
console_handler.setLevel(logging.INFO)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# FIXME: 根据不同平台自适应获取创建时间的函数
# FIXME: 完善异常处理逻辑，不要直接终止流程，而是提示错误的文件
# FIXME: 考虑是否支持仅针对错误文件重新提取（从自己的log中找文件名或者给定之类）
def get_create_time(file_path):
    """
    获取文件的创建时间，适应不同平台。
    
    Args:
        file_path (str): 文件路径。
    
    Returns:
        float: 文件创建时间的时间戳，如果获取失败则返回None。
    """
    try:
        if platform.system() == 'Windows':
            return os.path.getctime(file_path)
        else:
            stat = os.stat(file_path)
            return stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime
    except Exception as e:
        logger.error(f"Failed to get creation time for {file_path}: {e}")
        return None

def get_modify_time(file_path):
    """
    获取文件的修改时间。
    
    Args:
        file_path (str): 文件路径。
    
    Returns:
        float: 文件修改时间的时间戳，如果获取失败则返回None。
    """
    try:
        return os.path.getmtime(file_path)
    except Exception as e:
        logger.error(f"Failed to get modification time for {file_path}: {e}")
        return None

# TODO: 是否要考虑同个category的Post使用同一个Cover
# IDEA: 考虑是否要支持基本的UI

class PostsIterator:
    DEFAULT_TYPE = ['default', 'newest', 'new']
    MODIFY_TYPE = ['modify']
    INIT_TYPE = ['init', 'initial', 'all']
    def __init__(self, post_path:str, pub_type:str="default", nums:int=1, depth:int=2) -> None:
        """
        初始化PostsIterator对象。
        
        Args:
            post_path (str): 帖子目录路径。
            pub_type (str): 发布类型。
            nums (int): 帖子数量。
            depth (int): 搜索深度。
        """
        self.post_dir_path = post_path
        self.pub_type = pub_type
        self.search_depth = depth
        self.nums = nums

        self.all_post_list = self._get_all_post_list()
        self.valid_posts = self.get_valid_posts_list(self.all_post_list)
        return
    
    def get_valid_posts_list(self, post_list) -> list:
        """
        获取有效的帖子列表。
        
        Args:
            post_list (list): 所有帖子列表。
        
        Returns:
            list: 有效的帖子列表。
        """
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
        """
        获取所有帖子列表。
        
        Returns:
            list: 所有帖子列表。
        """
        all_post_list = []

        for i in range(self.search_depth):
            all_post_list += glob(
                os.path.join(self.post_dir_path, "*/"*i+"*.md")
            )
        return all_post_list

    def _get_sort_by_ctime(self, post_list:list, verbose:bool=True) -> list:
        """
        根据创建时间对帖子进行排序。
        
        Args:
            post_list (list): 帖子列表。
            verbose (bool): 是否输出详细信息。
        
        Returns:
            list: 排序后的帖子列表。
        """
        file_data_list = []
        for post in post_list:
            if os.path.isfile(post):
                ctime = get_create_time(post)
                if ctime:
                    file_data_list.append({"pth": post, "ctime": ctime})
                else:
                    logger.warning(f"Skipping file {post} due to missing creation time.")
        sort_file_list = sorted(file_data_list, key=lambda x: x["ctime"])
        if verbose:
            for post in sort_file_list:
                logger.info(f"{post['pth']} - {datetime.fromtimestamp(post['ctime'])}")
        return sort_file_list

    def _get_sort_by_mtime(self, post_list:list) -> list:
        """
        根据修改时间对帖子进行排序。
        
        Args:
            post_list (list): 帖子列表。
        
        Returns:
            list: 排序后的帖子列表。
        """
        return 
    

    def __getitem__(self, index):
        """
        获取指定索引的帖子。
        
        Args:
            index (int): 索引。
        
        Returns:
            dict: 指定索引的帖子。
        """
        return self.valid_post_list[index]


class PostManipulator:
    HEXO_TYPE = ['icarus', 'hexo']
    HUGO_TYPE = ['papermod', 'hugo']
    def __init__(self, pub_type:str, pub_path:str = "./") -> None:
        """
        初始化PostManipulator对象。
        
        Args:
            pub_type (str): 发布类型。
            pub_path (str): 发布路径。
        """
        # base attr setting
        self.cover_base_path = "/cover/cover{}.jpeg"
        self.cover_list = None # none will not assign cover if cover-mod is none.
        self.cover_nums = 0 

        self.pub_type = pub_type
        self.pub_path = pub_path
        
        return

    def publish(self, post_path) -> bool:
        """
        发布帖子。
        
        Args:
            post_path (str or list): 帖子路径或路径列表。
        
        Returns:
            bool: 发布是否成功。
        """
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
        """
        根据类别存储帖子。
        
        Args:
            post_path (str or list): 帖子路径或路径列表。
        
        Returns:
            bool: 存储是否成功。
        """
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
        """
        根据类别移动文件。
        
        Args:
            post_path (str): 帖子路径。
        
        Returns:
            bool: 移动是否成功。
        """
        try:
            post_info = frontmatter.load(post_path)
            meta_info = post_info.metadata

            category = meta_info["categories"][0]
            category = category.replace(" ", "_").replace("/", "|")

            post_name = os.path.basename(post_path)
            final_dir_path = os.path.join(self.pub_path, category)
            
            if not os.path.exists(final_dir_path):
                os.mkdir(final_dir_path)
            final_post_path = os.path.join(final_dir_path, post_name)
            frontmatter.dump(post_info, final_post_path)
            return True
        except Exception as e:
            logger.error(f"Failed to move file by categories for {post_path}: {e}")
            return False

    
    def _publish(self, post_path:str) -> bool:
        """
        发布帖子。
        
        Args:
            post_path (str): 帖子路径。
        
        Returns:
            bool: 发布是否成功。
        """
        try:
            if self.pub_type.lower() in self.HEXO_TYPE:
                return self.publish_hexo(post_path)
            elif self.pub_type.lower() in self.HUGO_TYPE:
                return self.publish_hugo(post_path)
            else:
                logger.warning(f"Publish type {self.pub_type} not supported.")
                return False
        except Exception as e:
            logger.error(f"Failed to publish {post_path}: {e}")
            return False

    def publish_hexo(self, post:str)->bool:
        """
        发布Hexo类型的帖子。
        
        Args:
            post (str): 帖子路径。
        
        Returns:
            bool: 发布是否成功。
        """
        post_info = frontmatter.load(post)
        meta_info = post_info.metadata

        # * the dict will pass the obj directly.
        res = self._modify_hexo_metadata(meta_info)
        
        # 
        return res

    def publish_hugo(self, post:str)->bool:
        """
        发布Hugo类型的帖子。
        
        Args:
            post (str): 帖子路径。
        
        Returns:
            bool: 发布是否成功。
        """
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
        """
        修改Hexo元数据。
        
        Args:
            meta_info (dict): 元数据字典。
        
        Returns:
            bool: 修改是否成功。
        """
        # * catch the exception, if something wrong happen return false.
        # maybe pass the exception info as well

        return True

    def _modify_hugo_metadata(self, meta_info:dict) -> bool:
        """
        修改Hugo元数据。
        
        Args:
            meta_info (dict): 元数据字典。
        
        Returns:
            bool: 修改是否成功。
        """
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
        """
        修改Hugo内容。
        
        Args:
            post_content (str): 帖子内容。
            encrypt (str): 加密字符串。
        
        Returns:
            str: 修改后的内容。
        """
        # modify those special display.
        # * 1. update latex display by surround by <span></span> or <div></div>
        post_content = self._surround_latex_by_tag(post_content)

        # * 2. update gallery formate.
        post_content = self._update_gallery_to_hugo(post_content)

        # * 3. del more-tag in file.
        post_content = self._del_more_tag(content=post_content)

        # * 4. replace <small>...</small> with <sidenote>...</sidenote>
        post_content = self._replace_small_with_sidenote(post_content)

        # * 5. update for password article
        if (encrypt is None): 
            return post_content
        post_content = self._encrypt_hugo_content(post_content, encrypt)
        
        return post_content
    
    def _record_fail_log(self, res:bool, post_path:str):
        """
        记录失败日志。
        
        Args:
            res (bool): 结果。
            post_path (str): 帖子路径。
        """
        if (not res):    
            logger.error("[Publish] {} failed, check what happen".format(post_path))

        return

    def _update_gallery_to_hugo(self, content:str) -> str:
        """
        更新Hugo画廊格式。
        
        Args:
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
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
        """
        删除Hugo的more标签。
        
        Args:
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
        more_pattern = re.compile(r'<!--\s*more\s*-->')
        if not more_pattern:
            return content
        
        logger.error("[_del more tag for hugo] execute")
        
        new_content = more_pattern.sub('',content)
        return new_content

    def _encrypt_hugo_content(self, content:str, encrypt:str) -> str:
        """
        加密Hugo内容。
        
        Args:
            content (str): 帖子内容。
            encrypt (str): 加密字符串。
        
        Returns:
            str: 加密后的内容。
        """
        logger.error("[_encrypt_hugo_content] {}".format(encrypt))

        encrypt_content = '{{{{% hugo-encryptor "{}" %}}}} \n'.format(encrypt)
        encrypt_content += content
        encrypt_content += "\n{{% /hugo-encryptor %}}"
        return encrypt_content
    
    def _replace_small_with_sidenote(self, content: str) -> str:
        """
        将<small>标签替换为<sidenote>标签。
        
        Args:
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
        # ignore code blocks
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        preserved_code_blocks = {}
        for i, match in enumerate(code_block_pattern.finditer(content)):
            placeholder = f"__CODE_BLOCK_{i}__"
            preserved_code_blocks[placeholder] = match.group(0)
            content = content.replace(match.group(0), placeholder)
        
        # replace <small>...</small> with <sidenote>...</sidenote>
        content = re.sub(r'<small>(.*?)</small>', r'<sidenote>\1</sidenote>', content, flags=re.DOTALL)
        
        # restore code blocks
        for placeholder, code_block in preserved_code_blocks.items():
            content = content.replace(placeholder, code_block)
        
        return content
        
    def _surround_latex_by_tag(self, content:str) -> str:
        """
        用标签包围LaTeX内容。
        
        Args:
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
        # *. need to match those inline latex & block latex & ignore those $ in ``` block
        # 1. read code block and ignore it.
        # 非贪婪匹配
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        preserved_code_blocks = {}
        for i, match in enumerate(code_block_pattern.finditer(content)):
            placeholder = f"__CODE_BLOCK_{i}__"
            preserved_code_blocks[placeholder] = match.group(0)
            content = content.replace(match(0), placeholder)

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
        """
        在LaTeX行内公式周围添加空格。
        
        Args:
            match (re.Match): 正则匹配对象。
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
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
        """
        在LaTeX块公式周围添加<div>标签。
        
        Args:
            match (re.Match): 正则匹配对象。
            content (str): 帖子内容。
        
        Returns:
            str: 修改后的内容。
        """
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


class PostModificationScanner:
    def __init__(self, source_folder, publish_folder):
        """
        初始化PostModificationScanner对象。
        
        Args:
            source_folder (str): 源文件夹路径。
            publish_folder (str): 发布文件夹路径。
        """
        self.source_folder = source_folder
        self.publish_folder = publish_folder

    def scan_and_update(self):
        """
        扫描并更新帖子。
        """
        for dirpath, dirnames, filenames in os.walk(self.source_folder):
            if self.is_publish_folder(dirpath):
                continue
        
            for filename in filenames:
                if filename.endswith('.md'):
                    self.process_file(os.path.join(dirpath, filename))

    def is_publish_folder(self, path):
        """
        判断是否为发布文件夹。
        
        Args:
            path (str): 文件夹路径。
        
        Returns:
            bool: 是否为发布文件夹。
        """
        return os.path.normpath(path) == os.path.normpath(self.publish_folder)

    def is_modify_within_days(self, file_path, days=5):
        """
        判断文件是否在指定天数内修改过。
        
        Args:
            file_path (str): 文件路径。
            days (int): 天数。
        
        Returns:
            bool: 是否在指定天数内修改过。
        """
        modification_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(modification_time)
        # logger.info(f"{file_path}: delta f{datetime.now() - file_date}")
        return datetime.now() - file_date <= timedelta(days=days)

    def calculate_md5(self, file_path):
        """
        计算文件的MD5值。
        
        Args:
            file_path (str): 文件路径。
        
        Returns:
            str: 文件的MD5值。
        """
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        return md5_hash.hexdigest()
    
    def process_file(self, file_path):
        """
        处理文件。
        
        Args:
            file_path (str): 文件路径。
        """
        try:
            if not self.is_modify_within_days(file_path):
                return 
            filename = os.path.basename(file_path)
            publish_file_path = os.path.join(self.publish_folder, filename)

            if os.path.exists(publish_file_path):
                current_md5 = self.calculate_md5(file_path)
                publish_md5 = self.calculate_md5(publish_file_path)
                if current_md5 != publish_md5:
                    logger.info(f"Updating {filename} in the Publish folder")
                    shutil.copy(file_path, publish_file_path)
                else:
                    logger.info(f"{filename} has no changes.")
            else:
                logger.debug(f" {filename} is not a publish file, just ignore it.")
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")

class PublishDirectoryUpdateScanner:
    def __init__(self, published_folder, db_path='publish_info.db'):
        """
        初始化PublishDirectoryUpdateScanner对象。
        
        Args:
            published_folder (str): 发布文件夹路径。
            db_path (str): 数据库路径。
        """
        self.published_folder = published_folder
        self.db_path = db_path
        self._init_db()
        logger.info(f"Initialized PublishDirectoryUpdateScanner with folder: {published_folder} and database: {db_path}")

    def _init_db(self):
        """
        初始化数据库。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publish_info (
                id INTEGER PRIMARY KEY,
                last_update_time TIMESTAMP,
                human_readable_time TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized and table created if not exists.")

    def _get_last_update_time(self):
        """
        获取最后更新时间。
        
        Returns:
            float: 最后更新时间的时间戳。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_update_time, human_readable_time FROM publish_info ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        last_update_time = result[0] if result else None
        human_readable_time = result[1] if result else None
        logger.info(f"Last update time retrieved: {last_update_time} ({human_readable_time})")
        return last_update_time

    def _update_last_update_time(self, update_time):
        """
        更新最后更新时间。
        
        Args:
            update_time (float): 更新时间的时间戳。
        """
        human_readable_time = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO publish_info (last_update_time, human_readable_time) VALUES (?, ?)', (update_time, human_readable_time))
        conn.commit()
        conn.close()
        logger.info(f"Last update time updated to: {update_time} ({human_readable_time})")

    def _get_newest_file_time(self):
        """
        获取最新文件的时间。
        
        Returns:
            float: 最新文件的时间戳。
        """
        newest_time = None
        for dirpath, dirnames, filenames in os.walk(self.published_folder):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_time = max(os.path.getctime(file_path), os.path.getmtime(file_path))
                if newest_time is None or file_time > newest_time:
                    newest_time = file_time
        human_readable_time = datetime.fromtimestamp(newest_time).strftime('%Y-%m-%d %H:%M:%S') if newest_time else None
        logger.info(f"Newest file time in publish directory: {newest_time} ({human_readable_time})")
        return newest_time

    def scan_and_update(self):
        """
        扫描并更新发布目录。
        """
        last_update_time = self._get_last_update_time()
        newest_file_time = self._get_newest_file_time()

        if last_update_time is None or newest_file_time > last_update_time:
            logger.info("Publish directory has been updated. Starting publish process.")
            self._publish_new_files(last_update_time)
            self._update_last_update_time(newest_file_time)
            # self._commit_and_push_changes()
        else:
            logger.info("No updates in the publish directory.")

    def _publish_new_files(self, last_update_time):
        """
        发布新文件。
        
        Args:
            last_update_time (float): 最后更新时间的时间戳。
        """
        post_manager = PostManipulator(pub_type='hugo', pub_path='/path/to/deploy/dir')
        for dirpath, dirnames, filenames in os.walk(self.published_folder):
            for filename in filenames:
                if not filename.endswith('.md'):
                    continue
                file_path = os.path.join(dirpath, filename)
                file_time = max(get_create_time(file_path), get_modify_time(file_path))
                if last_update_time is None or file_time > last_update_time:
                    human_readable_time = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"Publishing file: {file_path} (modified at {human_readable_time})")
                    try:
                        post_manager.publish(file_path)
                    except Exception as e:
                        logger.error(f"Failed to publish file {file_path}: {e}")

    def _commit_and_push_changes(self):
        """
        提交并推送更改。
        """
        deploy_dir = '/path/to/deploy/dir'
        os.chdir(deploy_dir)
        logger.info("Committing and pushing changes to remote repository.")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Auto-publish updated files'], check=True)
        subprocess.run(['git', 'push'], check=True)


def test_platform_specific_functionality():
    """
    测试平台特定功能。
    """
    current_platform = platform.system()
    logger.info(f"Running tests on platform: {current_platform}")

    if current_platform == "Windows":
        logger.info("Testing on Windows platform.")
        post_scanner = PostModificationScanner("D:\OneDrive\Posts文档", "D:\OneDrive\Posts文档\Published发布")
        post_scanner.scan_and_update()

    elif current_platform == "Darwin":
        logger.info("Testing on macOS platform.")
        post_scanner = PostModificationScanner("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档", "/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档/Published发布")
        post_scanner.scan_and_update()
    elif current_platform == "Linux":
        logger.info("Testing on Linux platform.")

    else:
        logger.warning("Unknown platform. No specific tests available.")
        return
    
    return
    # post_manager.publish(post_path=post_list)

if __name__ == "__main__":
    # ----------------test publish 
    post_list = glob("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档/Published发布/*.md")
    post_manager = PostManipulator(pub_type='hugo', pub_path='/Users/aikenhong/workspace/hugo-theme/content/posts')
    # post_manager.publish(post_path=post_list)

    # ----------------test metadata
    # metadata = frontmatter.load("./test.md")
    # logger.warning("[metadata]"+str(metadata.metadata))


    # ----------------test organize by categories.
    # posts = PostsIterator("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档")
    # post_manager.store_by_categories(post_list)


    # ----------------test sync post.
    # post_scanner = PostModificationScanner("D:\OneDrive\Posts文档", "D:\OneDrive\Posts文档\Published发布")
    # post_scanner.scan_and_update()

    # Test logger functionality
    # test_logger()

    # Test platform-specific functionality
    test_platform_specific_functionality()

    # Test PublishDirectoryUpdateScanner
    publish_scanner = PublishDirectoryUpdateScanner("/Users/aikenhong/Library/CloudStorage/OneDrive-个人/Posts文档/Published发布")
    publish_scanner.scan_and_update()

