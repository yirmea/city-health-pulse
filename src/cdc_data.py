import pandas as pd

def get_cities():
    return pd.read_csv("../data/raw/500_Cities__Local_Data_for_Better_Health__2019_release_20250719.csv")

def to_california(df: pd.DataFrame):
    return df.query("StateAbbr == 'CA'")