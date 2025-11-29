def search(profile):
    #######################conceptnet#######################
    from langconv import Converter

    import pandas as pd

    FILE = 'chineseconceptnet.csv'
    data = pd.read_csv(FILE, delimiter='\t')
    data.columns = ['uri', 'relation', 'start', 'end', 'json']

    # 删除不只含有中文节点的关系
    data = data[data['start'].apply(lambda row: row.find('zh') > 0) & data['end'].apply(lambda row: row.find('zh') > 0)]
    data.index = range(data.shape[0])
    #print(data)

    # 从json列中提取权重信息
    import json

    weights = data['json'].apply(lambda row: json.loads(row)['weight'])
    data.pop('json')
    data.insert(4, 'weights', weights)
    #print(data)


    # 繁体转简体
    def cht_to_chs(line):
        line =Converter('zh-hans').convert(line.encode('utf-8').decode('utf-8'))
        line.encode('utf-8')
        return line


    # 简体转繁体
    def chs_to_cht(line):
        # line = line.encode('unicode_escape')
        line =Converter('zh-hant').convert(line.encode('utf-8').decode('utf-8'))
        line.encode('utf-8')
        return line

    # 查询起始节点
    def search(words, n=20):
        result = data[data['start'].str.contains(chs_to_cht(words))]
        topK_result = result.sort_values("weights", ascending=False).head(n)
        return topK_result

    template = {
        '/r/RelatedTo': '和{}相关',
        '/r/FormOf': '的形式为{}',
        '/r/IsA': '是{}',
        '/r/PartOf': '是{}的一部分',
        '/r/HasA': '具有{}',
        '/r/UsedFor': '用来{}',
        '/r/CapableOf': '可以{}',
        '/r/AtLocation': '在{}',
        '/r/Causes': '导致{}',
        '/r/HasSubevent': ',接下来,{}',
        '/r/HasFirstSubevent': '，紧接着，{}',
        '/r/HasLastSubevent': '的最后一步是{}',
        '/r/HasPrerequisite': '的前提为{}',
        '/r/HasProperty': '具有{}的属性',
        '/r/MotivatedByGoal': '受到{}的驱动',
        '/r/ObstructedBy': '受到{}的影响',
        '/r/Desires': '想要{}',
        '/r/CreatedBy': '被{}创造',
        '/r/Synonym': '和{}同义',
        '/r/Antonym': '和{}反义',
        '/r/DistinctFrom': '和{}相区别',
        '/r/DerivedFrom': '由{}导致',
        '/r/SymbolOf': '象征着{}',
        '/r/DefinedAs': '定义为{}',
        '/r/MannerOf': '',
        '/r/LocatedNear': '和{}相邻',
        '/r/HasContext': '的背景是{}',
        '/r/SimilarTo': '和{}相似',
        '/r/EtymologicallyRelatedTo': '',
        '/r/EtymologicallyDerivedFrom': '',
        '/r/CausesDesire': '',
        '/r/MadeOf': '由{}制成',
        '/r/ReceivesAction': '',
        '/r/ExternalURL': ''
    }


    def strip(str):
        return str.split('/')[3]

    topK_result = search(profile, 20)
    for i in topK_result.index:
        i = topK_result.loc[i]
        if len(template[i['relation']]) > 0:
            fanti = strip(i['start']) + template[i['relation']].format(strip(i['end']))
            jianti = cht_to_chs(fanti)
            print('conceptnet:',jianti)
            with open('result.txt', 'a+') as f:
                print('conceptnet:',jianti, file=f)

    print("FINISH CONCEPTNET!")

    ###################cndb######################
    import pymongo
    client = pymongo.MongoClient(
    'mongodb://gdmdbuser:6QEUI8dhnq@10.176.40.106:27017')
    db = client.cndbpedia
    collection = db.triples
    results = collection.find({"s": profile})
    for result in results:
        print('cndb:',result['o'])
        with open('result.txt', 'a+') as f:
            print('cndb:',result['o'], file=f)

    print("FINISH CNDB!")


    # ###################c3kgb######################
    import pandas as pd
    # 读取tsv文件并设置间隔为空
    data=pd.read_csv('ATOMIC_Chinese.tsv', sep='\t',header=0)
    #data.to_dict(orient='records')
    #print(data)
    #exit()
    #d = data.set_index('head').T.to_dict('list')
    #print(d)
    d = data.set_index('head').agg(list, axis=1).to_dict()
    # print(d)
    try:
        print('c3kg:',d[profile][1])
        with open('result.txt', 'a+') as f:
            print('c3kg:',d[profile][1], file=f)
    except:
        pass

    print("FINISH C3KG!")



    ###################zhishime######################
    import json
    from urllib.request import quote, unquote

    import os
    import glob
    from xml.dom.pulldom import parseString

    def find_disc(will_find_dist, find_keys):  # will_find_dist要查找的字典，find_keys要查找的keys，found找到值存放处
        value_found = []
        if(isinstance(will_find_dist, (list))):  # 含有列表的值处理
            if (len(will_find_dist) > 0):
                for now_dist in will_find_dist:
                    found = find_disc(now_dist, find_keys)
                    if(found):
                        value_found.extend(found)
                return value_found

        if(not isinstance(will_find_dist, (dict))):  # 没有字典类型的了
            return 0

        else:  # 查找下一层
            dict_key = will_find_dist.keys()
            #print (dict_key)
            for i in dict_key:
                if(i == find_keys):
                    value_found.append(will_find_dist[i])
                found = find_disc(will_find_dist[i], find_keys)
                if(found):
                    value_found.extend(found)

            return value_found



    d={} 
    file_dir = ''

    path1=''
    path2=''
    path3=''
    files1=glob.glob(path1 + "/*.json")
    files2=glob.glob(path2 + "/*.json")
    files3=glob.glob(path3 + "/*.json")

    files=files1+files2+files3
    

    for file in files:
    # for root, dirs, files in os.walk(file_dir, topdown=False):
    #     for file in files:
        with open(file, "r") as f:
            row_data = json.load(f)
        
        import re
        result = re.findall(".*_(.*)_zh.json.*",file)
        if "_" in result:
            result1=result.split("_",1)[0]
            result2=result.split("_",1)[1]
            result=result1+result2.capitalize()


        # 读取每一条json数据
        for data in row_data:
            ret3 = unquote(data["@id"], encoding='utf-8')
            ent=ret3.rsplit('/',1)[-1]
            # try:
            # print(data)
            des=find_disc(data, '@value')
            # des=data['http://zhishi.me/ontology/%s'%result[0]][0]['@value']
            # print(des)
            if des!=[]:
                if not ent in d:
                    d[ent]=des
                elif d[ent]!=des:
                    d[ent]=[d[ent]].append(des)

            # except:
            #     pass

    # print(d)
    try:
        print('zhishime:',d[profile])
        with open('result.txt', 'a+') as f:
            print('zhishime:',d[profile], file=f)
    except:
        pass
        
    print("FINISH ZHISHIME!")

    print('\n')



profiles=['李蛋儿','14岁','男','双鱼座','178cm','65kg','3月20日','牛','学生','小学生','北京','篮球']
for profile in profiles:
    print('【',profile,'】')
    with open('result.txt', 'a+') as f:
        print('【',profile,'】', file=f)
    search(profile)