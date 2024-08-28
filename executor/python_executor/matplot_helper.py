
def import_helper(logger):
    # matplotlib 的 use() 替换
    try:
        import matplotlib # type: ignore
        matplotlib.use('module://matplotlib_oomol') # matplotlib_oomol.py 文件所在目录加入 PYTHONPATH
    except:
        logger.error("import matplotlib failed")

    # plotly 的 show() 替换
    try:
        from plotly.io import renderers # type: ignore
        from plotly.io.base_renderers import ExternalRenderer # type: ignore

        class OomolRenderer(ExternalRenderer):
            def render(self, fig_dict):
                var = globals().get('oomol')
                if var:
                    context = var.get('context')

                    from plotly.io import to_html # type: ignore
                    html = to_html(
                        fig_dict,
                        include_plotlyjs=True,
                        include_mathjax="cdn",
                        full_html=True,
                        default_width="100%",
                        default_height="100%",
                        validate=False,
                    )

                    context.preview({ "type": "html", "data": html })
                else:
                    logger.warning("OomolRenderer: no globals().get('oomol')")

        renderers['oomol'] = OomolRenderer()
        renderers.default = 'oomol'
    except:
        logger.warning("import plotly failed")