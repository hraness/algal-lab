/* quad.c - count concyclic 4-subsets of [0,n)^3, split symmetric vs asymmetric.
 * Symmetric = has a reflection axis in its plane:
 *   - isosceles trapezoid: some perfect matching has equal lengths
 *   - kite: some chord is a diameter and the other two points are mirror images
 * Concyclic test: coplanar (det=0) AND consistency nu.R=0 as in circ4.c.
 * Usage: quad n [samples]   (samples=0 -> exact enumeration)
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef long long ll;
typedef __int128 lll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static ll det3(const ll a[3], const ll b[3], const ll c[3]){
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);
}
static ll d2(const ll a[3], const ll b[3]){
    ll x=a[0]-b[0],y=a[1]-b[1],z=a[2]-b[2]; return x*x+y*y+z*z;
}
/* concyclic? assumes 4 distinct points */
static int concyclic(const ll P[4][3]){
    ll d[3][3], R[3];
    for(int i=0;i<3;i++){ for(int j=0;j<3;j++) d[i][j]=P[i+1][j]-P[0][j];
        R[i]=P[i+1][0]*P[i+1][0]+P[i+1][1]*P[i+1][1]+P[i+1][2]*P[i+1][2]
           -P[0][0]*P[0][0]-P[0][1]*P[0][1]-P[0][2]*P[0][2]; }
    if (det3(d[0],d[1],d[2])!=0) return 0;
    /* left kernel of d (rows): nu with sum nu_i d_i = 0 */
    /* columns of d as vectors w0,w1,w2; kernel vector = w_a x w_b for an
       independent pair of ROWS... use cross of two row-differences? Standard:
       nu = d_i x d_j? no: kernel of the 3x3 with rows d_i is det-related.
       circ4.c uses nu = cross of COLUMNS w[0],w[1]. Replicate that. */
    ll w[3][3], nu[3];
    for(int i=0;i<3;i++) for(int j=0;j<3;j++) w[j][i]=d[i][j];
    nu[0]=w[0][1]*w[1][2]-w[0][2]*w[1][1];
    nu[1]=w[0][2]*w[1][0]-w[0][0]*w[1][2];
    nu[2]=w[0][0]*w[1][1]-w[0][1]*w[1][0];
    if (!(nu[0]||nu[1]||nu[2])){
        nu[0]=w[0][1]*w[2][2]-w[0][2]*w[2][1];
        nu[1]=w[0][2]*w[2][0]-w[0][0]*w[2][2];
        nu[2]=w[0][0]*w[2][1]-w[0][1]*w[2][0];
    }
    if (!(nu[0]||nu[1]||nu[2])){
        nu[0]=w[1][1]*w[2][2]-w[1][2]*w[2][1];
        nu[1]=w[1][2]*w[2][0]-w[1][0]*w[2][2];
        nu[2]=w[1][0]*w[2][1]-w[1][1]*w[2][0];
    }
    if (!(nu[0]||nu[1]||nu[2])) return 0; /* collinear -> not concyclic */
    return nu[0]*R[0]+nu[1]*R[1]+nu[2]*R[2]==0;
}
static int symmetric(const ll P[4][3]){
    /* pairings: {01,23},{02,13},{03,12} */
    static const int P_[3][4]={{0,1,2,3},{0,2,1,3},{0,3,1,2}};
    for(int m=0;m<3;m++){
        int a=P_[m][0],b=P_[m][1],c=P_[m][2],e=P_[m][3];
        if (d2(P[a],P[b])==d2(P[c],P[e])) return 1;                 /* trapezoid */
        if (d2(P[c],P[a])==d2(P[c],P[b]) && d2(P[e],P[a])==d2(P[e],P[b])) return 1; /* ce axis */
        if (d2(P[a],P[c])==d2(P[a],P[e]) && d2(P[b],P[c])==d2(P[b],P[e])) return 1; /* ab axis */
    }
    return 0;
}
static ll F[4][3];
static void rec(int idx,int st,int n,long *cnt,long *sym){
    if (idx==4){
        if (concyclic((const ll(*)[3])F)){ (*cnt)++; if (symmetric((const ll(*)[3])F)) (*sym)++; }
        return;
    }
    int M=n*n*n;
    for(int p=st;p<M-(3-idx);p++){
        F[idx][0]=p%n; F[idx][1]=(p/n)%n; F[idx][2]=p/(n*n);
        rec(idx+1,p+1,n,cnt,sym);
    }
}
int main(int argc,char**argv){
    int n=atoi(argv[1]); long samples=argc>2?atol(argv[2]):0;
    if (samples==0){
        long cnt=0,sym=0; rec(0,0,n,&cnt,&sym);
        printf("n=%d exact: N_circ4=%ld sym=%ld asym=%ld  N/n^8=%.5f sym/n^7=%.4f asym/n^8=%.5f\n",
            n,cnt,sym,cnt-sym,(double)cnt/pow(n,8),(double)sym/pow(n,7),(double)(cnt-sym)/pow(n,8));
        return 0;
    }
    rng_s=2654435761ULL;
    long circ=0,sym=0;
    for(long s=0;s<samples;s++){
        ll P[4][3]; int dup;
        do{ dup=0;
            for(int i=0;i<4;i++)for(int j=0;j<3;j++)P[i][j]=(ll)(rnd()%(unsigned)n);
            for(int i=0;i<4&&!dup;i++)for(int j=i+1;j<4;j++)
                if(P[i][0]==P[j][0]&&P[i][1]==P[j][1]&&P[i][2]==P[j][2]){dup=1;break;}
        }while(dup);
        if (concyclic((const ll(*)[3])P)){ circ++; if (symmetric((const ll(*)[3])P)) sym++; }
    }
    double c4=(double)n*n*n*(n*n*n-1.0)*(n*n*n-2.0)*(n*n*n-3.0)/24.0;
    double N=(double)circ/samples*c4, S=(double)sym/samples*c4;
    printf("n=%d samples=%ld: circ=%ld sym=%ld | N~%.3e (n^%.3f) sym~%.3e asym~%.3e | sym frac=%.4f N/n^8=%.5f asym/n^8=%.5f\n",
        n,samples,circ,sym,N,log(N)/log(n),S,N-S,(double)sym/(circ?circ:1),N/pow(n,8),(N-S)/pow(n,8));
    return 0;
}
