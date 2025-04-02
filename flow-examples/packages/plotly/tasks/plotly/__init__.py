#region generated meta
import typing
Inputs = typing.Dict[str, typing.Any]
#endregion

from oocana import Context
import plotly.express as px

def main(params: Inputs, context: Context) -> None:

    fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
    fig.show()
    

    return
