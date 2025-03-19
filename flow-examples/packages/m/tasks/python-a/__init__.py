#region generated meta
import typing
class Inputs(typing.TypedDict):
  input: str
class Outputs(typing.TypedDict):
  output: str
#endregion

from oocana import Context
from my.a import boo

def main(params: Inputs, context: Context) -> Outputs:

  # your code
  boo()

  return { "output": "output_value" }
