#region generated meta
import typing
class Inputs(typing.TypedDict):
  input: str
class Outputs(typing.TypedDict):
  output: str
#endregion

from oocana import Context
from a import boo
import sys

def main(params: Inputs, context: Context) -> Outputs:

  print(sys.path)
  context.logger.info(sys.path)
  boo()

  return { "output": "output_value" }
