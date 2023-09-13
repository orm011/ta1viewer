from .viewer import display_pdf_bbox
from fuzzywuzzy import process, fuzz

def best_substring_match(query, string):
    assert len(query) <= len(string), 'maybe mixed order of arguments up?'
    # This will extract all substrings of length equal to the query from the string
    candidates = [string[i:i+len(query)] for i in range(len(string) - len(query) + 1)]
    
    # Find the best match among the candidates
    best_match, score = process.extractOne(query, candidates, scorer=fuzz.ratio)
    # display(query)
    # display(best_match)
    positions = [ can == best_match for can in candidates ]
    start = positions.index(True)
    end = start + len(query)
    return start, end

def get_box_data(xdd_df, n):
    sample_annotation = xdd_df.iloc[n:n+1]
    pageno = int(sample_annotation.page_num.values[0])
    box = sample_annotation.bounding_box.values[0].tolist()
    content = sample_annotation.content.values[0]
    return {'pageno':pageno, 'box':box}, content

## example of displaying 
def display_extraction(xdd_df, entity):
    import IPython.display as display
    from IPython.display import HTML

    display(entity['payload'])
    mentions_dict = dict(list(xdd_df.groupby('page_num')))
    source = entity['payload']['mentions'][0]['extraction_source']
    row = mentions_dict[source['page']].iloc[source['block']]
    box = row.bounding_box.tolist()
    page_num = source['page']

    surrounding=source['surrounding_passage']
    content = row.content

    display(display_pdf_bbox(pdf_path='./sidarthe_paper/sidarthe.pdf', pageno=page_num, 
                   box=box, scale=1.3))
    display(HTML('<b>Approx location of surrounding passage within XDD text:</b>'))
    s,e = best_substring_match(surrounding, content)
    display(HTML(f'<span>{content[:s]}<b>{content[s:e]}</b>{content[e:]}'))