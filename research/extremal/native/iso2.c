/* iso2: tabu search + exact repair for isosceles-free subsets of the n x n grid
 * (no three distinct points a, b, c with |ab| = |bc|; collinear triples count).
 * A violation is (apex b; pair {a,c}) with all three in S.
 * F[q]    = violations involving q among S u {q}
 * G[i][q] = those violations that also involve slot i
 * swap(S[i] out, r in): delta = (F[r] - G[i][r]) - F[S[i]];  3*violations = sum_{q in S} F[q]
 * SYM=1: mirror-symmetric mode, S is a union of orbits {(x,y),(x,n-1-y)} (n even); moves swap
 * whole orbits, candidate deltas are estimated and the true cost is recomputed after each move.
 * Every reported set is re-verified by brute force before it is printed.
 * Usage: iso2 n k seconds seed [initfile]   env: KMAX SYM REPAIR_MAX RMAXR TEN_ADD TEN_REM PERT
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
typedef long long ll;
#define MAXP 16384
#define MAXK 320
static int n, np, K, SYM; static int px[MAXP], py[MAXP];
static int S[MAXK], inS[MAXP], slot[MAXP]; static int F[MAXP]; static int *G;
static long tabu_add[MAXP], tabu_rem[MAXP];
static unsigned long long rs;
static inline unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static int *cq, *cd; static size_t *coff;
static int dist2(int a,int b){ int dx=px[a]-px[b], dy=py[a]-py[b]; return dx*dx+dy*dy; }
static int cmp_p; static int cmpd(const void*a,const void*b){ return dist2(cmp_p,*(const int*)a)-dist2(cmp_p,*(const int*)b); }
static void build_circles(void){ size_t tot=(size_t)np*(np-1); cq=malloc(sizeof(int)*tot); cd=malloc(sizeof(int)*tot); coff=malloc(sizeof(size_t)*(np+1));
  for(int p=0;p<np;p++){ coff[p]=(size_t)p*(np-1); int m=0; for(int q=0;q<np;q++) if(q!=p) cq[coff[p]+m++]=q; cmp_p=p; qsort(cq+coff[p],np-1,sizeof(int),cmpd); for(int j=0;j<np-1;j++) cd[coff[p]+j]=dist2(p,cq[coff[p]+j]); } coff[np]=tot; }
static size_t lo_idx(int p,int d){ size_t lo=coff[p], hi=coff[p+1]; while(lo<hi){ size_t mid=(lo+hi)/2; if(cd[mid]<d) lo=mid+1; else hi=mid; } return lo; }
static int m_;
#define FOR_CIRCLE(p,d,q) for(size_t _i=lo_idx(p,d); _i<coff[(p)+1] && cd[_i]==(d); _i++){ int q=cq[_i];
#define END_CIRCLE }
static inline void bump(int q,int i,int j,int delta){ F[q]+=delta; G[(size_t)i*np+q]+=delta; G[(size_t)j*np+q]+=delta; }
static void apply_pair(int p,int c,int sp,int sc,int delta){
  int d=dist2(p,c);
  FOR_CIRCLE(p,d,q) if(q!=c) bump(q,sp,sc,delta); END_CIRCLE
  FOR_CIRCLE(c,d,q) if(q!=p) bump(q,sp,sc,delta); END_CIRCLE
  int ax=2*(px[c]-px[p]), ay=2*(py[c]-py[p]); int rhs=px[c]*px[c]+py[c]*py[c]-px[p]*px[p]-py[p]*py[p];
  if(ax!=0){ for(int y=0;y<n;y++){ int num=rhs-ay*y; if(num%ax) continue; int x=num/ax; if(x<0||x>=n) continue; int q=x*n+y; if(q!=p&&q!=c) bump(q,sp,sc,delta); } }
  else { for(int x=0;x<n;x++){ int num=rhs-ax*x; if(num%ay) continue; int y=num/ay; if(y<0||y>=n) continue; int q=x*n+y; if(q!=p&&q!=c) bump(q,sp,sc,delta); } } }
static void add_point(int r){ int sl=m_; S[sl]=r; inS[r]=1; slot[r]=sl; memset(G+(size_t)sl*np,0,sizeof(int)*np);
  for(int i=0;i<sl;i++) apply_pair(r,S[i],sl,i,+1); m_++; }
static void remove_slot(int sl){ int p=S[sl];
  for(int i=0;i<m_;i++){ if(i==sl) continue; apply_pair(p,S[i],sl,i,-1); }
  inS[p]=0; m_--; if(sl!=m_){ S[sl]=S[m_]; slot[S[sl]]=sl; memcpy(G+(size_t)sl*np,G+(size_t)m_*np,sizeof(int)*np); } }
static inline int mirror(int q){ return px[q]*n+(n-1-py[q]); }
static void add_unit(int q){ add_point(q); if(SYM) add_point(mirror(q)); }
static void remove_unit(int q){ remove_slot(slot[q]); if(SYM) remove_slot(slot[mirror(q)]); }
static ll cur_cost(void){ ll c=0; for(int i=0;i<m_;i++) c+=F[S[i]]; return c; }
static int bruteforce_ok(void){
  static int seen[2*MAXP*2]; static int stamp=0;
  for(int i=0;i<m_;i++){ stamp++; for(int j=0;j<m_;j++){ if(i==j) continue; int d=dist2(S[i],S[j]); if(seen[d]==stamp) return 0; seen[d]=stamp; } }
  return 1; }
static void print_sol(FILE*f){ fprintf(f,"{\"n\": %d, \"k\": %d, \"points\": [",n,m_); for(int i=0;i<m_;i++) fprintf(f,"%s[%d, %d]",i?", ":"",px[S[i]],py[S[i]]); fprintf(f,"]}\n"); fflush(f); }
static double elapsed(clock_t t0){ return (double)(clock()-t0)/CLOCKS_PER_SEC; }
/* units: representatives of the moves (all points, or y < n/2 in SYM mode) */
static int nunits, unit[MAXP];
static int unit_F(int q){ if(!SYM) return F[q]; int qm=mirror(q); add_point(q); int f=F[qm]; remove_slot(m_-1); return F[q]+f; }
static long nodes, node_budget=20000; static int order[MAXP], rank_[MAXP];
static void shuffle_order(void){ for(int i=0;i<nunits;i++) order[i]=unit[i]; for(int i=nunits-1;i>0;i--){ int j=rnd()%(i+1); int t=order[i]; order[i]=order[j]; order[j]=t; } for(int i=0;i<nunits;i++) rank_[order[i]]=i; }
static int dfs(int need, int from){
  if(need==0) return 1; if(nodes>node_budget) return 0;
  int cnt=0; for(int pos=from;pos<nunits;pos++){ int q=order[pos]; if(!inS[q]&&F[q]==0) cnt++; }
  if(cnt<need) return 0;
  for(int pos=from;pos<nunits;pos++){ int q=order[pos]; if(inS[q]||F[q]!=0) continue;
    if(SYM && unit_F(q)!=0) continue;
    nodes++; add_unit(q); if(dfs(need-1,pos+1)) return 1; remove_unit(q); if(nodes>node_budget) return 0; }
  return 0; }
static long repairs_tried=0, repairs_ok=0;
static int exact_repair(int rmax){
  int V[MAXK], nv=0; for(int i=0;i<m_;i++){ int q=S[i]; if(F[q]<=0) continue; if(SYM && py[q]>=n/2) q=mirror(q); int dup=0; for(int j=0;j<nv;j++) if(V[j]==q) dup=1; if(!dup) V[nv++]=q; }
  if(nv==0) return 1; if(nv>12) return 0; repairs_tried++;
  for(int r=1;r<=rmax&&r<=nv;r++){ int c[8]; for(int i=0;i<r;i++) c[i]=i;
    while(1){ int removed[8]; for(int i=0;i<r;i++) removed[i]=V[c[i]];
      for(int i=0;i<r;i++) remove_unit(removed[i]);
      if(cur_cost()==0){ shuffle_order(); nodes=0; if(dfs(r,0)){ repairs_ok++; return 1; } }
      for(int i=0;i<r;i++) add_unit(removed[i]);
      int i=r-1; while(i>=0&&c[i]==nv-r+i) i--; if(i<0) break; c[i]++; for(int j=i+1;j<r;j++) c[j]=c[j-1]+1; } }
  return 0; }
static int best_new_unit(void){ int best=-1,bv=1<<30,cnt=0; for(int t=0;t<nunits;t++){ int q=unit[t]; if(inS[q]) continue; int f=SYM?F[q]+F[mirror(q)]:F[q]; if(f<bv){bv=f;best=q;cnt=1;} else if(f==bv){ cnt++; if(rnd()%cnt==0) best=q; } } return best; }
int main(int argc,char**argv){
  if(argc<5){ fprintf(stderr,"usage: iso2 n k seconds seed [initfile]\n"); return 2; }
  n=atoi(argv[1]); K=atoi(argv[2]); double secs=atof(argv[3]); rs=strtoull(argv[4],0,10)*2654435761ULL+88172645463325252ULL; np=n*n;
  SYM=getenv("SYM")?atoi(getenv("SYM")):0;
  if(np>MAXP||K>=MAXK||K<3){ fprintf(stderr,"bad n/k\n"); return 2; }
  if(SYM&&(n%2||K%2)){ fprintf(stderr,"SYM needs even n and k\n"); return 2; }
  int idx=0; for(int x=0;x<n;x++)for(int y=0;y<n;y++){px[idx]=x;py[idx]=y;idx++;}
  build_circles(); G=calloc((size_t)MAXK*np,sizeof(int)); m_=0;
  nunits=0; for(int q=0;q<np;q++) if(!SYM||py[q]<n/2) unit[nunits++]=q;
  int TEN_REM=getenv("TEN_REM")?atoi(getenv("TEN_REM")):2, TEN_ADD=getenv("TEN_ADD")?atoi(getenv("TEN_ADD")):(SYM?K/4:K/2)+2; long PERT=getenv("PERT")?atol(getenv("PERT")):5000;
  int REPAIR_MAX=getenv("REPAIR_MAX")?atoi(getenv("REPAIR_MAX")):9, RMAXR=getenv("RMAXR")?atoi(getenv("RMAXR")):3; int KMAX=getenv("KMAX")?atoi(getenv("KMAX")):K;
  if(KMAX>=MAXK) KMAX=MAXK-2;
  if(argc>5){ FILE*f=fopen(argv[5],"r"); if(!f){ fprintf(stderr,"cannot open %s\n",argv[5]); return 2; } int x,y; while(fscanf(f,"%d %d",&x,&y)==2){ if(x<0||y<0||x>=n||y>=n) continue; int q=x*n+y; if(SYM&&py[q]>=n/2) q=mirror(q); if(!inS[q]&&m_+(SYM?2:1)<=K) add_unit(q);} fclose(f); }
  while(m_<K) add_unit(best_new_unit());
  clock_t t0=clock(); long it=0; ll bestcost=1LL<<60; long since=0, last_repair=-1000; int tenure_add=TEN_ADD, tenure_rem=TEN_REM;
  while(1){
    ll cost=cur_cost();
    if(cost<bestcost){ bestcost=cost; since=0; fprintf(stderr,"k=%d it=%ld violations=%lld t=%.1fs\n",m_,it,cost/3,elapsed(t0)); }
    if(cost>0 && cost<=REPAIR_MAX && it-last_repair>=50){ last_repair=it; if(exact_repair(RMAXR)) cost=cur_cost(); }
    if(cost==0){
      if(!bruteforce_ok()){ fprintf(stderr,"SELFCHECK FAIL\n"); print_sol(stderr); return 3; }
      print_sol(stdout); fprintf(stderr,"FOUND n=%d k=%d it=%ld t=%.1fs repairs=%ld/%ld selfcheck=ok\n",n,m_,it,elapsed(t0),repairs_ok,repairs_tried);
      if(m_>=KMAX) return 0;
      add_unit(best_new_unit()); bestcost=1LL<<60; since=0; memset(tabu_add,0,sizeof(tabu_add)); memset(tabu_rem,0,sizeof(tabu_rem)); continue; }
    if((it&1023)==0 && it){ double e=elapsed(t0); fprintf(stderr,"rate k=%d it=%ld %.0f it/s violations=%lld best=%lld t=%.0fs\n",m_,it,it/e,cost/3,bestcost/3,e); }
    if(elapsed(t0)>secs){ fprintf(stderr,"TIMEOUT k=%d best violations=%lld it=%ld\n",m_,bestcost/3,it); return 1; }
    if(++since>PERT){ int reps=SYM?1+(int)(rnd()%2):2+(int)(rnd()%3); for(int t=0;t<reps;t++){ int p=S[rnd()%m_]; if(SYM&&py[p]>=n/2) p=mirror(p); remove_unit(p); int r; do r=unit[rnd()%nunits]; while(inS[r]); add_unit(r); tabu_add[p]=it+tenure_add; } since=0; it++; continue; }
    ll bestd=1LL<<60; int bi=-1,br=-1,cnt=0;
    for(int i=0;i<m_;i++){ int c=S[i]; if(SYM&&py[c]>=n/2) continue; int tr=tabu_rem[c]>it; const int*Gi=G+(size_t)i*np;
      ll ci; const int*Gj=0; if(SYM){ int i2=slot[mirror(c)]; Gj=G+(size_t)i2*np; ci=F[c]+F[mirror(c)]; } else ci=F[c];
      for(int t=0;t<nunits;t++){ int r=unit[t]; if(inS[r]) continue; ll d;
        if(SYM){ int rm=mirror(r); d=(F[r]-Gi[r]-Gj[r])+(F[rm]-Gi[rm]-Gj[rm])-ci; } else d=(F[r]-Gi[r])-ci;
        int tabu=tr||tabu_add[r]>it; if(tabu && cost+3*d>=bestcost) continue;
        if(d<bestd){bestd=d;bi=i;br=r;cnt=1;} else if(d==bestd){cnt++; if(rnd()%cnt==0){bi=i;br=r;}} } }
    if(bi<0){ it++; continue; }
    int p=S[bi]; remove_unit(p); add_unit(br); tabu_add[p]=it+tenure_add+(int)(rnd()%5); tabu_rem[br]=it+tenure_rem; it++;
  }
}
