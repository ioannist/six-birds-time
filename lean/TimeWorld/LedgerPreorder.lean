namespace TimeWorld

variable {Y : Type} {α : Type} [Preorder α]


def LedgerLE (A : Y → α) (y y' : Y) : Prop := A y ≤ A y'

lemma ledgerLE_refl (A : Y → α) (y : Y) : LedgerLE A y y := by
  exact le_rfl

lemma ledgerLE_trans (A : Y → α) {y1 y2 y3 : Y} :
    LedgerLE A y1 y2 → LedgerLE A y2 y3 → LedgerLE A y1 y3 := by
  intro h12 h23
  exact le_trans h12 h23


def ledgerPreorder (A : Y → α) : Preorder Y :=
  { le := LedgerLE A,
    lt := fun y y' => LedgerLE A y y' ∧ ¬ LedgerLE A y' y,
    le_refl := ledgerLE_refl A,
    le_trans := by
      intro a b c hab hbc
      exact ledgerLE_trans A hab hbc,
    lt_iff_le_not_le := by
      intro a b
      rfl }

lemma ledger_step_le_of_monotone {A : Y → α} {L : Y → Y}
    (hmono : ∀ y, A y ≤ A (L y)) (y : Y) : LedgerLE A y (L y) := by
  exact hmono y

end TimeWorld
