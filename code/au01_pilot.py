"""AU01 PILOTO (fuera del diseno): T1 (adversario), T2 (habilitador/rematador natural), T3 (gradiente), T4 (empates)."""
import sys
import numpy as np
import au01_core as A
sys.stdout.reconfigure(encoding='utf-8')
rng = np.random.default_rng(1)

# ---- T1: dos agentes, dos pasos; decision en el paso 1; paso 2 sin decision ----
R = np.array([[1.0, 0.0], [0.2, 0.3]])     # filas: agente1 A,B ; columnas: agente2 A,B
def scores_T1(a1, a2):
    # paso 1 con puntuacion agregada mayor que el paso 2 (para que w_temp_1 ~ 1)
    # credito en paso 1: (A,A) -> agente 2 ; si agente 1 juega B -> agente 1
    if a1 == 0 and a2 == 0:
        c1 = [0.1, 0.9]
    else:
        c1 = [0.9, 0.1]
    c2 = [0.0, 0.0]
    return np.array([c1, c2]).T            # (N, T)
sh = np.zeros((2, 2, 2))
for a1 in range(2):
    for a2 in range(2):
        sh[:, a1, a2] = A.tar2_shares(scores_T1(a1, a2))
print('T1 cuotas agente1:\n', sh[0].round(6), '\n agente2:\n', sh[1].round(6))
tar2, glob = A.game_payoffs(R, sh)
def outcome(pis): return float(pis[0] @ R @ pis[1])
res_t, res_g = [], []
for k in range(100):
    s = np.random.default_rng(1000 + k)
    pt = A.exact_pg(tar2, [2, 2], s, steps=3000)
    pg = A.exact_pg(glob, [2, 2], np.random.default_rng(1000 + k), steps=3000)
    res_t.append(outcome(pt)); res_g.append(outcome(pg))
print('T1 valor equipo TAR2: medio %.3f, frac >=0.99: %.2f' % (np.mean(res_t), np.mean(np.array(res_t) >= 0.99)))
print('T1 valor equipo global: medio %.3f, frac >=0.99: %.2f' % (np.mean(res_g), np.mean(np.array(res_g) >= 0.99)))

# ---- T2: habilitador (agente 1, paso 1: Abrir/Forrajear/Nada) y rematador (agente 2, paso 2: Tirar/Nada) ----
def R2(a1, a2):
    if a1 == 0 and a2 == 0: return 1.0      # abrir y tirar
    if a1 == 1: return 0.4                  # forrajear da 0.4 solo
    return 0.0
def marginal_scores(a1, a2, eta=0.05):
    # contribucion marginal contrafactual (accion por defecto = Nada) + sesgo de causa proxima eta*t
    base = R2(a1, a2)
    m1 = base - R2(2, a2)                   # agente 1 en paso 1
    m2 = base - R2(a1, 1)                   # agente 2 en paso 2
    c = np.zeros((2, 2))
    c[0, 0] = m1 + eta * 1                  # agente1, paso1
    c[1, 1] = m2 + eta * 2                  # agente2, paso2
    c[1, 0] = 0.0 + eta * 1                 # agente2 inactivo en paso 1
    c[0, 1] = 0.0 + eta * 2                 # agente1 inactivo en paso 2
    return c
RR = np.array([[R2(a1, a2) for a2 in range(2)] for a1 in range(3)])
sh2 = np.zeros((2, 3, 2))
for a1 in range(3):
    for a2 in range(2):
        sh2[:, a1, a2] = A.tar2_shares(marginal_scores(a1, a2))
print('T2 cuotas agente1:\n', sh2[0].round(4), '\n agente2:\n', sh2[1].round(4))
tar2b, globb = A.game_payoffs(RR, sh2)
rt, rg, ft = [], [], []
for k in range(100):
    pt = A.exact_pg(tar2b, [3, 2], np.random.default_rng(2000 + k), steps=3000)
    pg = A.exact_pg(globb, [3, 2], np.random.default_rng(2000 + k), steps=3000)
    rt.append(float(pt[0] @ RR @ pt[1])); rg.append(float(pg[0] @ RR @ pg[1])); ft.append(pt[0][0])
print('T2 TAR2: valor %.3f, P(abrir) media %.3f, frac abandona habilitacion %.2f' % (np.mean(rt), np.mean(ft), np.mean(np.array(ft) < 0.5)))
print('T2 global: valor %.3f, frac optimo %.2f' % (np.mean(rg), np.mean(np.array(rg) >= 0.99)))

# ---- T3: producto escalar de gradientes esperados (agente 1) en T1 ----
def grad_agent1(P, p1, p2):
    pis = [p1, p2]
    Q = P[0] @ p2 if P[0].ndim == 2 else None
    v = p1 @ Q
    return p1 * (Q - v)
p1 = np.array([0.5, 0.5]); p2 = np.array([0.95, 0.05])
gt = grad_agent1(tar2, p1, p2); gg = grad_agent1(glob, p1, p2)
print('T3 gradientes agente1 TAR2', gt.round(4), 'global', gg.round(4), 'producto', float(gt @ gg))

# ---- T4: empates ----
print('T4 cuotas con puntuaciones empatadas:', A.tar2_shares(np.ones((3, 4))))
