import os
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import numpy as np
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from graphviz import Digraph

# 假设图片路径放在一个列表中
# image_paths = ["data/picture/1/start.png", "data/picture/2/start.png", "data/picture/3/start.png"]
image_paths = []
for i in range(21):
    substr=str(i+1)
    str1="data/AAtest/"+substr+"/start.png"
    image_paths.append(str1)

dot = Digraph('测试AAtest3')
for idx,image_path in enumerate(image_paths):
    # dot.node(str(idx),image=image_path, shape='none',width='108', height='240', fixedsize='true',imagescale='true')
    dot.node(str(idx), image=image_path, shape='none', label="")
# dot.node("2", "I learn Python")
for idx in range(20):
    dot.edge(str(idx), str(idx+1))
# dot.edge(str(4), str(10))
dot.attr(dpi='300', rankdir='LR')
dot.view()










