/* ls5x: tabu search + exact repair for k points in [n]^3 with no five on a
 * common sphere or plane: the 5x5 determinant with rows (x,y,z,x^2+y^2+z^2,1)
 * must be nonzero for every 5-subset (AlphaEvolve problem 60 verifier).
 *
 * Z(T) for a 4-subset T = grid points q with det(T u {q}) = 0:
 *   T not coplanar                         -> grid points on the circumsphere of T
 *   T coplanar, lifted 4x5 matrix rank 4   -> grid points on the plane of T
 *   T collinear or concyclic (rank <= 3)   -> every grid point (any fifth point is
 *                                             cospherical with a circle or line)
 * F[q]    = #{4-subsets T of S : q in Z(T)}
 * G[i][q] = #{T containing slot i : q in Z(T)}
 * conf(i) = F[S[i]] - C(m-1,3) = #degenerate 5-subsets containing S[i]
 * swap(i out, r in) changes #degenerate by (F[r] - G[i][r]) - conf(i).
 * Every reported set is re-verified by brute force over all 5-subsets before it
 * is printed; a failed self-check aborts the run.
 * Usage: ls5x n k seconds seed [initfile]
 * env: KMAX TEN_ADD TEN_REM PERT REPAIR_MAX RMAXR
 * Compile-time caps: -DMAXP (grid points, default 4096 = 16^3), -DMAXK (set size + 1).
 * The search path depends only on n, k, seed, the initial file and the env knobs;
 * `seconds` (CPU time) only decides when it stops, so a run is reproducible in
 * iteration count.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
typedef long long ll;
#ifndef MAXP
#define MAXP 4096
#endif
#ifndef MAXK
#define MAXK 64
#endif
static int n, np, K; static int px[MAXP], py[MAXP], pz[MAXP]; static ll pw[MAXP];
static int S[MAXK], inS[MAXP], slot[MAXP]; static int F[MAXP]; static int G[MAXK][MAXP];
static long tabu_add[MAXP], tabu_rem[MAXP];
static unsigned long long rs;
static inline unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static ll det3(ll m[3][3]){ return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]); }
static ll det4(ll m[4][4]){ ll s=0; for(int c=0;c<4;c++){ ll sub[3][3]; for(int r=1;r<4;r++){ int cc=0; for(int j=0;j<4;j++) if(j!=c) sub[r-1][cc++]=m[r][j]; } ll t=m[0][c]*det3(sub); s+=(c&1)?-t:t; } return s; }
static inline ll isq(ll v){ ll r=(ll)sqrt((double)v); while(r*r>v) r--; while((r+1)*(r+1)<=v) r++; return r; }
/* rank of the 4x5 lifted matrix of T is <= 3 iff every 3x3 minor of the lifted differences vanishes */
static int lifted_rank_le3(const int P[4]){
  ll D[3][4]; for(int r=0;r<3;r++){ int e=P[r+1], a=P[0]; D[r][0]=px[e]-px[a]; D[r][1]=py[e]-py[a]; D[r][2]=pz[e]-pz[a]; D[r][3]=pw[e]-pw[a]; }
  static const int cols[4][3]={{0,1,2},{0,1,3},{0,2,3},{1,2,3}};
  for(int c=0;c<4;c++){ ll m[3][3]; for(int r=0;r<3;r++) for(int j=0;j<3;j++) m[r][j]=D[r][cols[c][j]]; if(det3(m)!=0) return 0; }
  return 1; }
/* ---- Z cache ---- */
typedef struct { unsigned long long key; int off, len; } Ent;
static Ent *tab; static size_t tabsz=1<<23, tabcnt; static int *pool; static size_t poolsz=1<<26, poolused;
static int zbuf[MAXP];
static long n_concyclic=0;
static int computeZ(int a,int b,int c,int d,int *out){
  int m=0; int q[3]={b,c,d}; ll A[3][3], rhs[3];
  for(int r=0;r<3;r++){ int e=q[r]; A[r][0]=2*(px[e]-px[a]); A[r][1]=2*(py[e]-py[a]); A[r][2]=2*(pz[e]-pz[a]); rhs[r]=pw[e]-pw[a]; }
  ll D=det3(A);
  if(D!=0){ ll N[3]; for(int i=0;i<3;i++){ ll M[3][3]; memcpy(M,A,sizeof(M)); for(int r=0;r<3;r++) M[r][i]=rhs[r]; N[i]=det3(M); }
    if(D<0){D=-D;N[0]=-N[0];N[1]=-N[1];N[2]=-N[2];}
    ll R2=0; { ll t=D*px[a]-N[0]; R2+=t*t; t=D*py[a]-N[1]; R2+=t*t; t=D*pz[a]-N[2]; R2+=t*t; }
    ll R=isq(R2)+1; ll xlo=(N[0]-R)/D-1, xhi=(N[0]+R)/D+1; if(xlo<0) xlo=0; if(xhi>n-1) xhi=n-1;
    for(int x=(int)xlo;x<=(int)xhi;x++){ ll tx=D*x-N[0]; tx*=tx; if(tx>R2) continue; ll Ry=isq(R2-tx)+1; ll ylo=(N[1]-Ry)/D-1, yhi=(N[1]+Ry)/D+1; if(ylo<0) ylo=0; if(yhi>n-1) yhi=n-1;
      for(int y=(int)ylo;y<=(int)yhi;y++){ ll ty=D*y-N[1]; ty*=ty; ll rem=R2-tx-ty; if(rem<0) continue; ll s=isq(rem); if(s*s!=rem) continue;
        ll num=N[2]+s; if(num%D==0){ ll z=num/D; if(z>=0&&z<n) out[m++]=x*n*n+y*n+(int)z; }
        if(s){ num=N[2]-s; if(num%D==0){ ll z=num/D; if(z>=0&&z<n) out[m++]=x*n*n+y*n+(int)z; } } } }
    return m; }
  int P[4]={a,b,c,d};
  if(lifted_rank_le3(P)){ n_concyclic++; for(int q2=0;q2<np;q2++) out[m++]=q2; return m; }
  ll Nn[3]={0,0,0}; int found=0;
  for(int i=0;i<4&&!found;i++)for(int j=i+1;j<4&&!found;j++)for(int k=j+1;k<4&&!found;k++){
    ll u[3]={px[P[j]]-px[P[i]],py[P[j]]-py[P[i]],pz[P[j]]-pz[P[i]]}, v[3]={px[P[k]]-px[P[i]],py[P[k]]-py[P[i]],pz[P[k]]-pz[P[i]]};
    Nn[0]=u[1]*v[2]-u[2]*v[1]; Nn[1]=u[2]*v[0]-u[0]*v[2]; Nn[2]=u[0]*v[1]-u[1]*v[0]; if(Nn[0]||Nn[1]||Nn[2]) found=1; }
  ll off=Nn[0]*px[a]+Nn[1]*py[a]+Nn[2]*pz[a];
  for(int q2=0;q2<np;q2++) if(Nn[0]*px[q2]+Nn[1]*py[q2]+Nn[2]*pz[q2]==off) out[m++]=q2;
  return m; }
static const int* getZ(int a,int b,int c,int d,int *len){
  int v[4]={a,b,c,d}; for(int i=1;i<4;i++){int t=v[i],j=i-1;while(j>=0&&v[j]>t){v[j+1]=v[j];j--;}v[j+1]=t;}
  unsigned long long key=((unsigned long long)v[0]<<48)|((unsigned long long)v[1]<<32)|((unsigned long long)v[2]<<16)|(unsigned long long)v[3]; key+=1;
  unsigned long long h=key*0x9E3779B97F4A7C15ULL; size_t j=(h>>20)&(tabsz-1);
  while(tab[j].key){ if(tab[j].key==key){ *len=tab[j].len; return pool+tab[j].off; } j=(j+1)&(tabsz-1); }
  int m=computeZ(a,b,c,d,zbuf);
  if(tabcnt*2>tabsz || poolused+m>poolsz){ memset(tab,0,tabsz*sizeof(Ent)); tabcnt=0; poolused=0; j=(h>>20)&(tabsz-1); }
  tab[j].key=key; tab[j].off=(int)poolused; tab[j].len=m; memcpy(pool+poolused,zbuf,m*sizeof(int)); poolused+=m; tabcnt++;
  *len=m; return pool+tab[j].off; }
static int m_;
static inline void applyT(int i,int j,int k,int l,int delta){
  int len; const int*z=getZ(S[i],S[j],S[k],S[l],&len);
  for(int t=0;t<len;t++){ int q=z[t]; F[q]+=delta; G[i][q]+=delta; G[j][q]+=delta; G[k][q]+=delta; G[l][q]+=delta; } }
static void add_point(int r){ int sl=m_; S[sl]=r; inS[r]=1; slot[r]=sl; memset(G[sl],0,sizeof(int)*np);
  for(int i=0;i<sl;i++)for(int j=i+1;j<sl;j++)for(int k=j+1;k<sl;k++) applyT(i,j,k,sl,+1);
  m_++; }
static void remove_slot(int sl){ int p=S[sl];
  for(int i=0;i<m_;i++){ if(i==sl) continue; for(int j=i+1;j<m_;j++){ if(j==sl) continue; for(int k=j+1;k<m_;k++){ if(k==sl) continue; applyT(i,j,k,sl,-1); } } }
  inS[p]=0; m_--; if(sl!=m_){ S[sl]=S[m_]; slot[S[sl]]=sl; memcpy(G[sl],G[m_],sizeof(int)*np); } }
static ll C3(int m){ return (ll)m*(m-1)*(m-2)/6; }
static ll cur_cost(void){ ll base=C3(m_-1), c=0; for(int i=0;i<m_;i++) c+=F[S[i]]-base; return c; }
/* independent brute-force check over all 5-subsets (4x4 determinant of lifted differences) */
static int bruteforce_ok(void){
  ll X[MAXK][4]; for(int i=0;i<m_;i++){ int p=S[i]; X[i][0]=px[p]; X[i][1]=py[p]; X[i][2]=pz[p]; X[i][3]=pw[p]; }
  for(int a=0;a<m_;a++) for(int b=a+1;b<m_;b++) for(int c=b+1;c<m_;c++) for(int d=c+1;d<m_;d++) for(int e=d+1;e<m_;e++){
    int R[4]={b,c,d,e}; ll M[4][4]; for(int r=0;r<4;r++) for(int j=0;j<4;j++) M[r][j]=X[R[r]][j]-X[a][j];
    if(det4(M)==0) return 0; }
  return 1; }
static void print_sol(FILE*f){ fprintf(f,"{\"n\": %d, \"k\": %d, \"points\": [",n,m_); for(int i=0;i<m_;i++) fprintf(f,"%s[%d, %d, %d]",i?", ":"",px[S[i]],py[S[i]],pz[S[i]]); fprintf(f,"]}\n"); fflush(f); }
static double elapsed(clock_t t0){ return (double)(clock()-t0)/CLOCKS_PER_SEC; }

static long nodes, node_budget=20000; static int order[MAXP], rank_[MAXP];
static void shuffle_order(void){ for(int i=0;i<np;i++) order[i]=i; for(int i=np-1;i>0;i--){ int j=rnd()%(i+1); int t=order[i]; order[i]=order[j]; order[j]=t; } for(int i=0;i<np;i++) rank_[order[i]]=i; }
/* add `need` points, each creating no degenerate 5-subset with the current (valid) set */
static int dfs(int need, int from){
  if(need==0) return 1;
  if(nodes>node_budget) return 0;
  int cnt=0; for(int q=0;q<np;q++) if(!inS[q]&&F[q]==0&&rank_[q]>=from) cnt++;
  if(cnt<need) return 0;
  for(int pos=from;pos<np;pos++){ int q=order[pos]; if(inS[q]||F[q]!=0) continue;
    nodes++; add_point(q);
    if(dfs(need-1,pos+1)) return 1;
    remove_slot(m_-1); if(nodes>node_budget) return 0; }
  return 0; }
/* remove r conflicting points (r = 1..rmax); if the remainder is valid, look for r
 * conflict-free replacements by exact DFS.  Returns 1 iff S is now valid. */
static long repairs_tried=0, repairs_ok=0;
static int exact_repair(int rmax){
  ll base=C3(m_-1); int V[MAXK], nv=0; for(int i=0;i<m_;i++) if(F[S[i]]-base>0) V[nv++]=S[i];
  if(nv==0) return 1; if(nv>12) return 0;
  repairs_tried++;
  for(int r=1;r<=rmax&&r<=nv;r++){
    int c[8]; for(int i=0;i<r;i++) c[i]=i;
    while(1){
      int removed[8]; for(int i=0;i<r;i++) removed[i]=V[c[i]];
      for(int i=0;i<r;i++) remove_slot(slot[removed[i]]);
      if(cur_cost()==0){ shuffle_order(); nodes=0; if(dfs(r,0)){ repairs_ok++; return 1; } }
      for(int i=0;i<r;i++) add_point(removed[i]);
      int i=r-1; while(i>=0&&c[i]==nv-r+i) i--; if(i<0) break; c[i]++; for(int j=i+1;j<r;j++) c[j]=c[j-1]+1; } }
  return 0; }
int main(int argc,char**argv){
  if(argc<5){ fprintf(stderr,"usage: ls5x n k seconds seed [initfile]\n"); return 2; }
  n=atoi(argv[1]); K=atoi(argv[2]); double secs=atof(argv[3]); rs=strtoull(argv[4],0,10)*2654435761ULL+88172645463325252ULL; np=n*n*n;
  if(n<2||np>MAXP||K<5||K>=MAXK){ fprintf(stderr,"bad n/k\n"); return 2; }
  tab=calloc(tabsz,sizeof(Ent)); pool=malloc(poolsz*sizeof(int));
  int idx=0; for(int x=0;x<n;x++)for(int y=0;y<n;y++)for(int z=0;z<n;z++){px[idx]=x;py[idx]=y;pz[idx]=z;pw[idx]=(ll)x*x+(ll)y*y+(ll)z*z;idx++;}
  m_=0;
  if(argc>5){ FILE*f=fopen(argv[5],"r"); if(!f){ fprintf(stderr,"cannot open %s\n",argv[5]); return 2; } int x,y,z; while(fscanf(f,"%d %d %d",&x,&y,&z)==3){ if(x<0||y<0||z<0||x>=n||y>=n||z>=n) continue; int q=x*n*n+y*n+z; if(!inS[q]&&m_<K) add_point(q);} fclose(f); }
  while(m_<K){ int best=-1,bv=1<<30,cnt=0; for(int q=0;q<np;q++) if(!inS[q]){ if(F[q]<bv){bv=F[q];best=q;cnt=1;} else if(F[q]==bv){ cnt++; if(rnd()%cnt==0) best=q; } } add_point(best); }
  int TEN_REM=getenv("TEN_REM")?atoi(getenv("TEN_REM")):2, TEN_ADD=getenv("TEN_ADD")?atoi(getenv("TEN_ADD")):K/2+2; long PERT=getenv("PERT")?atol(getenv("PERT")):5000;
  int REPAIR_MAX=getenv("REPAIR_MAX")?atoi(getenv("REPAIR_MAX")):15, RMAXR=getenv("RMAXR")?atoi(getenv("RMAXR")):3; int KMAX=getenv("KMAX")?atoi(getenv("KMAX")):K;
  if(KMAX>=MAXK) KMAX=MAXK-1;
  clock_t t0=clock(); long it=0; ll bestcost=1LL<<60; long since=0, last_repair=-1000; int tenure_add=TEN_ADD, tenure_rem=TEN_REM;
  while(1){
    ll cost=cur_cost();
    if(cost<bestcost){ bestcost=cost; since=0; fprintf(stderr,"k=%d it=%ld degenerate5=%lld t=%.1fs\n",m_,it,cost/5,elapsed(t0)); }
    if(cost>0 && cost<=REPAIR_MAX && it-last_repair>=50){ last_repair=it; if(exact_repair(RMAXR)) cost=cur_cost(); }
    if(cost==0){
      if(!bruteforce_ok()){ fprintf(stderr,"SELFCHECK FAIL: incremental cost 0 but brute force finds a degenerate 5-subset\n"); print_sol(stderr); return 3; }
      print_sol(stdout); fprintf(stderr,"FOUND n=%d k=%d it=%ld t=%.1fs repairs=%ld/%ld selfcheck=ok\n",n,m_,it,elapsed(t0),repairs_ok,repairs_tried);
      if(m_>=KMAX) return 0;
      int best=-1,bv=1<<30,cnt=0; for(int q=0;q<np;q++) if(!inS[q]){ if(F[q]<bv){bv=F[q];best=q;cnt=1;} else if(F[q]==bv){cnt++; if(rnd()%cnt==0) best=q;} }
      add_point(best); bestcost=1LL<<60; since=0; memset(tabu_add,0,sizeof(tabu_add)); memset(tabu_rem,0,sizeof(tabu_rem)); continue; }
    if((it&4095)==0 && it){ double e=elapsed(t0); fprintf(stderr,"rate k=%d it=%ld %.0f it/s degenerate5=%lld best=%lld concyclicZ=%ld t=%.0fs\n",m_,it,it/e,cost/5,bestcost/5,n_concyclic,e); }
    if(elapsed(t0)>secs){ fprintf(stderr,"TIMEOUT k=%d best degenerate5=%lld it=%ld\n",m_,bestcost/5,it); return 1; }
    if(++since>PERT){ for(int t=0;t<2+(int)(rnd()%3);t++){ int sl=rnd()%m_; int p=S[sl]; remove_slot(sl); int r; do r=rnd()%np; while(inS[r]); add_point(r); tabu_add[p]=it+tenure_add; } since=0; it++; continue; }
    ll bestd=1LL<<60; int bi=-1,br=-1,cnt=0;
    for(int i=0;i<m_;i++){ ll ci=F[S[i]]-C3(m_-1); int p=S[i]; int tr=tabu_rem[p]>it;
      for(int r=0;r<np;r++){ if(inS[r]) continue; ll d=(F[r]-G[i][r])-ci;
        int tabu=tr||tabu_add[r]>it; if(tabu && cost+5*d>=bestcost) continue;
        if(d<bestd){bestd=d;bi=i;br=r;cnt=1;} else if(d==bestd){cnt++; if(rnd()%cnt==0){bi=i;br=r;}} } }
    if(bi<0){ it++; continue; }
    int p=S[bi]; remove_slot(bi); add_point(br); tabu_add[p]=it+tenure_add+(int)(rnd()%5); tabu_rem[br]=it+tenure_rem; it++;
  }
}
