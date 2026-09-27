/*
 * c6-enum: layer-enumeration search for 19-subsets of {0..5}^3
 * with no 5 points on a common sphere or plane.
 *
 * Port of layer_enum5.c (n=5, k=15) to n=6, k=19.
 *
 * Model: 5 points are cospherical/coplanar iff the 5x5 determinant with rows
 * (x,y,z,x^2+y^2+z^2,1) vanishes.  For a 4-set T and point q,
 * f(q) = det4([q - t0, t1 - t0, t2 - t0, t3 - t0]) on lifted coords
 * (x,y,z,r^2) is a linear form in q; its zero set is the sphere/plane
 * through T (the whole grid when T is degenerate: concyclic or collinear).
 *
 * Method: fix z-layer 0 to one canonical subset per D4 orbit, extend layers
 * 1..5.  Bad 5-subsets with i>=1 new points are detected exactly as in n=5:
 *   i=1:  C & block1(U) != 0     (block1 = union of sphereSet(T4), T4 <= U)
 *   i=2:  some p in C has Mp[p] & C != 0   (Mp[p] = union over T3 <= U of
 *         sphereSet(T3+{p}) restricted to layer j)
 *   i=3:  some triple Tr <= C and u in U: sphereSet(Tr+{u}) hits U
 *   i=4:  sphereSet(C) hits U
 * All lookups go through a precomputed table SPH[rank4]*6 -> per-layer
 * 36-bit masks (u64).  N4 = C(216,4) = 88,201,170 entries, 48 B each,
 * ~4.23 GB flat table (fits the 36 GB host; cheaper at query time than a
 * memoized sphere-key hash, which would pay hashing on ~1e10 lookups).
 *
 * Prunes: size bounds to reach K, |L5| <= |L0| (z-flip), layer-1+ candidates
 * canonicalized under the D4 stabilizer of the placed set.
 *
 * DIFFERENCE FROM n=5 (soundness fix, see memo.md):
 *   the admissibility prune's "low" bound for future layer k now charges the
 *   capacity of ALL unplaced layers except k (layers j..5 minus k, with layer
 *   5 capped at |L0|).  The n=5 code charged only layers strictly after k
 *   (4*(4-k)), which overestimates low and is not a valid lower bound on
 *   |L_k|; here we use cap_others = 4*(4-j)+min(|L0|,4) for k<5 and
 *   cap_others = 4*(5-j) for k=5, i.e. low = K - m - cap_others.  Weaker but
 *   sound; we count firings for the memo.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <stdatomic.h>
#include <time.h>
#include <unistd.h>

typedef uint32_t u32; typedef uint64_t u64; typedef int64_t i64; typedef uint8_t u8;

#define NP 216
#define NZ 6
#define LP 36                 /* points per z-layer */
#define N4 88201170           /* C(216,4) */
#define ALL36 ((u64)0xFFFFFFFFF)   /* (1<<36)-1 */

static int  gx[NP], gy[NP], gz[NP], gr2[NP];
static u64  BIN[NP + 1][5];
static u64 *SPH;             /* SPH[rank*6 + layer] : 36-bit mask */

static inline int rank4(int a, int b, int c, int d)   /* a<b<c<d */
{
    return (int)(BIN[a][1] + BIN[b][2] + BIN[c][3] + BIN[d][4]);
}

static inline i64 det3(i64 a0,i64 a1,i64 a2, i64 b0,i64 b1,i64 b2,
                       i64 c0,i64 c1,i64 c2)
{
    return a0*(b1*c2 - b2*c1) - a1*(b0*c2 - b2*c0) + a2*(b0*c1 - b1*c0);
}

static inline i64 lift(int p, int j)
{
    switch (j) { case 0: return gx[p]; case 1: return gy[p];
                 case 2: return gz[p]; default: return gr2[p]; }
}

/* ---------------- sphere table build ---------------- */

static void build_range(int a0, int a1)
{
    for (int a = a0; a < a1; a++)
    for (int b = a + 1; b < NP-2; b++)
    for (int c = b + 1; c < NP-1; c++)
    for (int d = c + 1; d < NP; d++) {
        int r = rank4(a, b, c, d);
        u64 *dst = SPH + (size_t)r * NZ;
        i64 v[3][4];
        for (int i = 0; i < 3; i++) {
            int p = i == 0 ? b : i == 1 ? c : d;
            for (int j = 0; j < 4; j++) v[i][j] = lift(p, j) - lift(a, j);
        }
        i64 D0 = det3(v[0][1],v[0][2],v[0][3], v[1][1],v[1][2],v[1][3], v[2][1],v[2][2],v[2][3]);
        i64 D1 = det3(v[0][0],v[0][2],v[0][3], v[1][0],v[1][2],v[1][3], v[2][0],v[2][2],v[2][3]);
        i64 D2 = det3(v[0][0],v[0][1],v[0][3], v[1][0],v[1][1],v[1][3], v[2][0],v[2][1],v[2][3]);
        i64 D3 = det3(v[0][0],v[0][1],v[0][2], v[1][0],v[1][1],v[1][2], v[2][0],v[2][1],v[2][2]);
        if ((D0 | D1 | D2 | D3) == 0) {
            for (int k = 0; k < NZ; k++) dst[k] = ALL36;
        } else {
            i64 c0 = D0, c1 = -D1, c2 = D2, c3 = -D3;
            i64 E = -(c0*gx[a] + c1*gy[a] + c2*gz[a] + c3*gr2[a]);
            u64 m[NZ]; for (int k=0;k<NZ;k++) m[k]=0;
            for (int q = 0; q < NP; q++) {
                if (c0*gx[q] + c1*gy[q] + c2*gz[q] + c3*gr2[q] + E == 0)
                    m[q / LP] |= 1ull << (q % LP);
            }
            for (int k=0;k<NZ;k++) dst[k]=m[k];
        }
        dst[a/LP] &= ~(1ull << (a%LP));
        dst[b/LP] &= ~(1ull << (b%LP));
        dst[c/LP] &= ~(1ull << (c%LP));
        dst[d/LP] &= ~(1ull << (d%LP));
    }
}

/* independent recompute of one table entry for self-test */
static i64 det4x4(const i64 m[4][4]);

static void recompute_entry(int a,int b,int c,int d,u64 out[NZ])
{
    i64 v0[4] = {gx[a],gy[a],gz[a],gr2[a]};
    i64 v[3][4]; int ps[3]={b,c,d};
    for (int i=0;i<3;i++) for(int j=0;j<4;j++) v[i][j]=lift(ps[i],j)-v0[j];
    for (int k=0;k<NZ;k++) out[k]=0;
    for (int q=0;q<NP;q++) {
        if (q==a||q==b||q==c||q==d) continue;
        i64 w[4]={gx[q]-v0[0],gy[q]-v0[1],gz[q]-v0[2],gr2[q]-v0[3]};
        i64 m[4][4];
        for(int j=0;j<4;j++){m[0][j]=w[j];m[1][j]=v[0][j];m[2][j]=v[1][j];m[3][j]=v[2][j];}
        if (det4x4(m)==0) out[q/LP] |= 1ull<<(q%LP);
    }
}

static i64 det4x4(const i64 m[4][4])
{
    i64 a=m[0][0],b=m[0][1],c=m[0][2],d=m[0][3];
    i64 e=m[1][0],f=m[1][1],g=m[1][2],h=m[1][3];
    i64 i=m[2][0],j=m[2][1],k=m[2][2],l=m[2][3];
    i64 m0=m[3][0],n0=m[3][1],o=m[3][2],p=m[3][3];
    i64 kp_lo=k*p-l*o, jp_ln=j*p-l*n0, jo_kn=j*o-k*n0;
    i64 ip_lm=i*p-l*m0, io_km=i*o-k*m0, in_jm=i*n0-j*m0;
    return a*(f*kp_lo - g*jp_ln + h*jo_kn)
         - b*(e*kp_lo - g*ip_lm + h*io_km)
         + c*(e*jp_ln - f*ip_lm + h*in_jm)
         - d*(e*jo_kn - f*io_km + g*in_jm);
}

/* ---------------- candidates ---------------- */

/* ok4[r] = 1 iff the 4-subset of layer positions with combinadic rank r is
   non-degenerate (not concyclic/collinear): layer-valid candidates. */
static u8 ok4bit[58905];   /* C(36,4)=58905 entries, one byte each */
static u64 LBIN[LP + 1][5];
static inline int lrank4(int a,int b,int c,int d)
{
    return (int)(LBIN[a][1]+LBIN[b][2]+LBIN[c][3]+LBIN[d][4]);
}

#define MAXC 100000
typedef struct {
    u64 mask;
    u8  sz;
    u8  np, nt;
    u8  pr[6][2];    /* position pairs */
    u8  tr[4][3];    /* position triples */
    u8  qd[4];       /* positions when sz==4 */
    u64 d4[8];       /* images under square symmetries */
} Cand;

static Cand cands[MAXC];
static int  ncand;
static int  sz_off[5], sz_cnt[5];
static int  reps[MAXC]; static int nrep;
static u8   rep_stab[MAXC];

static int sympos(int g, int pos)
{
    int x = pos % 6, y = pos / 6, nx, ny;
    switch (g) {
    case 0: nx=x;   ny=y;   break;
    case 1: nx=5-y; ny=x;   break;
    case 2: nx=5-x; ny=5-y; break;
    case 3: nx=y;   ny=5-x; break;
    case 4: nx=5-x; ny=y;   break;
    case 5: nx=x;   ny=5-y; break;
    case 6: nx=y;   ny=x;   break;
    default:nx=5-y; ny=5-x; break;
    }
    return ny * 6 + nx;
}

static u64 symmask(int g, u64 m)
{
    u64 r = 0;
    while (m) { int p = __builtin_ctzll(m); m &= m-1; r |= 1ull << sympos(g, p); }
    return r;
}

/* layer-subset validity: 4-subsets must not be concyclic/collinear */
static int layer_ok4(int a,int b,int c,int d)
{
    /* points at z=0; valid iff rank == 3 iff the (x,y,r2) minor != 0 */
    i64 v[3][3]; int ps[3]={b,c,d};
    for (int i=0;i<3;i++){
        int p=ps[i];
        v[i][0]=gx[p]-gx[a]; v[i][1]=gy[p]-gy[a]; v[i][2]=gr2[p]-gr2[a];
    }
    return det3(v[0][0],v[0][1],v[0][2],v[1][0],v[1][1],v[1][2],v[2][0],v[2][1],v[2][2]) != 0;
}

static void add_cand(u64 mask, const int *ps, int sz)
{
    if (ncand >= MAXC) { fprintf(stderr,"MAXC overflow\n"); exit(2); }
    Cand *cd = &cands[ncand];
    cd->mask = mask; cd->sz = sz;
    cd->np = 0; cd->nt = 0;
    for (int i=0;i<sz;i++) for(int j=i+1;j<sz;j++){
        cd->pr[cd->np][0]=ps[i]; cd->pr[cd->np][1]=ps[j]; cd->np++; }
    for (int i=0;i<sz;i++) for(int j=i+1;j<sz;j++) for(int k=j+1;k<sz;k++){
        cd->tr[cd->nt][0]=ps[i]; cd->tr[cd->nt][1]=ps[j]; cd->tr[cd->nt][2]=ps[k]; cd->nt++; }
    if (sz==4) for(int i=0;i<4;i++) cd->qd[i]=ps[i];
    for (int g=0;g<8;g++) cd->d4[g]=symmask(g,mask);
    ncand++;
}

static void build_candidates(void)
{
    int ps[4];
    for (int a=0;a<LP;a++){ ps[0]=a; add_cand(1ull<<a,ps,1); }
    for (int a=0;a<LP;a++) for(int b=a+1;b<LP;b++){ ps[0]=a;ps[1]=b;
        add_cand((1ull<<a)|(1ull<<b),ps,2); }
    for (int a=0;a<LP;a++) for(int b=a+1;b<LP;b++) for(int c=b+1;c<LP;c++){
        ps[0]=a;ps[1]=b;ps[2]=c; add_cand((1ull<<a)|(1ull<<b)|(1ull<<c),ps,3); }
    int total4=0;
    memset(ok4bit,0,sizeof ok4bit);
    for (int a=0;a<LP;a++) for(int b=a+1;b<LP;b++) for(int c=b+1;c<LP;c++)
    for(int d=c+1;d<LP;d++){ total4++;
        if(!layer_ok4(a,b,c,d)) continue;
        ok4bit[lrank4(a,b,c,d)] = 1;
        ps[0]=a;ps[1]=b;ps[2]=c;ps[3]=d;
        add_cand((1ull<<a)|(1ull<<b)|(1ull<<c)|(1ull<<d),ps,4); }
    sz_off[0]=0; sz_cnt[0]=0;
    int idx=0;
    for (int s=1;s<=4;s++){ sz_off[s]=idx; int c=0;
        while (idx<ncand && cands[idx].sz==s){ idx++; c++; }
        sz_cnt[s]=c; }
    fprintf(stderr,"candidates: total=%d size4: total=%d kept=%d\n",
            ncand, total4, sz_cnt[4]);
}

/* ---------------- search state ---------------- */

typedef struct {
    int m;
    int pts[26];
    u64 L[NZ];
    int l0sz;
    u64 nodes[NZ+1];
    u64 bf[NZ];   /* union of SPH masks of all placed 4-subsets, per layer */
} St;

static _Atomic int found_flag;
static _Atomic int next_rep;
static _Atomic u64 orbits_done;
static int rep_lo=0, rep_hi=0;       /* process reps[rep_lo..rep_hi) */
static _Atomic u64 g_nodes[NZ+1];
static _Atomic u64 g_admiss_fire;     /* admissibility prune firings */
static int g_solution[26];
static pthread_mutex_t sol_mtx = PTHREAD_MUTEX_INITIALIZER;
static double deadline = 1e30;
static int K = 19;
static double t_start;

static double now_sec(void)
{
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts);
    return ts.tv_sec + ts.tv_nsec*1e-9;
}

static void record_solution(const St *st)
{
    pthread_mutex_lock(&sol_mtx);
    if (!atomic_load(&found_flag)) {
        atomic_store(&found_flag,1);
        memcpy(g_solution,st->pts,sizeof(int)*st->m);
        char fn[64]; snprintf(fn,sizeof fn,"solution_k%d.txt",K);
        FILE *f=fopen(fn,"w");
        if (f) {
            for (int i=0;i<st->m;i++)
                fprintf(f,"%d %d %d\n",gx[st->pts[i]],gy[st->pts[i]],gz[st->pts[i]]);
            fclose(f);
        }
        fprintf(stderr,"FOUND %d-set (m=%d):",K,st->m);
        for (int i=0;i<st->m;i++) fprintf(stderr," %d",st->pts[i]);
        fprintf(stderr,"\n");
    }
    pthread_mutex_unlock(&sol_mtx);
}


/* add_delta: propagate forbidden-position masks into st->bf[k], k>j, for a
   set C (mask, s points) being placed at layer j.  st->pts[0..m) = U only
   (call BEFORE extending pts).  Adds the SPH layer-k masks of every
   4-subset meeting C:
     1 C-point x 3 U-points:  PD[p][k] (accumulated during the Mp build)
     2 C-points x 2 U-points: direct rank4 loop (m>=2, s>=2)
     3 C-points x 1 U-point:  direct rank4 loop (m>=1, s>=3)
     4 C-points:              single rank4 (s==4)
*/
static void add_delta(St *st, int j, u64 C, int s, u64 PD[LP][NZ])
{
    const int m = st->m;
    u64 t;
    /* 1-of-C */
    for (t=C; t; ){ int p=__builtin_ctzll(t); t&=t-1;
        for (int k=j+1;k<NZ;k++) st->bf[k] |= PD[p][k]; }
    /* extract C positions once */
    int cp[4]; int cn=0;
    for (t=C; t; ){ cp[cn++]=__builtin_ctzll(t); t&=t-1; }
    /* 2-of-C x 2-of-U */
    if (s>=2 && m>=2) {
        for (int a=0;a<m-1;a++) for(int b=a+1;b<m;b++){
            size_t partial=(size_t)BIN[st->pts[a]][1]+BIN[st->pts[b]][2];
            for (int x=0;x<cn-1;x++) for(int y=x+1;y<cn;y++){
                const u64 *e=SPH+(size_t)(partial+(size_t)BIN[LP*j+cp[x]][3]+(size_t)BIN[LP*j+cp[y]][4])*NZ;
                for (int k=j+1;k<NZ;k++) st->bf[k] |= e[k];
            }
        }
    }
    /* 3-of-C x 1-of-U */
    if (s>=3 && m>=1) {
        for (int u=0;u<m;u++){
            for (int x=0;x<cn-2;x++) for(int y=x+1;y<cn-1;y++) for(int z=y+1;z<cn;z++){
                int r=rank4(st->pts[u], LP*j+cp[x], LP*j+cp[y], LP*j+cp[z]);
                const u64 *e=SPH+(size_t)r*NZ;
                for (int k=j+1;k<NZ;k++) st->bf[k] |= e[k];
            }
        }
    }
    /* 4-of-C */
    if (s==4) {
        int r=rank4(LP*j+cp[0],LP*j+cp[1],LP*j+cp[2],LP*j+cp[3]);
        const u64 *e=SPH+(size_t)r*NZ;
        for (int k=j+1;k<NZ;k++) st->bf[k] |= e[k];
    }
}

static void dfs(St *st, int j, u8 stab);   /* fwd */

/* On-the-fly subset enumerator over the allowed set A = ~blockf[j].
   Integrates the i=2 pair-block and i=3 triple-block checks incrementally.
   Only valid when stabU == 0 (no canonicalisation needed).               */
typedef struct {
    St *st;
    int j;
    const u64 *Mp;
    u64 (*PD)[NZ];  /* per-position future-layer deltas (from dfs frame) */
    int apos[LP];   /* sorted allowed positions */
    int nap;
    FILE *out;      /* non-NULL: collect accepted masks instead of recursing */
} GenCtx;

static void gen_rec(GenCtx *g, int sz, int lo, u64 P, u64 pairbad, int np)
{
    St *st = g->st;
    int m = st->m;
    if (np == sz) {
        /* completion checks */
        if (sz == 4) {
            int pp[4]; u64 t=P; int w=0;
            while(t){pp[w++]=__builtin_ctzll(t);t&=t-1;}
            if (!ok4bit[lrank4(pp[0],pp[1],pp[2],pp[3])]) return;
            if (m>=1) {                       /* i=4 */
                int r=rank4(LP*g->j+pp[0],LP*g->j+pp[1],LP*g->j+pp[2],LP*g->j+pp[3]);
                const u64 *e=SPH+(size_t)r*NZ;
                for(int k=0;k<g->j;k++) if(e[k]&st->L[k]) return;
            }
        }
        if (g->out) { fprintf(g->out, "%llu\n",(unsigned long long)P); return; }
        /* place: save bf, add C's delta, recurse, restore */
        u64 saved[NZ]; memcpy(saved, st->bf, sizeof saved);
        int s = __builtin_popcountll(P);
        add_delta(st, g->j, P, s, g->PD);
        int nm=m; u64 t=P;
        while(t){int p=__builtin_ctzll(t);t&=t-1;st->pts[nm++]=LP*g->j+p;}
        st->m=nm; st->L[g->j]=P;
        dfs(st,g->j+1,0);
        st->m=m; st->L[g->j]=0;
        memcpy(st->bf, saved, sizeof saved);
        return;
    }
    int rem = sz - np;
    for (int i = lo; i <= g->nap - rem; i++) {
        int p = g->apos[i];
        u64 pb = 1ull<<p;
        if (pairbad & pb) continue;            /* p forbidden by some q in P */
        if (g->Mp[p] & P) continue;            /* p forbids some q in P (i=2) */
        /* incremental i=3: each new triple {p,q,r}, q<r in P, vs every u in U */
        int ok = 1;
        if (m>=1 && np>=2) {
            int qs[3]; u64 t=P; int w=0;
            while(t){qs[w++]=__builtin_ctzll(t);t&=t-1;}
            int gp = LP*g->j + p;
            for (int a=0;a<w && ok;a++) for(int b=a+1;b<w && ok;b++){
                int gq = LP*g->j+qs[a], gr = LP*g->j+qs[b];
                for (int u=0;u<m;u++){
                    int rr=rank4(st->pts[u], gq, gr, gp);
                    const u64 *e=SPH+(size_t)rr*NZ;
                    for(int k=0;k<g->j;k++) if(e[k]&st->L[k]){ok=0;break;}
                    if(!ok) break;
                }
            }
        }
        if (!ok) continue;
        gen_rec(g, sz, i+1, P|pb, pairbad|g->Mp[p], np+1);
        if (atomic_load_explicit(&found_flag,memory_order_relaxed)) return;
    }
}


static void dfs(St *st, int j, u8 stab)
{
    if (atomic_load_explicit(&found_flag,memory_order_relaxed)) return;
    st->nodes[j]++;
    if (j==NZ) { if (st->m==K) record_solution(st); return; }
    if (j<=2 && now_sec()>deadline) return;   /* cheap expiry check */

    int l0cap = st->l0sz<4 ? st->l0sz : 4;

    /* capacity of layers j..NZ-1: j..NZ-2 hold <=4 each, last <= min(|L0|,4) */
    if (st->m + 4*(NZ-1-j) + l0cap < K) return;
    /* capacity of layers j+1..NZ-1 (used for need_min and admissibility) */
    int cap_after = (j<=NZ-2) ? 4*(NZ-2-j) + l0cap : 0;
    int need_min = K - st->m - cap_after; if (need_min<0) need_min=0;
    int need_max = K - st->m; if (need_max>4) need_max=4;
    if (j==NZ-1 && need_max > st->l0sz) need_max = st->l0sz;
    if (need_min>need_max) return;

    int m = st->m;
    const int *pts = st->pts;

    /* blockf[k]: layer-k positions forbidden as singletons (i=1), k>=j.
       INCREMENTAL: st->bf carries the union of placed 4-subsets' SPH masks;
       each placement edge adds the 4-subsets meeting the new layer set. */
    const u64 *blockf = st->bf;
    u64 block1 = blockf[j];
    /* capacity prune: even the largest admissible sets per remaining layer
       must reach K.  cap_k = 4 (or min(|L0|,4) for the last layer). */
    if (m>=4) {
        int cap = 0;
        for (int k=j;k<NZ;k++){
            int ck = (k==NZ-1)?l0cap:4;
            int a = __builtin_popcountll(ALL36 & ~blockf[k]);
            cap += ck<a?ck:a;
        }
        if (st->m + cap < K) { atomic_fetch_add(&g_admiss_fire,1); return; }
    }
    /* admissibility prune for future layers k>j.  SOUND bound: every
       candidate for layer k lives in A_k = ~blockf[k]; |L_k| >= low where
       low = K - m - cap(layers j..5 except k).  cap_others counts ALL
       unplaced layers except k (incl. layer j itself and the |L5|<=|L0|
       cap when k<5).  A size-low member needs >= low-1 allowed partners
       (pair-block Q_k); drop low-degree positions to a fixpoint. */
    if (m>=4) {
        for (int k=j+1;k<NZ;k++){
            int cap_others = (k==NZ-1) ? 4*(NZ-1-j)
                                       : 4*(NZ-2-j) + l0cap;
            int low = K - m - cap_others; if (low<=0) continue;
            u64 A = ALL36 & ~blockf[k];
            if (__builtin_popcountll(A) < low) {
                atomic_fetch_add(&g_admiss_fire,1); return;
            }
            if (low>=2 && m>=3) {
                u64 Q[LP]; memset(Q,0,sizeof Q);
                int base=LP*k;
                for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++)
                for(int c=b+1;c<m;c++){
                    size_t partial = (size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
                    u64 t = A;
                    while (t){ int p=__builtin_ctzll(t); t&=t-1;
                        Q[p] |= SPH[(partial + (size_t)BIN[base+p][4])*NZ + k]; }
                }
                int changed=1;
                while (changed && A){ changed=0; u64 t=A;
                    while(t){int p=__builtin_ctzll(t);t&=t-1;
                        int deg=__builtin_popcountll(A & ~Q[p])-1;
                        if (deg < low-1){ A &= ~(1ull<<p); changed=1; } }
                }
                if (__builtin_popcountll(A) < low) {
                    atomic_fetch_add(&g_admiss_fire,1); return;
                }
            }
        }
    }
    /* allowed positions; Mp[p] (i=2 partners in layer j) plus PD[p][k]:
       layer-k masks of sphere(triple U {p}), accumulated per position so a
       placed set C can add its 1-of-C delta as  OR_{p in C} PD[p][k]. */
    u64 A_j = ALL36 & ~block1;
    u64 Mp[LP]; memset(Mp,0,sizeof Mp);
    u64 PD[LP][NZ];   /* per-dfs-frame: child calls use their own */
    memset(PD,0,sizeof PD);
    int apos[LP], nap=0;
    { u64 t=A_j; while(t){int p=__builtin_ctzll(t);t&=t-1;apos[nap++]=p;} }
    if (m>=3) {
        int base = LP*j;
        for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++) for(int c=b+1;c<m;c++){
            size_t partial = (size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
            for (int i=0;i<nap;i++){ int p=apos[i];
                const u64 *e = SPH + (size_t)(partial + (size_t)BIN[base+p][4])*NZ;
                Mp[p] |= e[j];
                for (int k=j+1;k<NZ;k++) PD[p][k] |= e[k];
            }
        }
    }
    /* stabilizer of the placed set U under D4 (fixes each layer mask);
       at j==1 it equals stab(L0), passed in by the caller */
    u8 stabU = stab;
    if (j>=2) {
        stabU = 0;
        for (int g=1;g<8;g++){
            int ok=1;
            for(int k=0;k<j;k++) if (symmask(g,st->L[k])!=st->L[k]){ok=0;break;}
            if (ok) stabU |= 1u<<g;
        }
    }

    if (!stabU) {
        /* generator path: enumerate subsets of A_j directly, integrating
           i=2 (pair-block) and i=3 (triple-block) checks incrementally. */
        GenCtx g; g.st=st; g.j=j; g.Mp=Mp; g.PD=PD; g.nap=nap; g.out=NULL;
        for(int i=0;i<nap;i++) g.apos[i]=apos[i];
        for (int sz=need_min; sz<=need_max; sz++) {
            if (sz==0) { st->L[j]=0; dfs(st,j+1,0); continue; }
            if (sz > nap) break;
            gen_rec(&g, sz, 0, 0, 0, 0);
            if (atomic_load_explicit(&found_flag,memory_order_relaxed)) return;
            if (j<=2 && now_sec()>deadline) return;
        }
        return;
    }

    for (int sz=need_min; sz<=need_max; sz++) {
        if (j==NZ-1 && sz > st->l0sz) continue;      /* z-flip prune */
        if (sz==0) {                                 /* empty layer */
            st->L[j]=0; dfs(st,j+1,0); continue;
        }
        int lo = sz_off[sz], hi = lo + sz_cnt[sz];
        for (int ci=lo; ci<hi; ci++) {
            Cand *cd = &cands[ci];
            if (cd->mask & block1) continue;
            {                                   /* canonical under stab(U) */
                int canon=1;
                for (int g=1;g<8;g++) if ((stabU>>g)&1 && cd->d4[g] < cd->mask){canon=0;break;}
                if (!canon) continue;
            }
            int ok = 1;
            if (m>=3) {                          /* i=2 */
                u64 mm = cd->mask;
                while (mm) { int p=__builtin_ctzll(mm); mm&=mm-1;
                    if (Mp[p] & cd->mask) { ok=0; break; } }
            }
            if (ok && m>=1 && cd->nt) {          /* i=3 */
                for (int t=0;t<cd->nt && ok;t++){
                    int g1=LP*j+cd->tr[t][0], g2=LP*j+cd->tr[t][1], g3=LP*j+cd->tr[t][2];
                    for (int u=0;u<m;u++){
                        int r=rank4(pts[u],g1,g2,g3);
                        const u64 *e = SPH + (size_t)r*NZ;
                        for (int k=0;k<j;k++) if (e[k] & st->L[k]) { ok=0; break; }
                        if (!ok) break;
                    }
                }
            }
            if (ok && sz==4 && m>=1) {           /* i=4 */
                int r=rank4(LP*j+cd->qd[0],LP*j+cd->qd[1],LP*j+cd->qd[2],LP*j+cd->qd[3]);
                const u64 *e = SPH + (size_t)r*NZ;
                for (int k=0;k<j;k++) if (e[k] & st->L[k]) { ok=0; break; }
            }
            if (!ok) continue;
            /* place: save bf, add C's delta, recurse, restore */
            u64 saved[NZ]; memcpy(saved, st->bf, sizeof saved);
            add_delta(st, j, cd->mask, cd->sz, PD);
            u64 mm = cd->mask; int nm=m;
            while (mm) { int p=__builtin_ctzll(mm); mm&=mm-1; st->pts[nm++]=LP*j+p; }
            st->m=nm; st->L[j]=cd->mask;
            dfs(st,j+1,0);
            st->m=m; st->L[j]=0;
            memcpy(st->bf, saved, sizeof saved);
            if (atomic_load_explicit(&found_flag,memory_order_relaxed)) return;
            if (j<=2 && now_sec()>deadline) return;
        }
    }
}

static void *worker(void *arg)
{
    (void)arg;
    St st; memset(&st,0,sizeof st);
    for (;;) {
        int i = atomic_fetch_add(&next_rep,1);
        if (i>=rep_hi) break;
        Cand *cd = &cands[reps[i]];
        st.m = 0; st.l0sz = cd->sz;
        u64 mm = cd->mask;
        while (mm){int p=__builtin_ctzll(mm);mm&=mm-1;st.pts[st.m++]=p;}
        st.L[0]=cd->mask;
        u8 stab=0;
        for (int g=0;g<8;g++) if (cd->d4[g]==cd->mask) stab|=1u<<g;
        double t0 = now_sec();
        dfs(&st,1,stab);
        double el = now_sec()-t0;
        st.L[0]=0;
        u64 nd=0;
        for(int k=0;k<=NZ;k++){ nd+=st.nodes[k];
            atomic_fetch_add(&g_nodes[k],st.nodes[k]); st.nodes[k]=0; }
        u64 od = atomic_fetch_add(&orbits_done,1)+1;
        fprintf(stderr,"orbit-done %llu/%d idx=%d sz=%d nodes=%llu %.1fs%s\n",
                (unsigned long long)od,rep_hi-rep_lo,i,cd->sz,(unsigned long long)nd,el,
                now_sec()>deadline ? " PARTIAL" : "");
        if (atomic_load(&found_flag)) break;
    }
    return NULL;
}

static void *reporter(void *arg)
{
    (void)arg;
    for (;;) {
        sleep(10);
        u64 d = atomic_load(&orbits_done);
        fprintf(stderr,"[%.0fs] orbits %llu/%d  nodes L1=%llu L2=%llu L3=%llu L4=%llu L5=%llu L6=%llu admiss=%llu%s\n",
                now_sec()-t_start,(unsigned long long)d,rep_hi-rep_lo,
                (unsigned long long)atomic_load(&g_nodes[1]),
                (unsigned long long)atomic_load(&g_nodes[2]),
                (unsigned long long)atomic_load(&g_nodes[3]),
                (unsigned long long)atomic_load(&g_nodes[4]),
                (unsigned long long)atomic_load(&g_nodes[5]),
                (unsigned long long)atomic_load(&g_nodes[6]),
                (unsigned long long)atomic_load(&g_admiss_fire),
                atomic_load(&found_flag)?" FOUND":"");
        if (atomic_load(&found_flag) && d>=rep_hi-rep_lo) break;
        if (now_sec()>deadline+30) break;
    }
    return NULL;
}

/* ---------------- init & main ---------------- */

static void init_points(void)
{
    for (int z=0;z<6;z++) for(int y=0;y<6;y++) for(int x=0;x<6;x++){
        int i = x + 6*y + 36*z;
        gx[i]=x; gy[i]=y; gz[i]=z; gr2[i]=x*x+y*y+z*z;
    }
    for (int n=0;n<=NP;n++){ BIN[n][0]=1;
        for(int k=1;k<5;k++) BIN[n][k]=(n>=k)?BIN[n-1][k-1]+BIN[n-1][k]:0; }
    for (int n=0;n<=LP;n++){ LBIN[n][0]=1;
        for(int k=1;k<5;k++) LBIN[n][k]=(n>=k)?LBIN[n-1][k-1]+LBIN[n-1][k]:0; }
}

typedef struct { int a0,a1; } Range;
static void *build_worker(void *arg){ Range *r=arg; build_range(r->a0,r->a1); return NULL; }

static void selftest(void)
{
    unsigned long long s=88172645463325252ull; int bad=0;
    for (int t=0;t<200;t++){
        int q[4]; int i=0;
        while(i<4){ s^=s<<13; s^=s>>7; s^=s<<17; int p=(int)(s%216);
            int dup=0; for(int k=0;k<i;k++) if(q[k]==p) dup=1;
            if(!dup) q[i++]=p; }
        for(int x=0;x<3;x++)for(int y=x+1;y<4;y++)if(q[x]>q[y]){int t2=q[x];q[x]=q[y];q[y]=t2;}
        u64 got[NZ]; recompute_entry(q[0],q[1],q[2],q[3],got);
        int r=rank4(q[0],q[1],q[2],q[3]);
        for(int k=0;k<NZ;k++) if(got[k]!=SPH[r*NZ+k]) bad++;
    }
    fprintf(stderr,"selftest: %d mismatched entries\n",bad);
    if (bad) { fprintf(stderr,"TABLE MISMATCH - aborting\n"); exit(2); }
}

int main(int argc, char **argv)
{
    int testmode = argc>1 && !strcmp(argv[1],"test");
    int nthreads = (argc>1 && !testmode) ? atoi(argv[1]) : 8;
    double limit = (argc>2 && !testmode) ? atof(argv[2]) : 2400;
    if (argc>3 && !testmode) K = atoi(argv[3]);
    int want_lo = (argc>4 && !testmode) ? atoi(argv[4]) : -1;   /* rep range */
    int want_hi = (argc>5 && !testmode) ? atoi(argv[5]) : -1;
    if (nthreads<1) nthreads=8;
    t_start = now_sec(); deadline = t_start + limit;

    init_points();
    fprintf(stderr,"allocating %zu bytes table\n",(size_t)N4*NZ*8);
    SPH = malloc((size_t)N4*NZ*8);
    if (!SPH){ fprintf(stderr,"alloc fail\n"); return 1; }

    pthread_t bt[64]; Range rg[64];
    int nb = nthreads<64?nthreads:64;
    int per = (NP-2)/nb;
    for(int i=0;i<nb;i++){ rg[i].a0=(i==0?0:rg[i-1].a1); rg[i].a1=(i==nb-1?NP-2:rg[i].a0+per);
        pthread_create(&bt[i],NULL,build_worker,&rg[i]); }
    for(int i=0;i<nb;i++) pthread_join(bt[i],NULL);
    fprintf(stderr,"table built in %.1fs\n",now_sec()-t_start);

    selftest();
    build_candidates();

    fprintf(stderr,"sizes: 1:%d 2:%d 3:%d 4:%d\n",sz_cnt[1],sz_cnt[2],sz_cnt[3],sz_cnt[4]);

    /* canonical layer-0 reps, sorted by size descending.
       Completeness for K=19: every 19-set has an axis extreme >=2
       (else <= 1+4+4+4+4+1 = 18), so only reps with sz >= min_l0sz are
       needed, min_l0sz = 2 when K > 4*(NZ-2)+2 = 18. */
    int min_l0sz = (K > 4*(NZ-2)+2) ? 2 : 1;
    nrep=0;
    for (int i=0;i<ncand;i++){
        Cand *cd=&cands[i]; if (cd->sz < min_l0sz) continue;
        u64 mn=cd->mask;
        for(int g=0;g<8;g++) if(cd->d4[g]<mn) mn=cd->d4[g];
        if (mn==cd->mask){ reps[nrep]=i;
            u8 st=0; for(int g=0;g<8;g++) if(cd->d4[g]==cd->mask) st|=1u<<g;
            rep_stab[nrep]=st; nrep++; }
    }
    for (int a=0;a<nrep;a++) for(int b=a+1;b<nrep;b++)
        if (cands[reps[b]].sz > cands[reps[a]].sz){ int t=reps[a];reps[a]=reps[b];reps[b]=t;
            u8 ts=rep_stab[a];rep_stab[a]=rep_stab[b];rep_stab[b]=ts; }
    fprintf(stderr,"layer0 orbit reps: %d (min_l0sz=%d)\n",nrep,min_l0sz);
    rep_lo=0; rep_hi=nrep;
    if (want_lo>=0){ rep_lo=want_lo; rep_hi=(want_hi>=0&&want_hi<=nrep)?want_hi:rep_lo+1;
        if (rep_lo>=nrep) rep_lo=nrep-1;
        fprintf(stderr,"rep range: [%d,%d)  rep mask=%llu\n",rep_lo,rep_hi,
                (unsigned long long)cands[reps[rep_lo]].mask); }
    next_rep = rep_lo;

    /* TEST mode: enumerate accepted next-layer candidates for a fixed prefix.
       usage: ./layer_enum6 test <layermask0> [<layermask1> ...] */
    if (testmode) {
        St st; memset(&st,0,sizeof st);
        int nl = argc-2;
        for (int k=0;k<nl;k++){
            u64 mk=strtoull(argv[2+k],NULL,0);
            st.L[k]=mk; u64 mm=mk;
            while(mm){int p=__builtin_ctzll(mm);mm&=mm-1;st.pts[st.m++]=LP*k+p;}
        }
        int j=nl, m=st.m; const int *pts=st.pts;
        u64 block1=0;
        if (m>=4) for (int a=0;a<m-3;a++) for(int b=a+1;b<m-2;b++)
            for(int c=b+1;c<m-1;c++) for(int d=c+1;d<m;d++)
                block1 |= SPH[(size_t)rank4(pts[a],pts[b],pts[c],pts[d])*NZ + j];
        u64 Mp[LP]; memset(Mp,0,sizeof Mp);
        if (m>=3) { int base=LP*j;
            for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++) for(int c=b+1;c<m;c++){
                size_t partial=(size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
                for(int p=0;p<LP;p++) Mp[p]|=SPH[(partial+(size_t)BIN[base+p][4])*NZ+j];
            }
        }
        FILE *f=fopen("testout.txt","w");
        for (int ci=0;ci<ncand;ci++){
            Cand *cd=&cands[ci];
            if (cd->mask & block1) continue;
            int ok=1;
            if (m>=3){ u64 mm=cd->mask;
                while(mm){int p=__builtin_ctzll(mm);mm&=mm-1;
                    if(Mp[p]&cd->mask){ok=0;break;}}}
            if (ok && m>=1 && cd->nt)
                for (int t=0;t<cd->nt && ok;t++){
                    int g1=LP*j+cd->tr[t][0],g2=LP*j+cd->tr[t][1],g3=LP*j+cd->tr[t][2];
                    for(int u=0;u<m;u++){int r=rank4(pts[u],g1,g2,g3);
                        const u64 *e=SPH+(size_t)r*NZ;
                        for(int k=0;k<j;k++) if(e[k]&st.L[k]){ok=0;break;}
                        if(!ok)break;}
                }
            if (ok && cd->sz==4 && m>=1){
                int r=rank4(LP*j+cd->qd[0],LP*j+cd->qd[1],LP*j+cd->qd[2],LP*j+cd->qd[3]);
                const u64 *e=SPH+(size_t)r*NZ;
                for(int k=0;k<j;k++) if(e[k]&st.L[k]){ok=0;break;}
            }
            if (ok) fprintf(f,"%llu\n",(unsigned long long)cd->mask);
        }
        fclose(f);
        /* equivalence check: same accepted set via the generator path */
        u64 Mp2[LP]; memset(Mp2,0,sizeof Mp2);
        for (int ci2=0;ci2<ncand;ci2++){ Cand *cd=&cands[ci2];
            (void)cd; }
        FILE *g2=fopen("genout.txt","w");
        GenCtx gc; gc.st=&st; gc.j=j; gc.Mp=Mp2; gc.out=g2; gc.nap=0;
        { u64 t=~block1 & ALL36;
          while(t){int p=__builtin_ctzll(t);t&=t-1;gc.apos[gc.nap++]=p;} }
        /* rebuild Mp exactly like dfs does (restricted to allowed set) */
        if (m>=3) { int base=LP*j;
            for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++) for(int c=b+1;c<m;c++){
                size_t partial=(size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
                for(int ii=0;ii<gc.nap;ii++){int p=gc.apos[ii];
                    Mp2[p]|=SPH[(partial+(size_t)BIN[base+p][4])*NZ+j];}
            }
        }
        for (int sz=1;sz<=4;sz++) if (sz<=gc.nap) gen_rec(&gc,sz,0,0,0,0);
        fclose(g2);
        fprintf(stderr,"test done m=%d j=%d (genout.txt written)\n",m,j);
        return 0;
    }

    pthread_t rt; pthread_create(&rt,NULL,reporter,NULL);
    pthread_t th[64];
    for(int i=0;i<nthreads;i++) pthread_create(&th[i],NULL,worker,NULL);
    for(int i=0;i<nthreads;i++) pthread_join(th[i],NULL);

    u64 total[NZ+1]={0};
    for(int k=0;k<=NZ;k++) total[k]=atomic_load(&g_nodes[k]);
    fprintf(stderr,"done. found=%d admiss=%llu  nodes:",atomic_load(&found_flag),
            (unsigned long long)atomic_load(&g_admiss_fire));
    for(int k=0;k<=NZ;k++) fprintf(stderr," L%d=%llu",k,(unsigned long long)total[k]);
    fprintf(stderr,"\n");
    return atomic_load(&found_flag)?0:3;
}
