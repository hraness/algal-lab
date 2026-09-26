/*
 * c5-structural: layer-enumeration search for 15-subsets of {0..4}^3
 * with no 5 points on a common sphere or plane.
 *
 * Model (same as research/extremal/verifiers/no_five_on_sphere.py):
 *   5 points are cospherical or coplanar iff the 5x5 determinant with rows
 *   (x,y,z,x^2+y^2+z^2,1) vanishes.  Equivalently, for a 4-set T and point q,
 *   f(q) = det4([q - t0, t1 - t0, t2 - t0, t3 - t0]) on lifted coords
 *   (x,y,z,r^2) is a linear form in q; its zero set is the sphere/plane
 *   through T (the whole grid when T is degenerate: concyclic or collinear).
 *
 * Method: fix z-layer 0 to one canonical subset per D4 orbit, extend layers
 * 1..4.  When adding candidate C at layer j over placed set U, a bad 5-subset
 * with i >= 1 new points is detected by:
 *   i=1:  C & block1(U) != 0     (block1 = union of sphereSet(T4), T4 <= U)
 *   i=2:  some p in C has Mp[p] & C != 0   (Mp[p] = union over T3 <= U of
 *         sphereSet(T3+{p}) restricted to layer j)
 *   i=3:  some triple Tr <= C and u in U: sphereSet(Tr+{u}) hits U
 *   i=4:  sphereSet(C) hits U
 * All lookups go through a precomputed table SPH[rank4]*5 -> per-layer masks.
 *
 * Prunes: size bounds to reach 15, |L4| <= |L0| (z-flip), layer-1 candidates
 * canonicalized under the D4 stabilizer of L0.
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

#define NP 125
#define N4 9691375           /* C(125,4) */
#define ALL25 0x1FFFFFFu

static int  gx[NP], gy[NP], gz[NP], gr2[NP];
static i64  BIN[NP + 1][5];
static u32 *SPH;             /* SPH[rank*5 + layer] : 25-bit mask */

static inline int rank4(int a, int b, int c, int d)   /* a<b<c<d */
{
    return (int)(BIN[a][1] + BIN[b][2] + BIN[c][3] + BIN[d][4]);
}

static inline i64 det3(i64 a0,i64 a1,i64 a2, i64 b0,i64 b1,i64 b2,
                       i64 c0,i64 c1,i64 c2)
{
    return a0*(b1*c2 - b2*c1) - a1*(b0*c2 - b2*c0) + a2*(b0*c1 - b1*c0);
}

/* lifted vector component j of point index i: j=0,1,2,3 -> x,y,z,r^2 */
static inline i64 lift(int p, int j)
{
    switch (j) { case 0: return gx[p]; case 1: return gy[p];
                 case 2: return gz[p]; default: return gr2[p]; }
}

/* ---------------- sphere table build ---------------- */

static void build_range(int a0, int a1)
{
    for (int a = a0; a < a1; a++)
    for (int b = a + 1; b < 124; b++)
    for (int c = b + 1; c < 125 - 1; c++)
    for (int d = c + 1; d < 125; d++) {
        int r = rank4(a, b, c, d);
        u32 *dst = SPH + (size_t)r * 5;
        /* differences d_i = lift(p_i) - lift(a), i=1..3 */
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
            /* degenerate T: every q makes a bad 5-set */
            for (int k = 0; k < 5; k++) dst[k] = ALL25;
        } else {
            i64 c0 = D0, c1 = -D1, c2 = D2, c3 = -D3;
            i64 E = -(c0*gx[a] + c1*gy[a] + c2*gz[a] + c3*gr2[a]);
            u32 m0=0,m1=0,m2=0,m3=0,m4=0;
            for (int q = 0; q < NP; q++) {
                if (c0*gx[q] + c1*gy[q] + c2*gz[q] + c3*gr2[q] + E == 0) {
                    switch (q / 25) {
                    case 0: m0 |= 1u << q; break;
                    case 1: m1 |= 1u << (q - 25); break;
                    case 2: m2 |= 1u << (q - 50); break;
                    case 3: m3 |= 1u << (q - 75); break;
                    default: m4 |= 1u << (q - 100); break;
                    }
                }
            }
            dst[0]=m0; dst[1]=m1; dst[2]=m2; dst[3]=m3; dst[4]=m4;
        }
        /* remove T's own points */
        dst[a/25] &= ~(1u << (a%25));
        dst[b/25] &= ~(1u << (b%25));
        dst[c/25] &= ~(1u << (c%25));
        dst[d/25] &= ~(1u << (d%25));
    }
}

/* independent recompute of one table entry for self-test */
static void recompute_entry(int a,int b,int c,int d,u32 out[5]);

static i64 det4x4(const i64 m[4][4]);

static void recompute_entry(int a,int b,int c,int d,u32 out[5])
{
    i64 v0[4] = {gx[a],gy[a],gz[a],gr2[a]};
    i64 v[3][4]; int ps[3]={b,c,d};
    for (int i=0;i<3;i++) for(int j=0;j<4;j++) v[i][j]=lift(ps[i],j)-v0[j];
    for (int k=0;k<5;k++) out[k]=0;
    for (int q=0;q<NP;q++) {
        if (q==a||q==b||q==c||q==d) continue;
        i64 w[4]={gx[q]-v0[0],gy[q]-v0[1],gz[q]-v0[2],gr2[q]-v0[3]};
        i64 m[4][4];
        for(int j=0;j<4;j++){m[0][j]=w[j];m[1][j]=v[0][j];m[2][j]=v[1][j];m[3][j]=v[2][j];}
        if (det4x4(m)==0) out[q/25] |= 1u<<(q%25);
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

#define MAXC 16000
typedef struct {
    u32 mask;
    u8  sz;
    u8  np, nt;
    u8  pr[6][2];    /* position pairs */
    u8  tr[4][3];    /* position triples */
    u8  qd[4];       /* positions when sz==4 */
    u32 d4[8];       /* images under square symmetries */
} Cand;

static Cand cands[MAXC];
static int  ncand;
static int  sz_off[5], sz_cnt[5];      /* index ranges per size (sorted) */
static int  reps[MAXC]; static int nrep;   /* canonical layer-0 reps */
static u8   rep_stab[MAXC];

static int sympos(int g, int pos)
{
    int x = pos % 5, y = pos / 5, nx, ny;
    switch (g) {
    case 0: nx=x;   ny=y;   break;
    case 1: nx=4-y; ny=x;   break;
    case 2: nx=4-x; ny=4-y; break;
    case 3: nx=y;   ny=4-x; break;
    case 4: nx=4-x; ny=y;   break;
    case 5: nx=x;   ny=4-y; break;
    case 6: nx=y;   ny=x;   break;
    default:nx=4-y; ny=4-x; break;
    }
    return ny * 5 + nx;
}

static u32 symmask(int g, u32 m)
{
    u32 r = 0;
    while (m) { int p = __builtin_ctz(m); m &= m-1; r |= 1u << sympos(g, p); }
    return r;
}

/* layer-subset validity: 4-subsets must not be concyclic/collinear */
static int layer_ok4(int a,int b,int c,int d)
{
    /* points at z=0; lifted diffs; valid iff rank == 3 iff D2 != 0
       (z column is all zero, so only the (x,y,r2) minor can be nonzero) */
    i64 v[3][3]; int ps[3]={b,c,d};
    for (int i=0;i<3;i++){
        int p=ps[i];
        v[i][0]=gx[p]-gx[a]; v[i][1]=gy[p]-gy[a]; v[i][2]=gr2[p]-gr2[a];
    }
    return det3(v[0][0],v[0][1],v[0][2],v[1][0],v[1][1],v[1][2],v[2][0],v[2][1],v[2][2]) != 0;
}

static void add_cand(u32 mask, const int *ps, int sz)
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
    /* sizes 1,2,3 (always fine) then 4 (filtered) */
    int ps[4];
    for (int a=0;a<25;a++){ ps[0]=a; add_cand(1u<<a,ps,1); }
    for (int a=0;a<25;a++) for(int b=a+1;b<25;b++){ ps[0]=a;ps[1]=b;
        add_cand((1u<<a)|(1u<<b),ps,2); }
    for (int a=0;a<25;a++) for(int b=a+1;b<25;b++) for(int c=b+1;c<25;c++){
        ps[0]=a;ps[1]=b;ps[2]=c; add_cand((1u<<a)|(1u<<b)|(1u<<c),ps,3); }
    int total4=0;
    for (int a=0;a<25;a++) for(int b=a+1;b<25;b++) for(int c=b+1;c<25;c++)
    for(int d=c+1;d<25;d++){ total4++;
        if(!layer_ok4(a,b,c,d)) continue;
        ps[0]=a;ps[1]=b;ps[2]=c;ps[3]=d;
        add_cand((1u<<a)|(1u<<b)|(1u<<c)|(1u<<d),ps,4); }
    /* size offsets (candidates appended in order 1,2,3,4) */
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
    int pts[24];
    u32 L[5];
    int l0sz;
    u64 nodes[6];
} St;

static _Atomic int found_flag;
static _Atomic int next_rep;
static _Atomic u64 orbits_done;
static _Atomic u64 g_nodes[6];
static int g_solution[24];
static pthread_mutex_t sol_mtx = PTHREAD_MUTEX_INITIALIZER;
static double deadline = 1e30;
static int K = 15;
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
        FILE *f=fopen(K==15?"solution.txt":"solution_k.txt","w");
        if (f) {
            for (int i=0;i<st->m;i++)
                fprintf(f,"%d %d %d\n",gx[st->pts[i]],gy[st->pts[i]],gz[st->pts[i]]);
            fclose(f);
        }
        fprintf(stderr,"FOUND 15-set (m=%d):",st->m);
        for (int i=0;i<st->m;i++) fprintf(stderr," %d",st->pts[i]);
        fprintf(stderr,"\n");
    }
    pthread_mutex_unlock(&sol_mtx);
}

static void dfs(St *st, int j, u8 stab)
{
    if (atomic_load_explicit(&found_flag,memory_order_relaxed)) return;
    st->nodes[j]++;
    if (j==5) { if (st->m==K) record_solution(st); return; }
    if (j<=2 && now_sec()>deadline) return;   /* cheap expiry check */

    /* reach bound: remaining layers j..4 hold at most 4 each except layer 4
       capped at |L0| (z-flip prune |L4| <= |L0|) */
    if (st->m + 4*(4-j) + (st->l0sz<4?st->l0sz:4) < K) return;
    int rem_after = 4 - j;
    int need_min = K - st->m - 4*rem_after; if (need_min<0) need_min=0;
    int need_max = K - st->m;               if (need_max>4) need_max=4;
    if (need_min>need_max) return;
    if (j==4 && need_min > st->l0sz) return; /* |L4|<=|L0| impossible */

    int m = st->m;
    const int *pts = st->pts;

    /* blockf[k]: layer-k positions forbidden as singletons (i=1), k>=j */
    u32 blockf[5] = {0,0,0,0,0};
    if (m>=4) {
        for (int a=0;a<m-3;a++) for(int b=a+1;b<m-2;b++)
        for(int c=b+1;c<m-1;c++) for(int d=c+1;d<m;d++){
            const u32 *e = SPH + (size_t)rank4(pts[a],pts[b],pts[c],pts[d])*5;
            for (int k=j;k<5;k++) blockf[k] |= e[k];
        }
    }
    u32 block1 = blockf[j];
    /* admissibility prune for future layers k>j: every candidate lives in
       A_k = ~blockf[k]; a size-low candidate member needs >= low-1 allowed
       partners in A_k (pair-block Q_k), so drop low-degree positions to a
       fixpoint and prune if too few remain. */
    if (m>=4) {
        for (int k=j+1;k<5;k++){
            /* sound bound: layers j..4 except k are ALL still unplaced at
               this node and can each contribute at most 4, so layer k must
               supply >= K - m - 4*(4-j).  The previous form 4*(4-k) ignored
               the not-yet-placed layers j..k-1, inflating low and allowing
               wrongly-pruned branches (found by the n=6 port review). */
            int low = K - m - 4*(4-j); if (low<=0) continue;
            u32 A = ALL25 & ~blockf[k];
            if (__builtin_popcount(A) < low) return;
            if (low>=2 && m>=3) {
                u32 Q[25]; memset(Q,0,sizeof Q);
                int base=25*k;
                for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++)
                for(int c=b+1;c<m;c++){
                    size_t partial = (size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
                    u32 t = A;
                    while (t){ int p=__builtin_ctz(t); t&=t-1;
                        Q[p] |= SPH[(partial + (size_t)BIN[base+p][4])*5 + k]; }
                }
                int changed=1;
                while (changed && A){ changed=0; u32 t=A;
                    while(t){int p=__builtin_ctz(t);t&=t-1;
                        int deg=__builtin_popcount(A & ~Q[p])-1;
                        if (deg < low-1){ A &= ~(1u<<p); changed=1; } }
                }
                if (__builtin_popcount(A) < low) return;
            }
        }
    }
    /* Mp[p]: layer-j positions forbidden as partners of p (i=2) */
    u32 Mp[25]; memset(Mp,0,sizeof Mp);
    if (m>=3) {
        int base = 25*j;
        for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++) for(int c=b+1;c<m;c++){
            size_t partial = (size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
            for (int p=0;p<25;p++)
                Mp[p] |= SPH[(partial + (size_t)BIN[base+p][4])*5 + j];
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

    for (int sz=need_min; sz<=need_max; sz++) {
        if (j==4 && sz > st->l0sz) continue;      /* z-flip prune */
        if (sz==0) {                             /* empty layer */
            st->L[j]=0; dfs(st,j+1,0); continue;
        }
        int lo = sz_off[sz], hi = lo + sz_cnt[sz];
        for (int ci=lo; ci<hi; ci++) {
            Cand *cd = &cands[ci];
            if (cd->mask & block1) continue;
            if (stabU) {                         /* canonical under stab(U) */
                int canon=1;
                for (int g=1;g<8;g++) if ((stabU>>g)&1 && cd->d4[g] < cd->mask){canon=0;break;}
                if (!canon) continue;
            }
            int ok = 1;
            if (m>=3) {                          /* i=2 */
                u32 mm = cd->mask;
                while (mm) { int p=__builtin_ctz(mm); mm&=mm-1;
                    if (Mp[p] & cd->mask) { ok=0; break; } }
            }
            if (ok && m>=1 && cd->nt) {          /* i=3 */
                for (int t=0;t<cd->nt && ok;t++){
                    int g1=25*j+cd->tr[t][0], g2=25*j+cd->tr[t][1], g3=25*j+cd->tr[t][2];
                    for (int u=0;u<m;u++){
                        int r=rank4(pts[u],g1,g2,g3);
                        const u32 *e = SPH + (size_t)r*5;
                        for (int k=0;k<j;k++) if (e[k] & st->L[k]) { ok=0; break; }
                        if (!ok) break;
                    }
                }
            }
            if (ok && sz==4 && m>=1) {           /* i=4 */
                int r=rank4(25*j+cd->qd[0],25*j+cd->qd[1],25*j+cd->qd[2],25*j+cd->qd[3]);
                const u32 *e = SPH + (size_t)r*5;
                for (int k=0;k<j;k++) if (e[k] & st->L[k]) { ok=0; break; }
            }
            if (!ok) continue;
            /* place */
            u32 mm = cd->mask; int nm=m;
            while (mm) { int p=__builtin_ctz(mm); mm&=mm-1; st->pts[nm++]=25*j+p; }
            st->m=nm; st->L[j]=cd->mask;
            dfs(st,j+1,0);
            st->m=m; st->L[j]=0;
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
        if (i>=nrep) break;
        Cand *cd = &cands[reps[i]];
        st.m = 0; st.l0sz = cd->sz;
        u32 mm = cd->mask;
        while (mm){int p=__builtin_ctz(mm);mm&=mm-1;st.pts[st.m++]=p;}
        st.L[0]=cd->mask;
        u8 stab=0;
        for (int g=0;g<8;g++) if (cd->d4[g]==cd->mask) stab|=1u<<g;
        double t0 = now_sec();
        dfs(&st,1,stab);
        double el = now_sec()-t0;
        st.L[0]=0;
        u64 nd=0;
        for(int k=0;k<6;k++){ nd+=st.nodes[k];
            atomic_fetch_add(&g_nodes[k],st.nodes[k]); st.nodes[k]=0; }
        u64 od = atomic_fetch_add(&orbits_done,1)+1;
        fprintf(stderr,"orbit-done %llu/%d idx=%d sz=%d nodes=%llu %.1fs%s\n",
                (unsigned long long)od,nrep,i,cd->sz,(unsigned long long)nd,el,
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
        u64 n1=atomic_load(&g_nodes[1]),n2=atomic_load(&g_nodes[2]),
            n3=atomic_load(&g_nodes[3]),n4=atomic_load(&g_nodes[4]),
            n5=atomic_load(&g_nodes[5]);
        fprintf(stderr,"[%.0fs] orbits %llu/%d  nodes L1=%llu L2=%llu L3=%llu L4=%llu L5=%llu%s\n",
                now_sec()-t_start,(unsigned long long)d,nrep,
                (unsigned long long)n1,(unsigned long long)n2,
                (unsigned long long)n3,(unsigned long long)n4,
                (unsigned long long)n5, atomic_load(&found_flag)?" FOUND":"");
        if (atomic_load(&found_flag) && d>=nrep) break;
        if (now_sec()>deadline+30) break;
    }
    return NULL;
}

/* ---------------- init & main ---------------- */

static void init_points(void)
{
    for (int z=0;z<5;z++) for(int y=0;y<5;y++) for(int x=0;x<5;x++){
        int i = x + 5*y + 25*z;
        gx[i]=x; gy[i]=y; gz[i]=z; gr2[i]=x*x+y*y+z*z;
    }
    for (int n=0;n<=NP;n++){ BIN[n][0]=1;
        for(int k=1;k<5;k++) BIN[n][k]=(n>=k)?BIN[n-1][k-1]+BIN[n-1][k]:0; }
}

typedef struct { int a0,a1; } Range;
static void *build_worker(void *arg){ Range *r=arg; build_range(r->a0,r->a1); return NULL; }

static void selftest(void)
{
    /* verify ~200 random entries against brute det4 */
    unsigned long long s=88172645463325252ull; int bad=0;
    for (int t=0;t<200;t++){
        int q[4]; int i=0;
        while(i<4){ s^=s<<13; s^=s>>7; s^=s<<17; int p=(int)(s%125);
            int dup=0; for(int k=0;k<i;k++) if(q[k]==p) dup=1;
            if(!dup) q[i++]=p; }
        for(int x=0;x<3;x++)for(int y=x+1;y<4;y++)if(q[x]>q[y]){int t2=q[x];q[x]=q[y];q[y]=t2;}
        u32 got[5]; recompute_entry(q[0],q[1],q[2],q[3],got);
        int r=rank4(q[0],q[1],q[2],q[3]);
        for(int k=0;k<5;k++) if(got[k]!=SPH[r*5+k]) bad++;
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
    if (nthreads<1) nthreads=8;
    t_start = now_sec(); deadline = t_start + limit;

    init_points();
    fprintf(stderr,"allocating %zu bytes table\n",(size_t)N4*5*4);
    SPH = malloc((size_t)N4*5*4);
    if (!SPH){ fprintf(stderr,"alloc fail\n"); return 1; }

    /* parallel table build over first index a */
    pthread_t bt[64]; Range rg[64];
    int nb = nthreads<64?nthreads:64;
    int per = 124/nb;
    for(int i=0;i<nb;i++){ rg[i].a0=(i==0?0:rg[i-1].a1); rg[i].a1=(i==nb-1?124:rg[i].a0+per);
        pthread_create(&bt[i],NULL,build_worker,&rg[i]); }
    for(int i=0;i<nb;i++) pthread_join(bt[i],NULL);
    fprintf(stderr,"table built in %.1fs\n",now_sec()-t_start);

    selftest();
    build_candidates();

    fprintf(stderr,"sizes: 1:%d 2:%d 3:%d 4:%d\n",sz_cnt[1],sz_cnt[2],sz_cnt[3],sz_cnt[4]);

    /* canonical layer-0 reps, sorted by size descending */
    nrep=0;
    for (int i=0;i<ncand;i++){
        Cand *cd=&cands[i]; u32 mn=cd->mask;
        for(int g=0;g<8;g++) if(cd->d4[g]<mn) mn=cd->d4[g];
        if (mn==cd->mask){ reps[nrep]=i;
            u8 st=0; for(int g=0;g<8;g++) if(cd->d4[g]==cd->mask) st|=1u<<g;
            rep_stab[nrep]=st; nrep++; }
    }
    for (int a=0;a<nrep;a++) for(int b=a+1;b<nrep;b++)
        if (cands[reps[b]].sz > cands[reps[a]].sz){ int t=reps[a];reps[a]=reps[b];reps[b]=t;
            u8 ts=rep_stab[a];rep_stab[a]=rep_stab[b];rep_stab[b]=ts; }
    fprintf(stderr,"layer0 orbit reps: %d\n",nrep);

    /* TEST mode: enumerate accepted next-layer candidates for a fixed prefix.
       usage: ./search test <layermask0> [<layermask1> ...]  -> writes
       testout.txt with accepted masks (decimal) for the next layer, using the
       same check machinery as dfs (block1+Mp+i3+i4, no symmetry/size prune). */
    if (testmode) {
        St st; memset(&st,0,sizeof st);
        int nl = argc-2;
        for (int k=0;k<nl;k++){
            u32 mk=(u32)strtoul(argv[2+k],NULL,0);
            st.L[k]=mk; u32 mm=mk;
            while(mm){int p=__builtin_ctz(mm);mm&=mm-1;st.pts[st.m++]=25*k+p;}
        }
        int j=nl, m=st.m; const int *pts=st.pts;
        u32 block1=0;
        if (m>=4) for (int a=0;a<m-3;a++) for(int b=a+1;b<m-2;b++)
            for(int c=b+1;c<m-1;c++) for(int d=c+1;d<m;d++)
                block1 |= SPH[(size_t)rank4(pts[a],pts[b],pts[c],pts[d])*5 + j];
        u32 Mp[25]; memset(Mp,0,sizeof Mp);
        if (m>=3) { int base=25*j;
            for (int a=0;a<m-2;a++) for(int b=a+1;b<m-1;b++) for(int c=b+1;c<m;c++){
                size_t partial=(size_t)BIN[pts[a]][1]+BIN[pts[b]][2]+BIN[pts[c]][3];
                for(int p=0;p<25;p++) Mp[p]|=SPH[(partial+(size_t)BIN[base+p][4])*5+j];
            }
        }
        FILE *f=fopen("testout.txt","w");
        for (int ci=0;ci<ncand;ci++){
            Cand *cd=&cands[ci];
            if (cd->mask & block1) continue;
            int ok=1;
            if (m>=3){ u32 mm=cd->mask;
                while(mm){int p=__builtin_ctz(mm);mm&=mm-1;
                    if(Mp[p]&cd->mask){ok=0;break;}}}
            if (ok && m>=1 && cd->nt)
                for (int t=0;t<cd->nt && ok;t++){
                    int g1=25*j+cd->tr[t][0],g2=25*j+cd->tr[t][1],g3=25*j+cd->tr[t][2];
                    for(int u=0;u<m;u++){int r=rank4(pts[u],g1,g2,g3);
                        const u32 *e=SPH+(size_t)r*5;
                        for(int k=0;k<j;k++) if(e[k]&st.L[k]){ok=0;break;}
                        if(!ok)break;}
                }
            if (ok && cd->sz==4 && m>=1){
                int r=rank4(25*j+cd->qd[0],25*j+cd->qd[1],25*j+cd->qd[2],25*j+cd->qd[3]);
                const u32 *e=SPH+(size_t)r*5;
                for(int k=0;k<j;k++) if(e[k]&st.L[k]){ok=0;break;}
            }
            if (ok) fprintf(f,"%u\n",cd->mask);
        }
        fclose(f);
        fprintf(stderr,"test done m=%d j=%d\n",m,j);
        return 0;
    }

    pthread_t rt; pthread_create(&rt,NULL,reporter,NULL);
    pthread_t th[64];
    for(int i=0;i<nthreads;i++) pthread_create(&th[i],NULL,worker,NULL);
    for(int i=0;i<nthreads;i++) pthread_join(th[i],NULL);

    u64 total[6]={0};
    for(int k=0;k<6;k++) total[k]=atomic_load(&g_nodes[k]);
    fprintf(stderr,"done. found=%d  nodes:",atomic_load(&found_flag));
    for(int k=0;k<6;k++) fprintf(stderr," L%d=%llu",k,(unsigned long long)total[k]);
    fprintf(stderr,"\n");
    return atomic_load(&found_flag)?0:3;
}
