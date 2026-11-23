/-
AU01 · Auditoría de TAR² (Kapoor et al., arXiv 2502.04864v2): el crédito por agente no preserva el
óptimo del equipo. Carril del portátil, 23/11/2026.

* `c1_sufficiency`: si la cuota de i no depende de su propia acción, ninguna desviación unilateral de i
  mejora su pago S = δ·R desde un óptimo del equipo.
* `c1_necessity`: si la cuota depende de la propia acción (δ(a,b) < δ(a',b), δ(a',b) > 0), existe una
  recompensa de equipo con (a,b) como único óptimo en la que i prefiere desviarse a a'.
* `tar2_agentWeight`, `tar2_tempWeight`: ecuaciones (1)–(2) de TAR² para dos agentes / dos pasos.
* `tar2_tie_zero`: con puntuaciones empatadas el peso es 0 (la «equivalencia de retornos por
  construcción» falla).
* `t1_AA_not_equilibrium`: contraejemplo T1 con las fórmulas exactas y ε > 0 simbólico.
-/
import Mathlib

namespace AaNash.CA

/-! ### Teorema C1 -/

/-- Suficiencia: cuota independiente de la propia acción ⇒ el óptimo del equipo es mejor respuesta. -/
theorem c1_sufficiency {A B : Type*} (d : B → ℝ) (hd : ∀ b, 0 ≤ d b) (R : A → B → ℝ)
    (a : A) (b : B) (hopt : ∀ a', R a' b ≤ R a b) (a' : A) :
    d b * R a' b ≤ d b * R a b :=
  mul_le_mul_of_nonneg_left (hopt a') (hd b)

/-- Necesidad: si la cuota de i en (a,b) es menor que en (a',b) y positiva en (a',b), la recompensa
R(a,b) = 1, R(a',b) = r con δ(a,b)/δ(a',b) < r < 1 (y 0 en el resto) tiene a (a,b) como óptimo
estricto frente a a', pero S(a',b) > S(a,b). -/
theorem c1_necessity (δab δa'b : ℝ) (h0 : 0 ≤ δab) (hpos : 0 < δa'b) (hlt : δab < δa'b) :
    ∃ r : ℝ, r < 1 ∧ 0 < r ∧ δab * 1 < δa'b * r := by
  refine ⟨(δab / δa'b + 1) / 2, ?_, ?_, ?_⟩
  · have : δab / δa'b < 1 := (div_lt_one hpos).mpr hlt
    linarith
  · have : 0 ≤ δab / δa'b := div_nonneg h0 hpos.le
    linarith
  · have hq : δab / δa'b < 1 := (div_lt_one hpos).mpr hlt
    have key : δa'b * ((δab / δa'b + 1) / 2) = (δab + δa'b) / 2 := by
      field_simp
    rw [key]
    linarith

/-! ### Fórmulas de TAR² (dos agentes, dos pasos) -/

/-- Ecuación (2): peso del agente 1 en un paso con puntuaciones c₁, c₂ (desplazar al mínimo y normalizar). -/
noncomputable def tar2_agentWeight (ε c₁ c₂ : ℝ) : ℝ :=
  (c₁ - min c₁ c₂) / ((c₁ - min c₁ c₂) + (c₂ - min c₁ c₂) + ε)

/-- Ecuación (1): peso temporal del paso 1 con puntuaciones agregadas g₁, g₂. -/
noncomputable def tar2_tempWeight (ε g₁ g₂ : ℝ) : ℝ :=
  (g₁ - min g₁ g₂) / ((g₁ - min g₁ g₂) + (g₂ - min g₁ g₂) + ε)

/-- Con puntuaciones empatadas, el peso es exactamente 0 (para cualquier ε > 0): la recompensa
redistribuida se anula y Σ s ≠ R. -/
theorem tar2_tie_zero (ε c : ℝ) : tar2_agentWeight ε c c = 0 := by
  unfold tar2_agentWeight; simp

/-- El agente de menor puntuación recibe peso 0 («el ganador se lleva todo»). -/
theorem tar2_min_gets_zero (ε c₁ c₂ : ℝ) (h : c₁ ≤ c₂) : tar2_agentWeight ε c₁ c₂ = 0 := by
  unfold tar2_agentWeight; rw [min_eq_left h]; simp

/-! ### Contraejemplo T1 -/

/-- Cuota del agente 1 en T1: paso 1 con puntuaciones (c₁, c₂), paso 2 con (0, 0); peso temporal del
paso 1 con agregados (c₁ + c₂, 0). -/
noncomputable def share1 (ε c₁ c₂ : ℝ) : ℝ :=
  tar2_tempWeight ε (c₁ + c₂) 0 * tar2_agentWeight ε c₁ c₂

/-- T1 con R(A,A) = 1, R(B,A) = 0,2; puntuaciones en (A,A): (0,1; 0,9) (crédito al agente 2);
en (B,A): (0,9; 0,1). Para todo ε > 0, el pago TAR² del agente 1 en (A,A) es 0 y en (B,A) es positivo:
(A,A), óptimo del equipo, no es equilibrio del juego que TAR² hace jugar. -/
theorem t1_AA_not_equilibrium (ε : ℝ) (hε : 0 < ε) :
    share1 ε (1/10) (9/10) * 1 = 0 ∧ 0 < share1 ε (9/10) (1/10) * (2/10) := by
  constructor
  · unfold share1 tar2_agentWeight
    norm_num
  · unfold share1 tar2_tempWeight tar2_agentWeight
    have h1 : min ((9:ℝ)/10 + 1/10) 0 = 0 := by norm_num
    have h2 : min ((9:ℝ)/10) (1/10) = 1/10 := by norm_num
    rw [h1, h2]
    have : 0 < (9 / 10 + 1 / 10 - 0) / (9 / 10 + 1 / 10 - 0 + (0 - 0) + ε) *
        ((9 / 10 - 1 / 10) / (9 / 10 - 1 / 10 + (1 / 10 - 1 / 10) + ε)) := by
      apply mul_pos
      · apply div_pos <;> linarith
      · apply div_pos <;> linarith
    linarith

end AaNash.CA

#print axioms AaNash.CA.c1_sufficiency
#print axioms AaNash.CA.c1_necessity
#print axioms AaNash.CA.tar2_tie_zero
#print axioms AaNash.CA.tar2_min_gets_zero
#print axioms AaNash.CA.t1_AA_not_equilibrium
