/* circ4.c - Monte Carlo for the number of CONCYCLIC 4-subsets of [0,n)^3.
 * Four distinct points are concyclic iff coplanar and the equidistant system
 *   d_i . c = R_i/2,   d_i = p_{i+1}-p_1,  R_i = |p_{i+1}|^2-|p_1|^2  (i=1,2,3)
 * is consistent.  For non-collinear coplanar points rank(A)=2 and consistency is
 * nu . R = 0 where nu = d_i x d_j for the independent pair (left kernel of A).
 * (Four collinear points are coplanar but never concyclic.)
 * Usage: circ4 n samples seed
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef long long ll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static ll dot(ll a[3], ll b[3]){ return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
static void cross(ll a[3], ll b[3], ll o[3]){ o[0]=a[1]*b[2]-a[2]*b[1]; o[1]=a[2]*b[0]-a[0]*b[2]; o[2]=a[0]*b[1]-a[1]*b[0]; }
static ll det3(ll a[3], ll b[3], ll c[3]){ return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]); }
int main(int argc, char **argv){
    int n = atoi(argv[1]); long samples = atol(argv[2]); rng_s = strtoull(argv[3],0,10)*2654435761ULL+1;
    long copl=0, circ=0, redo=0, coll=0;
    for (long s=0;s<samples;s++){
        ll P[4][3];
        for (int i=0;i<4;i++) for(int j=0;j<3;j++) P[i][j]=(ll)(rnd()%(unsigned)n);
        int dup=0;
        for (int i=0;i<4 && !dup;i++) for(int j=i+1;j<4;j++)
            if (P[i][0]==P[j][0] && P[i][1]==P[j][1] && P[i][2]==P[j][2]){ dup=1; break; }
        if (dup){ redo++; s--; continue; }
        ll d[3][3], R[3];
        for (int i=0;i<3;i++){ for(int j=0;j<3;j++) d[i][j]=P[i+1][j]-P[0][j];
            R[i]=P[i+1][0]*P[i+1][0]+P[i+1][1]*P[i+1][1]+P[i+1][2]*P[i+1][2]-P[0][0]*P[0][0]-P[0][1]*P[0][1]-P[0][2]*P[0][2]; }
        /* coplanarity first: det(d0,d1,d2) */
        ll cp0 = det3(d[0],d[1],d[2]);
        if (cp0 != 0) continue;                   /* non-coplanar */
        copl++;
        /* concyclic iff equidistant system A c = R/2 consistent; rank(A)=2 for
           non-collinear coplanar; consistency iff nu.R=0 for nu spanning
           ker(A^T) = orthogonal to COLUMNS of A. */
        ll w[3][3]; for (int i=0;i<3;i++) for(int j=0;j<3;j++) w[j][i]=d[i][j];
        ll nu[3] = {0,0,0};
        cross(w[0],w[1],nu);
        if (!(nu[0]||nu[1]||nu[2])) cross(w[0],w[2],nu);
        if (!(nu[0]||nu[1]||nu[2])) cross(w[1],w[2],nu);
        if (!(nu[0]||nu[1]||nu[2])){ coll++; continue; }  /* 4 collinear */
        if (dot(nu,R)==0) circ++;                          /* consistent -> concyclic */
    }
    double c4 = (double)n*n*n*(n*n*n-1.0)*(n*n*n-2.0)*(n*n*n-3.0)/24.0;
    printf("n=%d samples=%ld coplanar4=%ld concyclic4=%ld collinear4=%ld redo=%ld\n", n, samples, copl, circ, coll, redo);
    printf("  P(coplanar4)=%.4e P(concyc4)=%.4e Z_plane4~%.3e N_circ4~%.3e N_circ4/n^8=%.5f Z_circ/n^11~%.5f\n",
        (double)copl/samples, (double)circ/samples,
        (double)copl/samples*c4, (double)circ/samples*c4,
        (double)circ/samples*c4/((double)n*n*n*n*n*n*n*n),
        (double)circ/samples*c4*(double)n*n*n/((double)pow(n,11)));
    return 0;
}
