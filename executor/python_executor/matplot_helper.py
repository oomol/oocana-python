def add_matplot_module():
    import sys
    import os.path
    dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, dir)

def import_helper(logger):
    # matplotlib 的 use() 替换
    try:
        import matplotlib # type: ignore
        matplotlib.use('module://matplotlib_oomol') # matplotlib_oomol.py 文件所在目录加入 PYTHONPATH
    except:
        logger.error("import matplotlib failed")

    # plotly 的 show() 替换
    try:
        import sys
        import plotly.io as pio # type: ignore
        from plotly.io import renderers # type: ignore
        from plotly.io.base_renderers import ExternalRenderer # type: ignore

        pio.templates.default = "plotly_dark"

        class OomolRenderer(ExternalRenderer):
            def render(self, fig_dict):
                var = sys.modules["oomol"]
                if var:
                    context = var.get('context')

                    from plotly.io import to_html # type: ignore
                    html = to_html(
                        fig_dict,
                        include_plotlyjs="cdn", # <-- See comments below.
                        include_mathjax="cdn",
                        full_html=True,
                        default_width="100%",
                        default_height="100%",
                        validate=False,
                    )

                    # ^ The cdn may be hard to fetch.
                    # We use CDN here because the html is about 3 MB long,
                    # but the handler seems only support 100 kB long data.
                    # If we fixed that later we can use include_plotlyjs=True instead.

                    # The generated html has default body margin 8px in chrome, remove it.
                    html = html.replace('<body>', '<body style="margin:0">', 1)
                    context.preview({ "type": "html", "data": html })
                else:
                    logger.warning('plotly: no sys.modules["oomol"]')

        renderers['oomol'] = OomolRenderer()
        renderers.default = 'oomol'
    except:
        logger.warning("import plotly failed")
