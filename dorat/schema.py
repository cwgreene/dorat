from typing import List

class DoratVariable:
    def __init__(self, js):
        self.name : str = js["name"]
        self.size : int = js["size"]
        self.stackOffset : int = js["stackOffest"]

class DoratCall:
    def __init__(self, js):
        self.funcName : str = js["funcName"]
        self.address : int = int(js["address"], 16)
        self.arguments : List[str] = [s for s in js["arguments"]]

class DoratFunction:
    def __init__(self, js):
        self.name : str = js["name"]
        self.address : int = int(js["address"], 16)
        self.arguments : List[str] = js["arguments"]    # TODO: wrap this somehow
        self.exitAddresses = [int(addr, 16) for addr in js["exitAddresses"]]
        self.variables = [DoratVariable(var) for var in js["variables"]]
        self.calls = [DoratCall(call) for call in js["calls"]]
        self.functionBytes : str = js["functionBytes"]

class DoratProgram:
    def __init__(self, js):
        self.functions = [DoratFunction(f) for f in js["functions"]]
