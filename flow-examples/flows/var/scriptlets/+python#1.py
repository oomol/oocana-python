from oocana import Context
from typing import Any

def main(inputs: dict[str, Any], context: Context):

  if isinstance(inputs["a"], dict):
    print("a is a dict var")
  else:
    raise Exception("a is not a dict var")

  return { "out": None }
