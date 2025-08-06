import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

study = '/home/reza/oaibaseline/'
data_raw = study + 'Data_Raw/'

# Load tab-delimited .txt
scores = pd.read_csv(data_raw + 'scores/oai_koos_womac01.txt', sep='\t', low_memory=False)


# Filter for visit = V00
scores_v00 = scores[scores['visit'] == 'V00']


output_path = data_raw + 'scores/v00_womac_koos.csv'
scores_v00.to_csv(output_path, index=False)
print(scores_v00.head())
print(f"Saved {len(scores_v00)} rows to {output_path}")

# Getting womac and koos
score_list = ['koos_lkpain','koos_rkpain']
scores_reduced = scores_v00[score_list]


tempdata = scores_reduced['koos_rkpain'].astype(float)
koos_rkpain = tempdata.dropna()
tempdata = scores_reduced['koos_lkpain'].astype(float)
koos_lkpain = tempdata.dropna()





# print(scores_reduced.head())
scores_reduced.to_csv(data_raw + 'scores/koos_baseline.csv', index=False)


plt.figure()
data = scores_reduced['koos_rkpain'].astype(float)
data = data.dropna()
print(data.isna().sum())         # Are there NaNs?
print(len(data))
plt.boxplot(
            [koos_rkpain, koos_lkpain],
            # pd.to_numeric(scores_reduced['koos_lkpain'])
            labels=['KOOS Pain (Left)', 'KOOS Pain (Right)'],
            # patch_artist=True,
            # boxprops=dict(facecolor='lightblue', color='blue'),
            # whiskerprops=dict(color='blue'),
            # capprops=dict(color='blue'),
            # medianprops=dict(color='red')
        )
plt.show()