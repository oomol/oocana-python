from python_executor.data import vars

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

    # matplotlib 主题替换
    try:
        import os
        import matplotlib.pyplot as plt # type: ignore
        plt.style.use("classic" if os.getenv("OOMOL_COLOR_SCHEME", "dark") == "light" else "dark_background")
        plt.rcParams['font.sans-serif'] = ['Source Han Sans SC']
    except:
        pass

    # plotly 的 show() 替换
    try:
        import os
        import plotly.io as pio # type: ignore
        from plotly.io import renderers # type: ignore
        from plotly.io.base_renderers import ExternalRenderer # type: ignore

        pio.templates.default = "plotly" if os.getenv("OOMOL_COLOR_SCHEME", "dark") == "light" else "plotly_dark"

        class OomolRenderer(ExternalRenderer):
            def render(self, fig_dict):
                if vars:
                    context = vars.get()

                    import re
                    from plotly.io import to_html # type: ignore
                    from plotly.offline import get_plotlyjs_version # type: ignore

                    cdn_ver = get_plotlyjs_version()
                    cdn_url = f"https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{cdn_ver}/plotly.min.js"

                    html = to_html(
                        fig_dict,
                        include_plotlyjs=cdn_url,
                        include_mathjax="cdn",
                        full_html=True,
                        default_width="100%",
                        default_height="100%",
                        validate=False,
                    )

                    color_scheme = os.getenv("OOMOL_COLOR_SCHEME", "dark")
                    # The generated html has default body margin 8px in chrome, remove it.
                    html = re.sub(r'<html[^>]*?>', r'\g<0><style>html { color-scheme: ' + color_scheme + '; height: 100%; align-content: center } ' +
                        'body { overflow: hidden; margin: 0 }</style>', html, flags=re.I)
                    context.preview({ "type": "html", "data": html })
                else:
                    logger.warning('plotly: no sys.modules["oomol"]')

        renderers['oomol'] = OomolRenderer()
        renderers.default = 'oomol'
    except:
        logger.warning("import plotly failed")
