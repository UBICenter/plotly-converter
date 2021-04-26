import subprocess
import sys
import datetime
from pathlib import Path
from pathlib import PurePath

# print(f"Arguments count: {len(sys.argv)}")
# for i, arg in enumerate(sys.argv):
#     print(f"Argument {i:>6}: {arg}")

# check that input is a python notebook
notebook_path = Path(sys.argv[1])
if notebook_path.suffix != '.ipynb':
    raise ValueError('Expected a Python notebook (".ipynb"), got "%s"' % notebook_path.suffix)

# retrieve notebook file name
title = notebook_path.stem
print(title)
format = "%Y-%m-%d"

# check that the title begins with a proper datetime; this is required by jekyll. 
# eg, 2020-01-02 for January 2, 2020
# 2020-1-2 also works in jekyll but not here, but it's easier to just require the zeros here
add_date = False
try:
    datetime.datetime.strptime(title[:10], format)
except:
    # raise ValueError('File name must start with a date in the format YYYY-MM-DD')
    add_date = True

# set up the output directories for the markdown file and the graphs, respectively
assets_dir = Path()
markdown_dir = Path()
assets_internal = ('assets/markdown_assets/%s' % title)

# check if an output directory is provided
if len(sys.argv) > 2:
    markdown_dir = Path(sys.argv[2])
    if not markdown_dir.exists():
        raise ValueError('Directory "%s" does not exist' % markdown_dir)
    assets_dir = markdown_dir.joinpath('assets', 'markdown_assets', title)
    assets_dir.mkdir(parents = True, exist_ok = True)

# search upwards through the current directory to try to find the ubicenter.org directory
else: 
    dest_path = Path('ubicenter.org', '_posts')
    curr_path = Path(__file__).parent.absolute()
    test_path = curr_path.joinpath(dest_path)
    test_count = 0
    while not test_path.exists() and test_count < 5:
        curr_path = curr_path.parent
        test_path = curr_path.joinpath(dest_path)
        test_count += 1
    if test_path.exists():
        markdown_dir = test_path.absolute()
    else:
        raise ValueError('Could not find destination directory "ubicenter.org/_posts"')

    assets_dir = curr_path.joinpath('ubicenter.org', 'assets', 'markdown_assets', title)
    assets_dir.mkdir(parents = True, exist_ok = True)

print('Destination directory:\n%s' % markdown_dir)
print('Assets directory:\n%s' % assets_dir)

# metadata template
metadata = """---
layout: post
current: post
cover:
navigation: True
title:
date:
tags:
class:
subclass:
author:
---
"""

# convert notebook to myst
myst_file = ''
temp_num = 1
while Path('temp%d.md' % temp_num).exists():
    temp_num += 1
myst_file = 'temp%d.md' % temp_num
subprocess.run(['jupytext', notebook_path, '--to', 'myst', '-o', myst_file])

# open myst file
file = open(myst_file, 'r') 

# update the title if necessary to make it meet jekyll requirements
title = title.replace('_', '-')

date = None
metadata_store = ''
metadata_found = False
for line in file:
    if add_date and 'date' in line:
        date = datetime.datetime.strptime(line[6:].strip(), format)
    # metadata is not included
    if line == '+++':
        metadata_store = metadata
    elif metadata_found:
        if line[:3] == '%%%':
            metadata_store += '---\n'
            break
        metadata_store += line
    elif line[:3] == '%%%':
        metadata_found = True
        metadata_store += '---\n'

if add_date:
    if date == None:
        raise ValueError('File name must start with a date or include a date in metadata in the format YYYY-MM-DD')
    else:
        title = str(date.date()) + '-' + title

# open output file
out_file = open(markdown_dir.joinpath('%s.md' % title), 'w')
# out_file.write('---\n')

out_file.write(metadata_store)

out_file.write(
"""
<head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</head>
""")

# open graph helper file
code_file = open('make_graphs.py', 'w')
code_file.write('import plotly.io as io\n')
code_file.write('from pathlib import Path\n')
code_file.write("\nfolder_path = Path('%s')\n" % assets_dir)
# code_file.write("\nfolder_path.mkdir(parents = True, exist_ok = True)\n")

def clean_text(text):
    return text.replace('\\$', '$')

# code prefix
def add_code_start(count):
  out_file.write("""
<button class="code-button" id="button%d" onclick="f%d()">&#9654; Click to show code</button>
<div class="code-cell" id="asset_code_%d" style="display: none;">
  <pre>
    <code>
""" % (count, count, count))

# code postfix
def add_code_end(block, count):
    out_file.write(block.strip())
    out_file.write("""
    </code>
  </pre>
</div>

<script>
function f%d() {
  var x = document.getElementById("asset_code_%d");
  var b = document.getElementById("button%d");
  if (x.style.display === "none") {
    x.style.display = "block";
    b.innerHTML = "&#9660 Click to hide code";
  } else {
    x.style.display = "none";
    b.innerHTML = "&#9654 Click to show code";
  }
}
</script> \n""" % (count, count, count))

    out_file.write("""
<div>
  <script>
    $(document).ready(function(){
      $("#asset%d").load("{{site.baseurl}}%s/%s-asset-%d.html");
    });
  </script>
</div>
<div id = "asset%d"></div>\n""" % (count, assets_internal, title, count, count))

def add_plotly_code(block, count):
    code_file.write(block)
    code_file.write("io.write_html(fig, str(folder_path.joinpath('%s-asset-%d.html')), full_html = False, include_plotlyjs = False, config = {'displayModeBar': False, 'responsive': True})\n\n" % (title, count))

def add_dataframe_code(block, count):
    block = block.strip()
    block += ".to_html(str(folder_path.joinpath('%s-asset-%d.html')))\n\n" % (title, count)
    code_file.write(block)

def add_stargazer_code(block, code):
    block = block.strip()
    last_line = block.split('\n')[-1]
    block += '\n\n'

    block += "_sg_html = %s.render_html()\n" % last_line
    block += "_sg_file = open(str(folder_path.joinpath('%s-asset-%d.html')), 'w')\n" % (title, count)
    block += "_sg_file.write(_sg_html)\n"
    block += "_sg_file.close()\n\n"
    code_file.write(block)

count = 1
code_block = False
code_metadata = False
block_text = ''
block_code = ''

PLOTLY = 0
STARGAZER = 1
DATAFRAME = 2
block_tyep_max = 10
block_type = block_tyep_max

for line in file:
    if code_metadata: 
        if line[:3] == '---':
            code_metadata = False

    elif line[:14] == '```{code-cell}':
        code_block = True
        out_file.write(clean_text(block_text))
        block_text = ''
        add_code_start(count)

    elif code_block:
        if line[:3] == '---':
            code_metadata = True
        
        elif line[:3] == '```':
            code_block = False
            if block_type == PLOTLY:
                add_plotly_code(block_code, count)
            elif block_type == STARGAZER:
                add_stargazer_code(block_code, count)
            elif block_type == DATAFRAME:
                add_dataframe_code(block_code, count)
            else:
                code_file.write(block_code)
            add_code_end(block_text, count)
            count += 1
            block_text = ''
            block_code = ''
            block_type = block_tyep_max

        else:
            if block_type > STARGAZER and 'Stargazer' in line:
                block_type = STARGAZER
            elif block_type > DATAFRAME and 'DataFrame' in line:
                block_type = DATAFRAME

            if block_type > PLOTLY and 'fig.show' in line:
                block_text += line
                block_type = PLOTLY
            elif not line[0] == ':':
                block_code += line
                block_text += line

    elif line[:3] != '+++':
        block_text += line

if len(block_text) > 0:
    out_file.write(clean_text(block_text))

code_file.close()
out_file.close()

subprocess.run(['rm', myst_file])
subprocess.run(['python', 'make_graphs.py'])
subprocess.run(['rm', 'make_graphs.py'])

print('---------------- Task %s completed successfully -------------------\n\n\n' % title)
















        