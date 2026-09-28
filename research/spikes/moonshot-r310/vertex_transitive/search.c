/* Explicit orbital-union search, n <= 63. Single process, bounded CPU and nodes.
 * Input: n k min_degree max_degree target max_nodes max_cpu_seconds;
 * then k rows: orbital degree followed by n decimal uint64 adjacency masks.
 * Optional argv[1]: rejection-certificate file (selection and independent set).
 * C uses include/exclude branching. checker.py uses complement coloring.
 */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define CAP 63
static int n, k, minimum, maximum, target, weights[CAP];
static uint64_t orbital[CAP][CAP], nodes, independent_nodes, limit, counts[CAP];
static uint64_t candidates, hit_selection, hit_adj[CAP];
static double seconds;
static clock_t started;
static int stopped, hit;
static const char *reason = "exhausted";
static FILE *certificates;

static int tick(int independent) {
    if (independent) independent_nodes++; else nodes++;
    uint64_t total = nodes + independent_nodes;
    if (total > limit) { stopped = 1; reason = "node_limit"; return 0; }
    if (total % 1024 == 1 && (double)(clock() - started) / CLOCKS_PER_SEC >= seconds) {
        stopped = 1; reason = "cpu_limit"; return 0;
    }
    return 1;
}

static int independent_set(const uint64_t *adj, uint64_t p, int need,
                           uint64_t chosen, uint64_t *witness) {
    if (!tick(1)) return 0;
    if (need == 0) { *witness = chosen; return 1; }
    if (__builtin_popcountll(p) < need) return 0;
    /* Select the least constrained remaining vertex, then include/exclude it. */
    int v = -1, best = CAP + 1;
    for (uint64_t q = p; q; q &= q - 1) {
        int w = __builtin_ctzll(q), degree = __builtin_popcountll(adj[w] & p);
        if (degree < best) { v = w; best = degree; if (!degree) break; }
    }
    uint64_t bit = UINT64_C(1) << v;
    if (independent_set(adj, p & ~bit & ~adj[v], need - 1, chosen | bit, witness)) return 1;
    if (stopped) return 0;
    return independent_set(adj, p & ~bit, need, chosen, witness);
}

static int triangle_free(const uint64_t *adj) {
    for (int u = 0; u < n; u++) {
        uint64_t neighbors = adj[u];
        while (neighbors) {
            int v = __builtin_ctzll(neighbors);
            neighbors &= neighbors - 1;
            if (adj[u] & adj[v]) return 0;
        }
    }
    return 1;
}

static void visit(int i, int degree, uint64_t selection, const uint64_t *adj) {
    if (stopped || hit || !tick(0)) return;
    if (i == k) {
        if (degree < minimum) return;
        uint64_t witness = 0;
        int rejected = independent_set(adj, (UINT64_C(1) << n) - 1, target, 0, &witness);
        if (stopped) return;
        candidates++;
        counts[degree]++;
        if (rejected) {
            if (certificates && fprintf(certificates, "%" PRIx64 " %" PRIx64 "\n", selection, witness) < 0) {
                stopped = 1; reason = "certificate_io_error";
            }
        } else {
            hit = 1; hit_selection = selection; reason = "candidate";
            for (int v = 0; v < n; v++) hit_adj[v] = adj[v];
        }
        return;
    }
    visit(i + 1, degree, selection, adj);
    if (stopped || hit || degree + weights[i] > maximum) return;
    uint64_t next[CAP];
    for (int v = 0; v < n; v++) next[v] = adj[v] | orbital[i][v];
    if (triangle_free(next)) visit(i + 1, degree + weights[i], selection | (UINT64_C(1) << i), next);
}

static int invalid(const char *message) { fprintf(stderr, "%s\n", message); return 2; }

int main(int argc, char **argv) {
    if (argc > 2) return invalid("usage: search [new-certificate-file]");
    if (scanf("%d%d%d%d%d%" SCNu64 "%lf", &n, &k, &minimum, &maximum, &target, &limit, &seconds) != 7)
        return invalid("invalid input header");
    if (n < 2 || n > CAP || k < 1 || k > n - 1 || minimum < 0 || maximum < minimum
            || maximum >= n || target < 1 || target > n || limit < 1
            || limit > UINT64_C(1000000000) || !(seconds > 0 && seconds <= 300))
        return invalid("input bounds exceeded");
    uint64_t full = (UINT64_C(1) << n) - 1, seen[CAP] = {0};
    for (int i = 0; i < k; i++) {
        if (scanf("%d", &weights[i]) != 1 || weights[i] < 1 || weights[i] >= n)
            return invalid("invalid orbital degree");
        for (int v = 0; v < n; v++) {
            uint64_t *row = &orbital[i][v];
            if (scanf("%" SCNu64, row) != 1 || (*row & ~full) || (*row & (UINT64_C(1) << v))
                    || __builtin_popcountll(*row) != weights[i] || (*row & seen[v]))
                return invalid("invalid, nonregular, or overlapping orbital");
            seen[v] |= *row;
        }
        for (int v = 0; v < n; v++) for (int w = 0; w < n; w++)
            if (((orbital[i][v] >> w) & 1) != ((orbital[i][w] >> v) & 1))
                return invalid("asymmetric orbital");
    }
    for (int v = 0; v < n; v++) if (seen[v] != (full ^ (UINT64_C(1) << v)))
        return invalid("incomplete edge partition");
    int extra;
    do { extra = getchar(); } while (extra == ' ' || extra == '\t' || extra == '\r' || extra == '\n');
    if (extra != EOF) return invalid("unexpected trailing input");
    if (argc == 2) {
        /* Exclusive creation keeps a retry from overwriting earlier evidence. */
        certificates = fopen(argv[1], "wx");
        if (!certificates) return invalid("cannot create new certificate file");
    }
    started = clock();
    uint64_t empty[CAP] = {0};
    visit(0, 0, 0, empty);
    if (certificates && fclose(certificates) != 0) { stopped = 1; reason = "certificate_io_error"; }
    printf("{\"complete\":%s,\"reason\":\"%s\",\"search_nodes\":%" PRIu64
           ",\"independence_nodes\":%" PRIu64 ",\"candidate_count\":%" PRIu64 ",\"degree_counts\":[",
           (!stopped && !hit) ? "true" : "false", reason, nodes, independent_nodes, candidates);
    for (int d = 0; d < n; d++) printf("%s%" PRIu64, d ? "," : "", counts[d]);
    printf("],\"cpu_seconds\":%.6f,\"candidate\":", (double)(clock() - started) / CLOCKS_PER_SEC);
    if (!hit) printf("null");
    else {
        printf("{\"selection\":%" PRIu64 ",\"adjacency\":[", hit_selection);
        for (int v = 0; v < n; v++) printf("%s%" PRIu64, v ? "," : "", hit_adj[v]);
        printf("]}");
    }
    printf("}\n");
    return stopped ? 3 : 0;
}
