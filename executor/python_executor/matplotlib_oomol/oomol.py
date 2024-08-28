"""matplotlib.use('module://matplotlib_oomol'), remember to add this file to PYTHONPATH"""

from matplotlib.backend_bases import Gcf # type: ignore
from matplotlib.backends.backend_agg import FigureCanvasAgg # type: ignore

FigureCanvas = FigureCanvasAgg

def show(*args, **kwargs):
    import sys
    from io import BytesIO
    from base64 import b64encode
    var = sys.modules["oomol"]
    if var:
        context = var.get('context')
        for figmanager in Gcf.get_all_fig_managers():
                buffer = BytesIO()
                figmanager.canvas.figure.savefig(buffer, format='png')
                buffer.seek(0)
                png = buffer.getvalue()
                buffer.close()
                url = f'data:image/png;base64,{b64encode(png).decode('utf-8')}'
                payload = { "type": "image", "data": url }
                context.preview(payload)
    else:
        print('matplotlib_oomol: no globals().get("oomol")', file=sys.stderr)
