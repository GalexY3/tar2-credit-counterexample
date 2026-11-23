# AU01 · El crédito por agente no preserva el óptimo del equipo: auditoría de TAR² (Kapoor et al. 2024–2025)

**Fecha:** 23/11/2026, noche. Portátil, carril de auditoría (ala A10).

**Estado:** teoría escrita **antes** de la verificación. El piloto se declarará fuera del diseño.

## 0. Objeto auditado (leído en texto completo)

**Artículos:**
- **TAR² v2:** Kapoor, Tessera, Khadilkar, Baranwal, Peters, Albrecht y Sun, «Redistributing Rewards Across Time and Agents for Multi-Agent Reinforcement Learning», arXiv 2502.04864v2 (29/10/2025), con código público.
- **Predecesor:** Kapoor et al., «Agent-Temporal Credit Assignment for Optimal Policy Preservation in Sparse MARL», arXiv 2412.14779 (póster en CoCoMARL, RLC 2024), con el Teorema 2 y la Proposición 1 equivalentes.

**Afirmaciones (v2, textuales):**
- **A1 (resumen):** «this method is equivalent to a valid Potential-Based Reward Shaping (PBRS), which guarantees the optimal policy is preserved regardless of model accuracy».
- **A2 (§3.1):** la normalización «enforc[es] strict return equivalence (Σ_{t,i} r_{i,t} = R(s_T)) by construction».
- **A3 (Proposición 3.1):** el agente i recibe r′_{i,t} = r^orig_{i,t} + s_{i,t}; con el potencial de historia Φ_i(τ_t) = Σ_{k<t} s_{i,k}, s es PBRS válido (Devlin y Kudenko 2011) y «any joint policy π* optimal in M_TAR2 is also optimal in M_env».
- **A4 (§3.3):** «TAR² … preserves the gradient direction for each agent individually», y aunque el sesgo pueda llevar a otro punto de convergencia θ*_TAR2, «our PBRS guarantee ensures the resulting policy … remains in the set of optimal policies».
- **Construcción (ecs. 1–3):**
  - pesos temporales w^temp_t = (c^agg_t − min c^agg)/(Σ(·) + ϵ);
  - pesos por agente w^agent_{i,t} = (c_{i,t} − min_j c_{j,t})/(Σ_k(c_{k,t} − min_j c_{j,t}) + ϵ);
  - s_{i,t} = w^temp_t · w^agent_{i,t} · R(s_T).
  - **TAR² entrena cada agente solo con s_{i,t}** (§3.2).

## 1. Diagnóstico

**D1 (potencial no causal).** s_{i,k} depende de R(s_T) y de la normalización sobre **toda** la trayectoria. Φ_i(τ_t) = Σ_{k<t} s_{i,k} no es función de la historia τ_t. Con un «potencial» así, cualquier recompensa sería PBRS (basta tomar Φ = la suma acumulada de la propia recompensa). El argumento de A3 es circular.

**D2 (la suma no es el objetivo de nadie).** «J_PBRS = 2·J_env» es cierto para Σ_i, pero en el entrenamiento cada agente maximiza su propio J_i(π) = E[δ_i(τ)·R(s_T)], con δ_i(τ) = Σ_t w^temp_t w^agent_{i,t}. Eso es un **juego de suma general**. La equivalencia de retornos en suma no implica equivalencia por agente. La implicación sí vale con un solo agente (RUDDER) y con recompensa compartida (AREL), y se trasladó sin justificar al crédito por agente.

**D3 (el ganador se lleva todo).** Con desplazamiento al mínimo, el agente de menor puntuación recibe peso 0 en cada paso. Con dos agentes, los pesos son 0/1 (salvo ϵ). Igual ocurre con los pesos temporales: el paso de menor puntuación recibe 0.

**D4 (la equivalencia no es «por construcción»).** Σ_i w^agent_{i,t} = X_t/(X_t + ϵ) < 1. Si las puntuaciones empatan (X_t = 0), por ejemplo con agentes homogéneos y una red invariante a permutaciones (que AREL impone a propósito), **toda** la recompensa redistribuida de ese paso es 0. Si empatan todos los pasos, Σ s = 0 ≠ R.

## 2. Teoremas propuestos

**Marco:**
- Juego en forma normal con resultado conjunto a (o trayectorias τ) y recompensa de equipo R ≥ 0.
- Las cuotas son δ_i(a) ≥ 0, con Σ_i δ_i ≤ 1.
- El agente i aprende de S_i(a) = δ_i(a)·R(a).

**Teorema C1 (preservación ⇔ cuota independiente de la propia acción).** Para un agente i, son equivalentes:
- (a) para toda R ≥ 0, todo perfil puro óptimo para el equipo es mejor respuesta (débil) de i en el juego S;
- (b) para todo a_{−i} y todo par a_i, a′_i con δ_i(a′_i, a_{−i}) > 0: δ_i(a_i, a_{−i}) ≥ δ_i(a′_i, a_{−i}). Es decir, δ_i(·, a_{−i}) es constante en las acciones de i (en los resultados con cuota positiva).

**Prueba:**
- **(b ⇒ a):** con a_{−i} fijo, S_i = d_i(a_{−i})·R(·, a_{−i}). Maximizar S_i es maximizar R.
- **(¬b ⇒ ¬a):** si δ_i(a_i, a_{−i}) < δ_i(a′_i, a_{−i}), se toma R(a_i, a_{−i}) = 1 como único óptimo, R(a′_i, a_{−i}) = r con δ_i(a)/δ_i(a′) < r < 1, y R = 0 en el resto. Entonces S_i(a′) > S_i(a): el óptimo no es mejor respuesta. □

Es el «factoredness» de Wolpert y Tumer en forma multiplicativa; se cita.

**Teorema C2 (dirección del gradiente esperado).**
- **Enunciado:** el gradiente esperado de i, E[δ_i ĝ_i] = E[S_i ∇log π_i], es paralelo y del mismo sentido que E[R ∇log π_i] para **toda** política producto y toda R si y solo si δ_i es constante en el soporte.
- **Por qué:** con δ_i(a) = d_i(a_{−i}), E[S_i | a_i] = Σ_{a_{−i}} π_{−i}(a_{−i}) d_i(a_{−i}) R(a_i, a_{−i}). Es una reponderación por las acciones de los demás, que puede invertir el orden de las acciones de i.
- **Consecuencia:** la «preservación de la dirección por agente» (A4) solo es cierta por muestra (Proposición 3.2), no en esperanza.

**Corolario C3 (TAR² con sus ecuaciones exactas).**
- **Enunciado:** existen puntuaciones c_{i,t} (cualquier red puede producirlas) tales que, en un juego cooperativo de dos pasos y dos agentes, el perfil óptimo para el equipo **no** es equilibrio del juego TAR², y el gradiente de política exacto e independiente converge a un perfil subóptimo.
- **Consecuencia:** A1 y A4 son falsas tal como están enunciadas.

**Proposición C4 (D4).** Con puntuaciones empatadas en todos los pasos, s ≡ 0 para todo R. A2 es falsa.

## 3. Lectura sociológica

**Trabajo invisible.** Un evaluador de contribuciones que premia la causa próxima (quien remata) y no la habilitadora (quien abre la puerta) hace que la habilitación deje de ser mejor respuesta.
- Star y Strauss (1999) llaman a esto «trabajo invisible».
- Para la cibernética, es un regulador cuyo modelo de atribución no está «controlado por el incentivo». Es la misma estructura que C21: lo que un regulador conserva es lo que lee.
- La condición C1 es la versión de AU01 de la compuerta por incentivos: la cuota de crédito no debe responder a la propia acción del acreditado.

## 4. Predicciones para la verificación

| Código | Predicción |
|---|---|
| T1 | Juego de dos pasos y dos agentes, puntuaciones adversarias dentro de las ecs. 1–3: (A, A) es óptimo del equipo y no es equilibrio del juego TAR². El gradiente exacto independiente (softmax), con TAR², termina en un perfil subóptimo en ≥ 90 % de 200 inicializaciones aleatorias; con la recompensa global termina en el óptimo en ≥ 90 % |
| T2 | Puntuaciones **naturales** (contribución marginal de la causa próxima) en una tarea de habilitador y rematador: el habilitador abandona la habilitación con TAR² en ≥ 80 % de las inicializaciones; con la recompensa global no |
| T3 | Gradiente esperado: existe una política mixta en la que el producto escalar ⟨E[ĝ_TAR2], E[ĝ_global]⟩ < 0 para un agente (se exhibe una exacta) |
| T4 | Empates: con puntuaciones iguales, Σ s = 0 exactamente (salvo ϵ), para R arbitraria |
| T5 | C1 exhaustivo: en juegos 2×2 y 3×3 con cuotas aleatorias, el óptimo es equilibrio del juego S para toda R muestreada si la cuota de i no depende de a_i; si depende, una R construida lo rompe en el 100 % de los casos |
