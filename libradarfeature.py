import os
from tqdm import tqdm
import time
workplace=os.getcwd()
#apk解压，返回解压目录
def Decompile(apkpath:str):
    apkname=apkpath.split("\\")[-1]
    print("decompile apk named ",apkname)
    apkdir=apkpath.replace(apkname,"")
    os.chdir(apkdir)
    
    if not os.path.exists(apkpath.replace('.apk','')):  
        os.system('java -jar '+workplace+'\\apktool.jar d -r --no-assets '+apkpath)
    return apkpath.replace('.apk','')
#提取libradar的API
def LibradarApiExtractor(smalifile:str,ApiList:list):
    L=len(ApiList)
    vector=[0]*L
    if os.path.exists(smalifile):
        with open(smalifile,"r",encoding="utf-8") as f:
            # print("smalifile=",smalifile)
            for line in f.readlines():
                line=line.strip()
                # if line.startswith('.class'):
                #     curclassname=line.split(' ')[-1]
                #     curclassname=curclassname[1:-1].replace("/",".")
                #     Apicnt["floor"]=len(curclassname.split("."))
                if line.startswith("invoke"):
                    classname=line.split(" ")[-1][1:].split(";")[0]
                    classname=classname.replace("/",".")
                    methodname=line.split("->")[-1].split("(")[0]
                    # category=GetCategory(classname,categorybasis)
                    # if category in categorybasis.keys():
                    #     Apicnt[category]+=1
                    api=classname+":"+methodname
                    if api in ApiList:
                        vector[ApiList.index(api)]+=1
    # prime=1125899839733759
    # result=[0]*3#1.hash 2.sum 3.kinds
    # for i in range(0,L):
    #     result[1]+=vector[i]
    #     if vector[i]!=0:
    #         result[2]+=1
    #     result[0]+=(i*vector[i])%prime
    # return result
    return vector
def GetApiList():
    ApiList=[]
    with open(workplace+"\APIlist.txt","r") as f:
        for line in f.readlines():
            line=line.strip()
            if line:
                ApiList.append(line)   
    return ApiList
def GetDirFeature(dirname:str,decompilepath:str,preapiextract:dict):
    L=len(list(preapiextract.values())[0])
    vector=[0]*L
    
    for root,dirnames,filenames in os.walk(dirname):
        for filename in filenames:
            if filename.endswith(".smali"):
                filepath=root+"\\"+filename
                tmp=preapiextract[filepath]
                for i in range(0,L):
                    vector[i]+=tmp[i]
    # vector[10]=GetDirFloor(dirname,decompilepath)
    """
    卡罗尔质数
    每一个质数皆符合 {\displaystyle (2^{n}-1)^{2}-2}(2^{n}-1)^{2}-2的数式表达。

    7, 47, 223, 3967, 16127, 1046527, 16769023, 1073676287, 68718952447, 
    274876858367, 4398042316799, 1125899839733759, 18014398241046527, 
    1298074214633706835075030044377087 (A091516)
    """
    prime=1125899839733759
    result=[0]*3#1.hash 2.sum 3.kinds
    for i in range(0,L):
        result[1]+=vector[i]
        if vector[i]!=0:
            result[2]+=1
        result[0]+=(i*vector[i])%prime
    print("dirname=",dirname)
    print("result=",result)
    return result
    
def FeatureGeneration(apkpath:str):
    #traverse the folder of decompiled apk
    #store all feature vector into "feature.txt" in the form "dirname:vector "

    apkname=apkpath.split("\\")[-1]
    decompilepath=Decompile(apkpath)#改变了工作路径
    ignorelist=["assets","original","res"]
    #进行预处理，计算所有smali文件的特征并记录在字典中
    preapiextract={}
    apilist=GetApiList()
    print("预处理")
    for root,dirnames,filenames in os.walk(decompilepath):
        for filename in filenames:
            if filename.endswith(".smali"):
                filepath=root+"\\"+filename
                preapiextract[filepath]=LibradarApiExtractor(filepath,apilist)
                # print(filepath)
                # print(preapiextract[filepath])
    print("记录特征")
    with open(workplace+"\\featurelibradar\\"+apkname.replace(".apk","")+".txt","w") as f:
        for root,dirnames,filenames in os.walk(decompilepath):
            for dirname in dirnames:
                if dirname not in ignorelist:
                    abpath=root+"\\"+dirname
                    vector=GetDirFeature(abpath,decompilepath,preapiextract)
                    if IsVectorValid(vector):
                        line=abpath+":"
                        for i in vector:
                            line+=str(i)+","
                        line=line[0:-1]
                        print(line)
                        f.write(line+"\n")
    # # 删除反编译后的文件夹      
    # filedel_flag=0
    # if os.path.exists(decompilepath):      
    #     shutil.rmtree(decompilepath)
    #     filedel_flag=1
    # if not os.path.exists(decompilepath) and filedel_flag==1:
    #     print(decompilepath+'文件夹删除')
def IsVectorValid(vector:list):
    result=False

    for i in range(0,3):
        if vector[i]!=0:
            result=True
    return result
if __name__=="__main__":
    apkdir="D:\\workplace\\main\\testapks"
    #apkdir="D:\\workplace\\2345apps"
    stime=time.time()
    for rname,dnames,fnames in os.walk(apkdir):   
        for fname in tqdm(fnames):
            if fname.endswith('.apk'):
                apkpath=rname+"\\"+fname
                FeatureGeneration(apkpath)
    etime=time.time()
    print("总用时为",etime-stime)