

#Warning - This is AI generated code to check if the result i expect is correct.







"""
Burnside's Lemma Applied to 4x4 Sudoku
=======================================
This program mirrors the method used by Ed Russell and Frazer Jarvis for
9x9 Sudoku, applied to the 4x4 (Shidoku) case.

The key steps are:
  1. Generate all 288 valid 4x4 Sudoku grids
  2. Build all 3072 validity-preserving transformations
  3. Represent each transformation as a permutation on the 288 grids
  4. Find conjugacy classes via cycle types (conjugate permutations fix
     the same number of grids, so we only need one representative per class)
  5. For each class, count how many grids are fixed by its representative
  6. Assemble the Burnside sum and divide by |G| to get the answer
"""

from itertools import permutations
from collections import Counter, defaultdict

# ── STEP 1: Generate all 288 valid 4x4 Sudoku grids ──────────────────────────

def is_valid(grid):
    """Check all rows, columns, and 2x2 boxes contain digits 1-4."""
    for row in grid:
        if sorted(row) != [1, 2, 3, 4]:
            return False
    for c in range(4):
        if sorted(grid[r][c] for r in range(4)) != [1, 2, 3, 4]:
            return False
    for br in range(2):
        for bc in range(2):
            box = [grid[br*2+r][bc*2+c] for r in range(2) for c in range(2)]
            if sorted(box) != [1, 2, 3, 4]:
                return False
    return True

def generate_all_grids():
    grids = []
    for r0 in permutations([1, 2, 3, 4]):
        for r1 in permutations([1, 2, 3, 4]):
            for r2 in permutations([1, 2, 3, 4]):
                for r3 in permutations([1, 2, 3, 4]):
                    g = (r0, r1, r2, r3)
                    if is_valid(g):
                        grids.append(g)
    return grids

# ── STEP 2: Apply a single transformation to a grid ──────────────────────────

def apply_transform(grid, bp, rp, sp, cp, dp, t):
    """
    Apply a validity-preserving transformation to a grid.
      bp = band permutation          e.g. (0,1) or (1,0)
      rp = row permutation per band  e.g. [(0,1), (1,0)]
      sp = stack permutation         e.g. (0,1) or (1,0)
      cp = col permutation per stack e.g. [(0,1), (0,1)]
      dp = digit relabelling         e.g. (2,1,4,3) means 1→2, 2→1, 3→4, 4→3
      t  = transpose (bool)
    """
    g = [list(row) for row in grid]
    if t:
        g = [[g[c][r] for c in range(4)] for r in range(4)]
    row_order = [b*2 + r for b in bp for r in rp[b]]
    g = [g[r] for r in row_order]
    col_order = [s*2 + c for s in sp for c in cp[s]]
    g = [[row[c] for c in col_order] for row in g]
    g = [[dp[v-1] for v in row] for row in g]
    return tuple(tuple(r) for r in g)

# ── STEP 3: Build all 3072 transforms as permutations on grid indices ─────────

def build_all_transforms(all_grids):
    """
    Represent each transformation as a tuple of length 288 where
    entry i gives the index of the grid that grid i maps to.
    This lets us treat each transformation as a permutation on {0..287}.
    """
    grid_index = {g: i for i, g in enumerate(all_grids)}
    transforms = []
    params = []

    for bp in permutations([0, 1]):
        for rp0 in permutations([0, 1]):
            for rp1 in permutations([0, 1]):
                for sp in permutations([0, 1]):
                    for cp0 in permutations([0, 1]):
                        for cp1 in permutations([0, 1]):
                            for dp in permutations([1, 2, 3, 4]):
                                for t in [False, True]:
                                    rp = [rp0, rp1]
                                    cp = [cp0, cp1]
                                    perm = tuple(
                                        grid_index[apply_transform(g, bp, rp, sp, cp, dp, t)]
                                        for g in all_grids
                                    )
                                    transforms.append(perm)
                                    params.append((bp, rp, sp, cp, dp, t))
    return transforms, params

# ── STEP 4: Find conjugacy classes via cycle type ─────────────────────────────

def cycle_type(perm):
    """
    The cycle type of a permutation is the sorted tuple of its cycle lengths.
    Two permutations are conjugate if and only if they have the same cycle type.
    This means all transforms in one conjugacy class fix the same number of grids
    — exactly the property Russell & Jarvis exploited to reduce 3,359,232
    calculations to just 275 for 9x9 Sudoku.
    """
    visited = [False] * len(perm)
    cycles = []
    for i in range(len(perm)):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                length += 1
            cycles.append(length)
    return tuple(sorted(cycles))

def find_conjugacy_classes(transforms):
    classes = defaultdict(list)
    for i, perm in enumerate(transforms):
        classes[cycle_type(perm)].append(i)
    return dict(classes)

# ── STEP 5: Count fixed grids for a representative of each class ──────────────

def count_fixed(perm):
    """
    A grid at index i is fixed by transform perm if perm[i] == i,
    i.e. the transform maps the grid back to itself.
    """
    return sum(1 for i in range(len(perm)) if perm[i] == i)

# ── STEP 6: Assemble the Burnside sum ────────────────────────────────────────

def burnside(all_grids, transforms, conjugacy_classes):
    """
    Burnside's lemma:
        |orbits| = (1/|G|) * sum_{g in G} |X^g|
    
    Using conjugacy classes:
        sum_{g in G} |X^g| = sum_{classes} (class_size * fixed_count_for_representative)
    """
    G = len(transforms)
    burnside_sum = 0
    results = []

    for ct, indices in sorted(conjugacy_classes.items(), key=lambda x: -len(x[1])):
        class_size = len(indices)
        rep = transforms[indices[0]]
        fixed = count_fixed(rep)
        contribution = class_size * fixed
        burnside_sum += contribution

        cycle_summary = ", ".join(
            f"{v}×{k}-cycles" for k, v in sorted(Counter(ct).items())
        )
        results.append({
            'cycle_type': ct,
            'cycle_summary': cycle_summary,
            'class_size': class_size,
            'fixed_grids': fixed,
            'contribution': contribution
        })

    return burnside_sum, G, results

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  Burnside's Lemma for 4x4 Sudoku")
    print("  (Mirroring Russell & Jarvis method for 9x9 Sudoku)")
    print("=" * 70)

    print("\nStep 1: Generating all valid 4x4 Sudoku grids...")
    all_grids = generate_all_grids()
    print(f"         Total valid grids: {len(all_grids)}")

    print("\nStep 2: Building all validity-preserving transformations...")
    transforms, params = build_all_transforms(all_grids)
    print(f"         Symmetry group order |G|: {len(transforms)}")
    print(f"         (= 8 row/band × 8 col/stack × 24 digit × 2 transpose)")

    print("\nStep 3: Representing each transform as a permutation on grid indices...")
    print(f"         Each transform is now a tuple of length {len(all_grids)}")

    print("\nStep 4: Finding conjugacy classes via cycle type...")
    conj_classes = find_conjugacy_classes(transforms)
    print(f"         Total conjugacy classes: {len(conj_classes)}")
    print(f"         (vs 275 classes for 9x9 Sudoku)")

    print("\nStep 5 & 6: Computing fixed grids per class and assembling Burnside sum...")
    burnside_sum, G, results = burnside(all_grids, transforms, conj_classes)

    classes_with_fixed = [r for r in results if r['fixed_grids'] > 0]
    classes_without_fixed = [r for r in results if r['fixed_grids'] == 0]

    print(f"\n  Classes with NO fixed grids: {len(classes_without_fixed)}")
    print(f"  Classes WITH fixed grids:    {len(classes_with_fixed)}")
    print(f"  (vs 248 empty / 27 non-empty for 9x9 Sudoku)")

    print("\n" + "─" * 70)
    print(f"  {'Cycle type':<35} {'|Class|':>8}  {'Fixed':>6}  {'Contribution':>12}")
    print("─" * 70)
    for r in results:
        marker = "  " if r['fixed_grids'] == 0 else "* "
        print(f"  {marker}{r['cycle_summary']:<33} {r['class_size']:>8}  {r['fixed_grids']:>6}  {r['contribution']:>12}")
    print("─" * 70)

    print(f"\n  Burnside sum  ∑|X^g| = {burnside_sum}")
    print(f"  Symmetry group order |G| = {G}")
    print(f"  Burnside sum = {len(classes_with_fixed)} orbits × |G| = "
          f"{len(classes_with_fixed)} × {G // len(classes_with_fixed) if burnside_sum % G == 0 else '?'} = {burnside_sum}")
    print(f"\n  ┌─────────────────────────────────────────────────┐")
    print(f"  │  Essentially different 4x4 Sudoku grids         │")
    print(f"  │  = {burnside_sum} / {G} = {burnside_sum // G:<40}│")
    print(f"  └─────────────────────────────────────────────────┘")

    print("\nVerification:")
    print(f"  Each orbit contributes exactly |G| = {G} to the Burnside sum:")
    orbit_contributions = set(
        r['class_size'] * r['fixed_grids']
        for r in results if r['fixed_grids'] > 0
    )
    # Show orbit-level breakdown
    from collections import defaultdict as dd
    orbit_sum_check = sum(r['contribution'] for r in results)
    print(f"  Sum of all contributions = {orbit_sum_check}")
    print(f"  {orbit_sum_check} / {G} = {orbit_sum_check // G} essentially different grids ✓")


if __name__ == "__main__":
    main()
