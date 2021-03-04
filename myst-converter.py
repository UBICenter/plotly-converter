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
"""

### All edits go above ###

# convert notebook to myst
subprocess.run(['jupytext', '%s.ipynb' % notebook, '--to', 'myst'])

# open myst file
file = open('%s.md' % notebook, 'r') 

# open output file
out_file = open('%s.md' % title,'w')

# open graph helper file
code_file = open('make_graphs.py', 'w')
code_file.write('import plotly.io as io\n')
code_file.close()

out_file.write(
"""
<head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</head>
""")

code_block = False
for line in file:
    if line[:3] == '```':
        code_block = False
    if line[:14] == '```{code-cell}':
        code_block = True

    if line[:3] != '+++':
        out_file.write(line)

















        