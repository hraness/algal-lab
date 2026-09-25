/* mc_extra.c - Monte Carlo estimate of E(n) = mean number of further grid points of
 * {0..n-1}^3 on the circumsphere of four uniformly random grid points in general position
 * (coplanar quadruples are resampled).  Exact integer arithmetic (__int128).
 *
 * The circumsphere of A,B,C,D: with M the 3x3 matrix of rows 2(B-A),2(C-A),2(D-A) and
 * rhs |B|^2-|A|^2 etc., det = det(M) != 0 and the center is c = adj(M) rhs / det.  Then
 * u := det * c is an integer vector, and a grid point E lies on the sphere iff
 * |det*E - u|^2 = |det*A - u|^2 =: T.  For each (x, y) this is a quadratic in z.
 *
 * Also reports the split by whether the circumsphere denominator is small (|det| <= 2n).
 * Usage: mc_extra n samples seed
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef __int128 i128; typedef long long ll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static ll isqrt_ll(i128 t){ if (t < 0) return -1; long double r = sqrtl((long double)t); ll s=(ll)r; while ((i128)s*s > t) s--; while ((i128)(s+1)*(s+1) <= t) s++; return ((i128)s*s==t)? s : -1; }
int main(int argc, char **argv){
    int n = atoi(argv[1]); long samples = atol(argv[2]); rng_s = strtoull(argv[3],0,10)*2654435761ULL+1;
    double sum=0, sum_small=0; long cnt_small=0; long hist[8]={0};
    for (long s=0; s<samples; s++){
        ll P[4][3]; for (int i=0;i<4;i++) for(int j=0;j<3;j++) P[i][j]=rnd()%n;
        ll Mx[3][3], rhs[3];
        for (int i=0;i<3;i++){ for(int j=0;j<3;j++) Mx[i][j]=2*(P[i+1][j]-P[0][j]);
            rhs[i]=(P[i+1][0]*P[i+1][0]+P[i+1][1]*P[i+1][1]+P[i+1][2]*P[i+1][2])-(P[0][0]*P[0][0]+P[0][1]*P[0][1]+P[0][2]*P[0][2]); }
        i128 det = (i128)Mx[0][0]*(Mx[1][1]*Mx[2][2]-Mx[1][2]*Mx[2][1]) - (i128)Mx[0][1]*(Mx[1][0]*Mx[2][2]-Mx[1][2]*Mx[2][0]) + (i128)Mx[0][2]*(Mx[1][0]*Mx[2][1]-Mx[1][1]*Mx[2][0]);
        if (det==0){ s--; continue; }
        if (det<0){ det=-det; for(int i=0;i<3;i++){ for(int j=0;j<3;j++) Mx[i][j]=-Mx[i][j]; rhs[i]=-rhs[i]; } }
        /* u = adj(M) * rhs  (so that c = u/det) */
        i128 u[3];
        i128 adj[3][3] = {{(i128)Mx[1][1]*Mx[2][2]-(i128)Mx[1][2]*Mx[2][1], -((i128)Mx[0][1]*Mx[2][2]-(i128)Mx[0][2]*Mx[2][1]), (i128)Mx[0][1]*Mx[1][2]-(i128)Mx[0][2]*Mx[1][1]},
                          {-((i128)Mx[1][0]*Mx[2][2]-(i128)Mx[1][2]*Mx[2][0]), (i128)Mx[0][0]*Mx[2][2]-(i128)Mx[0][2]*Mx[2][0], -((i128)Mx[0][0]*Mx[1][2]-(i128)Mx[0][2]*Mx[1][0])},
                          {(i128)Mx[1][0]*Mx[2][1]-(i128)Mx[1][1]*Mx[2][0], -((i128)Mx[0][0]*Mx[2][1]-(i128)Mx[0][1]*Mx[2][0]), (i128)Mx[0][0]*Mx[1][1]-(i128)Mx[0][1]*Mx[1][0]}};
        for (int i=0;i<3;i++) u[i]=adj[i][0]*rhs[0]+adj[i][1]*rhs[1]+adj[i][2]*rhs[2];
        i128 T=0; for(int j=0;j<3;j++){ i128 d=det*P[0][j]-u[j]; T+=d*d; }
        long extra=0;
        for (int x=0;x<n;x++){ i128 dx=det*x-u[0]; i128 rx=T-dx*dx; if (rx<0) continue;
            for (int y=0;y<n;y++){ i128 dy=det*y-u[1]; i128 r=rx-dy*dy; if (r<0) continue;
                ll sq=isqrt_ll(r); if (sq<0) continue;
                for (int sgn=-1; sgn<=1; sgn+=2){ i128 num=u[2]+sgn*(i128)sq; if (sgn==1 && sq==0) break;
                    if (num % det) continue; i128 z=num/det; if (z<0||z>=n) continue; extra++; } } }
        extra -= 4; sum += extra; if (extra>7) extra=7; hist[extra]++;
        if (det <= 2*n) { sum_small += extra; cnt_small++; }
    }
    printf("n=%d samples=%ld mean_extra=%.5f  P(extra>=1)=%.5f  hist0..7=", n, samples, sum/samples, 1.0-(double)hist[0]/samples);
    for (int i=0;i<8;i++) printf("%ld ", hist[i]); printf(" small_denom_frac=%.4f\n", (double)cnt_small/samples);
    return 0;
}
