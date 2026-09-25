#### Full-grid census (`count5 grid n`): degenerate 5-subsets of `[n]^3` by type

| n | 5-subsets | in an axis plane | other coplanar | cospherical (not coplanar) | ...of which contain a concyclic quadruple | total degenerate |
|---|---|---|---|---|---|---|
| 3 | 80730 | 1134 | 1140 | 13752 | 9156 | 16026 |
| 4 | 7624512 | 52416 | 57264 | 605256 | 330768 | 714936 |
| 5 | 234531275 | 796875 | 1033360 | 8471308 | n/a | 10301543 |
| 6 | 3739729608 | 6785208 | 8914512 | 77221000 | n/a | 92920720 |
| 7 | 38421292833 | 40041477 | 58834860 | 478788016 | n/a | 577664353 |

#### Random plane-4-regular sets (`rand4reg.py`, `count5 file`): degenerate 5-subsets

| n | seed | coplanar (non-axis) | cospherical | ...with concyclic quadruple | total | cospherical / n |
|---|---|---|---|---|---|---|
| 8 | 1 | 163 | 1108 | n/a | 1271 | 138 |
| 8 | 2 | 129 | 1296 | n/a | 1425 | 162 |
| 8 | 3 | 151 | 1088 | n/a | 1239 | 136 |
| 12 | 1 | 349 | 2321 | n/a | 2670 | 193 |
| 12 | 2 | 484 | 2303 | n/a | 2787 | 192 |
| 12 | 3 | 561 | 2786 | n/a | 3347 | 232 |
| 16 | 1 | 663 | 2922 | n/a | 3585 | 183 |
| 16 | 2 | 467 | 2650 | n/a | 3117 | 166 |
| 16 | 3 | 547 | 2991 | n/a | 3538 | 187 |
| 24 | 1 | 1312 | 4733 | n/a | 6045 | 197 |
| 24 | 2 | 744 | 4074 | n/a | 4818 | 170 |
| 24 | 3 | 1011 | 4771 | n/a | 5782 | 199 |
| 32 | 1 | 1515 | 6812 | n/a | 8327 | 213 |
| 32 | 2 | 1093 | 6583 | n/a | 7676 | 206 |
| 32 | 3 | 1364 | 6815 | n/a | 8179 | 213 |
| 48 | 1 | 4907 | 8260 | 751 | 13167 | 172 |
| 48 | 2 | 1631 | 8339 | 938 | 9970 | 174 |
| 48 | 3 | 1656 | 9038 | 1125 | 10694 | 188 |
| 64 | 1 | 2864 | 11122 | 2010 | 13986 | 174 |
| 64 | 2 | 3240 | 10233 | 1762 | 13473 | 160 |
| 64 | 3 | 2519 | 12119 | 3526 | 14638 | 189 |
| 96 | 1 | 4895 | 11497 | 760 | 16392 | 120 |
| 96 | 2 | 5400 | 11608 | 760 | 17008 | 121 |

#### Monte Carlo `E(n)` (`mc_extra n samples 7`): further grid points on the circumsphere of four random grid points (exact arithmetic per sample)

| n | samples | E(n) | n·E(n) | n²·E(n) | P(≥1 further point) | 8.53·n²·E(n) (predicted cospherical 5-subsets of a random 4n-set) |
|---|---|---|---|---|---|---|
| 3 | 200000 | 4.0823 | 12.2 | 37 | 0.93403 | 314 |
| 4 | 200000 | 4.7385 | 19.0 | 76 | 0.85614 | 647 |
| 5 | 200000 | 4.2104 | 21.1 | 105 | 0.78948 | 898 |
| 6 | 200000 | 4.2014 | 25.2 | 151 | 0.72686 | 1291 |
| 8 | 100000 | 3.7108 | 29.7 | 237 | 0.63116 | 2026 |
| 12 | 100000 | 2.6777 | 32.1 | 386 | 0.48634 | 3290 |
| 16 | 100000 | 2.0100 | 32.2 | 515 | 0.38978 | 4391 |
| 24 | 50000 | 1.2168 | 29.2 | 701 | 0.26688 | 5980 |
| 32 | 50000 | 0.8557 | 27.4 | 876 | 0.19694 | 7477 |
| 48 | 20000 | 0.4808 | 23.1 | 1108 | 0.12475 | 9452 |
| 64 | 20000 | 0.3286 | 21.0 | 1346 | 0.09160 | 11483 |
| 96 | 10000 | 0.1689 | 16.2 | 1557 | 0.05700 | 13282 |
| 128 | 10000 | 0.0788 | 10.1 | 1291 | 0.03500 | 11017 |

#### Window maxima `W(k,n)` (`window_max.py n k 900`)

| k | n | W(k,n) | proved optimal | rounds | 5-clauses | 4-clauses | seconds |
|---|---|---|---|---|---|---|---|
| 2 | 3 | 7 | yes | 83 | 608 | 95 | 5.1 |
| 2 | 4 | 8 | yes | 53 | 305 | 50 | 1.0 |
| 2 | 5 | 8 | yes | 30 | 128 | 20 | 0.5 |
| 2 | 6 | 8 | yes | 14 | 68 | 10 | 0.7 |
| 2 | 7 | 8 | yes | 21 | 200 | 21 | 0.9 |
| 2 | 8 | 8 | yes | 3 | 28 | 4 | 0.0 |
| 3 | 3 | 8 | yes | 253 | 5264 | 421 | 745.4 |

#### Spheres with at least five grid points (`spheres n 5`) and certified LP values (`lp_bound.py`)

| n | spheres with ≥5 points | max points on one sphere | n² | LP constraints | GLOP primal | certified dual bound | ⌊bound⌋ | 4n |
|---|---|---|---|---|---|---|---|---|
| 3 | 849 | 12 | 9 | 1312* | 10.000000 | 10 | 10 | 12 |
| 4 | 32964 | 24 | 16 | 37658* | 13.333333 | 40/3 | 13 | 16 |
| 5 | 539397 | 24 | 25 | 570042* | 20.000000 | 20 | 20 | 20 |
| 6 | 4975281 | 48 | 36 | not solved (see out/lp-n6.txt) | | | | 24 |

\* Corrected by hand in the referee revision to the counts reported in `out/lp-n3.txt`,
`out/lp-n4.txt` and `out/lp-n5.txt`.  The previously rendered values (1267, 36908, 563650) predate the
fix of the concentric-circle bug in the constraint generator; the certified LP values did not change.
The table was not regenerated because `make_tables.py` needs `out/spheres-n5.txt` and
`out/spheres-n6.txt`, which are larger than 1 MB and not committed.
