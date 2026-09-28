/* Independent bounded decision search for a K-set in {0,...,n-1}^3 with
 * no five points on one sphere or plane (n <= 6).
 *
 * Adapted from the unfinished indep_enum.c experiment, with three correctness
 * repairs: a terminating combination iterator; rank-deficient four-tuples
 * forbid EVERY fifth point; and complete initial-layer coverage, including
 * empty layers and singletons. The hash cache replaces colliding entries and
 * therefore cannot loop when full. No shared table or canonical augmentation
 * from layer_enum5.c is used.
 *
 * Completeness: five points in a z-layer are coplanar, so each layer has <=4
 * points. Enumerate its subsets. D4 canonicalization of layer 0 keeps one
 * member of every orbit. Reflection z -> n-1-z permits |Llast| <= |Lfirst|;
 * both reductions can be disabled. The only other search bound sums the
 * remaining layer capacities after individually forbidden points are removed.
 * A rank-deficient four-tuple is excluded early only when K >= 5.
 *
 * Exact oracle: signed 4x4 minors of lifted rows (x,y,z,x*x+y*y+z*z,1)
 * give the linear form for a fifth point. An independent direct 5x5 Bareiss
 * evaluation checks the oracle and every output witness. With n <= 6 these
 * small-integer determinants and intermediates fit comfortably in int128.
 *
 * Compile: cc -O3 -std=c11 -Wall -Wextra -Werror independent_enum.c -o <out>
 * Run:     <out> --n 3 --target 9 --seconds 30
 * JSON status is found, exhausted, unknown, or inspected. Only exhausted
 * establishes nonexistence; a deadline/node limit/signal returns unknown.
 * Exit codes: found/inspected 0; exhausted 1; invalid input/internal error 2;
 * unknown 124. Maximum requested wall time is 600 seconds, single threaded.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
typedef __int128 i128;
enum { MAX_SIDE = 6, MAX_POINTS = 216, MAX_LAYER = 36, MAX_REPS = 67000 };
typedef struct { u64 key; u64 masks[MAX_SIDE]; } CacheEntry;

static int side = 3, layer_size, point_count, target = 9, symmetry = 1;
static int cache_bits = 18, inspect_only, selftest_only;
static CacheEntry *cache;
static size_t cache_count;
static u64 cache_hits, cache_misses, cache_replacements, nodes, candidates;
static u64 max_nodes, deadline_polls;
static double time_limit = 30.0, start_time, deadline;
static volatile sig_atomic_t signaled;
static int stopped, found, witness_size, witness[MAX_POINTS];
static int placed[MAX_POINTS], placed_count;
static u64 layer_masks[MAX_SIDE], all_layer;
static u64 reps[MAX_REPS];
static int rep_count, reps_done, current_rep = -1;
static int rep_sizes[5];

static void fail(const char *message) {
    fprintf(stderr, "error: %s\n", message);
    exit(2);
}

static double now_seconds(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts)) fail("clock_gettime failed");
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static void signal_handler(int number) { signaled = number; }

static int expired(void) {
    if (stopped) return 1;
    if (signaled || (max_nodes && nodes >= max_nodes)) stopped = 1;
    /* Poll time even when every subset fails before making a DFS node. */
    if (((++deadline_polls & 255) == 0) && now_seconds() >= deadline) stopped = 1;
    return stopped;
}

static int point(int x, int y, int z) { return x + side*y + layer_size*z; }

static void lifted_row(int v, i128 out[5]) {
    int x = v % side, y = (v / side) % side, z = v / layer_size;
    out[0] = x; out[1] = y; out[2] = z;
    out[3] = x*x + y*y + z*z; out[4] = 1;
}

static i128 determinant(i128 matrix[5][5], int size) {
    i128 previous = 1;
    int sign = 1;
    for (int k = 0; k < size-1; ++k) {
        int pivot = k;
        while (pivot < size && matrix[pivot][k] == 0) ++pivot;
        if (pivot == size) return 0;
        if (pivot != k) {
            for (int j = k; j < size; ++j) {
                i128 tmp = matrix[k][j];
                matrix[k][j] = matrix[pivot][j]; matrix[pivot][j] = tmp;
            }
            sign = -sign;
        }
        for (int i = k+1; i < size; ++i) {
            for (int j = k+1; j < size; ++j) {
                i128 numerator = matrix[i][j]*matrix[k][k] - matrix[i][k]*matrix[k][j];
                if (numerator % previous) fail("non-exact Bareiss division");
                matrix[i][j] = numerator / previous;
            }
        }
        previous = matrix[k][k];
    }
    return sign * matrix[size-1][size-1];
}

static int degenerate_five(const int ids[5]) {
    i128 matrix[5][5];
    for (int i = 0; i < 5; ++i) lifted_row(ids[i], matrix[i]);
    return determinant(matrix, 5) == 0;
}

static void locus(const int ids[4], i128 coefficients[5]) {
    i128 rows[4][5];
    for (int i = 0; i < 4; ++i) lifted_row(ids[i], rows[i]);
    for (int omitted = 0; omitted < 5; ++omitted) {
        i128 minor[5][5] = {{0}};
        for (int i = 0; i < 4; ++i) {
            int column = 0;
            for (int j = 0; j < 5; ++j)
                if (j != omitted) minor[i][column++] = rows[i][j];
        }
        coefficients[omitted] = (omitted & 1 ? -1 : 1) * determinant(minor, 4);
    }
}

static int on_locus(const i128 coefficients[5], int v) {
    i128 row[5], value = 0;
    lifted_row(v, row);
    for (int i = 0; i < 5; ++i) value += coefficients[i] * row[i];
    return value == 0;
}

static void sort_four(int ids[4]) {
    for (int i = 1; i < 4; ++i) {
        int value = ids[i], j = i;
        while (j && ids[j-1] > value) { ids[j] = ids[j-1]; --j; }
        ids[j] = value;
    }
}

static const u64 *forbidden(const int input[4]) {
    int ids[4]; memcpy(ids, input, sizeof ids); sort_four(ids);
    u64 key = 0;
    for (int i = 0; i < 4; ++i) key |= (u64)(unsigned)ids[i] << (8*i);
    ++key; /* zero denotes an unused slot */
    u64 hash = key * UINT64_C(0x9e3779b97f4a7c15);
    hash ^= hash >> 29; hash *= UINT64_C(0xbf58476d1ce4e5b9);
    CacheEntry *entry = &cache[hash & (cache_count-1)];
    if (entry->key == key) { ++cache_hits; return entry->masks; }
    ++cache_misses; if (entry->key) ++cache_replacements;
    entry->key = key;
    i128 coefficients[5]; locus(ids, coefficients);
    /* If all cofactors vanish, on_locus is true for EVERY grid point.
     * Returning the empty mask here was a bug in the old experiment. */
    for (int z = 0; z < side; ++z) {
        u64 mask = 0;
        for (int i = 0; i < layer_size; ++i)
            if (on_locus(coefficients, z*layer_size+i)) mask |= UINT64_C(1) << i;
        entry->masks[z] = mask;
    }
    return entry->masks;
}

/* Call once on [0,...,r-1] after processing it. r=0 has one combination. */
static int next_combination(int *indices, int r, int count) {
    int j = r-1;
    while (j >= 0 && indices[j] == count-r+j) --j;
    if (j < 0) return 0;
    ++indices[j];
    for (int k = j+1; k < r; ++k) indices[k] = indices[k-1]+1;
    return 1;
}

static int transformed_position(int pos, int operation) {
    int x = pos % side, y = pos / side;
    if (operation & 1) { int tmp = x; x = y; y = tmp; }
    for (int r = 0; r < operation/2; ++r) {
        int tmp = x; x = y; y = side-1-tmp;
    }
    return x + side*y;
}

static u64 canonical_mask(u64 mask) {
    u64 best = mask;
    if (!symmetry) return best;
    for (int op = 1; op < 8; ++op) {
        u64 image = 0, remaining = mask;
        while (remaining) {
            int p = __builtin_ctzll(remaining); remaining &= remaining-1;
            image |= UINT64_C(1) << transformed_position(p, op);
        }
        if (image < best) best = image;
    }
    return best;
}

static int compare_masks(const void *aa, const void *bb) {
    u64 a = *(const u64 *)aa, b = *(const u64 *)bb;
    return (a > b) - (a < b);
}

static int extendable_four(const int ids[4]) {
    i128 coefficients[5]; locus(ids, coefficients);
    for (int i = 0; i < 5; ++i) if (coefficients[i]) return 1;
    return 0;
}

static void build_representatives(void) {
    for (int size = 0; size <= 4 && size <= layer_size; ++size) {
        int ids[4] = {0, 1, 2, 3};
        do {
            if (target >= 5 && size == 4 && !extendable_four(ids)) continue;
            u64 mask = 0;
            for (int i = 0; i < size; ++i) mask |= UINT64_C(1) << ids[i];
            if (rep_count >= MAX_REPS) fail("representative buffer capacity exceeded");
            reps[rep_count++] = canonical_mask(mask);
        } while (next_combination(ids, size, layer_size));
    }
    qsort(reps, (size_t)rep_count, sizeof reps[0], compare_masks);
    int kept = 0;
    for (int i = 0; i < rep_count; ++i)
        if (i == 0 || reps[i] != reps[i-1]) reps[kept++] = reps[i];
    rep_count = kept;
    for (int i = 0; i < rep_count; ++i) ++rep_sizes[__builtin_popcountll(reps[i])];
}

static int valid_set(const int *ids, int count) {
    for (int a = 0; a < count; ++a) for (int b = a+1; b < count; ++b)
    for (int c = b+1; c < count; ++c) for (int d = c+1; d < count; ++d)
    for (int e = d+1; e < count; ++e) {
        int five[5] = {ids[a], ids[b], ids[c], ids[d], ids[e]};
        if (degenerate_five(five)) return 0;
    }
    return 1;
}

/* Check new-point multiplicities 2,3,4 directly. Multiplicity 1 has already
 * been removed by forbidden masks; >=5 new points are never proposed. */
static int subset_ok(const int *fresh, int count) {
    for (int i = 1; i < count; ++i) {
        for (int j = 0; j < i; ++j)
            for (int a = 0; a < placed_count; ++a)
            for (int b = a+1; b < placed_count; ++b)
            for (int c = b+1; c < placed_count; ++c) {
                int five[5] = {fresh[j],fresh[i],placed[a],placed[b],placed[c]};
                if (degenerate_five(five)) return 0;
            }
        for (int j = 0; j < i; ++j) for (int k = j+1; k < i; ++k)
            for (int a = 0; a < placed_count; ++a)
            for (int b = a+1; b < placed_count; ++b) {
                int five[5] = {fresh[j],fresh[k],fresh[i],placed[a],placed[b]};
                if (degenerate_five(five)) return 0;
            }
        for (int j = 0; j < i; ++j) for (int k = j+1; k < i; ++k)
        for (int l = k+1; l < i; ++l)
            for (int a = 0; a < placed_count; ++a) {
                int five[5] = {fresh[j],fresh[k],fresh[l],fresh[i],placed[a]};
                if (degenerate_five(five)) return 0;
            }
    }
    return 1;
}

static void record_solution(void) {
    if (placed_count != target || !valid_set(placed, placed_count))
        fail("output witness failed independent full 5-subset check");
    found = 1; witness_size = placed_count;
    memcpy(witness, placed, sizeof placed[0] * (size_t)placed_count);
}

static void dfs(int layer, int first_size) {
    if (found || expired()) return;
    ++nodes;
    if (placed_count == target) { record_solution(); return; }
    if (layer == side) return;

    int maximum = layer_size < 4 ? layer_size : 4;
    int end_maximum = symmetry ? first_size : maximum;
    int crude_capacity = maximum*(side-1-layer) + end_maximum;
    if (placed_count + crude_capacity < target) return;

    u64 blocked[MAX_SIDE] = {0};
    for (int a = 0; a < placed_count; ++a) for (int b = a+1; b < placed_count; ++b)
    for (int c = b+1; c < placed_count; ++c) for (int d = c+1; d < placed_count; ++d) {
        int four[4] = {placed[a],placed[b],placed[c],placed[d]};
        const u64 *mask = forbidden(four);
        for (int k = layer; k < side; ++k) blocked[k] |= mask[k];
    }
    int capacity[MAX_SIDE] = {0}, capacity_sum = 0;
    for (int k = layer; k < side; ++k) {
        int available = __builtin_popcountll(all_layer & ~blocked[k]);
        int cap = k == side-1 ? end_maximum : maximum;
        capacity[k] = available < cap ? available : cap;
        capacity_sum += capacity[k];
    }
    if (placed_count + capacity_sum < target) return;
    int min_size = target - placed_count - (capacity_sum-capacity[layer]);
    if (min_size < 0) min_size = 0;
    int max_size = target-placed_count;
    if (max_size > capacity[layer]) max_size = capacity[layer];

    int positions[MAX_LAYER], available_count = 0;
    for (int i = 0; i < layer_size; ++i)
        if (!(blocked[layer] & (UINT64_C(1) << i))) positions[available_count++] = i;
    for (int size = min_size; size <= max_size && !found; ++size) {
        int indices[4] = {0,1,2,3};
        do {
            if (expired()) return;
            ++candidates;
            int fresh[4]; u64 mask = 0;
            for (int i = 0; i < size; ++i) {
                int pos = positions[indices[i]];
                fresh[i] = layer*layer_size + pos; mask |= UINT64_C(1) << pos;
            }
            if (target >= 5 && size == 4 && !extendable_four(fresh)) continue;
            if (!subset_ok(fresh, size)) continue;
            int previous_count = placed_count;
            for (int i = 0; i < size; ++i) placed[placed_count++] = fresh[i];
            layer_masks[layer] = mask;
            dfs(layer+1, first_size);
            placed_count = previous_count; layer_masks[layer] = 0;
            if (found || stopped) return;
        } while (next_combination(indices, size, available_count));
    }
}

static u64 random_state = UINT64_C(0x3141592653589793);
static unsigned random_bounded(unsigned bound) {
    random_state ^= random_state << 13; random_state ^= random_state >> 7;
    random_state ^= random_state << 17;
    return (unsigned)(random_state % bound);
}

static int oracle_selftest(void) {
    for (int count = 0; count <= 10; ++count) for (int size = 0; size <= 4 && size <= count; ++size) {
        int indices[4] = {0,1,2,3}; u64 seen = 0, expected = 1;
        for (int i = 1; i <= size; ++i) expected = expected*(unsigned)(count-i+1)/(unsigned)i;
        do {
            ++seen;
            if (seen > expected) fail("combination iterator did not terminate");
            for (int i = 0; i < size; ++i)
                if (indices[i] >= count || (i && indices[i] <= indices[i-1]))
                    fail("invalid combination");
        } while (next_combination(indices, size, count));
        if (seen != expected) fail("combination iterator omitted a subset");
    }
    if (point_count < 4) return 0;
    int checked = 0;
    for (int test = 0; test < 200; ++test) {
        int ids[4], count = 0;
        while (count < 4) {
            int v = (int)random_bounded((unsigned)point_count), repeated = 0;
            for (int i = 0; i < count; ++i) if (ids[i] == v) repeated = 1;
            if (!repeated) ids[count++] = v;
        }
        const u64 *masks = forbidden(ids);
        for (int v = 0; v < point_count; ++v) {
            int five[5] = {ids[0],ids[1],ids[2],ids[3],v};
            int masked = (int)((masks[v/layer_size] >> (v%layer_size)) & 1);
            if (masked != degenerate_five(five)) fail("cached locus disagrees with direct determinant");
            ++checked;
        }
    }
    if (side >= 2) {
        int circle[4] = {point(0,0,0),point(1,0,0),point(0,1,0),point(1,1,0)};
        const u64 *masks = forbidden(circle);
        for (int z = 0; z < side; ++z)
            if (masks[z] != all_layer) fail("rank-deficient quad did not forbid every fifth point");
    }
    return checked;
}

static u64 parse_integer(const char *text, u64 maximum) {
    if (!*text || *text == '-') fail("invalid nonnegative integer");
    char *end; errno = 0; unsigned long long value = strtoull(text, &end, 10);
    if (errno || *end || value > maximum) fail("integer argument out of range");
    return (u64)value;
}

static void usage(const char *program) {
    printf("Usage: %s --n 1..6 --target 0..216 [--seconds 0.01..600]\n"
           "       [--cache-bits 0..20] [--max-nodes N] [--no-symmetry]\n"
           "       [--inspect | --selftest]\n", program);
}

int main(int argc, char **argv) {
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--help")) { usage(argv[0]); return 0; }
        if (!strcmp(argv[i], "--no-symmetry")) { symmetry = 0; continue; }
        if (!strcmp(argv[i], "--inspect")) { inspect_only = 1; continue; }
        if (!strcmp(argv[i], "--selftest")) { selftest_only = 1; continue; }
        if (i+1 >= argc) fail("missing argument value");
        const char *option = argv[i], *value = argv[++i];
        if (!strcmp(option, "--n")) side = (int)parse_integer(value, MAX_SIDE);
        else if (!strcmp(option, "--target")) target = (int)parse_integer(value, MAX_POINTS);
        else if (!strcmp(option, "--cache-bits")) cache_bits = (int)parse_integer(value, 20);
        else if (!strcmp(option, "--max-nodes")) max_nodes = parse_integer(value, UINT64_MAX);
        else if (!strcmp(option, "--seconds")) {
            char *end; errno = 0; time_limit = strtod(value, &end);
            if (errno || *end || !(time_limit >= 0.01 && time_limit <= 600)) fail("seconds must be between 0.01 and 600");
        } else fail("unknown option");
    }
    if (side < 1) fail("n must be between 1 and 6");
    layer_size = side*side; point_count = layer_size*side;
    all_layer = (UINT64_C(1) << layer_size)-1;
    cache_count = (size_t)1 << cache_bits;
    cache = calloc(cache_count, sizeof *cache);
    if (!cache) fail("cache allocation failed");
    signal(SIGINT, signal_handler); signal(SIGTERM, signal_handler);
    start_time = now_seconds(); deadline = start_time+time_limit;
    int oracle_checks = oracle_selftest();
    build_representatives();
    cache_hits = cache_misses = cache_replacements = 0;

    if (!inspect_only && !selftest_only) {
        for (current_rep = 0; current_rep < rep_count && !found; ++current_rep) {
            if (now_seconds() >= deadline || signaled) { stopped = 1; break; }
            placed_count = 0; u64 mask = reps[current_rep];
            int first_size = __builtin_popcountll(mask);
            if (first_size > target) { ++reps_done; continue; }
            memset(layer_masks, 0, sizeof layer_masks); layer_masks[0] = mask;
            while (mask) {
                placed[placed_count++] = __builtin_ctzll(mask); mask &= mask-1;
            }
            dfs(1, first_size);
            if (stopped || found) break;
            ++reps_done;
        }
    }
    const char *status = inspect_only || selftest_only ? "inspected" : found ? "found" : stopped ? "unknown" : "exhausted";
    printf("{\"status\":\"%s\",\"n\":%d,\"target\":%d,\"complete\":%s,"
           "\"symmetry\":%s,\"orbits_total\":%d,\"orbits_completed\":%d,"
           "\"orbit_sizes\":[%d,%d,%d,%d,%d],\"nodes\":%" PRIu64 ","
           "\"candidates\":%" PRIu64 ",\"cache_entries\":%zu,\"cache_bytes\":%zu,"
           "\"cache_hits\":%" PRIu64 ",\"cache_misses\":%" PRIu64 ","
           "\"cache_replacements\":%" PRIu64 ",\"oracle_checks\":%d,"
           "\"seconds\":%.6f,\"points\":[",
           status, side, target, !strcmp(status,"exhausted") ? "true" : "false",
           symmetry ? "true" : "false", rep_count, reps_done,
           rep_sizes[0],rep_sizes[1],rep_sizes[2],rep_sizes[3],rep_sizes[4], nodes,
           candidates, cache_count, cache_count*sizeof *cache, cache_hits, cache_misses,
           cache_replacements, oracle_checks, now_seconds()-start_time);
    for (int i = 0; i < witness_size; ++i) {
        int v = witness[i];
        printf("%s[%d,%d,%d]", i ? "," : "", v%side, (v/side)%side, v/layer_size);
    }
    printf("]}\n");
    free(cache);
    return !strcmp(status,"exhausted") ? 1 : stopped ? 124 : 0;
}
