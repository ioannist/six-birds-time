import Std.Tactic

namespace TimeWorld

variable {V : Type}

lemma triangle_sum_of_potential (t : V → Int) (u v w : V) :
    (t v - t u) + (t w - t v) + (t u - t w) = 0 := by
  ring

lemma no_global_potential_of_nonzero_triangle_holonomy
    (ω : V → V → Int) (u v w : V)
    (h : ω u v + ω v w + ω w u ≠ 0) :
    ¬ ∃ t : V → Int,
      ω u v = t v - t u ∧ ω v w = t w - t v ∧ ω w u = t u - t w := by
  intro hExists
  rcases hExists with ⟨t, huv, hvw, hwu⟩
  have : ω u v + ω v w + ω w u = 0 := by
    simpa [huv, hvw, hwu] using triangle_sum_of_potential t u v w
  exact h this

end TimeWorld
