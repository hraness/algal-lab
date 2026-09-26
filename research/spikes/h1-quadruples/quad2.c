/* quad2.c - for each concyclic 4-subset of [0,n)^3: primitive normal s,
 * symmetric flag, and the sorted sub-triangle lattice-area multiset A_i
 * (in units of |v|). Verifies: |c_i| = A_i/g in [1, floor(3sqrt3 n^2/(2s))],
 * and all-|c|=1 => parallelogram => symmetric. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef long long ll;
typedef __int128 lll;
static ll det3(const ll a[3], const ll b[3], const ll c[3]){
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);
}
static ll d2(const ll a[3], const ll b[3]){ ll x=a[0]-b[0],y=a[1]-b[1],z=a[2]-b[2]; return x*x+y*y+z*z; }
static ll gcd3(ll a,ll b,ll c){ a=llabs(a);b=llabs(b);c=llabs(c);
    while(b){ll t=a%b;a=b;b=t;} while(c){ll t=a%c;a=c;c=t;} return a; }
static ll gcdn(ll a,ll b){ a=llabs(a);b=llabs(b); while(b){ll t=a%b;a=b;b=t;} return a; }
static int concyclic(const ll P[4][3], ll nrm[3]){
    ll d[3][3], R[3];
    for(int i=0;i<3;i++){ for(int j=0;j<3;j++) d[i][j]=P[i+1][j]-P[0][j];
        R[i]=P[i+1][0]*P[i+1][0]+P[i+1][1]*P[i+1][1]+P[i+1][2]*P[i+1][2]
           -P[0][0]*P[0][0]-P[0][1]*P[0][1]-P[0][2]*P[0][2]; }
    if (det3(d[0],d[1],d[2])!=0) return 0;
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
    if (!(nu[0]||nu[1]||nu[2])) return 0;
    if (nu[0]*R[0]+nu[1]*R[1]+nu[2]*R[2]!=0) return 0;
    nrm[0]=d[0][1]*d[1][2]-d[0][2]*d[1][1];
    nrm[1]=d[0][2]*d[1][0]-d[0][0]*d[1][2];
    nrm[2]=d[0][0]*d[1][1]-d[0][1]*d[1][0];
    if (!(nrm[0]||nrm[1]||nrm[2])){
        nrm[0]=d[0][1]*d[2][2]-d[0][2]*d[2][1];
        nrm[1]=d[0][2]*d[2][0]-d[0][0]*d[2][2];
        nrm[2]=d[0][0]*d[2][1]-d[0][1]*d[2][0];
    }
    return 1;
}
static int symmetric(const ll P[4][3]){
    static const int P_[3][4]={{0,1,2,3},{0,2,1,3},{0,3,1,2}};
    for(int m=0;m<3;m++){
        int a=P_[m][0],b=P_[m][1],c=P_[m][2],e=P_[m][3];
        if (d2(P[a],P[b])==d2(P[c],P[e])) return 1;
        if (d2(P[c],P[a])==d2(P[c],P[b]) && d2(P[e],P[a])==d2(P[e],P[b])) return 1;
        if (d2(P[a],P[c])==d2(P[a],P[e]) && d2(P[b],P[c])==d2(P[b],P[e])) return 1;
    }
    return 0;
}
/* |a x b|^2 / |v|^2 = A^2 : compute A in integer arithmetic when |v|^2 | |cross|^2.
 * cross of edges e_j = P_j - P_i for the triangle opposite vertex i. */
static ll crossn(const ll a[3], const ll b[3], ll out[3]){
    out[0]=a[1]*b[2]-a[2]*b[1]; out[1]=a[2]*b[0]-a[0]*b[2]; out[2]=a[0]*b[1]-a[1]*b[0];
    return out[0]*out[0]+out[1]*out[1]+out[2]*out[2];
}
static ll F[4][3];
static ll maxs_all, maxs_asym, badK;
static long tot, cnt_par;
static void rec(int idx,int st,int n){
    if (idx==4){
        ll nrm[3];
        if (!concyclic((const ll(*)[3])F,nrm)) return;
        tot++;
        int sym = symmetric((const ll(*)[3])F);
        /* primitive v = nrm/g; |v|^2 = |nrm|^2/g^2 ; s = max |v_i| */
        ll g = gcd3(nrm[0],nrm[1],nrm[2]);
        ll v[3]={nrm[0]/g,nrm[1]/g,nrm[2]/g};
        ll s=0,vv2=v[0]*v[0]+v[1]*v[1]+v[2]*v[2];
        for(int j=0;j<3;j++){ll a=llabs(v[j]); if(a>s)s=a;}
        if (s>maxs_all) maxs_all=s;
        if (!sym && s>maxs_asym) maxs_asym=s;
        /* sub-triangle areas: triangle opposite i uses edges from a base among j,k,l */
        ll A[4];
        for(int i=0;i<4;i++){
            int j=(i+1)%4,k=(i+2)%4,l=(i+3)%4;
            ll e1[3]={F[k][0]-F[j][0],F[k][1]-F[j][1],F[k][2]-F[j][2]};
            ll e2[3]={F[l][0]-F[j][0],F[l][1]-F[j][1],F[l][2]-F[j][2]};
            ll cr[3]; ll c2=crossn(e1,e2,cr);
            /* |cr|^2 = A^2 |v|^2 -> A = sqrt(c2/vv2) */
            if (c2 % vv2 != 0){ badK++; A[i]=-1; }
            else { ll q=c2/vv2; A[i]=(ll)(sqrt((double)q)+0.5); if(A[i]*A[i]!=q){A[i]=-1;badK++;} }
        }
        /* c_i = A_i / g_A */
        ll gA=A[0]; for(int i=1;i<4;i++) gA=gcdn(gA,A[i]);
        int allone=1; for(int i=0;i<4;i++) if(A[i]/gA!=1) allone=0;
        if (allone) cnt_par++;
        /* check K bound: A_i <= 3sqrt3 n^2/(2s) */
        double K = 3*sqrt(3.0)*n*n/(2.0*s);
        for(int i=0;i<4;i++) if (A[i] > K + 1e-9) badK++;
        /* the strong claim: s > 3sqrt3 n^2/4 and not all-one => violation print */
        if (!allone && s > 3*sqrt(3.0)*n*n/4.0){
            printf("VIOLATION s=%lld sym=%d A=(%lld,%lld,%lld,%lld) g=%lld P=%lld,%lld,%lld %lld,%lld,%lld %lld,%lld,%lld %lld,%lld,%lld\n",
                s,sym,A[0],A[1],A[2],A[3],gA,F[0][0],F[0][1],F[0][2],F[1][0],F[1][1],F[1][2],F[2][0],F[2][1],F[2][2],F[3][0],F[3][1],F[3][2]);
        }
        return;
    }
    int M=n*n*n;
    for(int p=st;p<M-(3-idx);p++){
        F[idx][0]=p%n; F[idx][1]=(p/n)%n; F[idx][2]=p/(n*n);
        rec(idx+1,p+1,n);
    }
}
int main(int argc,char**argv){
    int n=atoi(argv[1]);
    rec(0,0,n);
    printf("n=%d tot=%ld maxs_all=%lld (bound %.1f) maxs_asym=%lld (bound %.1f) parallelogram|allA=%ld badK=%lld\n",
        n,tot,maxs_all,3*sqrt(3.0)*n*n/2.0,maxs_asym,3*sqrt(3.0)*n*n/4.0,cnt_par,badK);
    return 0;
}
