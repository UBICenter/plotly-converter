

# with open('index.ipynb', 'r') as file:
#     nb = file.read()

# print(nb[0])
# print(nb[:10])
# print(type(nb))

import os

file = open('index.ipynb', 'r') 
out_file = open('index.md','w')
code_file = open('make_graphs.py', 'w').close()


out_file.write(
"""---
layout: post
current: post
cover: assets/images/bear.jpg
navigation: True
title: A Full and Comprehensive Style Test
date: 2012-09-01 10:00:00
tags:
class: post-template
subclass: 'post'
author: john
---
""")

out_file.write(
"""
<head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</head>
""")

# print(file.readline())
add = False
code = ''
text = ''
source = []
next_source = None
count = 1

def write_text():
    text = ''
    for line in source:
        split = line[5:].split('\\n",')
        for bit in split:
            # print(bit)
            text += bit 
    arr = text.split('"')[:-1]
    for t in arr:
        out_file.write(t)
    out_file.write('\n')

def write_code():
    global count
    code_file = open('make_graphs.py', 'a')
    code = ''
    for line in source:
        split = line[5:].split('\\n",')
        for bit in split:
            # print(bit)
            code += bit
    code = code.replace("\\\"", '\'')
    # print(code)

    # arr = code.split('"')[:-1]
    # for t in arr:
    code_file.write('import plotly.io as io\n')
    code_file.write(code)
    # code_file.write('fig.write_html("html_plotly.html", full_html = False)\n')
    code_file.write('io.write_html(fig, "assets/graphs/graph%d.html", full_html = False, include_plotlyjs = False)\n' % count)
    code_file.close()

    os.system('python make_graphs.py')

    # with open('html_plotly.html', 'r') as file:
        # plot = file.read()
    # rendered_template = html_template.format(plot=plot)

    out_file.write("""
<button onclick="f%d()">Click to show code</button>
<div id="code_graph%d" style="display: none;">
  <pre>
    <code>
%s
    </code>
  </pre>
</div>

<script>
function f%d() {
  var x = document.getElementById("code_graph%d");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script> \n""" % (count, count, code, count, count))

    # out_file.write('```\n' + code + '\n```\n')
    out_file.write("""
<div>
  <script>
    $(document).ready(function(){
      $("#graph%d").load("assets/graphs/graph%d.html");
    });
  </script>
</div>
<div id = "graph%d"></div>\n""" % (count, count, count))

    # out_file.write('<object type="text/html" data="graph%d.html"></object>\n' % count)
    # out_file.write('\n')
    count += 1



for line in file:
    if "\"cell_type\": \"markdown\"," in line:
        next_source = 'text'
    elif "\"cell_type\": \"code\"," in line:
        next_source = 'code'
    
    elif add:
        # print(line)
        if "]\n" in line:
            add = False
            if next_source == 'code':
                # code_sections.append((count, source))
                write_code()
            elif next_source == 'text':
                # text_sections.append((count, source))
                write_text()
            # count += 1
        elif not 'fig.show' in line:
            # print('append')
            source.append(line)

    elif "\"source\": [\n" in line:
        add = True
        source = []





# for c in code_sections:
    # print(c)
# for c,t in text_sections:
#     for t2 in t:
#         print(t2)

out_file.close()
# code_file.close()




