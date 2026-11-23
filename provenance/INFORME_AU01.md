# INFORME AU01 · TAR²: el crédito por agente no preserva el óptimo del equipo

**Fecha:** 23/11/2026, noche (portátil, carril de auditoría, ala A10).

**Documentos:** preregistro `PREREG_AU01.md` y congelación `FREEZE_AU01.txt` (commit c064b4c3; hashes comprobados tras la corrida); resultados en `AU01_RESULTS/au01_confirm.json`; Lean en `formal/aa_nash/AaNash/CreditAudit.lean` (salida en `LEAN_AXIOMS_AU01.txt`).

## 1. Qué se audita y qué se concluye

**Objeto:** Kapoor, Tessera, Khadilkar, Baranwal, Peters, Albrecht y Sun, «Redistributing Rewards Across Time and Agents for MARL» (TAR², arXiv 2502.04864v2, 29/10/2025, con código público), y su predecesor (arXiv 2412.14779, póster en CoCoMARL, RLC 2024).

**Afirmación central (resumen de la v2):** el método «is equivalent to a valid PBRS, which guarantees the optimal policy is preserved regardless of model accuracy». La §3.3 añade que, aunque el sesgo lleve a otro punto de convergencia, «our PBRS guarantee ensures the resulting policy … remains in the set of optimal policies».

**Conclusión:** la afirmación es **falsa** tal como está enunciada.
1. **El potencial no es causal.** Φ_i(τ_t) = Σ_{k<t} s_{i,k} depende de R(s_T) y de la normalización sobre toda la trayectoria. El argumento PBRS es circular: con ese criterio, toda recompensa sería «basada en potencial».
2. **La garantía solo vale para la suma.** «J = 2·J_env» es cierto para la suma sobre agentes, pero cada agente aprende de su propia parte S_i = δ_i(τ)·R. Eso es un juego de suma general.
3. **Teorema C1** (es el «factoredness» de Wolpert y Tumer 1999 en forma multiplicativa, y se cita como tal). El óptimo del equipo es mejor respuesta de i en el juego S para **toda** R si y solo si la cuota de i no depende de su propia acción. Las cuotas de TAR² dependen de las puntuaciones de la trayectoria, que incluyen la propia acción.
4. **Errores de construcción:**
   - el agente de menor puntuación recibe peso 0 en cada paso (con dos agentes, todo o nada);
   - con puntuaciones empatadas todo el crédito es 0, así que la «equivalencia de retornos por construcción» también es falsa.

## 2. Resultados de la corrida congelada (semilla 20261125)

| Código | Resultado | Veredicto |
|---|---|---|
| T1 | En el juego T1 (fórmulas exactas de TAR²), (A, A), óptimo del equipo, **no** es equilibrio del juego TAR². Con gradiente exacto independiente: **200/200 inicializaciones subóptimas con TAR²** (valor medio del equipo 0,21) frente a 93 % óptimas con la recompensa global (valor 0,95) | **CONFIRMADA** |
| T2 | Habilitador y rematador con puntuaciones «naturales» (contribución marginal contrafactual más un sesgo η hacia la causa próxima). Abandono de la habilitación ≥ 80 % en 6 de 8 combinaciones (100 % con η ∈ {0,01; 0,05}, con y sin ruido; η = 0 sin ruido; η = 0,2 con ruido). Fallan η = 0 con ruido 0,02 (20 %; el habilitador recibe de media un 48 % de cuota) y η = 0,2 sin ruido (68 %). La recompensa global llega al óptimo en el 97 % | **PARCIAL** |
| T3 | Gradiente esperado del agente 1 en (0,5; 0,5) frente a (0,95; 0,05): TAR² (−0,051; +0,051), global (+0,186; −0,186), producto escalar **−0,019** | **CONFIRMADA** |
| T4 | Con puntuaciones empatadas, cuota máxima 0 en 1000 casos aleatorios | **CONFIRMADA** |
| T5 | C1: con cuota independiente de la propia acción, 1000/1000 juegos preservan el óptimo; con cuota dependiente, la R construida lo rompe en 1000/1000 | **CONFIRMADA** |

**Lectura de T2:** el fallo «natural» necesita que el evaluador de contribuciones **favorezca a la causa próxima**. Es el caso típico de un modelo condicionado al resultado final, que TAR² usa a propósito (§3.5.1). Con un evaluador sin sesgo y con ruido, el habilitador recibe en promedio casi la mitad del crédito y suele mantener la habilitación. La refutación de la afirmación universal no depende de T2: basta T1 (y Lean).

## 3. Lean (5 declaraciones, solo axiomas estándar, sin `sorry`)

- `c1_sufficiency` y `c1_necessity`: las dos direcciones del Teorema C1.
- `tar2_tie_zero` y `tar2_min_gets_zero`: los empates anulan el crédito, y el mínimo recibe 0.
- `t1_AA_not_equilibrium`: con las ecuaciones (1)–(2) de TAR² para dos agentes y dos pasos, y **para todo ε > 0**, el pago TAR² del agente 1 en el óptimo (A, A) es 0 y en (B, A) es positivo.

## 4. Novedad (auditoría del 23/11)

- **No se encontró ninguna crítica publicada de TAR²** (web, arXiv, OpenReview). Ninguna versión corrige la garantía; la v2 la refuerza («regardless of model accuracy»).
- **El Teorema C1 es conocido en espíritu** (factoredness: Wolpert y Tumer 1999, arXiv cs/9908014, §4.3.2: «if g_η … is factored with respect to G, then a change … that improves g_η … improves G»). Lo nuevo es su forma exacta para cuotas multiplicativas y su aplicación a TAR².
- **AREL** (Xiao et al., AAMAS 2022) redistribuye una recompensa **compartida** y no está afectado. El error aparece al pasar a cuotas por agente.

## 5. Límites

- **No se ha ejecutado el código original de TAR²** (su red de puntuación entrenada en SMACLite o GRF). La afirmación auditada es universal, así que el contraejemplo basta para refutarla. Pero no sabemos con qué frecuencia el fallo ocurre con su modelo entrenado en sus tareas.
- **Prominencia del blanco:** es un preprint de 2025 y un póster de taller de 2024, de un grupo destacado. No consta publicación en una sede principal.
- No se ha contactado con los autores (regla del usuario).

## 6. Grado

- **1/3 sólido** (refutación verificada formalmente de la garantía central de un trabajo reciente).
- **Candidato a 2/3\*** si se cierra esta lista de pendientes externos:
  1. reproducir el fallo con el código público de TAR² en una tarea mínima de habilitación;
  2. confirmar el estado de publicación de la v2;
  3. lectura externa.
- **CT2:** sin asignar.

## Adenda (24/11): reproducción con el código original (AU02)

Con el modelo, la pérdida y la normalización originales de TAR², el habilitador abandona en 20/20 semillas (T = 2), frente a 0/20 con la recompensa global. La cuota aprendida del habilitador en el óptimo es 0 en las 20. Valor del equipo: 0,41 frente a 0,99. Ver `INFORME_AU02.md`. Se cierra el pendiente 1 de la §6. **Grado propuesto: 2/3\*** (autoevaluado), con la reserva de prominencia del blanco.
