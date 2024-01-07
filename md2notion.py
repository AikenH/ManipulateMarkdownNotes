# 要添加一个新单元，输入 '# %%'
# 要添加一个新的标记单元，输入 '# %% [markdown]'
# %% [markdown]
# # Translate markdown to notion
# @Aiken with the md2notion.pypi
# the most impotant problem is about transfer the  latex 

# %%
# inport the related modules
import os
import tqdm
from notion.client import NotionClient
from notion.block import PageBlock
from md2notion.upload import upload,convert, uploadBlock
from md2notion.NotionPyRenderer import NotionPyRenderer, addLatexExtension
import itertools

# %% [markdown]
# 主要自定义的地方👇

# %%
# basic client setting and token get from the websize setting 
client = NotionClient(token_v2=<u token_v2 here>)
page = client.get_block("<https://www.notion.so/yourpage>")

# basic files in the dir
path = r'D:\OneDrive\WorkSpace\Universal Framework\layers'
mdfiles = os.listdir(path)
mdfiles = [f for f in mdfiles if os.path.splitext(f)[1] == '.md']
mdfiles


# %%
print("The old title is:", page.title)
for file in mdfiles:
    filepath = os.path.join(path,file)
    with open(filepath, "r", encoding="utf-8") as mdFile:
        newPage = page.children.add_new(PageBlock, title=file)
        
        lines=mdFile.readlines()
        new_lines = []
        for (i, line) in enumerate(lines):
            new_line = [None, line, None]
            if i > 0 and i < len(lines) - 2:
                if line == '$$\n' and lines[i-1][0] != '\n':
                    new_line[0] = '\n'
                if line == '$$\n' and lines[i+1][0] != '\n':
                    new_line[2] = '\n'
                
            new_lines.append(new_line)
        new_lines = list(itertools.chain(*new_lines))
        new_lines = list(filter(lambda x: x is not None, new_lines))
        new_lines = ''.join(new_lines)
        
        lines = new_lines.splitlines(keepends=True)
        # lines = [line if line.endswith('\n') else '{}\n'.format(line) for line in lines]
        
        rendered = convert(lines, addLatexExtension(NotionPyRenderer))
        for blockDescriptor in rendered:
            uploadBlock(blockDescriptor, newPage, mdFile.name)


print(__doc__)
# %%
