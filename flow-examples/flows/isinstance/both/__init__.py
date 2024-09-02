from oocana import Context

class Both:
    def __init__(self):
        pass

    def a(self):
        return 

    def b(self):
        return

def a():
    return {"a":Both()}

def b(inputs: dict, context: Context):
    print("b in put is ", inputs)
    i = inputs["b"]
    
    if isinstance(i, Both):
        print("b in put isinstance is ", isinstance(i, Both))
    else:
        raise ValueError("b is not Both")