# INFORME AU02 · El fallo de TAR² se reproduce con el código original de los autores

**Fecha:** 23–24/11/2026 (portátil, ala A10).

**Documentos:**
- preregistro `PREREG_AU02.md` (commit eeee447f);
- análisis congelado `au02_analyze.py` (commit 3af67bb0), subido antes de ver resultados;
- hashes de `FREEZE_AU02.txt` verificados tras la corrida, incluidos los de los tres archivos originales usados;
- resultados en `AU02_RESULTS/`.

**Permiso:** el usuario autorizó descargar y ejecutar el código («Sí, ejecútalo»). No se ha contactado con los autores.

## Montaje

**Código original:** github.com/AdityaKapoor74/MARL_Agent_Temporal_Credit_Assignment, commit 883173c0, rama `TARR_v2`. Se leyó antes de ejecutarlo.
- **Su modelo** `TARR_v2.TARR`, con los hiperparámetros por defecto de `train_agent.py`.
- **Su pérdida:** MSE de la suma de recompensas predichas frente a la recompensa episódica, más la pérdida de dinámica.
- **Su redistribución:** copia literal de `agent.reward_model_output`, normalización min-max = ecuaciones 1–3 del artículo v2.

**Única sustitución:** políticas tabulares con REINFORCE en lugar de MAPPO. La garantía auditada es sobre la recompensa, no sobre el optimizador.

**Tarea:** habilitador (abrir, forrajear o nada) y rematador (disparar o nada). R = 1 si abre y dispara; 0,4 si forrajea. 20 semillas por condición, T ∈ {2, 4}, 300 iteraciones de 64 episodios.

## Resultados

| Código | Resultado | Veredicto |
|---|---|---|
| R1 | T = 2: el habilitador abandona la habilitación (P(abrir) final < 0,5) en **20/20** semillas con TAR², frente a **0/20** con la recompensa global | **CONFIRMADA** |
| R2 | T = 2: la cuota aprendida del habilitador en la trayectoria óptima (abrir, disparar) es **0,000 en las 20 semillas**; todo el crédito va al rematador | **CONFIRMADA** |
| R3 | T = 4: abandono del 65 % con TAR², frente a 0 % con la global | **CONFIRMADA** |
| R4 | Valor final del equipo con T = 2: TAR² 0,41 frente a global 0,99 (Mann–Whitney unilateral, p = 3,4·10⁻⁸). Con T = 4: 0,62 frente a 0,99 | **CONFIRMADA** |

**Análisis *post hoc*, marcado como tal: la cuota nula precede al abandono.** En la primera medición (iteración 25), cuando el habilitador todavía abre a menudo, su cuota en el óptimo ya es ≤ 0,05 en el 80 % de las semillas con T = 2 (media 0,20). Con T = 4 la media inicial es 0,41 y baja a 0,17 hacia la iteración 75. El modelo de crédito aprendido atribuye el resultado a la causa próxima (el rematador, en el paso de mayor puntuación), y la normalización min-max convierte esa preferencia en todo o nada.

## Lectura

- **El fallo no necesita puntuaciones adversarias.** Aparece con el modelo de crédito **aprendido** de los autores en una tarea mínima de cooperación con habilitación, la forma más simple del «trabajo invisible».
- **Con más pasos el efecto se diluye, pero persiste.** Con T = 4 hay más pasos entre los que repartir, y el paso de menor puntuación ya no siempre es el del habilitador.

## Límites

- **Tarea mínima y optimizador distinto.** No es SMACLite ni GRF, y se usa REINFORCE en lugar de MAPPO, cuya función de valor y recorte podrían amortiguar el efecto pero no cambian el objetivo de cada agente.
- **Versión del código.** Es la de octubre de 2024, anterior a la v2 del artículo, pero su rama `TARR_v2` ya implementa la normalización de la v2.

## Grado conjunto AU01 + AU02

- **Qué hay:**
  - la garantía central de TAR² (v2: preservar la política óptima «regardless of model accuracy») es falsa;
  - hay un contraejemplo exacto verificado en Lean (AU01);
  - la condición exacta es el Teorema C1, el factoredness de Wolpert y Tumer en forma multiplicativa;
  - y el fallo se reproduce con el código original de los autores (AU02, 4/4).
- **2/3\* propuesto** (autoevaluado), con la misma estructura que el contraejemplo AA/Nash: refutación, Lean y código original.
- **Reserva:** el blanco es menos prominente que AA (un preprint de 2025 y un póster de taller de 2024, frente a un artículo de ICLR).
- **Pendientes externos (lista cerrada):**
  1. estado de publicación de la v2;
  2. lectura experta externa;
  3. decisión del usuario sobre si comunicarlo a los autores, y cómo.
- **CT2:** sin asignar (regla del usuario).
