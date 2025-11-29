from multiprocessing.util import ForkAwareThreadLock
import pandas as pd
import numpy as np
import itertools
from pandas.core.frame import DataFrame
from itertools import product
import re
import json
import os
import random
# from macpath import split
profile=pd.read_excel('profile-reasonable1.xlsx')



'''first_relation'''
profile=profile[profile['reasonable'] !=0]
print(len(profile['长期记忆维度'].values))
first_relation= list(itertools.permutations(profile['长期记忆维度'].values, 2))#不考虑组合顺序。combinations改成permutations是考虑组合顺序
c={"first_relation" : first_relation,"reasonable":[0]*len(first_relation)}
data=DataFrame(c)





'''first_relation_value'''
d={}
d_ori={}
d1={}
t1=['姓名','爸爸','妈妈']
t2=['年龄']
t3=['生日']
t4=['身高']
t5=['体重']
t6=['籍贯','兴趣','偶像','特长','性格','食物','缺点','毕业院校']
t7=['不喜欢做的事','想去做的事']
t8=[i for i in profile['长期记忆维度'].values if not i in t1+t2+t3+t4+t5+t6+t7]
for k,v in zip(profile['长期记忆维度'],profile['值']):
    d_ori.update({k:v})

for k in t1:
    v_char= [one for one in d_ori[k]]
    v_new=['小'+i for i in v_char][:50]
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t2:
    v_new=[str(i)+'岁' for i in list(np.arange(10, 80+1, 10))]
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t3:
    month=list(np.arange(1, 12+1, 1))
    month=[str(i)+'月' for i in month]
    date=list(np.arange(1, 31+1, 1))
    date=[str(i)+'日' for i in date]    
    v_tmp = list(product(month, date))
    v_new=[]
    for i in v_tmp:
        tmp=''.join(str(j) for j in i)
        v_new.append(tmp)
    for i in ['2月30日','2月31日','4月31日','6月31日','9月31日','11月30日']:
        v_new.remove(i)
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t4:
    v_new=[str(i)+'cm' for i in list(np.arange(100, 190+1, 10))]
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t5:
    v_new=[str(i)+'kg' for i in list(np.arange(16, 105+1, 10))]
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t6:
    v=d_ori[k].replace(" ", "")
    v=v.replace("\n", "")
    v=v.replace("\n\n", "")
    v_new=v.split('、')
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t7:
    v=d_ori[k].replace("\n", "")
    v_new = re.split(r"\d+.",v)[1:]
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})
for k in t8:
    v_new=d_ori[k].split('、')
    d.update({k:[str(v_new)]})
    d1.update({k:v_new})


w=1
#把每个值分成单独文件保存，统计每个属性的值的数量
cnt=0
for k,v in d1.items():
    df = pd.DataFrame({k:v})
    df['length']=df.shape[0]
    cnt+=df.shape[0]
 print(cnt)#2617


'''first_relation_value_combination'''
d_comb={}        
profile_human=pd.read_excel('first_relation-reasonable-human.xlsx')
print(profile_human.shape)#1980*2


'''新增profile'''
add_profile_d={}
for k,v in zip(data['first_relation'],data['reasonable']):
    if '恋爱状况' in k or '结婚状况'  in k:
        add_profile_v="todo"
        add_profile_d.update({k:add_profile_v})
add_profile = pd.DataFrame([add_profile_d]).T
add_profile = add_profile.reset_index().rename(columns={'index':'first_relation',0:'reasonable'})    
new_profile=pd.concat([profile_human,add_profile])


profile_human=pd.read_excel('first_relation-reasonable-human1.xlsx')
print(profile_human.shape)#1980*2

profile_human['length']=0
cnt1=0


'''
规则+人工
'''
profile_human=profile_human[profile_human['reasonable'] ==1]
print(profile_human.shape)#109

profile_human_guize=profile_human[profile_human['是否需要规则'] ==1]
print(profile_human_guize.shape)#20


profile_human_rengong=profile_human[profile_human['是否需要人工'] ==1]
print(profile_human_rengong.shape)#66


profile_human_guize.set_index(["first_relation"], inplace=True)
profile_human_rengong.set_index(["first_relation"], inplace=True)
profile_human.set_index(["first_relation"], inplace=True)




def get_constellation(month, date):
    dates = (21, 20, 21, 21, 22, 22, 23, 24, 24, 24, 23, 22)
    constellations = ("摩羯座", "水瓶座", "双鱼座", "白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座", "天秤座", "天蝎座", "射手座", "摩羯座")
    if date < dates[month-1]:
        return constellations[month-1]
    else:
        return constellations[month]



remove_list=[]
all_list=[]
for i in profile_human.index:   
    result = i.split(", ")
    j1=result[0].split("('")[1]
    j1=j1.split("'")[0]
    j2=result[1].split("')")[0]
    j2=j2.split("'")[1]
    first_relation_comb=[[j1+'='+a1,j2+'='+b1] for a1, b1 in itertools.product(d1[j1],d1[j2])]


    if j1=="性别" and j2=="身高":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='女':
                if v[1].split("=")[1]=='180cm' or v[1].split("=")[1]=='190cm':
                    remove_list.append(v)
    
    if j1=="身高" and j2=="性别":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='女':
                if v[0].split("=")[1]=='180cm' or v[0].split("=")[1]=='190cm':
                    remove_list.append(v)


    if j1=="年龄" and j2=="身高":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='10岁':
                if v[1].split("=")[1]=='170cm' or v[1].split("=")[1]=='180cm' or v[1].split("=")[1]=='190cm':
                    remove_list.append(v)
            if v[0].split("=")[1]=='20岁' or v[0].split("=")[1]=='30岁' or v[0].split("=")[1]=='40岁' or v[0].split("=")[1]=='50岁':
                if v[1].split("=")[1]=='110cm' or v[1].split("=")[1]=='120cm' or v[1].split("=")[1]=='130cm' or v[1].split("=")[1]=='140cm' or v[1].split("=")[1]=='150cm':
                    remove_list.append(v)
            if v[0].split("=")[1]=='60岁' or v[0].split("=")[1]=='70岁' or v[0].split("=")[1]=='80岁':
                if not v[1].split("=")[1]=='150cm' and not v[1].split("=")[1]=='160cm' and not v[1].split("=")[1]=='170cm' and not v[1].split("=")[1]=='180cm':
                    remove_list.append(v)

    if j1=="年龄" and j2=="体重":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='10岁':
                if not v[1].split("=")[1]=='26kg' and not v[1].split("=")[1]=='36kg':
                    remove_list.append(v)
            if not v[0].split("=")[1]=='10岁':
                if v[1].split("=")[1]=='16kg' or v[1].split("=")[1]=='26kg':
                    remove_list.append(v)
            
    if j1=="年龄" and j2=="孩子":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='10岁' or v[0].split("=")[1]=='20岁':
                if not v[1].split("=")[1]=='没有孩子':
                    remove_list.append(v)

    if j1=="孩子" and j2=="年龄":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='10岁' or v[1].split("=")[1]=='20岁':
                if not v[0].split("=")[1]=='没有孩子':
                    remove_list.append(v)


    if j1=="生日" and j2=="星座":
        for v in first_relation_comb:
            month = int(v[0].split("=")[1].split("月")[0])
            temp = v[0].split("=")[1].split("月")[1]
            date=int(temp.split("日")[0])
            if v[1].split("=")[1]!=get_constellation(month, date):
                remove_list.append(v)



    if j1=="星座" and j2=="生日":
        for v in first_relation_comb:
            month = int(v[1].split("=")[1].split("月")[0])
            temp = v[1].split("=")[1].split("月")[1]
            date=int(temp.split("日")[0])
            if v[1].split("=")[0]!=get_constellation(month, date):
                remove_list.append(v)


    if j1=="性别" and j2=="恋爱状况":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='女':
                if v[1].split("=")[1]=='有女朋友':
                    remove_list.append(v)
            if v[0].split("=")[1]=='男':
                if v[1].split("=")[1]=='有男朋友':
                    remove_list.append(v)

    if j1=="恋爱状况" and j2=="性别":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='女':
                if v[0].split("=")[1]=='有女朋友':
                    remove_list.append(v)
            if v[1].split("=")[1]=='男':
                if v[0].split("=")[1]=='有男朋友':
                    remove_list.append(v)


    if j1=="性别" and j2=="结婚状况":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='女':
                if v[1].split("=")[1]=='有老婆':
                    remove_list.append(v)
            if v[0].split("=")[1]=='男':
                if v[1].split("=")[1]=='有老公':
                    remove_list.append(v)

    if j1=="结婚状况" and j2=="性别":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='女':
                if v[0].split("=")[1]=='有老婆':
                    remove_list.append(v)
            if v[1].split("=")[1]=='男':
                if v[0].split("=")[1]=='有老公':
                    remove_list.append(v)

    if j1=="年龄" and j2=="恋爱状况":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='10岁':
                if not v[1].split("=")[1]=='单身':
                    remove_list.append(v)

    if j1=="恋爱状况" and j2=="年龄":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='10岁':
                if not v[0].split("=")[1]=='单身':
                    remove_list.append(v)

    if j1=="年龄" and j2=="结婚状况":
        for v in first_relation_comb:
            if v[0].split("=")[1]=='10岁' or v[0].split("=")[1]=='20岁':
                if not v[1].split("=")[1]=='未婚':
                    remove_list.append(v)

    if j1=="结婚状况" and j2=="年龄":
        for v in first_relation_comb:
            if v[1].split("=")[1]=='10岁' or v[1].split("=")[1]=='20岁':
                if not v[1].split("=")[1]=='未婚':
                    remove_list.append(v)

    if j1=="孩子" and j2=="结婚状况":
        for v in first_relation_comb:
            if not v[0].split("=")[1]=='没有孩子':
                if v[1].split("=")[1]=='未婚':
                    remove_list.append(v)
    
    if j1=="恋爱状况" and j2=="孩子":
        for v in first_relation_comb:
            if not v[1].split("=")[1]=='没有孩子':
                remove_list.append(v)
    all_list.extend(first_relation_comb)

first_relation_comb_all=[i for i in all_list if not i in remove_list]

print(len(first_relation_comb_all))#44791

for i in first_relation_comb_all:
    if i[0].split("=")[1].isspace() or i[1].split("=")[1].isspace() or len(i[0].split("=")[1])==0 or len(i[1].split("=")[1])==0:
        remove_list.append(i)
first_relation_comb_all=[i for i in first_relation_comb_all if not i in remove_list]
print(len(first_relation_comb_all))#44416


for i in first_relation_comb_all:
    i[0]="".join(i[0].split())
    i[1]="".join(i[1].split())
print(len(first_relation_comb_all))#44416

first_relation_comb_all=[i for i in first_relation_comb_all if not i[0].split("=")[1]=="身高到" and not i[1].split("=")[1]=="身高到"]
print(len(first_relation_comb_all))#44338




'''去掉人工筛选不合理的'''
first_relation_comb_humanlabel=[]
path = ''
for file_name in os.listdir(path):
    data=pd.read_csv(path+file_name,sep="\t")   
    for q1,q2,a in zip(data['q1'],data['q2'],data["最后答案"]):
        q1="".join(q1.split())
        q2="".join(q2.split())
        if q1.split("=")[0]=='属相':
            q1=q1.split("=")[0]+"="+"属"+q1.split("=")[1]
        if q2.split("=")[0]=='属相':
            q2=q2.split("=")[0]+"="+"属"+q2.split("=")[1]

        if a=='B':
            remove_list.append([q1,q2])
        if a=='A':
            first_relation_comb_humanlabel.append([q1,q2])

first_relation_comb_all=[i for i in first_relation_comb_all if not i in remove_list]
print(len(first_relation_comb_all))#42679

print(len(first_relation_comb_humanlabel))#17867


first_relation_comb_humanlabel=[i for i in first_relation_comb_humanlabel if not i[0].split("=")[1]=="身高到" and not i[1].split("=")[1]=="身高到"]
print(len(first_relation_comb_humanlabel))#17865



remove_list1=[]
for i in first_relation_comb_humanlabel:
    if i[0].split("=")[1].isspace() or i[1].split("=")[1].isspace() or len(i[0].split("=")[1])==0 or len(i[1].split("=")[1])==0:
        remove_list1.append(i)
        remove_list.remove(i)
first_relation_comb_humanlabel=[i for i in first_relation_comb_humanlabel if not i in remove_list1]
print(len(first_relation_comb_humanlabel))#17865
print(len(remove_list))#12264



a=[i for i in first_relation_comb_humanlabel if not i in first_relation_comb_all]
first_relation_comb_humanlabel=[i for i in first_relation_comb_humanlabel if not i in a]
first_relation_comb_auto=[i for i in first_relation_comb_all if not i in first_relation_comb_humanlabel]




'''
构造plato所需要的knowledge
'''
first_relation_comb_all_label=first_relation_comb_auto+first_relation_comb_humanlabel
first_relation_comb_all_label=[[i[0],i[1]] for i in first_relation_comb_all_label if len(i[0].split("=")[1])!=0 and len(i[1].split("=")[1])!=0]


print(len(first_relation_comb_all_label))#41039
print(first_relation_comb_all_label[0:5])

with open("plato-knowledge.json", 'w',encoding='utf-8') as fp:
     json.dump(first_relation_comb_all_label, fp,ensure_ascii=False)



'''
构造不合理人设作为测试集
'''
unreason_data=[[i[0],i[1]] for i in remove_list if len(i[0].split("=")[1])!=0 and len(i[1].split("=")[1])!=0]
print(len(unreason_data))#11889
print(unreason_data[0:5])

with open("unreason_plato-knowledge.json", 'w',encoding='utf-8') as fp:
     json.dump(unreason_data, fp,ensure_ascii=False)



'''构成不合理人设的句子'''
sen_all=[]
for i in unreason_data:
    sen='我的'+i[0].split("=")[0]+'是'+i[0].split("=")[1]+'，'+'我的'+i[1].split("=")[0]+'是'+i[1].split("=")[1]
    sen_all.append(sen)
print(len(sen_all))#11889
print(sen_all[0:10])

with open("unreason_profile_sen.json", 'w',encoding='utf-8') as fp:
     json.dump(sen_all, fp,ensure_ascii=False)


print("finish!")

