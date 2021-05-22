import csv
import networkx as nx
from networkx import Graph
from bs4 import BeautifulSoup
from time import sleep
import requests
import re
from networkx.algorithms.traversal.depth_first_search import dfs_tree
import os
from zss import simple_distance, Node
# import urllib
# from  urllib.parse import urlparse
# from  urllib.parse import parse_qs
# from urllib import request
# from urllib.request import urlretrieve

def filedircount(path):
    if not os.path.exists(path):
        print(path,"不存在")
        return 0
    else:
        cnt=0
        for rnames,dnames,fnames in os.walk(path):
            for fname in fnames:
                if "$" not in fname and fname.endswith(".smali"):
                    cnt+=1
            for dname in dnames:
                cnt+=1 
        return cnt

def filecount(path):
    if not os.path.exists(path):
        print(path,"不存在")
        return 0
    else:
        cnt=0
        for rnames,dnames,fnames in os.walk(path):
            for fname in fnames:
                if "$" not in fname and fname.endswith(".smali"):
                    cnt+=1
        return cnt

def buildzsstree(code:str):
    if not code :return 
    if code=="10":
        a=Node("l_1")
        t=(a)
        return t
    if len(code)%2!=0:return "error"
    node_cnt=1
    codes=getcode_of_child(code,"none","")
    code=code[1:-1]
    a=Node("r_"+str(node_cnt))
    
    for i in codes:
        node_cnt+=1
        if i=="10":
            a.addkid(Node("l_"+str(node_cnt)))
        else:
            a.addkid(buildzsstree(i))
    return a


# def buildzsstree(code:str):
#     if not code :return 
#     if code=="10":
#         a=Node("l_1")
#         t=(a)
#         return t
#     if len(code)%2!=0:return "error"
#     node_cnt=1
#     codes=getcode_of_child(code)
#     code=code[1:-1]
#     a=Node("r_"+str(node_cnt))
#     node_cnt+=1
#     for i in codes:
#         if i=="10":
#             node_cnt+=1
#             a.addkid(Node("l_"+str(node_cnt)))
#         else:
#             a.addkid(buildzsstree(i))
#     return a

"""
#flag 是标志位，分为file和tree,none三类 
none表示不需要显示名字
"""
def getcode_of_child(code:str,flag:str,extra):
    #来自文件的编码 extra为根目录的绝对路径
    if flag=="file":
        ans={}
        if os.path.isfile(extra):
            return ans
        for dir in os.listdir(extra):
            abpath=extra+"\\"+dir
            ans[abpath]=getcode_for_file(abpath)
        return ans
    #来自树的编码 extra为树的Digraph对象以及根节点的列表
    if flag=="tree":
        TREE=extra[0]
        root=extra[1]
        ans={}
        if not sum(1 for i in TREE.successors(root)):
            return ans
        for child in TREE.successors(root):
            ans[child]=getcode_for_tree(TREE,child)
        return ans
    #不需要显示名字
    if flag=="none":
        # example code="111010011010010100"
        # code="111010011010010100"
        codes=[]
        if not code or code=="10":return codes
        if len(code)%2!=0:return ["error"]
        code=code[1:-1]
        stack=[]
        tmp=""
        for i in code:
            if i=='1':
                stack.append(i)
                tmp+=i
            else:
                tmp+=i
                stack.pop(-1)
            if not stack:
                codes.append(tmp)
                tmp=""
        return codes


def getcode_for_file(root :str):#考虑文件夹为空的情况？
    
    #root is a path
    if os.path.isfile(root) :
        if '$' not in root:
            return "10"
        else:
            return ""

    tmp=[]
    # flag_dir_exist=0
    # if "libfromfolder" in root:
    #     print("root= ",root)
    #     input("pause")
    for node in os.listdir(root):
        if node.endswith("META-INF"):
            continue
        node=root+"\\"+node
        # if os.path.isfile(node):
        #     tmp.append("10")
        # if os.path.isdir(node):
        tmp.append(getcode_for_file(node))
    tmp=sorted(tmp)
    ans="1"
    for i in tmp:
        ans+=i
    ans+="0"
    return ans


# def getgetcode_for_tree_withname(G: Graph,root: str)
#     if not sum(1 for i in G.successors(root)):
#         ans
#         return "10"

def getcode_for_tree(G: Graph,root: str):
    if root not in G.nodes():
        return ""

    if not sum(1 for i in G.successors(root)):
        return "10"
    tmp=[]
    ans="1"
    for child in G.successors(root):
        tmp.append(getcode_for_tree(G,child))
    tmp=sorted(tmp)
    for i in tmp:
        ans+=i
    ans+="0"
    return ans



def getPre2(community):
    if community:
        
        tmp=[]
        for package in community:
            tmp=package.split('.')
            if len(tmp)>2:
                return tmp[0]+'.'+tmp[1]
        #如果按点划分之后长度为2
        return community[0].split('.')[0]    
def getpre2_node(node):
    if node:
        pre2=''
        cnt=1
        for i in node.split('.'):
            if cnt<=2:
                pre2+=i
            cnt+=1
        return pre2
def getpredixdic(G):
    predixdic={}#dictionary for community and according predix
    for  c in nx.connected_components(G):
        c=list(c)
        #用社区里的第一个节点作为key
        predixdic[c[0]]= getPredix(c)
    return predixdic
def storeGraphAsCsv(G,filename):
    with open(filename,'w') as f:
        csvwriter=csv.writer(f)
        csvwriter.writerow(["source","direction","weight"])
        for edge in G.edges:
            pkgname=edge[0]
            cla=edge[1]
            weight=G[pkgname][cla]['weight']
            csvwriter.writerow([pkgname,cla,weight])
    f.close()
    print('图已保存为',filename)

def getDepth(community):
    depth=0
    for c in community:
        if c.count('.')>depth:
            depth=c.count('.')
    return depth

def getPredix(community):
    predix=community[0]

    for c in community:
        predix=getSharedSubstring(predix,c)
    return predix

def getSharedSubstring(s1,s2):
    #just for two package name,not a common string
    a1=s1.split('.');a2=s2.split('.')
    i=0
    s=''
    while i<len(a1) and i<len(a2):
        if a1[i]==a2[i]:
            if s:
                s+='.'+a1[i]
            else:
                s+=a1[i]
        else:
            break
        i+=1
    return s

#以下是对url进行解析
def getContent(url,headers):
    #def getContent(url,headers):
    try:
        res = requests.get(url,headers)
        res.encoding = 'utf-8'
        return res.text
    except Exception:
        sleep(0.1)
    return ""

def getLabel(url,headers,label):
    soup=BeautifulSoup(getContent(url,headers), 'html.parser')
    return soup.find_all(label)
def getPackagename(manifest):
    pattern_url="https?://.*[Pp][Rr][Ii][Vv][Aa][Cc][Yy].*"
    packagename=''
    try:
        with open(manifest,'r',encoding='utf-8') as f:
            #print(f.readlines())
            #soup=BeautifulSoup(f.readlines())
            for line in f.readlines():
                pattern_package="package=\".+\"" 
                ret=re.search(pattern_package,line)
                if not ret:
                    pass
                else:
                    packagename=ret.group(0).replace("\"",'').replace("package=",'')
                    break
            return packagename
    except:
        print("AndroidManifest.xml解析失败")

# print(getPackagename("AndroidManifest.xml"))
# pattern_package="package=\"[^\"]+\""
# line=package="package=\"com.bdego.android\" platformBuildVersionCode=\"23\" "
# print(re.search(pattern_package,line))
'''
community=['cn.hugeterry.updatefun.UpdateFunGO',
'cn.hugeterry.updatefun.UpdateFunGO',
'cn.hugeterry.updatefun.UpdateFunGO',
'cn.hugeterry.updatefun.UpdateFunGO',
'cn.hugeterry.updatefun.UpdateFunGO',
]
print(getSharedSubstring(community[0],community[1]))
print(getPredix(community))

'''



# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# import networkx as nx
# import csv
# import time
# import numpy as np
# from collections import defaultdict
# def buildG(G, file_, delimiter_):
#     #construct the weighted version of the contact graph from cgraph.dat file
#     #reader = csv.reader(open("/home/kazem/Data/UCI/karate.txt"), delimiter=" ")
#     reader = csv.reader(open(file_), delimiter=delimiter_)
#     for line in reader:
#         if line:
#             if len(line) > 2:
#                 if float(line[2]) != 0.0:
#                     #line format: u,v,w
#                     # G.add_edge(line[0],line[1],weight=calBonus(line[0],line[1])*float(line[2]))
#                     if not line[0].startswith('com.yingyb.lljs') and not line[1].startswith('com.yingyb.lljs'):
#                         # G.add_edge(line[0],line[1],weight=float(line[2]))
#                         G.add_edge(line[0],line[1],weight=0.01*float(line[2]))
#             else:
#                 #line format: u,v
#                 G.add_edge(line[0],line[1],weight=1.0)
# def find_communities1(G, T, r):
#     #将图中数据录入到数据字典中以便使用
#     weight = {j:{} for j in G.nodes()}
#     for q in weight.keys():
#         for m in G[q].keys():
#             weight[q][m] = G[q][m]['weight']
#     #建立成员标签记录
#     memory = {i:{i:1} for i in G.nodes()}
#     #开始遍历T次所有节点
#     for t in range(T):
#         listenerslist = list(G.nodes())
#         #随机排列遍历顺序
#         np.random.shuffle(listenerslist)
#         #开始遍历节点
#         for listener in listenerslist:
#             #每个节点的key就是与他相连的节点标签名
#             speakerlist = G[listener].keys()
#             if len(speakerlist) == 0:
#                 continue
#             labels = defaultdict(int)
#             #遍历所有与其相关联的节点
#             for j, speaker in enumerate(speakerlist):
#                 total = float(sum(memory[speaker].values()))
#                 #查看speaker中memory中出现概率最大的标签并记录，key是标签名，value是Listener与speaker之间的权
#                 #print(memory[speaker])
#                 labels[list(memory[speaker].keys())[np.random.multinomial(1,[freq / total for freq in memory[speaker].values()]).argmax()]] += weight[listener][speaker]
#             #查看labels中值最大的标签，让其成为当前listener的一个记录
#             maxlabel = max(labels, key=labels.get)
#             if maxlabel in memory[listener]:
#                 memory[listener][maxlabel] += 1
#             else:
#                 memory[listener][maxlabel] = 1.5
#     #提取出每个节点memory中记录标签出现最多的一个
#     for primary in memory:
#         # print([freq/total for freq in memory[primary].values()])
#         # print(np.random.multinomial(1,[freq/total for freq in memory[primary].values()]))
#         # print(np.random.multinomial(1,[freq/total for freq in memory[primary].values()]).argmax() )
#         # input()
#         next_probs=[freq/total for freq in memory[primary].values()]
#         for i in range(0,len(next_probs)):
#             next_probs[i] /= sum(next_probs)
#         p = list(memory[primary].keys())[np.random.multinomial(1,next_probs).argmax()]
#         memory[primary]={p:memory[primary][p]}
#     #如果希望将那种所属社区不明显的节点排除的就使用下面这段注释代码
#     '''
#     for primary, change in memory.items():
#         for change_name, change_number in change.items():
#             if change_number / float(T + 1) < r:
#                 del change[change_name]
#     '''
#     communities = {}
#     #扫描memory中的记录标签，相同标签的节点加入同一个社区中
#     for primary, change in memory.items():
#         for label in change.keys():
#             if label in communities:
#                 communities[label].add(primary)
#             else:
#                 communities[label] = set([primary])
#     freecommunities = set()
#     keys = communities.keys()
#     #排除相互包含的社区（上面那段注释代码不加这段也可以不加）
#     '''
#     for i, label0 in enumerate(keys[:-1]):
#         comm0 = communities[label0]
#         for label1 in keys[i+1:]:
#             comm1 = communities[label1]
#             if comm0.issubset(comm1):
#                 freecommunities.add(label0)
#             elif comm0.issuperset(comm1):
#                 freecommunities.add(label1)
#     for comm in freecommunities:
#         del communities[comm]
#     '''
#     #返回值是个数据字典，value以集合的形式存在
#     return communities

# def find_communities2(G,T,r):
#     """
#     Speaker-Listener Label Propagation Algorithm (SLPA)
#     see http://arxiv.org/abs/1109.5720
#     """

#     ##Stage 1: Initialization
#     memory = {i:{i:1} for i in G.nodes()}
    
#     ##Stage 2: Evolution
#     for t in range(T):

#         listenersOrder = list(G.nodes())
#         np.random.shuffle(listenersOrder)

#         for listener in listenersOrder:
#             speakers = G[listener].keys()
#             if len(speakers)==0:
#                 continue

#             labels = defaultdict(int)

#             for j, speaker in enumerate(speakers):
#                 # Speaker Rule
#                 total = float(sum(memory[speaker].values()))
#                 labels[list(memory[speaker].keys())[np.random.multinomial(1,[freq/total for freq in memory[speaker].values()]).argmax()]] += 1

#             # Listener Rule
#             acceptedLabel = max(labels, key=labels.get)

#             # Update listener memory
#             if acceptedLabel in memory[listener]:
#                 memory[listener][acceptedLabel] += 1
#             else:
#                 memory[listener][acceptedLabel] = 1


#     ## Stage 3:
#     for node, mem in memory.items():
#         for label, freq in mem.items():
#             if freq/float(T+1) < r:
#                 del mem[label]


#     # Find nodes membership
#     communities = {}
#     for node, mem in memory.items():
#         for label in mem.keys():
#             if label in communities:
#                 communities[label].add(node)
#             else:
#                 communities[label] = set([node])


#     # Remove nested communities
#     nestedCommunities = set()
#     keys = communities.keys()
#     for i, label0 in enumerate(keys[:-1]):
#         comm0 = communities[label0]
#         for label1 in keys[i+1:]:
#             comm1 = communities[label1]
#             if comm0.issubset(comm1):
#                 nestedCommunities.add(label0)
#             elif comm0.issuperset(comm1):
#                 nestedCommunities.add(label1)
    
#     for comm in nestedCommunities:
#         del communities[comm]

#     return communities


# s=time.time()
# G = nx.Graph()  #let's create the graph first
# buildG(G, 'liuliujians_V1.0.0.txt', ',')

# print(find_communities1(G, 10, 10))
# e=time.time()





