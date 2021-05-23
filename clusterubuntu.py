from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
import os
import numpy as np
import matplotlib.pyplot as plt
def GetData(testdir:str,floor:int):
    datadic={}
    data=[]
    labels=[]
    # floor=3
    for file in os.listdir(testdir):
        with open(testdir+"/"+file,"r") as f:
            for line in f.readlines():
                line=line.strip()
                if int(line[-1])==floor:
                    path=line.split(":")[0]+":"+line.split(":")[1]
                    tmp=[]
                    for i in line.split(":")[-1].split(","):
                        tmp.append(int(i))
                    tmp=tmp[0:-1]#把最后一个维度的层数信息去除掉
                    flag=0
                    for i in tmp:
                        if i!=0:
                            flag+=1
                    #筛选过于简单的API特征
                    if sum(tmp)>=60 :
                        data.append(tmp)
                        datadic[path]=tmp
                        label=""
                        for i in range(1,floor+1):
                            label=path.split("/")[-i]+"/"+label
                        labels.append(path)
    return data,labels,datadic
def Normalization(data:list):
    npdata=np.array(data,dtype=np.float_)

    #对数据进行归一化化 

    # #标准化 #使用numpy计算均值和标准差
    # arrmean=np.mean(npdata[:,1])
    # arrvar=np.var(npdata[:,1])
    # print(npdata.dtype)
    # print("mean=",arrmean,"var=",arrvar)
    
    #归一化
    dmin=np.amin(npdata,axis=0)
    dmax=np.amax(npdata,axis=0)
    diff=np.ptp(npdata,axis=0)

    rownum=len(npdata[:,1])
    colnum=len(npdata[1,:])
    for j in range(0,colnum):
        for i in range(0,rownum):
            npdata[i,j]=(npdata[i,j]-dmin[j])/diff[j]
    return npdata
    

def HierarchicalCluster(npdata):
    clustering = AgglomerativeClustering(n_clusters=None,distance_threshold=0.0001,linkage="ward").fit(npdata)
    print(clustering.labels_)
    return clustering.labels_

def DBSCANCluster(npdata):
    clustering = DBSCAN(eps=0.0001,min_samples=5).fit(npdata)
    print(clustering.labels_)

    return clustering.labels_
# for floor in range(1,6):
data,labels,datadic=GetData("~/hao/worlplace/libdetector/featureubuntu",3)
data=Normalization(data)
print(data)
clulabels=HierarchicalCluster(data)
#clulabels=DBSCANCluster(data)
l=len(clulabels)
tmplist=[]
tmpdic={}
candidate_threshold=5

for i in range(0,l):
    if clulabels[i] not in tmpdic.keys():
        tmpdic[clulabels[i]]=1
    else:
        tmpdic[clulabels[i]]+=1
for k,v in tmpdic.items():
    if v>candidate_threshold:
        tmplist.append(int(k))
with open("~/hao/worlplace/libdetector/result/HCubuntu/"+str(3)+".txt","w") as f:
    f.write(str(tmplist))
    f.write("\n\n")
    print("tmplist=",tmplist)
    for i in tmplist:
        for j in range(0,l):
            if i==clulabels[j]:
                print(labels[j])
                print(datadic[labels[j]])
                f.write(str(labels[j]))
                f.write("\n")
                f.write(str(datadic[labels[j]]))
                f.write("\n")
        print("\n")
        f.write("\n\n")
# data=[[1, 3], [1, 4], [1.5, 3], [4, 2], [4, 1.5], [4, 0],[3.5,0.5],[1,0],[1.5,0.5]]
# X = np.array(data)
# clustering = AgglomerativeClustering(n_clusters=None,distance_threshold=1).fit(X)
# print(clustering.labels_)
# for d in data:
#     plt.plot(d[0],d[1],color='b',marker='o',markersize=10)
# plt.axis("equal")
# plt.show()



