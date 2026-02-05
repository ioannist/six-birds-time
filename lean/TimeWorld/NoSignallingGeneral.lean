import Std.Tactic

namespace TimeWorld


def pFactBool
  (pL : Bool → Rat)
  (pA : Bool → Bool → Bool → Rat)
  (pB : Bool → Bool → Bool → Rat) :
  Bool → Bool → Bool → Bool → Rat :=
fun x y a b =>
  (pL false * pA x a false * pB y b false) +
  (pL true * pA x a true * pB y b true)


def marginalB
    (p : Bool → Bool → Bool → Bool → Rat) (x y b : Bool) : Rat :=
  p x y false b + p x y true b


lemma marginalB_independent_of_x_of_factorization_bool_lambda
  (pL : Bool → Rat)
  (pA : Bool → Bool → Bool → Rat)
  (pB : Bool → Bool → Bool → Rat)
  (hA : ∀ x l, pA x false l + pA x true l = 1)
  (x1 x2 y b : Bool) :
  marginalB (pFactBool pL pA pB) x1 y b =
  marginalB (pFactBool pL pA pB) x2 y b := by
  unfold marginalB pFactBool
  calc
    (pL false * pA x1 false false * pB y b false +
      pL true * pA x1 false true * pB y b true) +
      (pL false * pA x1 true false * pB y b false +
      pL true * pA x1 true true * pB y b true)
        = (pL false * (pA x1 false false + pA x1 true false) * pB y b false) +
          (pL true * (pA x1 false true + pA x1 true true) * pB y b true) := by
            ring
    _ = (pL false * 1 * pB y b false) + (pL true * 1 * pB y b true) := by
          simp [hA]
    _ = (pL false * (pA x2 false false + pA x2 true false) * pB y b false) +
        (pL true * (pA x2 false true + pA x2 true true) * pB y b true) := by
          ring
    _ = (pL false * pA x2 false false * pB y b false +
        pL true * pA x2 false true * pB y b true) +
        (pL false * pA x2 true false * pB y b false +
        pL true * pA x2 true true * pB y b true) := by
          ring

end TimeWorld
