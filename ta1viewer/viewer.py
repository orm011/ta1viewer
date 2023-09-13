
import os
import base64
import json
import random
import string
import io

import pypdf

def _get_viewer_data_url(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Convert the HTML content to base64
    base64_encoded_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

    # Construct the data URL
    data_url = f"data:text/html;base64,{base64_encoded_html}"
    return data_url


def get_page_subset(pdf_file, pages=[]):
    ''' gets only the pages in the list pages, or all pages if pages is empty, 
        and returns a pdf file object with only those pages. 
        Helps avoid slow load times into notebook when you only want to visualize one or a single pages.
    '''
    reader = pypdf.PdfReader(pdf_file)
    if pages is []:
        ps = reader.pages
    else:
        ps = [reader.pages[i] for i in pages]
    # Create a writer object
    writer = pypdf.PdfWriter()
    # Write the page to the writer object
    for page0 in ps:
        writer.add_page(page0)
    # Close the writer object
    b = io.BytesIO()
    writer.write(b)
    b.seek(0)
    return b

def _get_pdf_data_url(pdf_file):
    # Convert the HTML content to base64
    base64_encoded_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    data_url = f"data:application/pdf;base64,{base64_encoded_pdf}"
    return data_url   


def display_pdf_bbox(pdf_path, pageno, box, 
                     scale = 1., http_server_port=8000):
    """
        pdf_path is relative to this webserver starting dir.
            as is the viewer url.
            box is in [left, top, right, bottom] format, which is also as given in xDD parquet outputs

        scale: scale the image to fill this fraction of the cell width (1 = fill width, 0.5 = half width, etc)

        example:
        visualize_pdf_bbox(pdf_path='./ sidarthe/sidarthe.pdf', pageno=1, box=[737.0, 594.0, 1343.0, 1661.0], scale=2)
    """
    from IPython.display import HTML

    pageno = int(pageno)
    box = [int(n) for n in list(box)]
                          
    ## pass data directly to the iframe
    dir = os.path.dirname(os.path.abspath(__file__))
    viewer_path = str(os.path.join(dir, 'viewer.html'))

    with open(viewer_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        # Convert the HTML content to base64
        base64_encoded_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    
    #viewer_data_url = _get_viewer_data_url(viewer_path)
    #viewer_url = f'http://localhost:{http_server_port}/viewer.html'

    pdf_bytes = get_page_subset(open(pdf_path, 'rb'), pages=[pageno-1])
    pdf_url = _get_pdf_data_url(pdf_bytes)
    args = {
        'url': pdf_url,
        'pageno': 1,
        'box': box,
        'scale': scale,
    }
    random_id = ''.join(random.choices(population=string.ascii_letters, k=8))
    iframe_id = f'pdfviz_{random_id}'
    args['iframe_id'] = iframe_id
    args_json = json.dumps(args, indent=2)

    
    html = f'''<div>
                <iframe
                    id="{iframe_id}">
                </iframe>
                <script>
                    function init (){{
                        console.log('within iframe script 2')
                        function sizeHandler(event){{
                            console.log('size handler', event);
                            let args = event.data;
                            if (event.origin !== window.origin) {{
                                console.log('ignoring origin', event.origin, window.origin)
                                return; // some other origin: ignore
                            }}

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
                            console.log('loaded iframe')
                            let iframe = document.getElementById("{iframe_id}")
                            var iframeWindow = document.getElementById("{iframe_id}").contentWindow;

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