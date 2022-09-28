import pandas as pd

df = pd.read_csv('deidentified_data.csv')

df = df.sample(n=5000)

df.to_csv('sample_data.csv')
