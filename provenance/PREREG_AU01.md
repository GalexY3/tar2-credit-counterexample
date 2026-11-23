# PREREG AU01 · Auditoría de TAR²: el crédito por agente no preserva el óptimo del equipo

**Fecha:** 23/11/2026, noche (portátil, carril de auditoría, ala A10).

**Teoría congelada:** `TEORIA_AU01_CREDITO_POR_AGENTE.md`.

**Código:** `au01_core.py` y `au01_confirm.py`.

**Piloto, fuera del diseño:** `au01_pilot.py` (semillas 1000–1099 y 2000–2099). Valores:
- T1: TAR² llega al óptimo en 0/100 y la recompensa global en 95/100;
- T2 (η = 0,05 y sin ruido): el habilitador abandona en 100/100;
- T3: producto escalar −0,019;
- T4: cuotas 0 con empates.

El diseño confirmatorio usa otra semilla (20261125), 200 inicializaciones y un barrido de robustez en T2 (η ∈ {0; 0,01; 0,05; 0,2} × ruido de puntuación ∈ {0; 0,02}), que no estuvieron en el piloto.

**Corrida única:** `python -I -X utf8 au01_confirm.py AU01_RESULTS/au01_confirm.json`, tras el commit y el push de este preregistro y de `FREEZE_AU01.txt`.

| Código | CONFIRMADA si | PARCIAL | REFUTADA si |
|---|---|---|---|
| T1 | (A, A) no es equilibrio del juego TAR²; ≥ 90 % de las 200 inicializaciones de TAR² terminan subóptimas y ≥ 90 % de las globales en el óptimo | — | Alguna condición falla |
| T2 | En las 8 combinaciones (η, ruido): ≥ 80 % abandona la habilitación con TAR² y ≥ 80 % de las corridas globales llegan al óptimo | ≥ 4 combinaciones con abandono ≥ 80 % | Resto |
| T3 | Producto escalar del gradiente esperado del agente 1 (TAR² frente a global) < 0 en la política exhibida | — | ≥ 0 |
| T4 | Con puntuaciones empatadas, la cuota máxima es ≤ 10⁻⁶ en 1000 casos aleatorios | — | Mayor |
| T5 | C1: con cuota independiente de la propia acción, el óptimo puro es mejor respuesta en todas las R muestreadas; con cuota dependiente, la R construida lo rompe en el 100 % de los casos | — | Algún fallo |

**Qué no se prueba:**
- No se ejecuta el código original de TAR² (red de atención, SMACLite ni GRF).
- Las puntuaciones de T2 son «naturales» (contribución contrafactual más sesgo de causa próxima), pero no salen del modelo entrenado de los autores. La afirmación auditada es universal («regardless of model accuracy»), así que basta un contraejemplo admisible. T2 indica, además, que el fallo aparece con puntuaciones razonables.

**Regla de contacto:** no se contacta con los autores. Cualquier comunicación externa es decisión del usuario.
