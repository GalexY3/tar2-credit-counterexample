# PREREG AU02 · Reproducción con el código original de TAR²

**Fecha:** 23/11/2026, noche (portátil, ala A10).

**Permiso:** el usuario autorizó el 23/11 descargar y ejecutar el código público de TAR² («Sí, ejecútalo»).

**Código original:** github.com/AdityaKapoor74/MARL_Agent_Temporal_Credit_Assignment, commit 883173c04df31c06530d92aace647a5d5e11f7a9 (16/10/2024). Clonado en `C:\Programación\datos_externos\tar2_src`, fuera del repositorio.
- Antes de ejecutarlo se leyeron `MAPPO/TARR_v2/TARR_v2.py`, `modules.py` y las ramas `TAR^2_v2` de `agent.py`: PyTorch puro, sin red ni disco.
- La normalización min-max (agent.py, l. 651–671) coincide con las ecuaciones 1–3 del artículo v2.

**Entorno:** venv `datos_externos/tar2_venv` (PyTorch 2.15 CPU, numpy 2.5.5).

**Script:** `au02_repro.py`.
- Usa su modelo `TARR_v2.TARR` con los hiperparámetros por defecto de `train_agent.py` y su pérdida (rama `TAR^2_v2`).
- Copia literalmente su redistribución.
- Políticas: REINFORCE tabular (lote 64, lr 0,5). Sustituye a MAPPO porque la afirmación auditada es sobre la recompensa.
- Calentamiento: 10 iteraciones de modelo de recompensa sin actualizar políticas. Iteraciones: 300.

**Tarea:**
- Habilitador: el agente 0, en t = 0, elige abrir, forrajear o nada.
- Rematador: el agente 1, en t = 1, elige disparar o nada.
- R = 1 si abre y dispara; 0,4 si forrajea; 0 en otro caso. Hay pasos de relleno hasta T.

**Piloto, fuera del diseño:** prueba de humo con 2 semillas, T = 2 y 40 iteraciones.
- TAR²: P(abrir) 0,18 y 0,38, con cuotas del habilitador en el óptimo de 0,000 y 1,000.
- Global: P(abrir) 0,83 y 0,84.

**Corrida única:** `tar2_venv python au02_repro.py <repo>/MAPPO AU02_RESULTS/au02_repro.json 20 2,4`, con 20 semillas por condición y T ∈ {2, 4}. Va tras el commit y el push de este preregistro y de `FREEZE_AU02.txt`.

| Código | Afirmación | CONFIRMADA si | PARCIAL | REFUTADA si |
|---|---|---|---|---|
| R1 | Con el modelo y la normalización originales, el habilitador abandona (P(abrir) final < 0,5) en una fracción sustancial de semillas con T = 2, y no con la recompensa global | TAR² ≥ 40 % y global ≤ 10 % | TAR² entre 15 % y 40 % (con global ≤ 10 %) | TAR² ≤ 15 %, o global > 10 % |
| R2 | Todo o nada: con T = 2, la cuota aprendida del habilitador en la trayectoria óptima es ≥ 0,95 o ≤ 0,05 | en ≥ 80 % de las semillas TAR² | entre 50 % y 80 % | < 50 % |
| R3 | Con T = 4 (relleno), el abandono con TAR² se mantiene | TAR² ≥ 30 % y global ≤ 10 % | entre 10 % y 30 % | ≤ 10 % |
| R4 | Valor final del equipo con T = 2: TAR² < global (Mann–Whitney unilateral, p < 0,05) | p < 0,05 | p < 0,10 | p ≥ 0,10 |

**Lectura previa:** el resultado matemático no depende de esto (AU01, Lean). AU02 mide si el fallo aparece con el modelo de crédito **aprendido** de los autores en una tarea mínima. Una refutación de R1 significaría que, en esta tarea, su modelo aprende cuotas que no dañan al habilitador, y se informaría así.
