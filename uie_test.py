from pprint import pprint
from paddlenlp import Taskflow
import pandas as pd
from pandas.core.frame import DataFrame
from tqdm import tqdm
dialog_profile=pd.read_excel('dialog-profile.xlsx')
# print(dialog_profile)
dialog_profile.columns=['id','schema_en','content','no1','no2','time1','time2']

'''定义中文schema'''
schema_en=dialog_profile["schema_en"].unique()
schema_ch=["人格","姓名","兴趣","性别","年龄","家乡","教育","属相","生日","星座","工作","体重","身高","爸爸","妈妈"]
schema_dic = dict(zip(schema_en, schema_ch))
dialog_profile['schema_ch']=[schema_dic[i] for i in dialog_profile['schema_en']]
# print(dialog_profile.head)



'''抽取'''
schema = ["姓名","兴趣","性别","年龄","家乡","教育","属相","生日","星座","工作","体重","身高","爸爸","妈妈",""] # Define the schema for entity extraction
ie = Taskflow('information_extraction', schema=schema)
ie.set_schema(schema)

text_list=[]
output_schema_ch_list=[]
prob_list=[]
for i in tqdm(dialog_profile['content']):
    try:
        text=list(ie(i)[0].values())[0][0]['text']
        output_schema_ch=list(ie(i)[0].keys())[0]
        prob=list(ie(i)[0].values())[0][0]['probability']
    except:
        text="unavailable"
        output_schema_ch="unavailable"
        prob="unavailable"
    text_list.append(text)
    output_schema_ch_list.append(output_schema_ch)
    prob_list.append(prob)

dialog_profile['text']=text_list
dialog_profile['output_schema_ch']=output_schema_ch_list
dialog_profile['prob']=prob_list
print(dialog_profile.head)


dialog_profile.to_csv("dialog_profile_extracted_v1.csv",index=False)
print("Finish!")

