/* esamp.c - Monte Carlo for E(n) = expected number of further grid points of
 * [0,n)^3 on the circumsphere of four uniformly random DISTINCT NON-COPLANAR
 * grid points.  Exact integer arithmetic (__int128).
 *
 * Circumsphere of A,B,C,D: with M the 3x3 matrix of rows 2(B-A),2(C-A),2(D-A)
 * and rhs |B|^2-|A|^2 etc., det = det(M) != 0 and center c = adj(M) rhs / det.
 * Put u := adj(M) rhs (integer), T := |det*A - u|^2.  Grid point E is on the
 * sphere iff |det*E - u|^2 = T.
 *
 * Primitive integer equation of the sphere (canonical identity):
 *   det^2|p|^2 - 2 det u.p + (|u|^2 - T) = 0, divided by
 *   g = gcd(det^2, 2 det u_1, 2 det u_2, 2 det u_3, |u|^2 - T)
 * gives a|p|^2 + b.p + c = 0 with gcd(a,b,c) = 1, a > 0.
 *
 * Output (text):
 *   <prefix>.spheres.tsv : a b1 b2 b3 c det k            (one line per accepted sample)
 *   <prefix>.extras.tsv  : id tot | base x4 | pt x tot   (only when tot >= 5, i.e. k >= 1)
 * stdout: summary line.
 *
 * Usage: esamp n samples seed prefix
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef __int128 i128; typedef long long ll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static i128 igcd(i128 a, i128 b){ if(a<0)a=-a; if(b<0)b=-b; while(b){i128 t=a%b;a=b;b=t;} return a; }
static ll isqrt_i128(i128 t){ if(t<=0) return (t==0)?0:-1; long double r=sqrtl((long double)t); ll s=(ll)r; while((i128)s*s>t)s--; while((i128)(s+1)*(s+1)<=t)s++; return s; }
static i128 floordiv(i128 a, i128 d){ /* d>0 */ i128 q=a/d, r=a%d; if(r<0) q--; return q; }
static i128 ceildiv(i128 a, i128 d){ i128 q=a/d, r=a%d; if(r>0) q++; return q; }
static void pr128(FILE*f, i128 v){ if(v<0){fputc('-',f);v=-v;} char buf[64]; int i=63; buf[i]=0; do{buf[--i]='0'+(int)(v%10);v/=10;}while(v); fputs(buf+i,f); }

#define MAXSTORE 4096   /* max sphere points written to extras file (count still exact) */

int main(int argc, char **argv){
    int n = atoi(argv[1]); long samples = atol(argv[2]); rng_s = strtoull(argv[3],0,10)*2654435761ULL+1;
    char path[1024];
    snprintf(path, sizeof path, "%s.spheres.tsv", argv[4]); FILE *fs = fopen(path, "w");
    snprintf(path, sizeof path, "%s.extras.tsv", argv[4]); FILE *fe = fopen(path, "w");
    if(!fs || !fe){ fprintf(stderr, "cannot open output\n"); return 1; }
    fprintf(fs, "# a b1 b2 b3 c det k\n");
    fprintf(fe, "# id tot | base(12) | pts(3*tot)\n");

    double sum = 0, sumsq = 0; long degen = 0, accepted = 0;
    long hist[16] = {0}; long hibig = 0; long maxk = 0;
    int *px = malloc(sizeof(int)*MAXSTORE), *py = malloc(sizeof(int)*MAXSTORE), *pz = malloc(sizeof(int)*MAXSTORE);
    if(!px){ fprintf(stderr,"oom\n"); return 1; }

    for (long s = 0; s < samples; s++){
        ll P[4][3];
        for (int i=0;i<4;i++) for(int j=0;j<3;j++) P[i][j]=(ll)(rnd()%(unsigned)n);
        ll Mx[3][3], rhs[3];
        for (int i=0;i<3;i++){ for(int j=0;j<3;j++) Mx[i][j]=2*(P[i+1][j]-P[0][j]);
            rhs[i]=(P[i+1][0]*P[i+1][0]+P[i+1][1]*P[i+1][1]+P[i+1][2]*P[i+1][2])-(P[0][0]*P[0][0]+P[0][1]*P[0][1]+P[0][2]*P[0][2]); }
        i128 det = (i128)Mx[0][0]*(Mx[1][1]*Mx[2][2]-Mx[1][2]*Mx[2][1]) - (i128)Mx[0][1]*(Mx[1][0]*Mx[2][2]-Mx[1][2]*Mx[2][0]) + (i128)Mx[0][2]*(Mx[1][0]*Mx[2][1]-Mx[1][1]*Mx[2][0]);
        if (det==0){ degen++; s--; continue; }
        if (det<0){ det=-det; for(int i=0;i<3;i++){ for(int j=0;j<3;j++) Mx[i][j]=-Mx[i][j]; rhs[i]=-rhs[i]; } }
        i128 adj[3][3] = {{(i128)Mx[1][1]*Mx[2][2]-(i128)Mx[1][2]*Mx[2][1], -((i128)Mx[0][1]*Mx[2][2]-(i128)Mx[0][2]*Mx[2][1]), (i128)Mx[0][1]*Mx[1][2]-(i128)Mx[0][2]*Mx[1][1]},
                          {-((i128)Mx[1][0]*Mx[2][2]-(i128)Mx[1][2]*Mx[2][0]), (i128)Mx[0][0]*Mx[2][2]-(i128)Mx[0][2]*Mx[2][0], -((i128)Mx[0][0]*Mx[1][2]-(i128)Mx[0][2]*Mx[1][0])},
                          {(i128)Mx[1][0]*Mx[2][1]-(i128)Mx[1][1]*Mx[2][0], -((i128)Mx[0][0]*Mx[2][1]-(i128)Mx[0][1]*Mx[2][0]), (i128)Mx[0][0]*Mx[1][1]-(i128)Mx[0][1]*Mx[1][0]}};
        i128 u[3];
        for (int i=0;i<3;i++) u[i]=adj[i][0]*rhs[0]+adj[i][1]*rhs[1]+adj[i][2]*rhs[2];
        i128 T=0; for(int j=0;j<3;j++){ i128 d=det*P[0][j]-u[j]; T+=d*d; }

        /* primitive equation */
        i128 uu = u[0]*u[0]+u[1]*u[1]+u[2]*u[2];
        i128 g = igcd(det*det, igcd(2*det*u[0], igcd(2*det*u[1], igcd(2*det*u[2], uu - T))));
        i128 a = det*det/g, b0 = -2*det*u[0]/g, b1 = -2*det*u[1]/g, b2 = -2*det*u[2]/g, cc = (uu - T)/g;

        /* count grid points on sphere: |det p - u|^2 = T, x/y range-pruned */
        i128 S = isqrt_i128(T);
        i128 xlo = ceildiv(u[0]-S, det), xhi = floordiv(u[0]+S, det);
        if (xlo<0) xlo=0; if (xhi>=n) xhi=n-1;
        long tot = 0; int nstore = 0;
        for (i128 x=xlo; x<=xhi; x++){
            i128 dx = det*x - u[0]; i128 rx = T - dx*dx; if (rx<0) continue;
            i128 Sy = isqrt_i128(rx);
            i128 ylo = ceildiv(u[1]-Sy, det), yhi = floordiv(u[1]+Sy, det);
            if (ylo<0) ylo=0; if (yhi>=n) yhi=n-1;
            for (i128 y=ylo; y<=yhi; y++){
                i128 dy = det*y - u[1]; i128 r = rx - dy*dy; if (r<0) continue;
                ll sq = isqrt_i128(r); if (sq<0) continue;
                if ((i128)sq*sq != r) continue;
                for (int sgn=-1; sgn<=1; sgn+=2){
                    i128 num = u[2] + sgn*(i128)sq;
                    if (sgn==1 && sq==0) break;
                    if (num % det) continue;
                    i128 z = num/det; if (z<0||z>=n) continue;
                    tot++;
                    if (nstore<MAXSTORE){ px[nstore]=(int)x; py[nstore]=(int)y; pz[nstore]=(int)z; nstore++; }
                }
            }
        }
        long k = tot - 4;
        /* per-sample record */
        pr128(fs,a); fputc(' ',fs); pr128(fs,b0); fputc(' ',fs); pr128(fs,b1); fputc(' ',fs); pr128(fs,b2); fputc(' ',fs); pr128(fs,cc); fputc(' ',fs);
        pr128(fs,det); fprintf(fs," %ld\n", k);
        if (k>=1){
            fprintf(fe, "%ld %ld |", accepted, tot);
            for (int i=0;i<4;i++) fprintf(fe," %lld %lld %lld", P[i][0],P[i][1],P[i][2]);
            fprintf(fe," |");
            for (int i=0;i<nstore;i++) fprintf(fe," %d %d %d", px[i],py[i],pz[i]);
            if (nstore<tot) fprintf(fe," TRUNC(%ld)", tot);
            fputc('\n',fe);
        }
        accepted++;
        sum += k; sumsq += (double)k*k;
        if (k<16) hist[k]++; else hibig++;
        if (k>maxk) maxk = k;
    }
    double mean = sum/accepted, var = sumsq/accepted - mean*mean;
    printf("n=%d samples=%ld accepted=%ld degen=%ld mean_extra=%.6f se=%.6f P(k>=1)=%.6f hist0..15=",
        n, samples, accepted, degen, mean, sqrt(var/accepted), 1.0-(double)hist[0]/accepted);
    for (int i=0;i<16;i++) printf("%ld ", hist[i]);
    printf(" k>=16:%ld maxk=%ld\n", hibig, maxk);
    fclose(fs); fclose(fe);
    free(px); free(py); free(pz);
    return 0;
}
