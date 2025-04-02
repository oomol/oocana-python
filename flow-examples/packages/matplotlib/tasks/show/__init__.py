#region generated meta
import typing
Inputs = typing.Dict[str, typing.Any]
class Outputs(typing.TypedDict):
    output: str
#endregion

from oocana import Context
import matplotlib.pyplot as plt

def main(params: Inputs, context: Context) -> Outputs:


    plt.plot([1, 2, 3, 4])
    plt.ylabel('some numbers')
    plt.show()

    return { "output": "output_value" }
