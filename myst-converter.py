import subprocess

# do not include .ipynb
notebook = 'adult_child_ubi'
title = '2020-07-07-adult-child-ubi'

# user should fill in appropriate metadata
metadata = """---
layout: post
current: post
cover: 
navigation: True
title: To minimize poverty, should UBI be provided for adults, children, or both?
date: 2020-07-07
tags: [blog, child-allowance]
class: post-template
subclass: 'post'
author: nate
---
"""

##################### All edits go above ###################################

# convert notebook to myst
subprocess.run(['jupytext', '%s.ipynb' % notebook, '--to', 'myst'])

# open myst file
file = open('%s.md' % notebook, 'r') 

# open output file
out_file = open('../ubicenter.org/_posts/%s.md' % title,'w')
out_file.write(metadata)
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
code_file.write("\nfolder_path = Path('..', 'ubicenter.org', 'assets', 'graphs', '%s')\n" % title)
code_file.write("\nfolder_path.mkdir(parents = True, exist_ok = True)\n")

# code prefix
def add_code_start(count):
  out_file.write("""
<button onclick="f%d()">Click to show code</button>
<div id="graph_code_%d" style="display: none;">
  <pre>
    <code>
""" % (count, count))

# code postfix
def add_code_end(block, count):
    out_file.write(block)
    out_file.write("""
    </code>
  </pre>
</div>

<script>
function f%d() {
  var x = document.getElementById("graph_code_%d");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script> \n""" % (count, count))

    out_file.write("""
<div>
  <script>
    $(document).ready(function(){
      $("#graph%d").load("{{site.baseurl}}assets/graphs/%s/%s-graph-%d.html");
    });
  </script>
</div>
<div id = "graph%d"></div>\n""" % (count, title, title, count, count))

def add_graph_code(block, count):
  code_file.write(block)
  code_file.write("io.write_html(fig, str(folder_path.joinpath('%s-graph-%d.html')), full_html = False, include_plotlyjs = False)\n\n" % (title, count))

count = 1
code_block = False
code_metadata_block = False
block_text = ''
block_code = ''
metadata_skipped = 0
for line in file:
    if metadata_skipped == 2:
        if line[:14] == '```{code-cell}':
            code_block = True
            out_file.write(block_text)
            block_text = ''
            add_code_start(count)
            
        elif line[:3] == '```':
            code_block = False
            add_code_end(block_text, count)
            add_graph_code(block_code, count)
            count += 1
            block_text = ''
            block_code = ''

        elif code_block:
            if line[:3] == '---':
                code_metadata_block = not code_metadata_block
            elif not code_metadata_block:
                if not line[0] == ':' and not 'fig.show' in line:
                    block_code += line
                    block_text += line

        elif line[:3] != '+++':
            block_text += line
    elif line[:3] == '---':
        metadata_skipped += 1

code_file.close()
out_file.close()
subprocess.run(['python', 'make_graphs.py'])
















        