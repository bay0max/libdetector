#feature.py
#对整个app进行分析生成特征向量并储存到txt文档
def FeatureGeneration(apkfile:str):
    #traverse the folder of decompiled apk
    #store all feature vector into "feature.txt" in the form "dirname:vector "
    pass

#记录smali文件中的API
def ApiExtractor(smalifile:str):
    #遍历smali文本的每一行 找到invoke开头的行 提取出方法名+类名
    #初始化list=[0]*10 对应10类api 层数 总API数目、api种类数
    #查询列表进行API计数
    #返回vector
    pass
#读取API列表并进行分类：
'''
根据https://www.appbrain.com/stats/libraries/网站，TPL可以划分为41个tag
自己分类将API划分为文件读写、网络相关、设备ID、位置信息、UI、硬件、APP相关、多媒体、安全、基础库
英文分类写作io net device location UI hardware app multimedia security base    
https://dl-ssl.google.com/android/repository/docs-19_r02.zip
docs-19_r02.zip： 这个的组成："doc-"+API level+"r"+api level版本+".zip"
'''
def GetCategory(classname:str,categorybasis:dict):
    #输入一个类名返回该API的类型
    pass
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
        ,"base":[]
        }
    pass
# def GetApiList(txtfile:str):
#     pass
