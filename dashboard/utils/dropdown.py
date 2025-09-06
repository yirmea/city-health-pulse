import pandas as pd
import re



def clean_data(data: pd.DataFrame):
    
    def pretty_string(string: str):
        return re.match('^([^_]+)', string).group(1).lower().capitalize()
    
    columns = data.columns 
    out = []
    
    overlap = [
        'LILATracts_1And10',
        'LILATracts_halfAnd10', 
        'LILATracts_1And20', 
        "LATracts1", 
        "LATracts20", 
        "LATracts10", 
        "LATracts_half"
    ]
    
    for i in columns: 
        if 'CI' in i:
            pass
        elif 'TotalPop' == i:
            pass
        elif 'Prev' in i :
            label = pretty_string(i)
            entry = {"label": label, "value": i}
            out.append(entry)
        else:
            entry = {"label": i, "value": i}
            if i not in overlap:
                out.append(entry)
                
    colors = get_colors()
    for i in colors:
        out.append(i)
    
    return out

def get_colors():
    colors_dict = [
        {"value": 'LILATracts_1And10', "label": "Low Income & Low Access ( 1mi & 10mi )"},
        {"value": 'LILATracts_halfAnd10', "label": "Low Income & Low Access ( 0.5mi & 10mi )"},
        {"value": 'LILATracts_1And20', "label": "Low Income & Low Access ( 1mi & 20mi )"},
        {"value": "LATracts1", "label": "Low Access Tract ( 1mi )"}, 
        {"value": "LATracts10", "label": "Low Access Tract ( 10mi )"}, 
        {"value": "LATracts20", "label": "Low Access Tract ( 20mi )"}, 
        {"value": "LATracts_half", "label": "Low Access Tract ( 0.5mi )"}, 
    ]
    
    return colors_dict