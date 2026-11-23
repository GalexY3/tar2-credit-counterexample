"""AU01 confirmacion (T1-T5 del PREREG_AU01). Uso: python -I -X utf8 au01_confirm.py OUT_JSON"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import au01_core as A  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
OUT = sys.argv[1]
SEED = 20261125
R_ = {'seed': SEED}

try:
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.SetPriorityClass(k32.GetCurrentProcess(), 0x00004000)
except Exception:
    pass

N_INIT = 200

# ---------- T1 ----------
R1 = np.array([[1.0, 0.0], [0.2, 0.3]])


def scores_T1(a1, a2):
    c1 = [0.1, 0.9] if (a1 == 0 and a2 == 0) else [0.9, 0.1]
    return np.array([c1, [0.0, 0.0]]).T


sh1 = np.zeros((2, 2, 2))
for a1 in range(2):
    for a2 in range(2):
        sh1[:, a1, a2] = A.tar2_shares(scores_T1(a1, a2))
t1, g1 = A.game_payoffs(R1, sh1)
# (A,A) es equilibrio del juego TAR2?
aa_is_ne = all(t1[0][0, 0] >= t1[0][a, 0] for a in range(2)) and all(t1[1][0, 0] >= t1[1][0, b] for b in range(2))
vt, vg = [], []
for k in range(N_INIT):
    pt = A.exact_pg(t1, [2, 2], np.random.default_rng(SEED + k), steps=3000)
    pg = A.exact_pg(g1, [2, 2], np.random.default_rng(SEED + k), steps=3000)
    vt.append(float(pt[0] @ R1 @ pt[1]))
    vg.append(float(pg[0] @ R1 @ pg[1]))
R_['T1'] = {'AA_is_NE_in_TAR2_game': bool(aa_is_ne), 'frac_suboptimal_tar2': float(np.mean(np.array(vt) < 0.99)),
            'frac_optimal_global': float(np.mean(np.array(vg) >= 0.99)), 'mean_tar2': float(np.mean(vt)),
            'mean_global': float(np.mean(vg))}
R_['T1']['verdict'] = ('CONFIRMADA' if (not aa_is_ne and R_['T1']['frac_suboptimal_tar2'] >= 0.9
                                        and R_['T1']['frac_optimal_global'] >= 0.9) else 'REFUTADA')
print('T1', R_['T1'])


# ---------- T2 (puntuaciones naturales: contribucion marginal + sesgo de causa proxima eta) ----------
def R2(a1, a2):
    if a1 == 0 and a2 == 0:
        return 1.0
    if a1 == 1:
        return 0.4
    return 0.0


def marginal_scores(a1, a2, eta, noise, rng):
    base = R2(a1, a2)
    c = np.zeros((2, 2))
    c[0, 0] = base - R2(2, a2) + eta * 1
    c[1, 1] = base - R2(a1, 1) + eta * 2
    c[1, 0] = eta * 1
    c[0, 1] = eta * 2
    if noise > 0:
        c = c + rng.normal(0, noise, size=c.shape)
    return c


RR2 = np.array([[R2(a1, a2) for a2 in range(2)] for a1 in range(3)])
t2rows = []
for eta in [0.0, 0.01, 0.05, 0.2]:
    for noise in [0.0, 0.02]:
        nr = np.random.default_rng(SEED + int(1000 * eta) + int(1000 * noise))
        sh2 = np.zeros((2, 3, 2))
        for a1 in range(3):
            for a2 in range(2):
                # promedio sobre 50 realizaciones del ruido de puntuacion (un modelo aprendido no exacto)
                sh2[:, a1, a2] = np.mean([A.tar2_shares(marginal_scores(a1, a2, eta, noise, nr))
                                          for _ in range(50 if noise > 0 else 1)], axis=0)
        t2, g2 = A.game_payoffs(RR2, sh2)
        ab, vtv, vgv = [], [], []
        for k in range(N_INIT // 2):
            pt = A.exact_pg(t2, [3, 2], np.random.default_rng(SEED + 7 + k), steps=3000)
            pg = A.exact_pg(g2, [3, 2], np.random.default_rng(SEED + 7 + k), steps=3000)
            ab.append(pt[0][0] < 0.5)
            vtv.append(float(pt[0] @ RR2 @ pt[1]))
            vgv.append(float(pg[0] @ RR2 @ pg[1]))
        t2rows.append({'eta': eta, 'noise': noise, 'frac_abandon_enabling': float(np.mean(ab)),
                       'mean_tar2': float(np.mean(vtv)), 'frac_optimal_global': float(np.mean(np.array(vgv) >= 0.99)),
                       'share_enabler_at_opt': float(sh2[0, 0, 0])})
        print('T2', t2rows[-1])
ok2 = all(r['frac_abandon_enabling'] >= 0.8 for r in t2rows) and all(r['frac_optimal_global'] >= 0.8 for r in t2rows)
R_['T2'] = {'runs': t2rows, 'verdict': 'CONFIRMADA' if ok2 else ('PARCIAL' if sum(
    r['frac_abandon_enabling'] >= 0.8 for r in t2rows) >= len(t2rows) // 2 else 'REFUTADA')}


# ---------- T3 ----------
def grad_i(P, pis, i):
    Q = P[i] @ pis[1] if i == 0 else pis[0] @ P[i]
    return pis[i] * (Q - pis[i] @ Q)


pis = [np.array([0.5, 0.5]), np.array([0.95, 0.05])]
gt, gg = grad_i(t1, pis, 0), grad_i(g1, pis, 0)
R_['T3'] = {'grad_tar2': gt.tolist(), 'grad_global': gg.tolist(), 'inner': float(gt @ gg),
            'verdict': 'CONFIRMADA' if float(gt @ gg) < 0 else 'REFUTADA'}
print('T3', R_['T3'])

# ---------- T4 ----------
rng4 = np.random.default_rng(SEED)
mx = 0.0
for _ in range(1000):
    N, T = int(rng4.integers(2, 6)), int(rng4.integers(1, 8))
    v = rng4.normal()
    mx = max(mx, float(np.abs(A.tar2_shares(np.full((N, T), v))).max()))
R_['T4'] = {'max_share_with_ties': mx, 'verdict': 'CONFIRMADA' if mx <= 1e-6 else 'REFUTADA'}
print('T4', R_['T4'])

# ---------- T5: C1 exhaustivo en juegos aleatorios ----------
rng5 = np.random.default_rng(SEED + 5)
indep_ok, dep_broken, n_ind, n_dep = 0, 0, 0, 0
for trial in range(2000):
    k = int(rng5.integers(2, 4))
    dep = trial % 2 == 1
    # cuotas del agente 1: independientes de a1 (solo de a2) o dependientes
    if dep:
        d1 = rng5.uniform(0.05, 1, size=(k, k))
    else:
        d1 = np.tile(rng5.uniform(0.05, 1, size=(1, k)), (k, 1))
    if not dep:
        # muestrear R aleatorias: el optimo puro es mejor respuesta de 1 en el juego S
        good = True
        for _ in range(50):
            Rr = rng5.uniform(0, 1, size=(k, k))
            a_opt = np.unravel_index(np.argmax(Rr), Rr.shape)
            S1 = d1 * Rr
            if S1[a_opt] < S1[:, a_opt[1]].max() - 1e-12:
                good = False
        n_ind += 1
        indep_ok += good
    else:
        # construir R del Teorema C1 a partir de un par con d1(a1,a2) < d1(a1',a2)
        a2 = int(rng5.integers(k))
        col = d1[:, a2]
        lo, hi = int(np.argmin(col)), int(np.argmax(col))
        if col[lo] >= col[hi]:
            continue
        r = 0.5 * (col[lo] / col[hi] + 1)
        Rr = np.zeros((k, k))
        Rr[lo, a2] = 1.0
        Rr[hi, a2] = r
        S1 = d1 * Rr
        n_dep += 1
        dep_broken += S1[hi, a2] > S1[lo, a2]
R_['T5'] = {'independent_ok': indep_ok, 'n_independent': n_ind, 'dependent_broken': int(dep_broken),
            'n_dependent': n_dep}
R_['T5']['verdict'] = 'CONFIRMADA' if (indep_ok == n_ind and dep_broken == n_dep) else 'REFUTADA'
print('T5', R_['T5'])

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, 'wb') as fh:
    fh.write(json.dumps(R_, indent=1, default=float).encode('utf-8'))
