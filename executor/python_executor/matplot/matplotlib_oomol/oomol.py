"""matplotlib.use('module://matplotlib_oomol'), remember to add this file to PYTHONPATH"""

from matplotlib.backend_bases import Gcf # type: ignore
from matplotlib.backends.backend_agg import FigureCanvasAgg # type: ignore
from python_executor.data import block_var

FigureCanvas = FigureCanvasAgg

def show(*args, **kwargs):
    import sys
    from io import BytesIO
    from base64 import b64encode
    context = block_var.get(None)
    if context is not None:
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
