/* bruteforce_check: independent exhaustive check of the degenerate-set hypergraph for
 * "no five points of [n]^3 on a sphere or plane".
 *
 * Every 5-subset {a<b<c<d<e} of the grid is classified exactly: it is degenerate iff the
 * 4x4 integer determinant of the lifted differences (p - a) with p in {b,c,d,e},
 * lifted p = (x, y, z, x^2+y^2+z^2), vanishes (equivalent to the 5x5 determinant with
 * rows (x,y,z,x^2+y^2+z^2,1)). Every 4-subset is classified as rank-deficient iff the
 * 3x4 lifted-difference matrix has all four 3x3 minors zero (concyclic or collinear).
 *
 * Against a set file (lines "<bound> <m> i1 ... im", bound 4 = sphere/plane set,
 * bound 3 = circle/line set) it verifies
 *   soundness:    a 5-subset inside some bound-4 set is degenerate;
 *                 a 4-subset inside some bound-3 set is rank-deficient;
 *   completeness: a degenerate 5-subset lies inside some bound-4 set;
 *                 a rank-deficient 4-subset lies inside some bound-3 set.
 * It prints the counts and the number of violations of each kind (all must be 0).
 * Point index convention: idx = x*n*n + y*n + z.  Usage: bruteforce_check n [sets.txt]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
typedef long long ll;
#define MAXN 512
#define WORDS 8
typedef struct { uint64_t b[WORDS]; } bits;
static int n, N; static ll PX[MAXN], PY[MAXN], PZ[MAXN], PW[MAXN];
static bits *SB[5]; static int nS[5]; static int *Lst[5][MAXN]; static int Ln[5][MAXN];
static inline int has(const bits *s, int p) { return (int)((s->b[p >> 6] >> (p & 63)) & 1ULL); }
static inline ll det3(ll a, ll b, ll c, ll d, ll e, ll f, ll g, ll h, ll i) { return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g); }
static int merge(const int *A, int na, const int *B, int nb, int *out) {
  int i = 0, j = 0, m = 0;
  while (i < na && j < nb) { if (A[i] < B[j]) i++; else if (A[i] > B[j]) j++; else { out[m++] = A[i]; i++; j++; } }
  return m; }
static int filter(const int *A, int na, const bits *S, int p, int *out) {
  int m = 0; for (int i = 0; i < na; i++) if (has(&S[A[i]], p)) out[m++] = A[i]; return m; }
static void read_sets(const char *path) {
  FILE *f = fopen(path, "r"); if (!f) { perror(path); exit(2); }
  int bound, m; long cap[5] = {0, 0, 0, 0, 0};
  static int cnt[5][MAXN];
  while (fscanf(f, "%d %d", &bound, &m) == 2) {
    if (bound != 3 && bound != 4) { fprintf(stderr, "bad bound %d\n", bound); exit(2); }
    if (nS[bound] >= cap[bound]) { cap[bound] = cap[bound] ? cap[bound] * 2 : 1024; SB[bound] = realloc(SB[bound], cap[bound] * sizeof(bits)); }
    bits *s = &SB[bound][nS[bound]]; memset(s, 0, sizeof(bits));
    if (m <= bound) { fprintf(stderr, "set of size %d with bound %d\n", m, bound); exit(2); }
    for (int t = 0; t < m; t++) { int p; if (fscanf(f, "%d", &p) != 1 || p < 0 || p >= N) { fprintf(stderr, "bad index\n"); exit(2); }
      if (has(s, p)) { fprintf(stderr, "repeated index\n"); exit(2); } s->b[p >> 6] |= 1ULL << (p & 63); cnt[bound][p]++; }
    nS[bound]++; }
  fclose(f);
  for (int b = 3; b <= 4; b++) { for (int p = 0; p < N; p++) { Lst[b][p] = malloc((cnt[b][p] + 1) * sizeof(int)); Ln[b][p] = 0; }
    for (int s = 0; s < nS[b]; s++) for (int p = 0; p < N; p++) if (has(&SB[b][s], p)) Lst[b][p][Ln[b][p]++] = s; }
  printf("sets: bound4=%d bound3=%d\n", nS[4], nS[3]); }
int main(int argc, char **argv) {
  n = atoi(argv[1]); N = n * n * n; if (N > MAXN) { fprintf(stderr, "n too large\n"); return 2; }
  for (int x = 0; x < n; x++) for (int y = 0; y < n; y++) for (int z = 0; z < n; z++) { int i = x * n * n + y * n + z; PX[i] = x; PY[i] = y; PZ[i] = z; PW[i] = x * x + y * y + z * z; }
  int have = argc > 2; if (have) read_sets(argv[2]);
  int *Iab = malloc(sizeof(int) * (nS[4] + 1)), *Iabc = malloc(sizeof(int) * (nS[4] + 1)), *Iabcd = malloc(sizeof(int) * (nS[4] + 1));
  int *Jab = malloc(sizeof(int) * (nS[3] + 1)), *Jabc = malloc(sizeof(int) * (nS[3] + 1)), *Jabcd = malloc(sizeof(int) * (nS[3] + 1));
  long long n5 = 0, deg5 = 0, cov5 = 0, miss5 = 0, unsound5 = 0, n4 = 0, rank3 = 0, cov3 = 0, miss3 = 0, unsound3 = 0;
  clock_t t0 = clock();
  for (int a = 0; a < N; a++) {
    for (int b = a + 1; b < N; b++) {
      ll u0 = PX[b] - PX[a], u1 = PY[b] - PY[a], u2 = PZ[b] - PZ[a], u3 = PW[b] - PW[a];
      int nab = 0, mab = 0;
      if (have) { nab = merge(Lst[4][a], Ln[4][a], Lst[4][b], Ln[4][b], Iab); mab = merge(Lst[3][a], Ln[3][a], Lst[3][b], Ln[3][b], Jab); }
      for (int c = b + 1; c < N; c++) {
        ll v0 = PX[c] - PX[a], v1 = PY[c] - PY[a], v2 = PZ[c] - PZ[a], v3 = PW[c] - PW[a];
        int nabc = 0, mabc = 0;
        if (have) { nabc = filter(Iab, nab, SB[4], c, Iabc); mabc = filter(Jab, mab, SB[3], c, Jabc); }
        for (int d = c + 1; d < N; d++) {
          ll w0 = PX[d] - PX[a], w1 = PY[d] - PY[a], w2 = PZ[d] - PZ[a], w3 = PW[d] - PW[a];
          /* cofactors for a fourth row e = (e0,e1,e2,e3): det4 = e0*C0 + e1*C1 + e2*C2 + e3*C3 with C_t = (-1)^(3+t) det3(minor) */
          ll C0 = -det3(u1, u2, u3, v1, v2, v3, w1, w2, w3);
          ll C1 =  det3(u0, u2, u3, v0, v2, v3, w0, w2, w3);
          ll C2 = -det3(u0, u1, u3, v0, v1, v3, w0, w1, w3);
          ll C3 =  det3(u0, u1, u2, v0, v1, v2, w0, w1, w2);
          int r3 = (C0 == 0 && C1 == 0 && C2 == 0 && C3 == 0);
          n4++; if (r3) rank3++;
          int nabcd = 0, mabcd = 0;
          if (have) {
            nabcd = filter(Iabc, nabc, SB[4], d, Iabcd); mabcd = filter(Jabc, mabc, SB[3], d, Jabcd);
            if (r3) { if (mabcd) cov3++; else { miss3++; if (miss3 <= 5) printf("MISS3 %d %d %d %d\n", a, b, c, d); } }
            else if (mabcd) { unsound3++; if (unsound3 <= 5) printf("UNSOUND3 %d %d %d %d\n", a, b, c, d); }
          }
          for (int e = d + 1; e < N; e++) {
            ll det = (PX[e] - PX[a]) * C0 + (PY[e] - PY[a]) * C1 + (PZ[e] - PZ[a]) * C2 + (PW[e] - PW[a]) * C3;
            int dg = (det == 0); n5++; if (dg) deg5++;
            if (have) {
              int cv = 0; for (int t = 0; t < nabcd; t++) if (has(&SB[4][Iabcd[t]], e)) { cv = 1; break; }
              if (cv) cov5++;
              if (dg && !cv) { miss5++; if (miss5 <= 5) printf("MISS5 %d %d %d %d %d\n", a, b, c, d, e); }
              if (!dg && cv) { unsound5++; if (unsound5 <= 5) printf("UNSOUND5 %d %d %d %d %d\n", a, b, c, d, e); }
            }
          }
        }
      }
    }
    if ((a + 1) % 16 == 0 || a + 1 == N) { fprintf(stderr, "a=%d/%d n5=%lld deg5=%lld t=%.0fs\n", a + 1, N, n5, deg5, (double)(clock() - t0) / CLOCKS_PER_SEC); }
  }
  printf("n=%d N=%d subsets5=%lld degenerate5=%lld subsets4=%lld rankdeficient4=%lld\n", n, N, n5, deg5, n4, rank3);
  if (have) {
    printf("coverage5=%lld missing5=%lld unsound5=%lld coverage4=%lld missing4=%lld unsound4=%lld\n", cov5, miss5, unsound5, cov3, miss3, unsound3);
    printf("%s\n", (miss5 == 0 && unsound5 == 0 && miss3 == 0 && unsound3 == 0 && cov5 == deg5 && cov3 == rank3) ? "HYPERGRAPH EXACT" : "HYPERGRAPH MISMATCH");
  }
  printf("seconds=%.1f\n", (double)(clock() - t0) / CLOCKS_PER_SEC);
  return 0; }
