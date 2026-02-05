namespace TimeWorld

variable {Y : Type}

def Idempotent (e : Y → Y) : Prop := ∀ y, e (e y) = e y

def Commutes (e L : Y → Y) : Prop := ∀ y, e (L y) = L (e y)

def Fix (e : Y → Y) := { y : Y // e y = y }

lemma map_fix_of_commute {e L : Y → Y} (hid : Idempotent e) (hcomm : Commutes e L)
    {y : Y} (hy : e y = y) : e (L y) = L y := by
  calc
    e (L y) = L (e y) := hcomm y
    _ = L y := by simpa [hy]


def restrictToFix (e L : Y → Y) (hid : Idempotent e) (hcomm : Commutes e L) : Fix e → Fix e :=
  fun y =>
    ⟨L y.1, map_fix_of_commute (hid:=hid) (hcomm:=hcomm) (y:=y.1) y.2⟩

end TimeWorld
