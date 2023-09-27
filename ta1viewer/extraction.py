from .viewer import display_pdf_bbox
from fuzzywuzzy import process, fuzz

def best_substring_match(query, string):
    # This will extract all substrings of length equal to the query from the string
    candidates = [string[i:i+len(query)] for i in range(len(string) - len(query) + 1)]
    
    # Find the best match among the candidates
    ret = process.extractOne(query, candidates, scorer=fuzz.ratio)
    if ret is None: 
        return None
    
    best_match, score = ret
    positions = [ can == best_match for can in candidates ]
    start = positions.index(True)
    end = start + len(query)
    return start, end

def get_mention_locations(entity):
    mentions = entity['payload']['mentions']
    sources = []
    for mention in mentions:
        sources.append(mention['extraction_source'])
    return sources

def display_substring_match(surrounding, xdd_content):
    from IPython.display import HTML, display

    ret = best_substring_match(surrounding, xdd_content)
    display(HTML(f'<span style="font-size:smaller"><b>Surrounding passage:</b>{surrounding}</span>'))

    if ret is None:
        display(HTML('<em>Could not locate passage within xdd content</em>'))
        display(HTML(f'<span style="font-size:smaller"><b>XDD content:</b>{xdd_content}</span>'))
    else:
        s, e = ret
        display(HTML('<h1>Approx. location of passage within xdd content:</h1>'))
        display(HTML(f'<span style="font-size:smaller">{xdd_content[:s]}<b>{xdd_content[s:e]}</b>{xdd_content[e:]}</span>'))

def display_extraction(pdf_path, xdd_df, entity_json, scale=1.):
    from IPython.display import HTML, display
    sources = get_mention_locations(entity_json)
    source = sources[0]

    xdd_page = xdd_df[(xdd_df.page_num == source['page'])]
    record = xdd_page.iloc[source['block']].to_dict()

    xdd_box = record['bounding_box'].tolist()
    xdd_content = record['content']
    surrounding=source['surrounding_passage']
    display(display_pdf_bbox(pdf_path=pdf_path, pageno=source['page'], 
                   box=xdd_box, scale=scale))
    display_substring_match(surrounding, xdd_content)


