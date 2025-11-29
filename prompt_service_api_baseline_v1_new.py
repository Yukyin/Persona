# -*- coding: utf-8 -*- 
 
import os
import sys
import time
import json
import urllib
import urllib.request
import argparse
import flask
from negative_reply_classification_client import NegReplyClassify
#from config import label2reply

attr_map = {
        "姓名":"你叫什么名字",
        "性别":"你是男生还是女生呢",
        "年龄":"你多大了",
        "生日":"你生日是什么时候",
        "属相":"你属什么的",
        "星座":"你什么星座的",
        "身高":"你多高呢",
        "体重":"你多重呢",
        "爸爸":"你爸爸是谁",
        "妈妈":"你妈妈是谁",
        "爱好":"你喜欢什么",
        }

def mtseg(context):
    url = "http://10.90.243.43:22411/TextProcessService/PreProcess"
    headers = {'Content-type': 'application/json; charset=utf-8'}
    for i, utterance in enumerate(context):
        data = json.dumps({"query": utterance}, ensure_ascii=False)
        data = data.encode('utf8')
        req = urllib.request.Request(url, data=data, headers=headers)
        res = urllib.request.urlopen(req)
        res = json.loads(res.read())
        context[i] = res["result"][0]

neg_classify = NegReplyClassify()

def check_cross_turn_repetition(context, pred):
    if isinstance(pred[0], str):
        context = [ele.split(' ') for ele in context]
        pred_list = [pred.replace(' ', '')]
        mtseg(pred_list)
        pred = pred_list[0].split(' ')
        print("Context: ", context)
        print("Pred: ", pred)

    pred_tri_grams = set()
    for i in range(len(pred) - 2):
        tri_gram = tuple(pred[i:i + 3])
        pred_tri_grams.add(tri_gram)
    for utt in context:
        for i in range(len(utt) - 2):
            tri_gram = tuple(utt[i:i + 3])
            if tri_gram in pred_tri_grams:
                return True
    return False


def client(ori_context, context, knowledge=""):
    # url = "http://10.9.140.200:8124/api/chitchat"  # Original Plato
    #url = "http://10.14.25.97:8123/api/chitchat" # Plato 32L online
    #url = "http://10.138.1.12:8226/api/chitchat" # Plato 32L
    # curl 'http://10.27.164.11:8123/api/chitchat' -d '{"context":["你好"], "knowledge":"", "reply_num":3, "session_id":1}'
    #url = 'http://10.127.9.153:8030/api/chitchat'  # Plato-XL
    #url = 'http://10.9.140.200:8124/api/chitchat'  # Plato-fat12L
    url = "http://10.21.223.134:8090/api/chitchat" # Plato 32L
    headers = {'Content-type': 'application/json; charset=utf-8'}

    mtseg(context)
    #if knowledge:
    #    mtseg(knowledge)

    data = {"context": context, "knowledge": knowledge, "reply_num": 20}
    print(data)
    data = json.dumps(data, ensure_ascii=False)
    data = data.encode(encoding='utf8')
    req = urllib.request.Request(url, data=data, headers=headers)
    res = urllib.request.urlopen(req)
    res = json.loads(res.read())
    print(res)
    new_res = []
    a_list = [e['reply'] for e in res['result']]
    s_list = neg_classify.get_batch_score(a_list)
    for ele, ele_1 in zip(res['result'], s_list):
        if ele_1 >= 0.6:
            continue
        reply = ele['reply']
        score = ele['score']
        if score < -1000.:
            score += 1000.
        if check_cross_turn_repetition(ori_context, reply):
            continue
        new_res.append((reply, score))
    new_res = sorted(new_res, key=lambda x:x[1], reverse=True)
    print(new_res)
    return new_res[0][0]

def intent_client(q):
    url = 'http://10.27.144.50:8901/api/intent'
    headers = {'Content-type': 'application/json; charset=utf-8'}
    data = {'text_a':q}
    data = json.dumps(data, ensure_ascii=False)
    data = data.encode(encoding='utf8')
    req = urllib.request.Request(url, data=data, headers=headers)
    res = urllib.request.urlopen(req)
    res = json.loads(res.read())
    intent = res['result']['label']
    score = res['result']['score']
    if intent != 'none' and score >= 0.9:
        return intent
    else:
        return 'none'

def rank_client(context):
    url = 'http://10.27.144.33:8600/api/chitchat'
    headers = {'Content-type': 'application/json; charset=utf-8'}

    data = {"context": context, "bot_id": 1139627}
    data = json.dumps(data, ensure_ascii=False)
    data = data.encode(encoding='utf8')
    req = urllib.request.Request(url, data=data, headers=headers)
    res = urllib.request.urlopen(req)
    res = json.loads(res.read())
    return res

def get_prompt(context, K=5):
    res = rank_client(context)
    print(res)
    prompt = []
    profile = []
    k = min(len(res), K)
    sel_res = res['result'][:k]
    sel_res.reverse()
    for ele in sel_res:
        if ele['query'] in attr_map:
            q = attr_map[ele['query']]
        else:
            q = ele['query']
        r = ele['persona']
        score = ele['score']
        if score < 0.8:
            continue
        prompt.append(q)
        prompt.append(r)
        profile.append(r)
    return prompt, profile
    
profile_dict = {}
know_list = [
"机器||年龄||14岁",
"机器||性别||男",
"机器||星座||双鱼",
"机器||教育||小学生",
"机器||爱好||篮球"]

app = flask.Flask("socialbot")
app.config["JSON_AS_ASCII"] = False
@app.route("/api/chitchat", methods=["POST"])
def chitchat():
    req = flask.request.get_json(force=True)
    context = req["context"]
    knowledge = req["knowledge"]
    print('-----Context-------')
    print(context)
    print('------------')
    print('-----Knowledge-------')
    print(knowledge)
    print('-------------')
    for k in knowledge:
        tokens = k.strip().split('||')
        print(tokens)
        assert len(tokens) == 3
        profile_dict[tokens[1]] = tokens[2]
    """
    prompt_list = [ "你的名字叫什么", "我叫%s"%profile_dict['姓名'],
                    "你年龄是多少", "我%s呢"%profile_dict['年龄'],
                    "你身高多少", "我%s呢"%profile_dict['身高'],
                    "你体重多少", "我%s呢"%profile_dict['体重'],
                    "你生日哪天", "我%s呢"%profile_dict['生日'],
                    "你爸爸是谁", "我爸爸是%s呢"%profile_dict['爸爸'],
                    "你妈妈是谁", "我妈妈是%s呢"%profile_dict['妈妈'],
                    "你属相什么", "我属%s呢"%profile_dict['属相'],
                    "你工作是什么", "我工作是%s"%profile_dict['工作'],
                    "你的学历是什么", "我是%s呢"%profile_dict['教育'],
                    "你家乡哪里", "我是%s呢"%profile_dict['家乡'],
                    "你的兴趣是什么", "我爱好%s呢"%profile_dict['爱好']]
    """
    prompt_list = [ "你的名字叫什么", "我叫%s"%profile_dict['姓名'],
                    "你年龄是多少", "我%s呢"%profile_dict['年龄'],
                    "你身高多少", "我%s呢"%profile_dict['身高'],
                    "你体重多少", "我%s呢"%profile_dict['体重'],
                    "你生日哪天", "我%s呢"%profile_dict['生日'],
                    "你爸爸是谁", "我爸爸是%s呢"%profile_dict['爸爸'],
                    "你妈妈是谁", "我妈妈是%s呢"%profile_dict['妈妈'],
                    "你属相什么", "我属%s呢"%profile_dict['属相'],
                    "你工作是什么", "我工作是%s"%profile_dict['工作'],
                    "你的学历是什么", "我是%s呢"%profile_dict['教育'],
                    "你家乡哪里", "我是%s呢"%profile_dict['家乡'],
                    "你的兴趣是什么", "我爱好%s呢"%profile_dict['爱好']]
        
    label2reply = {
        "none": "任意回复均可",
        "name": "我叫%s"%(profile_dict['姓名']),
        "age": "我%s了"%(profile_dict['年龄']),
        "height": "我身高是%s"%(profile_dict['身高']),
        "heavy": "我体重是%s"%(profile_dict['体重']),
        "sex": "我是%s"%(profile_dict['性别']),
        "birth": "我生日是%s"%(profile_dict['生日']),
        "father": "我爸爸是%s"%(profile_dict['爸爸']),
        "mother": "我妈妈是%s"%(profile_dict['妈妈']),
        "constellation": "我星座是%s"%(profile_dict['星座']),
        "zodiac": "我属%s的"%(profile_dict['属相']),
        "job": "我的是%s"%(profile_dict['工作']),
        "education": "我是%s"%(profile_dict['教育']),
        "native place": "我的家乡是%s"%(profile_dict['家乡'])
    }

    p_intent = intent_client(context[-1])
    #if p_intent != 'none' and  p_intent in label2reply:
    if False:
        print('!!!')
        res = label2reply[p_intent]
        ret = {
            "name": "socialbot",
            "reply": res
        }
        time.sleep(0.2)
        return flask.jsonify(ret)
    ori_context = context
    context = prompt_list + context
    print('-----New Context-------')
    print(context)
    print('------------')
    res = client(ori_context, context, know_list)
    ret = {
        "name": "socialbot",
        "reply": res.replace(' ', '')
    }
    return flask.jsonify(ret)

app.run(host="0.0.0.0", port=8735, debug=False)


