/* count5.c - exact census of degenerate 5-subsets of a point set in Z^3.
 *
 * A 5-subset is degenerate iff the 5x5 determinant with rows (x,y,z,x^2+y^2+z^2,1)
 * vanishes (five points on a common sphere or plane).  Every 4-subset yields a
 * cofactor vector c in Z^4 with det(4-subset + m) = c . u_m, where u_m is the lifted
 * difference of point m from the first point of the 4-subset.  All arithmetic is
 * exact in int64 (|c . u| <= 216 n^6 < 2^63 for n <= 500).
 *
 * Classification of a degenerate 5-subset:
 *   axis   : all five share one coordinate (coplanar on an axis-parallel plane)
 *   plane  : coplanar, not on an axis plane
 *   sphere : cospherical but not coplanar; sphere_with_concyclic4 counts those that contain
 *            a concyclic (or collinear) quadruple, i.e. a lifted 4-subset of affine rank <= 2
 *
 * Usage: count5 grid N            (all points of {0..N-1}^3)
 *        count5 file PATH         (one "x y z" triple per line)
 * Optional third argument: path to dump the index 5-tuples of sphere-type subsets.
 * Output: one summary line with the counts and the total.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef long long ll;
static int N_PTS;
static int px[70000], py[70000], pz[70000];
static ll pw[70000];
static FILE *dumpf = NULL;  /* optional: dump sphere-type degenerate 5-subsets */

static int coplanar5(int i, int j, int k, int l, int m) {
    int idx[5] = {i, j, k, l, m};
    ll ax = px[i], ay = py[i], az = pz[i];
    ll ux[4], uy[4], uz[4];
    for (int t = 1; t < 5; t++) {
        ux[t-1] = px[idx[t]] - ax; uy[t-1] = py[idx[t]] - ay; uz[t-1] = pz[idx[t]] - az;
    }
    /* rank of the 4 difference vectors <= 2 iff every 3x3 minor vanishes */
    for (int a = 0; a < 4; a++) for (int b = a+1; b < 4; b++) for (int c = b+1; c < 4; c++) {
        ll d = ux[a]*(uy[b]*uz[c]-uz[b]*uy[c]) - uy[a]*(ux[b]*uz[c]-uz[b]*ux[c]) + uz[a]*(ux[b]*uy[c]-uy[b]*ux[c]);
        if (d != 0) return 0;
    }
    return 1;
}
static int axis5(int i, int j, int k, int l, int m) {
    if (px[i]==px[j] && px[i]==px[k] && px[i]==px[l] && px[i]==px[m]) return 1;
    if (py[i]==py[j] && py[i]==py[k] && py[i]==py[l] && py[i]==py[m]) return 1;
    if (pz[i]==pz[j] && pz[i]==pz[k] && pz[i]==pz[l] && pz[i]==pz[m]) return 1;
    return 0;
}


/* lifted affine rank of 4 points <= 2 iff they are concyclic or collinear */
static int conc4(int i, int j, int k, int l) {
    int idx[4] = {i, j, k, l};
    ll u[3][4];
    for (int t = 1; t < 4; t++) {
        u[t-1][0] = px[idx[t]]-px[i]; u[t-1][1] = py[idx[t]]-py[i];
        u[t-1][2] = pz[idx[t]]-pz[i]; u[t-1][3] = pw[idx[t]]-pw[i];
    }
    for (int a = 0; a < 4; a++) for (int b = a+1; b < 4; b++) for (int c = b+1; c < 4; c++) {
        ll d = u[0][a]*(u[1][b]*u[2][c]-u[1][c]*u[2][b]) - u[0][b]*(u[1][a]*u[2][c]-u[1][c]*u[2][a]) + u[0][c]*(u[1][a]*u[2][b]-u[1][b]*u[2][a]);
        if (d != 0) return 0;
    }
    return 1;
}
static int has_conc4(int i, int j, int k, int l, int m) {
    return conc4(i,j,k,l) || conc4(i,j,k,m) || conc4(i,j,l,m) || conc4(i,k,l,m) || conc4(j,k,l,m);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: count5 grid N | count5 file PATH\n"); return 2; }
    if (!strcmp(argv[1], "grid")) {
        int n = atoi(argv[2]); N_PTS = 0;
        for (int x = 0; x < n; x++) for (int y = 0; y < n; y++) for (int z = 0; z < n; z++) {
            px[N_PTS] = x; py[N_PTS] = y; pz[N_PTS] = z; N_PTS++;
        }
    } else {
        FILE *f = fopen(argv[2], "r"); if (!f) { perror("open"); return 2; }
        int x, y, z; N_PTS = 0;
        while (fscanf(f, "%d %d %d", &x, &y, &z) == 3) { px[N_PTS]=x; py[N_PTS]=y; pz[N_PTS]=z; N_PTS++; }
        fclose(f);
    }
    if (argc > 3) dumpf = fopen(argv[3], "w");
    for (int i = 0; i < N_PTS; i++) pw[i] = (ll)px[i]*px[i] + (ll)py[i]*py[i] + (ll)pz[i]*pz[i];
    ll n_axis = 0, n_plane = 0, n_sphere = 0, n_sphere_c = 0;
    int n = N_PTS;
    for (int i = 0; i < n; i++) {
        for (int j = i+1; j < n; j++) {
            ll a0 = px[j]-px[i], a1 = py[j]-py[i], a2 = pz[j]-pz[i], a3 = pw[j]-pw[i];
            for (int k = j+1; k < n; k++) {
                ll b0 = px[k]-px[i], b1 = py[k]-py[i], b2 = pz[k]-pz[i], b3 = pw[k]-pw[i];
                /* 2x2 minors of rows a,b */
                ll m01 = a0*b1-a1*b0, m02 = a0*b2-a2*b0, m03 = a0*b3-a3*b0;
                ll m12 = a1*b2-a2*b1, m13 = a1*b3-a3*b1, m23 = a2*b3-a3*b2;
                for (int l = k+1; l < n; l++) {
                    ll c0 = px[l]-px[i], c1 = py[l]-py[i], c2 = pz[l]-pz[i], c3 = pw[l]-pw[i];
                    /* cofactor vector: det[a;b;c;u] = u0*C0 + u1*C1 + u2*C2 + u3*C3 */
                    ll C0 = -(c1*m23 - c2*m13 + c3*m12);
                    ll C1 =  (c0*m23 - c2*m03 + c3*m02);
                    ll C2 = -(c0*m13 - c1*m03 + c3*m01);
                    ll C3 =  (c0*m12 - c1*m02 + c2*m01);
                    for (int m = l+1; m < n; m++) {
                        ll d = C0*(px[m]-px[i]) + C1*(py[m]-py[i]) + C2*(pz[m]-pz[i]) + C3*(pw[m]-pw[i]);
                        if (d == 0) {
                            if (axis5(i,j,k,l,m)) n_axis++;
                            else if (coplanar5(i,j,k,l,m)) n_plane++;
                            else { n_sphere++; if (has_conc4(i,j,k,l,m)) n_sphere_c++; if (dumpf) fprintf(dumpf, "%d %d %d %d %d\n", i, j, k, l, m); }
                        }
                    }
                }
            }
        }
    }
    printf("points=%d axis=%lld plane=%lld sphere=%lld sphere_with_concyclic4=%lld degenerate=%lld\n", n, n_axis, n_plane, n_sphere, n_sphere_c, n_axis+n_plane+n_sphere);
    return 0;
}
