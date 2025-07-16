#region generated meta
import typing
Inputs = typing.Dict[str, typing.Any]
class Outputs(typing.TypedDict):
    output: str
#endregion

from oocana import Context
import pandas as pd

def main(params: dict, context: Context):
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [7, 8, 9]
    })
    context.preview(df) #type: ignore

    return { "df": df }
