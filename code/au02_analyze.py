"""AU02 analisis congelado (escrito y subido antes de ver resultados). Uso: python au02_analyze.py IN_JSON OUT_JSON"""
import json
import sys

import numpy as np
from scipy.stats import mannwhitneyu

rows = json.load(open(sys.argv[1], encoding='utf-8'))


def sel(T, cond):
    return [r for r in rows if r['T'] == T and r['cond'] == cond]


def aband(rs):
    return float(np.mean([r['p_open'] < 0.5 for r in rs]))


out = {}
t2, g2 = sel(2, 'tar2'), sel(2, 'global')
t4, g4 = sel(4, 'tar2'), sel(4, 'global')
a_t2, a_g2, a_t4, a_g4 = aband(t2), aband(g2), aband(t4), aband(g4)
# R1
if a_t2 >= 0.40 and a_g2 <= 0.10:
    r1 = 'CONFIRMADA'
elif 0.15 < a_t2 < 0.40 and a_g2 <= 0.10:
    r1 = 'PARCIAL'
else:
    r1 = 'REFUTADA'
# R2
ext = float(np.mean([(r['enabler_share_at_opt'] >= 0.95 or r['enabler_share_at_opt'] <= 0.05) for r in t2]))
r2 = 'CONFIRMADA' if ext >= 0.80 else ('PARCIAL' if ext >= 0.50 else 'REFUTADA')
# R3
if a_t4 >= 0.30 and a_g4 <= 0.10:
    r3 = 'CONFIRMADA'
elif 0.10 < a_t4 < 0.30:
    r3 = 'PARCIAL'
else:
    r3 = 'REFUTADA'
# R4
p = float(mannwhitneyu([r['team_value'] for r in t2], [r['team_value'] for r in g2], alternative='less').pvalue)
r4 = 'CONFIRMADA' if p < 0.05 else ('PARCIAL' if p < 0.10 else 'REFUTADA')
out = {'abandon': {'T2_tar2': a_t2, 'T2_global': a_g2, 'T4_tar2': a_t4, 'T4_global': a_g4},
       'extreme_share_frac_T2': ext,
       'mean_value': {k: float(np.mean([r['team_value'] for r in v])) for k, v in
                      {'T2_tar2': t2, 'T2_global': g2, 'T4_tar2': t4, 'T4_global': g4}.items()},
       'enabler_share_T2': [r['enabler_share_at_opt'] for r in t2],
       'enabler_share_T4': [r['enabler_share_at_opt'] for r in t4],
       'mw_p_T2': p, 'verdicts': {'R1': r1, 'R2': r2, 'R3': r3, 'R4': r4}}
print(json.dumps(out, indent=1))
with open(sys.argv[2], 'wb') as fh:
    fh.write(json.dumps(out, indent=1).encode('utf-8'))
