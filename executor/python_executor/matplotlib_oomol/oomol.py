"""matplotlib.use('module://matplotlib_oomol'), remember to add this file to PYTHONPATH"""

from matplotlib.backend_bases import Gcf # type: ignore
from matplotlib.backends.backend_agg import FigureCanvasAgg # type: ignore
from python_executor.data import vars

FigureCanvas = FigureCanvasAgg

def show(*args, **kwargs):
    import sys
    from io import BytesIO
    from base64 import b64encode
    if vars is not None:
        context = vars.get()
        images = []
        for figmanager in Gcf.get_all_fig_managers():
                buffer = BytesIO()
                figmanager.canvas.figure.savefig(buffer, format='png')
                buffer.seek(0)
                png = buffer.getvalue()
                buffer.close()
                base64Data = b64encode(png).decode('utf-8')
                url = f'data:image/png;base64,{base64Data}'
                images.append(url)
        if images:
            context.preview({ "type": "image", "data": images })
    else:
        print('matplotlib_oomol: no sys.modules["oomol"]', file=sys.stderr)
