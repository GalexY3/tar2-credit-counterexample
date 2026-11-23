"""AU01 nucleo: pesos de TAR2 (ecs. 1-3 de arXiv 2502.04864v2), juegos de prueba y dinamica exacta.

Episodios deterministas dados los actos: la recompensa de equipo R depende de las acciones; las puntuaciones
c[i,t] (cualquier funcion de la trayectoria y del resultado final) se convierten en s[i,t] con las ecs. 1-3.
Cada agente aprende de S_i = sum_t s[i,t] (TAR2 usa solo s, sec. 3.2).
"""
import itertools

import numpy as np

EPS = 1e-8


def tar2_shares(c, eps=EPS):
    """c: array (N agentes, T pasos) de puntuaciones -> delta_i = sum_t w_temp[t] * w_agent[i,t]."""
    c = np.asarray(c, dtype=float)
    agg = c.sum(axis=0)
    wt = (agg - agg.min()) / ((agg - agg.min()).sum() + eps)          # ec. 1
    wa = (c - c.min(axis=0, keepdims=True))
    wa = wa / (wa.sum(axis=0, keepdims=True) + eps)                    # ec. 2
    return (wa * wt[None, :]).sum(axis=1)                              # delta_i ; s = delta * R (ec. 3)


def softmax(x):
    z = np.exp(x - x.max())
    return z / z.sum()


def exact_pg(payoffs, n_actions, rng, steps=4000, lr=1.0, init_scale=1.0):
    """Gradiente de politica exacto, independiente, softmax, en un juego de forma normal de N agentes.
    payoffs[i] : array con forma n_actions -> pago esperado del agente i. Devuelve politicas finales."""
    N = len(n_actions)
    th = [rng.normal(0, init_scale, size=k) for k in n_actions]
    for _ in range(steps):
        pis = [softmax(t) for t in th]
        for i in range(N):
            # pago esperado de cada accion de i frente a los demas (contraccion explicita)
            Q = np.zeros(n_actions[i])
            for a in itertools.product(*[range(k) for k in n_actions]):
                w = 1.0
                for j in range(N):
                    if j != i:
                        w *= pis[j][a[j]]
                Q[a[i]] += w * payoffs[i][a]
            v = pis[i] @ Q
            th[i] = th[i] + lr * pis[i] * (Q - v)
    return [softmax(t) for t in th]


def game_payoffs(R, shares):
    """R: array forma n_actions; shares: array forma (N,)+n_actions. Devuelve pagos TAR2 y globales."""
    N = shares.shape[0]
    tar2 = [shares[i] * R for i in range(N)]
    glob = [R.copy() for _ in range(N)]
    return tar2, glob
