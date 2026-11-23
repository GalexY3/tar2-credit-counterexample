"""AU02 · Reproduccion con el codigo original de TAR2 (repo AdityaKapoor74/MARL_Agent_Temporal_Credit_Assignment,
commit 883173c0, rama TARR_v2) en la tarea habilitador/rematador.

Uso: python au02_repro.py RUTA_REPO_MAPPO OUT_JSON N_SEEDS T_LIST [smoke]
- Modelo de recompensa: TARR_v2.TARR del repositorio, con los hiperparametros por defecto de train_agent.py
  (emb 64, 4 cabezas, profundidad 3, sample_num 5, dropout 0.3, AdamW lr 5e-4, dinamica 5e-2, lote 64).
- Perdida: la rama 'TAR^2_v2' de agent.update_reward_model (MSE de la suma + perdida de dinamica).
- Redistribucion: copia literal de agent.reward_model_output, rama 'TAR^2_v2' (normalizacion min-max).
- Politicas: REINFORCE tabular (sustituye a MAPPO; la afirmacion auditada es sobre la recompensa).
Condiciones: 'tar2' (cada agente aprende de su S_i) y 'global' (cada agente aprende de R).
"""
import copy
import json
import os
import sys

import numpy as np
import torch
import torch.nn.functional as F

REPO = sys.argv[1]
OUT = sys.argv[2]
N_SEEDS = int(sys.argv[3])
T_LIST = [int(x) for x in sys.argv[4].split(',')]
SMOKE = len(sys.argv) > 5 and sys.argv[5] == 'smoke'
sys.path.insert(0, REPO)
from TARR_v2 import TARR_v2  # noqa: E402  (codigo original, leido antes de ejecutar)

torch.set_num_threads(2)
try:
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.SetPriorityClass(k32.GetCurrentProcess(), 0x00004000)
except Exception:
    pass

N_AG, N_ACT = 2, 3
OPEN, FORAGE, NOTHING = 0, 1, 2
SHOOT = 0


def torch_nanmin(tensor, dim=None, keepdim=False):  # copia de MAPPO/utils.py
    max_value = torch.finfo(tensor.dtype).max
    return tensor.nan_to_num(max_value).min(dim=dim, keepdim=keepdim)


def team_reward(a0, b1):
    if a0 == OPEN and b1 == SHOOT:
        return 1.0
    if a0 == FORAGE:
        return 0.4
    return 0.0


def rollout(p0, p1, B, T, rng):
    """Devuelve acciones (B,T,N), obs aliados (B,N,T,F), recompensa episodica (B,), elecciones."""
    a0 = rng.choice(3, size=B, p=p0)
    b1 = rng.choice(2, size=B, p=p1)                 # 0 = disparar, 1 = nada
    act = np.full((B, T, N_AG), NOTHING, dtype=np.int64)
    act[:, 0, 0] = a0
    act[:, 1, 1] = np.where(b1 == 0, SHOOT, NOTHING)
    Fdim = T + N_AG + 2
    obs = np.zeros((B, N_AG, T, Fdim), dtype=np.float32)
    for t in range(T):
        obs[:, :, t, t] = 1.0
        for i in range(N_AG):
            obs[:, i, t, T + i] = 1.0
        if t >= 1:
            obs[:, :, t, T + N_AG] = (a0 == OPEN).astype(np.float32)[:, None]
            obs[:, :, t, T + N_AG + 1] = (a0 == FORAGE).astype(np.float32)[:, None]
    R = np.array([team_reward(x, 0 if y == 0 else 1) for x, y in zip(a0, b1)], dtype=np.float32)
    return act, obs, R, a0, b1


def model_forward(model, obs, act, R, T):
    B = obs.shape[0]
    ally = torch.from_numpy(obs)
    enemy = torch.zeros(B, 1, T, 1)
    actions = torch.from_numpy(act).permute(0, 2, 1)            # (B, N, T) como en agent.py
    ep_len = torch.full((B,), T, dtype=torch.long)
    ep_rew = torch.from_numpy(R)
    masks = torch.ones(B, T, N_AG)
    return model(ally, enemy, None, actions, ep_len, ep_rew, masks), actions, masks


def update_reward_model(model, opt, obs, act, R, T):
    (rewards, tw, aw, ts, ascore, action_pred), actions, masks = model_forward(model, obs, act, R, T)
    ep = torch.from_numpy(R)
    rpl = F.mse_loss(rewards.reshape(actions.shape[0], -1).sum(dim=-1), ep)
    ce = torch.nn.CrossEntropyLoss(reduction='none')
    dyn = 5e-2 * (ce(action_pred.reshape(-1, N_ACT), actions.long().reshape(-1)) * masks.reshape(-1)).sum() / (masks.sum() + 1e-5)
    loss = rpl + dyn
    opt.zero_grad()
    loss.backward()
    opt.step()
    return float(rpl)


def redistribute(model, obs, act, R, T):
    """Copia de agent.reward_model_output, rama TAR^2_v2 (normalizacion min-max)."""
    model.eval()
    with torch.no_grad():
        (rewards, tw, aw, ts, ascore, action_pred), actions, agent_masks_batch = model_forward(model, obs, act, R, T)
        temporal_rewards = (rewards * agent_masks_batch).sum(dim=-1, keepdim=True)
        temporal_rewards_copy = copy.deepcopy(temporal_rewards)
        temporal_rewards_copy[(agent_masks_batch.sum(dim=-1, keepdim=True) > 0).int() == 0] = float('nan')
        min_temporal_rewards, _ = torch_nanmin(temporal_rewards_copy, dim=-2, keepdim=True)
        temporal_rewards = (temporal_rewards - min_temporal_rewards) * (agent_masks_batch.sum(dim=-1, keepdim=True) > 0).int()
        temporal_weights = temporal_rewards / (temporal_rewards.sum(dim=1, keepdim=True) + 1e-5)
        agent_rewards_copy = copy.deepcopy(rewards)
        agent_rewards_copy[agent_masks_batch.int() == 0] = float('nan')
        min_agent_rewards, _ = torch_nanmin(agent_rewards_copy, dim=-1, keepdim=True)
        agent_rewards = (rewards - min_agent_rewards) * agent_masks_batch
        agent_weights = agent_rewards / (agent_rewards.sum(dim=-1, keepdim=True) + 1e-5)
        episodic_rewards = torch.from_numpy(R).reshape(-1, 1, 1)
        s = (temporal_weights * agent_weights) * episodic_rewards          # (B, T, N)
    model.train()
    return s.sum(dim=1).numpy()                                          # (B, N) retorno por agente


def softmax(x):
    z = np.exp(x - x.max())
    return z / z.sum()


def run(seed, T, cond, iters, B=64, warm=10, rm_updates=4, lr_pi=0.5):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    model = TARR_v2.TARR(environment='StarCraft', ally_obs_shape=T + N_AG + 2, enemy_obs_shape=1, obs_shape=None,
                         n_actions=N_ACT, emb_dim=64, n_heads=4, n_layer=3, seq_length=T, n_agents=N_AG,
                         n_enemies=1, sample_num=5, device=torch.device('cpu'), dropout=0.3, emb_dropout=0.0,
                         action_space='discrete')
    opt = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=0.0, eps=1e-5)
    th0, th1 = np.zeros(3), np.zeros(2)
    buf = []
    share_log = []
    for it in range(iters):
        p0, p1 = softmax(th0), softmax(th1)
        act, obs, R, a0, b1 = rollout(p0, p1, B, T, rng)
        buf.append((act, obs, R))
        buf = buf[-30:]
        if cond == 'tar2':
            for _ in range(rm_updates):
                j = int(rng.integers(len(buf)))
                update_reward_model(model, opt, buf[j][1], buf[j][0], buf[j][2], T)
            if it < warm:
                continue
            S = redistribute(model, obs, act, R, T)
            r0, r1 = S[:, 0], S[:, 1]
        else:
            if it < warm:
                continue
            r0, r1 = R, R
        # REINFORCE con linea base media
        g0 = np.zeros(3)
        g1 = np.zeros(2)
        for x, y, u, v in zip(a0, b1, r0 - r0.mean(), r1 - r1.mean()):
            e0 = -p0.copy(); e0[x] += 1
            e1 = -p1.copy(); e1[y] += 1
            g0 += u * e0
            g1 += v * e1
        th0 += lr_pi * g0 / B
        th1 += lr_pi * g1 / B
        if cond == 'tar2' and it % 25 == 0:
            m_open = (a0 == OPEN) & (b1 == 0)
            if m_open.any():
                share_log.append(float(S[m_open, 0].mean()))
    p0, p1 = softmax(th0), softmax(th1)
    value = p0[OPEN] * p1[0] * 1.0 + p0[FORAGE] * 0.4
    # cuota final del habilitador en la trayectoria optima (abrir, disparar)
    act, obs, R, a0, b1 = rollout(np.array([1.0, 0, 0]), np.array([1.0, 0]), 64, T, rng)
    S = redistribute(model, obs, act, R, T) if cond == 'tar2' else None
    return {'seed': seed, 'T': T, 'cond': cond, 'p_open': float(p0[OPEN]), 'p_forage': float(p0[FORAGE]),
            'p_shoot': float(p1[0]), 'team_value': float(value),
            'enabler_share_at_opt': (float(S[:, 0].mean()) if S is not None else None),
            'finisher_share_at_opt': (float(S[:, 1].mean()) if S is not None else None),
            'share_log': share_log}


if __name__ == '__main__':
    iters = 40 if SMOKE else 300
    rows = []
    for T in T_LIST:
        for cond in ['tar2', 'global']:
            for k in range(N_SEEDS):
                r = run(20261126 + 101 * k + 7 * T + (0 if cond == 'tar2' else 50000), T, cond, iters)
                rows.append(r)
                print(json.dumps({kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in r.items() if kk != 'share_log'}), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, 'wb') as fh:
        fh.write(json.dumps(rows, indent=1).encode('utf-8'))
