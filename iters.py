class boto:
  def __init__(self, func, prop, **kwargs):
    self.func = func
    self.prop = prop
    self.kwargs = kwargs
    self.token = None
    self.buffer = []
    self.done = False
    self.tokenAttr = None

  def __iter__(self):
    return self

  def _load_next(self):
    if self.token is None:
      res = self.func(**self.kwargs)
    else:
      if self.tokenAttr == "NextToken":
        res = self.func(NextToken=self.token, **self.kwargs)
      elif self.tokenAttr == "nextToken": 
        res = self.func(nextToken=self.token, **self.kwargs)
      else:
        raise Exception("Unknown pagination indicator.")

    self.buffer = res[self.prop]

    if "NextToken" in res:
      self.token = res["NextToken"]
      self.done = False
      self.tokenAttr = "NextToken"
    elif "nextToken" in res:
      self.token = res["nextToken"]
      self.done = False
      self.tokenAttr = "nextToken"
    else:
      self.token = None
      self.done = True
  
  def __next__(self):
    if len(self.buffer) == 0 and self.done == False:
      self._load_next()
    
    if len(self.buffer) > 0:
      obj = self.buffer[0]
      self.buffer = self.buffer[1:]
      return obj
    
    raise StopIteration()