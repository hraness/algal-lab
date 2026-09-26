/* quadc.c - enumerate concyclic 4-subsets of [0,n)^3, compute the primitive
 * dependency vector c (kernel of [1|x]), report:
 *   per |c|inf-shell: total, symmetric, asymmetric
 *   multiset class: {pppp}(par), {ppqq}(equal-pair), {pppq}, {ppqr}, {pqrs}
 * Cross-check: equal-pair c => symmetric?
 * Usage: quadc n */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
typedef long long ll;
static ll det3(const ll a[3], const ll b[3], const ll c[3]){
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);
}
static ll d2(const ll a[3], const ll b[3]){
    ll x=a[0]-b[0],y=a[1]-b[1],z=a[2]-b[2]; return x*x+y*y+z*z;
}
static int concyclic(const ll P[4][3]){
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
    return nu[0]*R[0]+nu[1]*R[1]+nu[2]*R[2]==0;
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
static ll gg(ll a,ll b){ a=llabs(a);b=llabs(b); while(b){ll t=a%b;a=b;b=t;} return a; }
/* dependency vector: left kernel of 4x4 matrix M with rows (1, x_i):
   c_i = (-1)^{r+i} det(minor_{r,i}) for fixed row r=0 */
static void depvec(const ll P[4][3], ll c[4]){
    /* M_{ij}: col0=1, cols1..3 = x_i */
    ll M[4][4];
    for(int i=0;i<4;i++){ M[i][0]=1; for(int j=0;j<3;j++) M[i][j+1]=P[i][j]; }
    /* left kernel = row of adj(M) = cofactors C_{j,s} along fixed column s;
       try s=0..3 until nonzero (minor deletes row i and column s) */
    for(int i=0;i<4;i++) c[i]=0;
    for(int s=0;s<4;s++){
        int nz=0;
        for(int i=0;i<4;i++){
            ll r[3][3]; int t=0;
            for(int j=0;j<4;j++) if(j!=i){
                int u=0;
                for(int q=0;q<4;q++) if(q!=s) r[t][u++]=M[j][q];
                t++;
            }
            ll v=(((i+s)%2)?-1:1)*det3(r[0],r[1],r[2]);
            c[i]=v; if(v)nz=1;
        }
        if(nz) break;
    }
    /* check sum c_i = 0 implicitly for coplanar; primitivize */
    ll g=gg(gg(c[0],c[1]),gg(c[2],c[3])); if(!g)g=1;
    for(int i=0;i<4;i++) c[i]/=g;
    if(c[0]<0||(c[0]==0&&c[1]<0)) for(int i=0;i<4;i++) c[i]=-c[i];
}
static long cnt[400], sy[400], epair_bad[400], asy[400];
static long cls_tot[8], cls_sym[8]; /* multiset classes */
int main(int argc,char**argv){
    int n=atoi(argv[1]); int N=n*n*n;
    long tot=0, symt=0;
    static ll P[4][3];
    for(int i=0;i<N-3;i++){ P[0][0]=i%n;P[0][1]=(i/n)%n;P[0][2]=i/(n*n);
      for(int j=i+1;j<N-2;j++){ P[1][0]=j%n;P[1][1]=(j/n)%n;P[1][2]=j/(n*n);
        for(int k=j+1;k<N-1;k++){ P[2][0]=k%n;P[2][1]=(k/n)%n;P[2][2]=k/(n*n);
          for(int l=k+1;l<N;l++){ P[3][0]=l%n;P[3][1]=(l/n)%n;P[3][2]=l/(n*n);
            if(!concyclic((const ll(*)[3])P)) continue;
            tot++;
            int sm=symmetric((const ll(*)[3])P); if(sm)symt++;
            ll c[4]; depvec((const ll(*)[3])P,c);
            /* sanity: c should satisfy sum c_i = 0 and sum c_i|x_i|^2=0 */
            ll s=0,s2=0; for(int u=0;u<4;u++){ s+=c[u]; s2+=c[u]*(P[u][0]*P[u][0]+P[u][1]*P[u][1]+P[u][2]*P[u][2]); }
            if(s||s2){ fprintf(stderr,"depvec fail %lld %lld\n",s,s2); }
            ll a[4]; for(int u=0;u<4;u++)a[u]=llabs(c[u]);
            /* sort */
            for(int x=0;x<4;x++)for(int y=x+1;y<4;y++) if(a[y]<a[x]){ll t=a[x];a[x]=a[y];a[y]=t;}
            int m=a[3]; if(m>=400)m=399;
            cnt[m]++; if(sm)sy[m]++; else asy[m]++;
            /* multiset class */
            int cl;
            if(a[0]==a[3]) cl=0;                        /* pppp */
            else if(a[0]==a[1]&&a[2]==a[3]&&a[1]!=a[2]) cl=1; /* ppqq */
            else if(a[0]==a[1]&&a[1]==a[2]) cl=2;       /* pppq */
            else if(a[1]==a[2]&&a[2]==a[3]) cl=2;
            else if(a[0]==a[1]||a[1]==a[2]||a[2]==a[3]) cl=3; /* ppqr exactly one pair */
            else cl=4;                                  /* pqrs distinct */
            cls_tot[cl]++; if(sm)cls_sym[cl]++;
            /* check equal-pair pattern: exists permutation s.t. c=(p,q,-p,-q) */
            int ep=0;
            for(int u=0;u<4&&!ep;u++)for(int v=0;v<4;v++) if(v!=u){
                for(int w=0;w<4;w++) if(w!=u&&w!=v){
                    int z=6-u-v-w; ll t1=c[u]+c[w], t2=c[v]+c[z];
                    if(t1==0&&t2==0) ep=1; /* c_u = -c_w, c_v = -c_z */
                }
            }
            if(ep&&!sm) epair_bad[m<400?m:399]++;
          }}}}
    printf("n=%d N_circ4=%ld sym=%ld asym=%ld\n",n,tot,symt,tot-symt);
    printf("classes: 0=pppp 1=ppqq 2=pppq 3=ppqr 4=pqrs\n");
    for(int cl=0;cl<5;cl++) printf("  cls%d: tot=%ld sym=%ld asym=%ld\n",cl,cls_tot[cl],cls_sym[cl],cls_tot[cl]-cls_sym[cl]);
    printf("equal-pair-patterned c but ASYMMETRIC quads: %ld total\n", ({long s=0;for(int i=0;i<400;i++)s+=epair_bad[i];s;}) );
    printf("shell: m | tot | sym | asym\n");
    for(int m=1;m<400&&m<=3.5*n*n;m++) if(cnt[m]) printf("  %d: %ld %ld %ld\n",m,cnt[m],sy[m],asy[m]);
    return 0;
}
