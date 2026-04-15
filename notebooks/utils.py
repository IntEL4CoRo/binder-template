import os
from IPython.display import display, HTML
from sidecar import Sidecar
import ipywidgets as widgets

def display_desktop(anchor="split-right"):
    """
    Display the remote desktop in a JupyterLab Sidecar tab.
    
    Args:
        anchor (str): Where the Sidecar tab will be placed. Options:
                    'split-right', 'split-left', 'split-top', 'split-bottom',
                    'tab-before', 'tab-after'
    """
    try:
        jupyterhub_user = os.environ["JUPYTERHUB_USER"]
        domain_name = os.environ["BINDER_LAUNCH_HOST"]
        domain_name = domain_name.replace("binder", "jupyter")
    except KeyError:
        jupyterhub_user = None
        domain_name = "http://localhost:8888"
    url_prefix = f"{domain_name}/user/{jupyterhub_user}" if jupyterhub_user is not None else ''

    remote_desktop_url = f"{url_prefix}/desktop"

    display(widgets.HTML(
        value=f'<a href="{remote_desktop_url}"  class="jupyter-button" style="color: #fff;background-color: #1976d2;" target="_blank">Open Desktop in new Tab</a>',
    ))
    
    sc = Sidecar(title='Desktop', anchor=anchor)
    with sc:
        # The inserted custom HTML and CSS snippets are to make the tab resizable
        display(HTML(f"""
            <style>
            body.p-mod-override-cursor div.iframe-widget {{
                position: relative;
                pointer-events: none;
            }}

            body.p-mod-override-cursor div.iframe-widget:before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: transparent;
            }}

            .jp-RenderedHTMLCommon:has(.iframe-widget) {{
                padding-right: 0;
                overflow: hidden;
            }}
            .jp-RenderedHTMLCommon > .iframe-widget:last-child {{
                margin-bottom: 0;
            }}
            </style>
            <div class="iframe-widget" style="width:100%;height:100%;overflow:hidden;">
                <iframe src="{remote_desktop_url}" style="width:100%;height:100%;border:none;margin:0;padding:0;display:block;"></iframe>
            </div>
        """))