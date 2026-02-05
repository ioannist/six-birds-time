import Std.Tactic

namespace TimeWorld


def bxor (a b : Bool) : Bool :=
  match a with
  | false => b
  | true => !b


def half : Rat := (1 : Rat) / 2


def p_g (g : Bool → Bool → Bool) (x y a b : Bool) : Rat :=
  if b = bxor a (g x y) then half else 0


def marginalB
    (p : Bool → Bool → Bool → Bool → Rat)
    (x y b : Bool) : Rat :=
  p x y false b + p x y true b


def marginalB_xor (g : Bool → Bool → Bool) (x y b : Bool) : Rat :=
  marginalB (p_g g) x y b


def p_sig (x y a b : Bool) : Rat :=
  if b = x then half else 0


def marginalB_sig (x y b : Bool) : Rat :=
  marginalB p_sig x y b


lemma marginalB_uniform_of_xor_constraint
    (g : Bool → Bool → Bool) (x y b : Bool) :
    marginalB (p_g g) x y b = (1 : Rat) / 2 := by
  cases hb : b <;> cases hg : g x y <;> simp [marginalB, p_g, bxor, half, hb, hg]


lemma signalling_marginalB_depends_on_x (y : Bool) :
    marginalB p_sig true y true ≠ marginalB p_sig false y true := by
  simp [marginalB, p_sig, half]

end TimeWorld
