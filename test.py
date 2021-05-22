import re
def match(line:str,cmd:str):
    if not cmd:
        return True
    contains=[]
    ends=[]
    greater=[]
    print("cmd=",cmd)
    notcmd=re.search("not\((.*)\)",cmd)
    if notcmd:
        notcmd=notcmd.groups()[0]
        print("notcmd=",notcmd)
        cmd=cmd.replace("not("+notcmd+")","")
        # input("pause")

    case=cmd.split("&")
    print("case=",case)
    for c in case: 
        if c.startswith("contains="):
            contains.append(c.split("\"")[-1])
        if c.startswith("ends="):
            ends.append(c.split("\"")[-1])
        if c.startswith("greater="):
            greater.append(c.split("\"")[-1])
    result=True
    for con in contains:
        if con in line:
            result=True
        else:
            return False
    for end in ends:
        if line.endswith(end):
            result=True
        else:
            return False
    for gre in greater:
        if line>gre:
            result=True
        else:
            return False
    if notcmd:
        notresult=not match(line,notcmd)
        print("1",notresult)
        print("2",result)
        result=result and notresult
        print("3",result)
    return result


cmd="contains=\"hello\"&not(not(contains=\"world\"))"

# notcmd=re.search("not\((.*)\)",cmd)
# print(notcmd.groups()[0])
line="hello worl"
# print(line.split("\""))
print(match(line,cmd))

# contains="hello"&not()
# with open("searchtest.txt","r") as f:
#     for line in f.readlines():
#         line=line.strip()


# import re
# class filter:

#     def init(self,cmd:str):
#         self.cmd=cmd
#         self.contains=[]
#         self.ends=[]
#         self.greater=[]
#     def parse(self):
#         # cases=self.cmd.split("&")
#         result=re.match("not(*)",self.cmd)
#         for c in cases: 
#             if c.startswith("contains="):
#                 self.contains.append(c.split("\"")[-2])
#             if c.startswith("ends="):
#                 self.ends.append(c.split("\"")[-2])
#             if c.startswith("greater="):
#                 self.greater.append(c.split("\"")[-2])
#             # if c.startswith("not"):
#             #     case=c.split("(")[-1].split("=")[0]
#             #     keyword=c.split("\"")[-2]
#             #     if case=="ends":
#             #         self.ends[1].append(keyword)
#             #     if case=="contains":
#             #         self.contains[1].append(keyword)
#             #     if case=="greater":
#             #         self.greater[1].append(keyword)
#     def match(self,line:str):
#         result=False
#         for con in self.contains:
#             if con in line:
#                 result=True
#             else:
#                 return False
#         for end in self.ends:
#             if line.endswith(end):
#                 result=True
#             else:
#                 return False

#         for gre in self.greater:
#             if line>gre:
#                 result=True
#             else:
#                 return False


# contains="hello"&not()
# with open("searchtest.txt","r") as f:
#     for line in f.readlines():
#         line=line.strip()

# def GetCategory(txtfile:str,ApiList:list):
#     #两个特殊的类android.manifest类属于security；而android.R属于UI
#     cataccord={
#          "io":[]\
#         ,"net":[]\
#         ,"device":[]\
#         ,"location":[]\
#         ,"UI":[]\
#         ,"hardware":[]\
#         ,"app":[]\
#         ,"multimedia":[]\
#         ,"security":[]\
#         ,"base":[]
#         }

# category={
#         "io":[]\
#     ,"net":[]\
#     ,"device":[]\
#     ,"location":[]\
#     ,"UI":[]\
#     ,"hardware":[]\
#     ,"app":[]\
#     ,"multimedia":[]\
#     ,"security":[]\
#     ,"base":[]
#     }
# # from sklearn import svm
# # from sklearn import datasets
# # iris=datasets.load_iris()
# # digits = datasets.load_digits()

# # clf = svm.SVC(gamma=0.001,C=100.)#模型和参数
# # clf.fit(digits.data[:-1], digits.target[:-1])#传递训练集给fit函数并进行学习
# # print(digits.data[-1:])
# # print(clf.predict(digits.data[-1:]))
# from sklearn.manifold import TSNE
# import numpy
# from sklearn import datasets

# import os
# testdir="D:\workplace\main\libdetector\\test"
# datadic={}
# data=[]
# labels=[]
# floor=3
# for file in os.listdir(testdir):
#     with open(testdir+"\\"+file,"r") as f:
#         for line in f.readlines():
#             line=line.strip()
#             if int(line[-1])==floor:
#                 path=line.split(":")[0]+":"+line.split(":")[1]
#                 tmp=[]
#                 for i in line.split(":")[-1].split(","):
#                     tmp.append(int(i))
#                 data.append(tmp)
#                 datadic[path]=tmp
#                 label=""
#                 for i in range(1,floor+1):
#                     label=path.split("\\")[-i]+"\\"+label
#                 labels.append(path)
# for i in labels:
#     if "org\\apache\\http" in i:
#         print(i)
#         if i in datadic.keys():
#             print(datadic[i])
# # npdata=numpy.array(data)
# # tsne = TSNE(n_components=2, init='pca', random_state=0)
# # result=tsne.fit_transform(npdata)

# # import matplotlib.pyplot as plt
# # for node in result:
# #     plt.plot(node[0],node[1],color='b',marker='o',markersize=10)
# # plt.show()