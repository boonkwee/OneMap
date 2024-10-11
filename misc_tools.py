import random
import time
_DEBUG = False

def wait_some_seconds(wait_factor:int=2, verbose:bool=False):
  actual_seconds = int(random.random() * wait_factor)
  if _DEBUG:
    print(f"Waiting for {actual_seconds} seconds")
  for each_sec in range(actual_seconds):
    if verbose:
      print(f"\r{each_sec*'.'}", end='')
    time.sleep(1)
  for each_sec in range(actual_seconds):
    if verbose:
      print('\b', end='')


if __name__=='__main__':
  print("Testing")
  wait_some_seconds()
  print("After some waiting")
  # for i in range(101):
  #     print ('\r'+str(i)+'% completed', end='')
  #     time.sleep(0.1)