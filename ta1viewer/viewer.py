
def display_pdf_bbox(pdf_url, pageno, box,  http_server_host='http://localhost', 
                     scale = 1.,
                      http_server_port=8000):
    """
        pdf_path is relative to this webserver starting dir.
            as is the viewer url.
            box is in [left, top, right, bottom] format, which is also as given in xDD parquet outputs

        scale: scale the image to fill this fraction of the cell width (1 = fill width, 0.5 = half width, etc.)

        assumes a local http server is running at project root:
            you can set it up with cd <mitaskem>/viz/ && python -m http.server
            (default port is 8000)
            plus, start your jupyter notebook server with 
            --ServerApp.allow_origin='*'  if you see no output in the notebook

        example:
        visualize_pdf_bbox(pdf_url='sidarthe/sidarthe.pdf', pageno=1, box=[737.0, 594.0, 1343.0, 1661.0], scale=2)
    """
    import json
    from IPython.display import HTML
    import random
    import string

    pageno = int(pageno)
    box = [int(n) for n in list(box)]

    args = {
        'url': pdf_url,
        'pageno': pageno,
        'box': box,
        'scale': scale,
    }
    random_id = ''.join(random.choices(population=string.ascii_letters, k=8))
    iframe_id = f'pdfviz_{random_id}'
    args['iframe_id'] = iframe_id
    args_json = json.dumps(args)
                          
    ## if transcript object is notpass data directly to the iframe
    viewer_url = f'{http_server_host}:{http_server_port}/viewer.html'
    
    html = f'''<div>
                <iframe
                    id="{iframe_id}" 
                    src="{viewer_url}"
                    sandbox='allow-same-origin allow-scripts'>
                </iframe>
                <script>
                    function sizeHandler(event){{
                        if (event.origin !== "{http_server_host}:{http_server_port}") {{
                            console.log('ignoring origin', event.origin)
                            return; // some other origin: ignore
                        }}

                        console.log('parent received', event);
                        let args = event.data;
                        if (args.iframe_id !== "{iframe_id}") {{
                            console.log('ignoring message from other iframe', args.iframe_id)                    
                            return; // some other iframe
                        }}

                        // console.log('size handler for iframe: ', "{iframe_id}", sizeHandler)
                        let iframe = document.getElementById("{iframe_id}")
                        iframe.width = args.width + 16;
                        iframe.height = args.height + 16;

                        // removes itself once this is done so we don't have a leak of 
                        // lots of handlers firing every time

                        window.removeEventListener('message', sizeHandler);
                        // console.log('ran and removed size handler for iframe: ', "{iframe_id}", sizeHandler)
                    }}

                   window.addEventListener('message', sizeHandler);

                    document.getElementById("{iframe_id}").onload = () => {{
                        var iframeWindow = document.getElementById("{iframe_id}").contentWindow;
                        let data = {args_json}
                
                        // postMessage to send the data to the iframe
                        console.log('sender', window.location.origin)
                        
                        iframeWindow.postMessage(data,'*');
                    }};
                </script>
            </div>
            '''
    
    return HTML(html)