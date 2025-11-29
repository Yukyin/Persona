#coding:utf-8
import sys
import urllib
import urllib.request
import json
import time

NEG_URL = '10.27.144.50'
#NEG_URL = '10.9.140.220'
#NEG_URL = '10.216.212.24'
#NEG_URL='10.185.245.28'
#NEG_URL = '10.12.46.4'
#NEG_URL = '10.21.218.182'
#NEG_URL = '10.185.245.28'
#NEG_URL = '10.108.116.11'
#NEG_URL = '10.197.125.14'
#`NEG_URL = '10.197.125.14'
#NEG_URL='10.153.104.19'
#NEG_URL='10.153.124.24'
#NEG_URL = '10.185.244.18'
#NEG_URL='10.154.60.21'
#NEG_PORT = '8126'
NEG_PORT = '9292'

#NEG_URL='10.21.218.182'
#NEG_PORT=8999

class NegReplyClassify(object):
    '''
    负向回复识别模型
    两种召回方式：单句和batch，当前服务支持最大batch size为10，超过batch size的内容会截断
    '''

    def __init__(self):
        self.one_url = 'http://%s:%s/v1/services/req'%(NEG_URL, NEG_PORT)
        self.batch_url = 'http://%s:%s/v1/services/batch_req'%(NEG_URL, NEG_PORT)

    def __http_url(self, common, atype):
        if atype == 'one':
            url = self.one_url
            data = {"text_a":common}
        elif atype == 'batch':
            url = self.batch_url
            data = {"texts_a":common}
        else:
            print('no valid type, check type')
            return None
        data = json.dumps(data).encode('utf-8')
        #print(url)
        #print(data)
        #post_res_str = urllib2.urlopen(url, data).read()
        req = urllib.request.Request(url, data)
        post_res_str = urllib.request.urlopen(req).read()
        result = json.loads(post_res_str)
        #print(result)
        if result['error_code'] != 52000:
            print('connect error, check')
            return None
        else:
            return result

    def get_one_piece_score(self, common):
        '''
        params: common -> str
        '''
        common = common.replace(' ', '')
        result = self.__http_url(common, 'one')
        if result:
            return result['result'][0]['value'][1]
        else:
            return None

    def get_batch_score(self, common):
        '''
        params: common -> list
        '''
        common = [tmp.replace(' ', '') for tmp in common]
        result = self.__http_url(common, 'batch')
        if not result:
            ValueError('error input type')
        if result is None:
            return None
        return result['result'][0]['value'][1::2]


if __name__ == '__main__':
    #common2 = '这文章说的是什么？'
    common_list = ['我们一起去杭州旅游吧', '你真是狗娘样的', '我们一起去杭州旅游吧', '卧槽', '你真厉害', '不会吧']
    start = time.time()
    neg_classify = NegReplyClassify()
    #res = neg_classify.get_one_piece_score(common2)
    res = neg_classify.get_batch_score(common_list)
    #print time.time()-start
    print(res)

"""
    neg_classify = NegReplyClassify()

    for line in sys.stdin:
        tokens = line.strip().split('\t')
        #if len(tokens) < 3:
        #    continue
        q = tokens[0].strip()
        #r = tokens[1]
        res_q = neg_classify.get_one_piece_score(q)
        #res_r = neg_classify.get_one_piece_score(r)
        #print line.strip() + '\t' + str(res_q) 
        print q.strip() + '\t' + str(res_q)
"""
