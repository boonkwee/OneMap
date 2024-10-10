import requests
import json
_DEBUG = False


class Api:
  def __init__(self, url:str='', method:str='', param:dict={}, header:dict={}):
    self.url = url
    self.method = 'GET' if method == '' else method
    self.params = param
    self.header = header

  def call(self):
    response = requests.request(self.method, self.url, params=self.params, headers=self.header)
    if _DEBUG:
      print (f"Called {self.url[:10]}:{self.params['searchVal']} - ")
    return response

  def set(self, keyword:str='', value:str=''):
    if keyword in self.params:
      self.params[keyword] = value

  def sets(self, **kwargs):
    for k, v in kwargs.items():
      if k in self.params:
        self.params[k] = v

  def get(self, keyword:str=''):
    value = self.params.get(keyword, None)
    return value


if __name__=='__main__':
  # url = 'https://www.mit.edu/~ecprice/wordlist.10000'
  # a = Api(url=url)
  # r = a.call()
  # print(r.replace('\\n', '\n'))

  url = "https://www.onemap.gov.sg/api/common/elastic/search"
  params = {
      'searchVal'     : "000001",
      'returnGeom'    : "Y",
      'getAddrDetails': "N",
      'pageNum'       : 1
  }
  a = Api(url=url, param=params)
  print("'hello' keyword => ", a.get('hello'))
  print("'searchVal' keyword => ",a.get('searchVal'))
  a.set('searchVal', '644987')
  print("'searchVal' keyword => ",a.get('searchVal'))
  a.sets(**{'searchVal': '574369', 'pageNum': 2})
  print("'searchVal' keyword => ",a.get('searchVal'))
  print("'pageNum' keyword => ",a.get('pageNum'), type(a.get('pageNum')))
  r = a.call()
  obj = json.loads(r.text)
  print(obj['found'], type(obj['found']))
  print(r.text)
  print(r.url)
