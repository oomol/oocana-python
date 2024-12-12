from oocana import Context
from base64 import b64encode

def main(inputs: dict, context: Context):

  # your code
  a = inputs["a"]
  # print binary
  print(b64encode(a))

  return { "out": None }
