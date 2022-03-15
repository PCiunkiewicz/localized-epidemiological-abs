# %%
import os
import itertools

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.colors import LogNorm

from tools.stats import StatsSimComplete, StatsSimStatus, StatsSimVirus

pal = sns.color_palette()

# %%
paths = [x for x in os.listdir() if x.startswith('outputs-')]

final_stats = {}
for path in tqdm(paths):
    name = path.replace('outputs-', '')
    stat = StatsSimComplete('scenarios/eng301.json', path, flat=True)
    final_stats[name] = stat.prob[-1]
# %%
df = pd.DataFrame(final_stats)
df.index = [f'Agent {i+1}' for i in df.index]
df.columns = pd.MultiIndex.from_tuples([x.split('-') for x in df], names=['mask', 'vaccine'])

sort = itertools.product(
    ['nomask', 'cloth', 'surgical', 'n95'],
    ['novax', '1dose', 'astra', 'mrna'])
df = df[sort]

df = df.T
df['Average'] = df.mean(axis=1)

_, ax = plt.subplots(figsize=[7, 7])
sns.heatmap(df, ax=ax, cmap='RdYlGn_r', square=True, norm=LogNorm(), cbar_kws={'label': 'Excess risk of infection'})
plt.savefig(f'exports/final-heatmap.png', dpi=600, bbox_inches='tight')



# %%
paths = [x for x in os.listdir() if x.startswith('outputs-')]

final_stats = {}
for path in tqdm(paths):
    name = path.replace('outputs-', '')
    stat = StatsSimComplete('scenarios/eng301.json', path, flat=True)
    final_stats[name] = stat.prob.mean(axis=1)
# %%
df = pd.DataFrame(final_stats)
df.columns = pd.MultiIndex.from_tuples([x.split('-') for x in df], names=['mask', 'vaccine'])

mask = ['nomask', 'cloth', 'surgical', 'n95']
vax = ['novax', '1dose', 'astra', 'mrna']
sort = itertools.product(mask[:], vax[:1]) # change here for slices

lines = [':', '-.', '--', '-']
colors = [pal[3], pal[-2], pal[2], pal[-1]]
# style = list(itertools.product(lines[:], colors[:])) # change here for slices

_, ax = plt.subplots(figsize=[5, 3.5])

for i, col in enumerate(df[sort].columns):
    # s = style[i]
    _ = ax.plot(stat.hours, df[col], color=colors[i], label='-'.join(col)) # s[0], color=s[1], put back for styling
_ = ax.set(
    xlabel='Time elapsed (hours)',
    ylabel='Excess Risk of Infection',
    xlim=[0, None],
    # ylim=[0, 0.1]
)
_ = ax.legend()
plt.savefig(f'exports/stats-comparison-mask.png', dpi=600, bbox_inches='tight')



# %%
status = StatsSimStatus('scenarios/eng301.json', 'outputs-nomask-novax')
# %%
status.export(fill=True, ylim=0.041)



# %%
virus = StatsSimVirus('scenarios/eng301.json', 'outputs-nomask-novax')
virus.export()



# %%
virus = StatsSimComplete('scenarios/eng301.json', 'outputs-nomask-novax', flat=True)
virus.export()
# %%
