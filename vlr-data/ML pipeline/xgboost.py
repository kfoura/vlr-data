import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("../player_stats.csv")
excluded_headers = ["team", "all_Kills", "all_Deaths", "all_Assists", "all_FK", "all_FD",
                    "attack_Rating", "attack_ACS", "attack_Kills", "attack_Deaths", ]

features = ["team",
            "all_Rating",
            "all_ACS",
            "all_Kills",
            "all_Deaths"]