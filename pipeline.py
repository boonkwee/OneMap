import datetime

class PipeLine:
  def __init__(self):
    self.que = []

  def append(self, obj):
    self.que.append(obj)

  def __len__(self):
    return len(self.que)

  def __next__(self):
    return self.next()

  def next(self):
    if len(self.que):
      return self.que.pop()
    raise StopIteration()

if __name__=='__main__':
  p = PipeLine()
  p.append(datetime.datetime.now())
  p.append(datetime.datetime.now())
  print(f"Length is {len(p)}")
  print(p.next())
  print(p.next())
  if len(p):
    print(p.next())
  else:
    print("No more")