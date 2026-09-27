/* seprof.c - per-section profiler for the sparse range.
 * For random primitive v with s=|v|_inf in dyadic blocks [B,min(2B,Smax)):
 *   - exact section decomposition: scan n^3 points, group by k=v.x
 *   - exact sums per v: nsec (nonempty k), nsec4 (k with N>=4),
 *     sumN2, sumN3, sumC4 = Sigma_k C(N,4)
 *   - sample up to sec_cap sections with N>=4; each section: exact C(N,4)
 *     enumeration if N<=excap else mc random 4-subsets; count concyclic
 *     and asymmetric; scale to the full v.
 * Per v also: max ear multiset max|c_i| over observed concyclic quads,
 * r2 = number of representations r_2-style proxy: we report vv2=|v|^2 and
 * the parity structure; post-analysis correlates asym with arithmetic.
 * Usage: seprof n Smin Smax nv sec_cap mc
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef long long ll;
static unsigned long long rng_s;
static unsigned long long rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
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
        nu[2]=w[1][0]*w[2][1]-w[1][0]*w[2][2];
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
static ll crossn(const ll a[3], const ll b[3], ll out[3]){
    out[0]=a[1]*b[2]-a[2]*b[1]; out[1]=a[2]*b[0]-a[0]*b[2]; out[2]=a[0]*b[1]-a[1]*b[0];
    return out[0]*out[0]+out[1]*out[1]+out[2]*out[2];
}
static int NPTS;
static ll (*PTS)[3]; /* decoded points of current section */
static ll F[4][3];
static ll g_circ, g_asym; /* counts for current section enumeration */
static int g_maxc; /* max |c_i| seen (exact mode) */
static void quad_done(void){
    ll nrm[3];
    if (!concyclic((const ll(*)[3])F,nrm)) return;
    g_circ++;
    int sym = symmetric((const ll(*)[3])F);
    if (!sym) g_asym++;
    /* ear areas -> |c_i| multiset max */
    ll g = gcd3(nrm[0],nrm[1],nrm[2]);
    ll vv2 = (nrm[0]/g)*(nrm[0]/g)+(nrm[1]/g)*(nrm[1]/g)+(nrm[2]/g)*(nrm[2]/g);
    ll mx=0;
    for(int i=0;i<4;i++){
        int j=(i+1)%4,k=(i+2)%4,l=(i+3)%4;
        ll e1[3]={F[k][0]-F[j][0],F[k][1]-F[j][1],F[k][2]-F[j][2]};
        ll e2[3]={F[l][0]-F[j][0],F[l][1]-F[j][1],F[l][2]-F[j][2]};
        ll cr[3]; ll c2=crossn(e1,e2,cr);
        if (c2%vv2==0){ ll q=c2/vv2; ll A=(ll)(sqrt((double)q)+0.5); if(A>mx)mx=A; }
    }
    if (mx>g_maxc) g_maxc=mx;
}
static void rec(int idx,int st){
    if (idx==4){ quad_done(); return; }
    for(int p=st;p<NPTS-(3-idx);p++){
        F[idx][0]=PTS[p][0]; F[idx][1]=PTS[p][1]; F[idx][2]=PTS[p][2];
        rec(idx+1,p+1);
    }
}
int main(int argc,char**argv){
    int n=atoi(argv[1]);
    int Smin=atoi(argv[2]), Smax=atoi(argv[3]);
    int nv=atoi(argv[4]), sec_cap=atoi(argv[5]), mc=atoi(argv[6]);
    int excap=40;
    rng_s=2654435761ULL+n*7919+Smin;
    int n3=n*n*n;
    int *cnt=NULL,*off=NULL,*pts=NULL,*cur=NULL;
    PTS=malloc(64*sizeof*PTS);
    double totC4=0,totCirc=0,totAsym=0,totN3=0,totN4C4=0;
    int totv=0, totvwithasym=0;
    for(int B=Smin;B<Smax;B*=2){
        int Bhi=2*B<Smax?2*B:Smax;
        double bN3=0,bC4=0,bCirc=0,bAsym=0,bN4C4=0,bCircRaw=0,bAsymRaw=0;
        int bv=0,bv4=0,bvasym=0, bmaxc=0;
        for(int t=0;t<nv;t++){
            /* sample primitive v with s in [B,Bhi) */
            ll v[3]; int tries=0;
            for(;;){
                tries++; if(tries>200000) break;
                int s=0;
                for(int j=0;j<3;j++){ v[j]=(ll)(rnd()%(unsigned)(2*Bhi-1))-(Bhi-1); if(llabs(v[j])>s)s=llabs(v[j]); }
                if (s<B||s>=Bhi) continue;
                if (gcd3(v[0],v[1],v[2])!=1) continue;
                if (v[0]<0||(v[0]==0&&v[1]<0)||(v[0]==0&&v[1]==0&&v[2]<0))
                    for(int j=0;j<3;j++) v[j]=-v[j];
                break;
            }
            if (tries>200000) continue;
            ll s=0,vv2=0;
            for(int j=0;j<3;j++){ if(llabs(v[j])>s)s=llabs(v[j]); vv2+=v[j]*v[j]; }
            ll lo=0,hi=0;
            for(int j=0;j<3;j++){ if(v[j]>0) hi+=v[j]*(n-1); else lo+=v[j]*(n-1); }
            ll R=hi-lo+1;
            cnt=realloc(cnt,R*sizeof(int)); memset(cnt,0,R*sizeof(int));
            /* pass 1: counts */
            for(int z=0;z<n;z++) for(int y=0;y<n;y++) for(int x=0;x<n;x++)
                cnt[v[0]*x+v[1]*y+v[2]*z-lo]++;
            off=realloc(off,R*sizeof(int));
            int acc=0, nsec=0, nsec4=0; double sN2=0,sN3=0,sC4=0; int maxN=0;
            for(ll k=0;k<R;k++){ int c=cnt[k]; off[k]=acc; acc+=c;
                if(c>0){nsec++; sN2+=(double)c*c; sN3+=(double)c*c*c; sC4+=(double)c*(c-1)*(c-2)*(c-3)/24.0;
                    if(c>maxN)maxN=c; if(c>=4)nsec4++;} }
            /* pass 2: fill pts */
            pts=realloc(pts,n3*sizeof(int)); cur=realloc(cur,R*sizeof(int));
            memcpy(cur,off,R*sizeof(int));
            for(int z=0;z<n;z++) for(int y=0;y<n;y++) for(int x=0;x<n;x++){
                int t2=v[0]*x+v[1]*y+v[2]*z-lo; pts[cur[t2]++]=(z*n+y)*n+x; }
            /* gather list of k-indices with cnt>=4 */
            int *big=malloc(nsec4*sizeof(int)); int nb=0;
            for(ll k=0;k<R;k++) if(cnt[k]>=4) big[nb++]=k;
            /* sample up to sec_cap uniformly without replacement */
            int msec=nb<sec_cap?nb:sec_cap;
            double vCirc=0,vAsym=0; int vasymf=0; int vmaxc=0;
            for(int i=0;i<msec;i++){
                int pick = i + (int)(rnd()%(unsigned)(nb-i));
                int tmp=big[i]; big[i]=big[pick]; big[pick]=tmp;
                int k=big[i], N=cnt[k];
                if (N>NPTS){ NPTS=N; PTS=realloc(PTS,N*sizeof*PTS); }
                NPTS=N;
                int base=off[k];
                for(int p=0;p<N;p++){ int id=pts[base+p];
                    PTS[p][0]=id%n; PTS[p][1]=(id/n)%n; PTS[p][2]=id/(n*n); }
                double C4=(double)N*(N-1)*(N-2)*(N-3)/24.0;
                g_circ=0; g_asym=0; g_maxc=0;
                if (N<=excap){
                    rec(0,0);
                    vCirc+=g_circ; vAsym+=g_asym; if(g_asym)vasymf=1;
                    if(g_maxc>vmaxc)vmaxc=g_maxc;
                } else {
                    long mcirc=0,masym=0; int mmaxc=0;
                    for(long q=0;q<mc;q++){
                        int a[4]; for(int i2=0;i2<4;i2++){ int u;
                            do{ u=rnd()%(unsigned)N; int ok=1;
                                for(int j2=0;j2<i2;j2++) if(a[j2]==u){ok=0;break;}
                                if(ok){a[i2]=u;break;} }while(1); }
                        for(int i2=0;i2<4;i2++){ F[i2][0]=PTS[a[i2]][0];F[i2][1]=PTS[a[i2]][1];F[i2][2]=PTS[a[i2]][2]; }
                        ll oc=g_circ,oa=g_asym; quad_done();
                        if(g_circ>oc){mcirc++; if(g_asym>oa)masym++;}
                        if(g_maxc>mmaxc)mmaxc=g_maxc;
                    }
                    vCirc+=C4*mcirc/mc; vAsym+=C4*masym/mc; if(masym)vasymf=1;
                    if(mmaxc>vmaxc)vmaxc=mmaxc;
                }
            }
            free(big);
            double scale = msec? (double)nb/msec : 0;
            vCirc*=scale; vAsym*=scale;
            if (s<B) continue;
            bv++; bN3+=sN3; bC4+=sC4; bCirc+=vCirc; bAsym+=vAsym; bN4C4+= (nb?sC4:0);
            if(nsec4)bv4++; if(vasymf)bvasym++;
            if(vmaxc>bmaxc)bmaxc=vmaxc;
            printf("  v=(%lld,%lld,%lld) s=%lld vv2=%lld nsec=%d nsec4=%d maxN=%d sumN3=%.3e sumC4=%.3e estCirc=%.3g estAsym=%.3g vmaxc=%d\n",
                v[0],v[1],v[2],s,vv2,nsec,nsec4,maxN,sN3,sC4,vCirc,vAsym,vmaxc);
        }
        totN3+=bN3; totC4+=bC4; totCirc+=bCirc; totAsym+=bAsym;
        totv+=bv; totvwithasym+=bvasym;
        printf("BLOCK s=[%d,%d): nv=%d nv4=%d nvasym=%d avgSumN3=%.3e avgSumC4=%.3e avgEstCirc=%.3g avgEstAsym=%.3g maxc=%d\n",
            B,Bhi,bv,bv4,bvasym,bN3/(bv?bv:1),bC4/(bv?bv:1),bCirc/(bv?bv:1),bAsym/(bv?bv:1),bmaxc);
    }
    printf("TOTAL nv=%d nvasym=%d  sum-avgN3=%.3e avgCirc=%.3g avgAsym=%.3g\n",
        totv,totvwithasym,totN3/(totv?totv:1),totCirc/(totv?totv:1),totAsym/(totv?totv:1));
    return 0;
}
