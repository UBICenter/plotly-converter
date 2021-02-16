

# with open('index.ipynb', 'r') as file:
#     nb = file.read()

# print(nb[0])
# print(nb[:10])
# print(type(nb))

import os
title = '2020-07-07-adult-child-ubi'

file = open('adult_child_ubi.ipynb', 'r') 
out_file = open('%s.md' % title,'w')
code_file = open('make_graphs.py', 'w')
code_file.write('import plotly.io as io\n')
code_file.close()


out_file.write(
"""---
layout: post
current: post
cover: 
navigation: True
title: To minimize poverty, should UBI be provided for adults, children, or both?
date: 2020-07-07
tags: [blog]
class: post-template
subclass: 'post'
author: nate
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
    code = code[:-1][:-1]
    code += '\n'
    # print(code)

    # arr = code.split('"')[:-1]
    # for t in arr:
    code_file.write(code)
    # code_file.write('fig.write_html("html_plotly.html", full_html = False)\n')
    code_file.write('io.write_html(fig, "assets/graphs/%s-graph%d.html", full_html = False, include_plotlyjs = False)\n' % (title, count))
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
      $("#graph%d").load("{{site.baseurl}}assets/graphs/%s-graph%d.html");
    });
  </script>
</div>
<div id = "graph%d"></div>\n""" % (count, title, count, count))

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
        elif 'fig.show' in line:
            source.append('xx')
        else:
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




