import json
import os
import base64
import string
import random

def display_json(json_str_or_dict, width='100%', height='600px'):
    """
        visualize a json dict interactively (in a collapsible tree)
        Args:
            json_str: a json in string or dict form.
            it can be invalid json in string form (useful to help find the issue)
            width: width of the iframe in a css string (e.g. '100%' or '600px')
            height: height of the iframe as a css string (e.g. '100%' or '600px')
    """
    from IPython.display import HTML
    assert isinstance(height, str)
    assert isinstance(width, str)

    hstr : str = height.replace('px','')
    if hstr.isnumeric():
        iframe_height = f'{int(hstr) + 30}px' # give it enough room so there's no second scroll bar
    else:
        iframe_height = height

    ## pass data directly to the iframe
    dir = os.path.dirname(os.path.abspath(__file__))
    viewer_path = str(os.path.join(dir, 'jsonviewer.html'))

    with open(viewer_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        # Convert the HTML content to base64
        base64_encoded_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    
    random_id = ''.join(random.choices(population=string.ascii_letters, k=8))
    iframe_id = f'jsonviewer_{random_id}'

    if isinstance(json_str_or_dict, str):
        json_str = json_str_or_dict
        try:
            obj = json.loads(json_str)
            json_str = json.dumps(obj, indent=2)
        except json.JSONDecodeError as e:
            # just pass the string through
            pass
    elif isinstance(json_str_or_dict, dict):
        json_str = json.dumps(json_str_or_dict, indent=2)

    args = {
        'json_str' : json_str,
        'width' : width,
        'height': height,
    }
    args_json = json.dumps(args)
    
    html = f'''<div>
                <iframe
                    id="{iframe_id}">
                </iframe>
                <script>
                    function init (){{
                        console.log('within iframe script')

                        document.getElementById("{iframe_id}").onload = () => {{
                            console.log('loaded iframe')
                            let iframe = document.getElementById("{iframe_id}")
                            var iframeWindow = document.getElementById("{iframe_id}").contentWindow;
                            iframe.style.width = "{width}";
                            iframe.style.height = "{iframe_height}";
                            let data = {args_json}
                    
                            // postMessage to send the data to the iframe
                            console.log('sender', window.location.origin)
                            
                            iframeWindow.postMessage(data,'*');
                        }};

                            console.log('setting iframe content.')
                            let viewer_html = atob("{base64_encoded_html}");
                            let iframe = document.getElementById("{iframe_id}");
                            let iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

                            iframeDocument.open();
                            iframeDocument.write(viewer_html);
                            iframeDocument.close();
                        }}
                    init();
                </script>
            </div>
            '''
    
    return HTML(html)