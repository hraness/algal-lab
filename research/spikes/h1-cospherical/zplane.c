/* zplane.c - Monte Carlo for Z_plane(n)/n^11: draw 5 uniformly random DISTINCT
 * grid points of [0,n)^3, test coplanarity (rank of the four difference vectors
 * <= 2, i.e. all four 3x3 minors vanish).  Reports coplanar count.
 * P(coplanar) = Z_plane / C(n^3,5) ~ 120 * Z_plane / n^15,
 * so Z_plane/n^11 ~ (cop/m) * n^4 / 120 * (1 + O(1/n)).
 * Usage: zplane n samples seed
 */
#include <stdio.h>
#include <stdlib.h>
typedef long long ll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static ll det3(ll a[3], ll b[3], ll c[3]){
    return a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]);
}
int main(int argc, char **argv){
    int n = atoi(argv[1]); long samples = atol(argv[2]); rng_s = strtoull(argv[3],0,10)*2654435761ULL+1;
    long cop = 0, redo = 0;
    for (long s=0; s<samples; s++){
        ll P[5][3];
        for (int i=0;i<5;i++) for(int j=0;j<3;j++) P[i][j]=(ll)(rnd()%(unsigned)n);
        /* distinctness: any coincidence -> resample (uniform measure on 5-subsets) */
        int dup = 0;
        for (int i=0;i<5 && !dup;i++) for(int j=i+1;j<5;j++)
            if (P[i][0]==P[j][0] && P[i][1]==P[j][1] && P[i][2]==P[j][2]){ dup=1; break; }
        if (dup){ redo++; s--; continue; }
        ll d[4][3];
        for (int i=0;i<4;i++) for(int j=0;j<3;j++) d[i][j]=P[i+1][j]-P[0][j];
        /* rank <= 2 iff all four 3x3 minors vanish; early exit */
        if (det3(d[0],d[1],d[2])) continue;
        if (det3(d[0],d[1],d[3])) continue;
        if (det3(d[0],d[2],d[3])) continue;
        if (det3(d[1],d[2],d[3])) continue;
        cop++;
    }
    printf("n=%d samples=%ld coplanar=%ld redo=%ld P=%.4e Z/n^11~%.5f\n",
        n, samples, cop, redo, (double)cop/samples,
        (double)cop/samples * ((double)n*n)*((double)n*n) / 120.0);
    return 0;
}
