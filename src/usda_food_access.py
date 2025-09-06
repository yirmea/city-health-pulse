import pandas as pd

def get_food_access():
    return pd.read_csv("../data/raw/food_access/Food Access Research Atlas.csv")

def to_california(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("State == 'California'")