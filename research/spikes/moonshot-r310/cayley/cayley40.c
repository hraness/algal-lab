/* cayley40.c — exhaustive triangle-free Cayley-graph search on a group of
 * order 40 with alpha <= 9. Reads one group from groups40.txt
 * (inverse map + 40x40 multiplication table), enumerates inverse-closed
 * connection sets S, |S|<=9, triangle-free, and tests alpha by a Tomita
 * max-clique search on the complement with greedy-coloring bounds.
 * Usage: ./cayley40 groups40.txt <group_index> [slot_limit]
 * prints per-group stats; writes any hitting connection set to stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 40
static int T[N][N], inv[N];
static int nslots;
static int slot_a[64], slot_b[64];   /* b==-1: involution slot */
static uint64_t slotmask[64];        /* 1<<a | (1<<b) */
static long tested, tf;
static int found;

/* Tomita max-clique on complement bitmasks; returns max clique size. */
static uint64_t comp[N];
static int clq_best;

static void color_sort(uint64_t P, int *order, int *bounds, int *cnt) {
    int c = 0; *cnt = 0;
    uint64_t U = P;
    while (U) {
        c++;
        uint64_t Q = U;
        while (Q) {
            int v = __builtin_ctzll(Q);
            Q &= Q - 1;
            order[*cnt] = v; bounds[*cnt] = c; (*cnt)++;
            U &= ~(1ULL << v);
            Q &= ~comp[v];
        }
    }
}
static void expand(uint64_t P, int cur) {
    int order[N], bounds[N], cnt;
    color_sort(P, order, bounds, &cnt);
    for (int i = cnt - 1; i >= 0; i--) {
        if (cur + bounds[i] <= clq_best) return;
        if (clq_best >= 10) return;          /* already failed */
        expand(P & comp[order[i]], cur + 1);
        P &= ~(1ULL << order[i]);
    }
    if (cur > clq_best) clq_best = cur;
}
static int alpha_le9(uint64_t *adj) {
    uint64_t full = (1ULL << N) - 1;
    for (int i = 0; i < N; i++) comp[i] = full & ~adj[i] & ~(1ULL << i);
    clq_best = 0;
    expand(full, 0);
    return clq_best <= 9;
}

/* S as u64 bitmask; triangle-free iff no a,b in S with a*b in S (a != inv[b]) */
static int in_S(uint64_t S, int x) { return (S >> x) & 1; }
static int tf_add(uint64_t S, int c) {
    /* c not yet in S; check c*t, t*c not in S and no a*b==c for a,b in S */
    for (int t = 0; t < N; t++) if (in_S(S, t)) {
        if (in_S(S, T[c][t]) || in_S(S, T[t][c])) return 0;
        for (int t2 = 0; t2 < N; t2++) if (in_S(S, t2) && T[t][t2] == c && inv[t] != t2) return 0;
    }
    return 1;
}

static void dfs(int i, uint64_t S, int sz) {
    if (found) return;
    if (i == nslots) {
        tested++;
        if (sz == 0) return;
        if (sz <= 9) {
            uint64_t adj[N];
            memset(adj, 0, sizeof adj);
            for (int g = 0; g < N; g++)
                for (int s = 0; s < N; s++) if (in_S(S, s)) adj[g] |= 1ULL << T[g][s];
            tf++;
            if (alpha_le9(adj)) {
                printf("HIT S:");
                for (int s = 0; s < N; s++) if (in_S(S, s)) printf(" %d", s);
                printf("\n"); fflush(stdout);
                found = 1;
            }
        }
        return;
    }
    dfs(i + 1, S, sz);
    int sl = (slot_b[i] < 0) ? 1 : 2;
    if (sz + sl <= 9) {
        int ok = 1;
        uint64_t S2 = S | slotmask[i];
        if (!tf_add(S, slot_a[i])) ok = 0;
        if (ok && slot_b[i] >= 0 && !tf_add(S | slotmask[i] & ~0ULL, slot_b[i])) {
            /* adding both: check b too (a already checked against S) */
            if (!tf_add(S | (1ULL << slot_a[i]), slot_b[i])) ok = 0;
        }
        /* NOTE: for pair slots check b against S+{a}; involutions: a only */
        if (ok) dfs(i + 1, S2, sz + sl);
    }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    if (!f) return 2;
    int gi = atoi(argv[2]);
    char line[4096];
    for (int g = 0; g <= gi; g++) {
        /* skip to group gi's block */
        if (!fgets(line, sizeof line, f)) return 2;
        while (line[0] != '#') if (!fgets(line, sizeof line, f)) return 2;
        /* inverse line */
        if (!fgets(line, sizeof line, f)) return 2;
        char *p = line;
        for (int i = 0; i < N; i++) inv[i] = strtol(p, &p, 10);
        for (int a = 0; a < N; a++) {
            if (!fgets(line, sizeof line, f)) return 2;
            p = line;
            for (int b = 0; b < N; b++) T[a][b] = strtol(p, &p, 10);
        }
    }
    fclose(f);
    /* slots */
    int seen[N]; memset(seen, 0, sizeof seen);
    nslots = 0;
    for (int g = 1; g < N; g++) if (!seen[g]) {
        seen[g] = 1;
        if (inv[g] == g) { slot_a[nslots] = g; slot_b[nslots] = -1; slotmask[nslots] = 1ULL << g; }
        else { seen[inv[g]] = 1; slot_a[nslots] = g; slot_b[nslots] = inv[g];
               slotmask[nslots] = (1ULL << g) | (1ULL << inv[g]); }
        nslots++;
    }
    dfs(0, 0, 0);
    printf("group %d: slots=%d tested=%ld tri-free=%ld hit=%d\n", gi, nslots, tested, tf, found);
    return found;
}
