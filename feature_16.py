import os
import time
import shutil
from tqdm import tqdm
workplace=os.getcwd()

#apk解压，返回解压目录
def Decompile(apkpath:str):
    apkname=apkpath.split("/")[-1]
    print("decompile apk named ",apkname)
    apkdir=apkpath.replace(apkname,"")
    os.chdir(apkdir)
    
    if not os.path.exists(apkpath.replace('.apk','')):  
        os.system('java -jar '+workplace+'/apktool.jar d -r --no-assets '+apkpath)
    return apkpath.replace('.apk','')
# Decompile("D:\workplace\main\\testapks\BuptRoom.apk")

def GetDirFeature(dirname:str,categorybasis:dict,decompilepath:str,preapiextract:dict):
    vector=[0]*16
    
    for root,dirnames,filenames in os.walk(dirname):
        for filename in filenames:
            if filename.endswith(".smali"):
                filepath=root+"/"+filename
                tmp=preapiextract[filepath]
                for i in range(0,15):
                    vector[i]+=tmp[i]
    vector[15]=GetDirFloor(dirname,decompilepath)
    return vector
def GetDirFloor(dirname:str,decompilepath:str):

    if decompilepath in dirname:
        tmp=dirname.replace(decompilepath,"")
        f=tmp.count("/")
        if f<=1:
            return 0
        else:
            return f-1
    else:
        return 0





#记录smali文件中的API
def ApiExtractor(smalifile:str,categorybasis:dict):
    #遍历smali文本的每一行 找到invoke开头的行 提取出方法名+类名
    #初始化list=[0]*10 对应10类api、总API数目、api种类数 层数
    #查询列表进行API计数
    #两个特殊的类android.manifest类属于security；而android.R属于UI
    Apicnt={"io":0,"net":0,"device":0,"location":0,"UI":0,"hardware":0,"app":0,"multimedia":0,"security":0,"database":0,"util":0,"system":0,"xml":0,"time":0,"datatype":0,"floor":0}
    if os.path.exists(smalifile):
        with open(smalifile,"r",encoding="utf-8") as f:
            # print("smalifile=",smalifile)
            for line in f.readlines():
                line=line.strip()
                if line.startswith('.class'):
                    curclassname=line.split(' ')[-1]
                    curclassname=curclassname[1:-1].replace("/",".")
                    Apicnt["floor"]=len(curclassname.split("."))
                if line.startswith("invoke"):
                    classname=line.split(" ")[-1][1:].split(";")[0]
                    classname=classname.replace("/",".")
                    methodname=line.split("->")[-1].split("(")[0]
                    category=GetCategory(classname,categorybasis)
                    if category in categorybasis.keys():
                        Apicnt[category]+=1
                    # else:
                    #     print(classname,":",methodname)
    # print(Apicnt)
    vector=list(Apicnt.values())
    return vector
def GetCategory(classname:str,categorybasis:dict):
    #输入一个类名返回该API的类型
    if classname=="android.manifest":
        return "security"
    if classname=="android.R":
        return "UI"
    for key,value in categorybasis.items():
        for basis in value:
            if "." in classname:#保证n>=2
                array=classname.split(".")
                n=len(array)
                tmp=""
                for i in range(0,n-1):
                    tmp+=array[i]+"."
                tmp=tmp[0:-1]
                if tmp==basis:
                    # print(key)
                    # print(tmp)
                    # print("matched")
                    return key
    return ""

def GetApiList():
    ApiList=[]
    with open(workplace+"/APIlist.txt","r") as f:
        for line in f.readlines():
            line=line.strip()
            if line:
                ApiList.append(line)   
    return ApiList
def GetCategoryBasis():
    #依据category.txt文件进行分类
    #返回一个分类字典作为依据，其中有两个特例
    #两个特殊的类android.manifest类属于security；而android.R属于UI
    categorybasis={
         "io":[]\
        ,"net":[]\
        ,"device":[]\
        ,"location":[]\
        ,"UI":[]\
        ,"hardware":[]\
        ,"app":[]\
        ,"multimedia":[]\
        ,"security":[]\
        ,"database":[]\
        ,"util":[]\
        ,"system":[]\
        ,"xml":[]\
        ,"time":[]\
        ,"datatype":[]
        } 
    
    with open(workplace+"/categorybasis_16.txt","r") as f:
        for line in f.readlines(): 
            line=line.strip()
            if line and ":" in line:
                category=line.split(":")[1]
                basis=line.split(":")[0]
                if category in categorybasis.keys():
                    categorybasis[category].append(basis)
    return categorybasis
    # print(categorybasis["io"])
    # print(categorybasis["hardware"])
    # print(categorybasis["security"])
def IsVectorValid(vector:list):
    result=False
    if vector[-1]==0:
        return False
    for i in range(0,15):
        if vector[i]!=0:
            result=True
    return result

#对整个app进行分析生成特征向量并储存到txt文档
def FeatureGeneration(apkpath:str):
    #traverse the folder of decompiled apk
    #store all feature vector into "feature.txt" in the form "dirname:vector "
    categorybasis=GetCategoryBasis()
    apkname=apkpath.split("/")[-1]
    decompilepath=Decompile(apkpath)#改变了工作路径
    ignorelist=["assets","original","res"]
    #进行预处理，计算所有smali文件的特征并记录在字典中
    preapiextract={}
    for root,dirnames,filenames in os.walk(decompilepath):
        for filename in filenames:
            if filename.endswith(".smali"):
                filepath=root+"/"+filename
                preapiextract[filepath]=ApiExtractor(filepath,categorybasis)

    with open(workplace+"/featureubuntu/"+apkname.replace(".apk","")+".txt","w") as f:
        for root,dirnames,filenames in os.walk(decompilepath):
            for dirname in dirnames:
                if dirname not in ignorelist:
                    abpath=root+"/"+dirname
                    vector=GetDirFeature(abpath,categorybasis,decompilepath,preapiextract)
                    if IsVectorValid(vector):
                        line=abpath+":"
                        for i in vector:
                            line+=str(i)+","
                        line=line[0:-1]
                        print(line)
                        f.write(line+"\n")
    # 删除反编译后的文件夹      
    filedel_flag=0
    if os.path.exists(decompilepath):      
        shutil.rmtree(decompilepath)
        filedel_flag=1
    if not os.path.exists(decompilepath) and filedel_flag==1:
        print(decompilepath+'文件夹删除')
if __name__=="__main__":
    #apkdir="D:\\workplace\\main\\testapks"
    apkdir="/home/hao/hao/crawler/2345apk"
    for rname,dnames,fnames in os.walk(apkdir):   
        for fname in tqdm(fnames):
            if fname.endswith('.apk'):
                apkpath=rname+"/"+fname
                num=fname.split("_")[2].split(".")[0]
                page=fname.split("_")[1]
                if int(num)<=100 and int(page)==1:
                    print(num)
                    FeatureGeneration(apkpath)
                else:
                    continue

#apilist=GetApiList()




# print(GetDirFloor("D:\workplace\main\BuptRoom\smali\cn","D:\workplace\main\BuptRoom"))
# GetApiList()
# categorybasis=GetCategoryBasis()
# # # GetCategory("android.accounts.AbstractAccountAuthenticator",categorybasis)
# ApiExtractor("D:\workplace\main\FlexboxLayout.smali",categorybasis)    
