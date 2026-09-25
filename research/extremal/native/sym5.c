/* sym5: iterated local search over centrally symmetric subsets of [n]^3 with no
 * five points on a common sphere or plane (5x5 determinant with rows
 * (x,y,z,x^2+y^2+z^2,1) nonzero for every 5-subset).
 *
 * The set is a union of orbit pairs {p, s(p)}, s(p) = (n-1,n-1,n-1) - p; for odd n
 * the fixed centre is excluded.  The set is kept valid at all times:
 *   F[q] = #{4-subsets T of S : det(T u {q}) = 0}  (maintained incrementally via Z(T))
 *   pair {p, p'} is addable iff F[p] = F[p'] = 0 and det(U u {p,p'}) != 0 for
 *   every 3-subset U of S (checked exactly with a multilinear expansion).
 * Loop: ruin r in {1,2,3} random pairs, rebuild greedily with random addable pairs
 * (just-removed pairs tabu), accept if not smaller, restart after STALL idle
 * iterations.  At each rebuilt local optimum single extra points (F = 0) are tried
 * to reach odd sizes.  Every printed set is re-verified by brute force.
 * Usage: sym5 n target seconds seed      env: STALL (default 800), PRINT_MIN
 * Compile-time caps: -DMAXP (grid points, default 4096 = 16^3), -DMAXK (set size + 1).
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
static int n, np; static int px[MAXP], py[MAXP], pz[MAXP]; static ll pw[MAXP]; static int sig[MAXP], shell[MAXP];
static int S[MAXK], inS[MAXP], slot[MAXP], m_; static int F[MAXP];
static unsigned long long rs;
static inline unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static ll det3(ll m[3][3]){ return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]); }
static ll det4(ll m[4][4]){ ll s=0; for(int c=0;c<4;c++){ ll sub[3][3]; for(int r=1;r<4;r++){ int cc=0; for(int j=0;j<4;j++) if(j!=c) sub[r-1][cc++]=m[r][j]; } ll t=m[0][c]*det3(sub); s+=(c&1)?-t:t; } return s; }
static inline ll isq(ll v){ ll r=(ll)sqrt((double)v); while(r*r>v) r--; while((r+1)*(r+1)<=v) r++; return r; }
static int lifted_rank_le3(const int P[4]){
  ll D[3][4]; for(int r=0;r<3;r++){ int e=P[r+1], a=P[0]; D[r][0]=px[e]-px[a]; D[r][1]=py[e]-py[a]; D[r][2]=pz[e]-pz[a]; D[r][3]=pw[e]-pw[a]; }
  static const int cols[4][3]={{0,1,2},{0,1,3},{0,2,3},{1,2,3}};
  for(int c=0;c<4;c++){ ll m[3][3]; for(int r=0;r<3;r++) for(int j=0;j<3;j++) m[r][j]=D[r][cols[c][j]]; if(det3(m)!=0) return 0; }
  return 1; }
/* ---- Z(T): grid points q with det(T u {q}) = 0, cached by sorted 4-tuple ---- */
typedef struct { unsigned long long key; int off, len; } Ent;
static Ent *tab; static size_t tabsz=1<<23, tabcnt; static int *pool; static size_t poolsz=1<<26, poolused;
static int zbuf[MAXP];
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
  if(lifted_rank_le3(P)){ for(int q2=0;q2<np;q2++) out[m++]=q2; return m; }
  ll Nn[3]={0,0,0}; int found=0;
  for(int i=0;i<4&&!found;i++)for(int j=i+1;j<4&&!found;j++)for(int k=j+1;k<4&&!found;k++){
    ll u[3]={px[P[j]]-px[P[i]],py[P[j]]-py[P[i]],pz[P[j]]-pz[P[i]]}, v[3]={px[P[k]]-px[P[i]],py[P[k]]-py[P[i]],pz[P[k]]-pz[P[i]]};
    Nn[0]=u[1]*v[2]-u[2]*v[1]; Nn[1]=u[2]*v[0]-u[0]*v[2]; Nn[2]=u[0]*v[1]-u[1]*v[0]; if(Nn[0]||Nn[1]||Nn[2]) found=1; }
  ll off=Nn[0]*px[a]+Nn[1]*py[a]+Nn[2]*pz[a];
  /* solve the plane equation for the coordinate with the largest |normal| component */
  int w=0; for(int t=1;t<3;t++) if(llabs(Nn[t])>llabs(Nn[w])) w=t;
  int u_=(w+1)%3, v_=(w+2)%3;
  for(int U=0;U<n;U++) for(int V=0;V<n;V++){ ll num=off-Nn[u_]*U-Nn[v_]*V; if(num%Nn[w]) continue; ll W=num/Nn[w]; if(W<0||W>=n) continue;
    int c3[3]; c3[w]=(int)W; c3[u_]=U; c3[v_]=V; out[m++]=c3[0]*n*n+c3[1]*n+c3[2]; }
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
static void add_point(int r){
  for(int i=0;i<m_;i++)for(int j=i+1;j<m_;j++)for(int k=j+1;k<m_;k++){ int len; const int*z=getZ(S[i],S[j],S[k],r,&len); for(int t=0;t<len;t++) F[z[t]]++; }
  S[m_]=r; inS[r]=1; slot[r]=m_; m_++; }
static void remove_point(int p){ int sl=slot[p];
  for(int i=0;i<m_;i++){ if(i==sl) continue; for(int j=i+1;j<m_;j++){ if(j==sl) continue; for(int k=j+1;k<m_;k++){ if(k==sl) continue; int len; const int*z=getZ(S[i],S[j],S[k],p,&len); for(int t=0;t<len;t++) F[z[t]]--; } } }
  inS[p]=0; m_--; if(sl!=m_){ S[sl]=S[m_]; slot[S[sl]]=sl; } }
/* exact test: det(U u {p, q}) != 0 for every 3-subset U of S (multilinear in the rows) */
static int pair_dets_ok(int p,int q){
  ll v[4]={px[q]-px[p],py[q]-py[p],pz[q]-pz[p],pw[q]-pw[p]}; static ll u[MAXK][4];
  for(int i=0;i<m_;i++){ int s=S[i]; u[i][0]=px[s]-px[p]; u[i][1]=py[s]-py[p]; u[i][2]=pz[s]-pz[p]; u[i][3]=pw[s]-pw[p]; }
  for(int i=0;i<m_;i++){ ll B[4][4]; /* bivector of (u_i, v): B[a][b] = u_i[a] v[b] - u_i[b] v[a] */
    for(int a=0;a<4;a++) for(int b=0;b<4;b++) B[a][b]=u[i][a]*v[b]-u[i][b]*v[a];
    for(int j=i+1;j<m_;j++){ /* trivector (u_i, v, u_j) -> dual vector w with det(u_i, v, u_j, x) = w . x */
      const ll *y=u[j]; ll w0= (B[1][2]*y[3]-B[1][3]*y[2]+B[2][3]*y[1]);
      ll w1=-(B[0][2]*y[3]-B[0][3]*y[2]+B[2][3]*y[0]);
      ll w2= (B[0][1]*y[3]-B[0][3]*y[1]+B[1][3]*y[0]);
      ll w3=-(B[0][1]*y[2]-B[0][2]*y[1]+B[1][2]*y[0]);
      for(int k=j+1;k<m_;k++){ const ll *x=u[k]; if(w0*x[0]+w1*x[1]+w2*x[2]+w3*x[3]==0) return 0; } } }
  return 1; }
static int bruteforce_ok(void){
  for(int a=0;a<m_;a++) for(int b=a+1;b<m_;b++) for(int c=b+1;c<m_;c++) for(int d=c+1;d<m_;d++) for(int e=d+1;e<m_;e++){
    int R[4]={S[b],S[c],S[d],S[e]}; int A=S[a]; ll M[4][4];
    for(int r=0;r<4;r++){ M[r][0]=px[R[r]]-px[A]; M[r][1]=py[R[r]]-py[A]; M[r][2]=pz[R[r]]-pz[A]; M[r][3]=pw[R[r]]-pw[A]; }
    if(det4(M)==0) return 0; }
  return 1; }
static void print_set(FILE*f,const int*P,int k,const char*tag){ fprintf(f,"{\"n\": %d, \"k\": %d, \"tag\": \"%s\", \"points\": [",n,k,tag); for(int i=0;i<k;i++) fprintf(f,"%s[%d, %d, %d]",i?", ":"",px[P[i]],py[P[i]],pz[P[i]]); fprintf(f,"]}\n"); fflush(f); }
static double elapsed(clock_t t0){ return (double)(clock()-t0)/CLOCKS_PER_SEC; }
static int reps[MAXP], nreps; static int shell_used[1<<16]; static long tabu_until[MAXP]; static long iter_no;
static int pair_addable(int p){ int q=sig[p];
  if(inS[p]||F[p]||F[q]||shell_used[shell[p]]) return 0;
  return pair_dets_ok(p,q); }
static void add_pair(int p){ add_point(p); add_point(sig[p]); shell_used[shell[p]]=1; }
static void remove_pair(int p){ remove_point(sig[p]); remove_point(p); shell_used[shell[p]]=0; }
static int rep_of(int q){ return q<sig[q]?q:sig[q]; }
static int order[MAXP];
/* greedy randomized rebuild: add random addable (non-tabu) pairs until none is left */
static void rebuild(void){
  while(1){ int cnt=0; for(int i=0;i<nreps;i++){ int p=reps[i]; if(!inS[p]&&!F[p]&&!F[sig[p]]&&!shell_used[shell[p]]&&tabu_until[p]<=iter_no) order[cnt++]=p; }
    int added=0;
    while(cnt>0){ int j=rnd()%cnt; int p=order[j]; order[j]=order[--cnt]; if(pair_addable(p)){ add_pair(p); added=1; break; } }
    if(!added) return; } }
int main(int argc,char**argv){
  if(argc<5){ fprintf(stderr,"usage: sym5 n target seconds seed\n"); return 2; }
  n=atoi(argv[1]); int target=atoi(argv[2]); double secs=atof(argv[3]); rs=strtoull(argv[4],0,10)*2654435761ULL+88172645463325252ULL; np=n*n*n;
  if(n<3||np>MAXP||target>=MAXK){ fprintf(stderr,"bad n/target\n"); return 2; }
  long STALL=getenv("STALL")?atol(getenv("STALL")):800; int PRINT_MIN=getenv("PRINT_MIN")?atoi(getenv("PRINT_MIN")):target;
  tab=calloc(tabsz,sizeof(Ent)); pool=malloc(poolsz*sizeof(int));
  int idx=0; for(int x=0;x<n;x++)for(int y=0;y<n;y++)for(int z=0;z<n;z++){px[idx]=x;py[idx]=y;pz[idx]=z;pw[idx]=(ll)x*x+(ll)y*y+(ll)z*z;idx++;}
  for(int q=0;q<np;q++){ int x=n-1-px[q], y=n-1-py[q], z=n-1-pz[q]; sig[q]=x*n*n+y*n+z; int a=2*px[q]-(n-1), b=2*py[q]-(n-1), c=2*pz[q]-(n-1); shell[q]=a*a+b*b+c*c; }
  nreps=0; for(int q=0;q<np;q++) if(q<sig[q]) reps[nreps++]=q;
  clock_t t0=clock(); int best=0, best_printed=0; long restarts=0, found_target=0; int saved[MAXK], nsaved; int removed[3];
  long since=0; m_=0; memset(F,0,sizeof(F)); rebuild();
  while(elapsed(t0)<secs){
    iter_no++;
    /* odd-size extension: any single point with F = 0 */
    int ext=-1; for(int q=0;q<np;q++) if(!inS[q]&&!F[q]){ ext=q; break; }
    int size=m_+(ext>=0);
    if(size>best || (size>=PRINT_MIN && size>best_printed) || (size>=target && found_target<50)){
      int P[MAXK]; memcpy(P,S,sizeof(int)*m_); int k=m_;
      if(ext>=0){ add_point(ext); memcpy(P,S,sizeof(int)*m_); k=m_; }
      int ok=bruteforce_ok();
      if(ext>=0) remove_point(ext);
      if(!ok){ fprintf(stderr,"SELFCHECK FAIL at size %d\n",k); print_set(stderr,P,k,"fail"); return 3; }
      if(size>best){ best=size; fprintf(stderr,"best=%d (pairs=%d%s) iter=%ld restarts=%ld t=%.1fs\n",best,m_/2,ext>=0?" +1":"",iter_no,restarts,elapsed(t0)); }
      if(size>=PRINT_MIN && (size>best_printed || size>=target)){ print_set(stdout,P,k,ext>=0?"sym+1":"sym"); if(size>best_printed) best_printed=size; }
      if(size>=target){ found_target++; fprintf(stderr,"FOUND n=%d k=%d iter=%ld t=%.1fs selfcheck=ok\n",n,size,iter_no,elapsed(t0)); }
    }
    if(++since>STALL){ /* restart */ while(m_>0) remove_pair(rep_of(S[0])); memset(tabu_until,0,sizeof(tabu_until)); rebuild(); since=0; restarts++; continue; }
    nsaved=m_; memcpy(saved,S,sizeof(int)*m_);
    int r=1+(int)(rnd()%3); if(r>m_/2) r=m_/2;
    for(int t=0;t<r;t++){ int p=rep_of(S[rnd()%m_]); removed[t]=p; remove_pair(p); tabu_until[p]=iter_no+1; }
    rebuild();
    if(m_<nsaved){ /* revert */
      int cur[MAXK], nc=m_; memcpy(cur,S,sizeof(int)*m_);
      for(int i=0;i<nc;i++){ int p=cur[i]; if(p<sig[p]){ int keep=0; for(int j=0;j<nsaved;j++) if(saved[j]==p) keep=1; if(!keep) remove_pair(p); } }
      for(int t=0;t<r;t++) if(!inS[removed[t]]) add_pair(removed[t]);
    } else if(m_>nsaved) since=0;
    if((iter_no&1023)==0){ fprintf(stderr,"iter=%ld size=%d best=%d restarts=%ld t=%.0fs\n",iter_no,m_,best,restarts,elapsed(t0)); }
  }
  fprintf(stderr,"TIMEOUT best=%d iter=%ld restarts=%ld\n",best,iter_no,restarts);
  return best>=target?0:1; }
