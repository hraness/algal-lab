/* chist2.c - two-pass version: group triples by EDM (d12,d13,d23) via open
 * hash; enumerate conic primitive points once per EDM; test div+box per
 * triple. Outputs sum_T N_T (should equal 4*N_circ4), N_T dist, shell sums,
 * h_T stats. Usage: chist2 n */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
typedef long long ll;
static int n; static ll K;
static ll (*P)[3]; static int np;
static ll gcdn_(ll a,ll b){ a=llabs(a);b=llabs(b); while(b){ll t=a%b;a=b;b=t;} return a; }
/* EDM hash */
typedef struct { ll A,B,C; int cnt; int nxt;} E;
static E *HT; static int HCAP = 1<<22, hn=0;
static int *Hhead; static int HMASK;
typedef struct { int x1,x2,x3; int nxt; } TI;
static TI *TL; static int tn=0, TCAP;
static int find(ll A,ll B,ll C){
    unsigned h=(unsigned)(A*1000003+B*31337+C*17)&(HCAP-1);
    for(int i=Hhead[h];i>=0;i=HT[i].nxt)
        if(HT[i].A==A&&HT[i].B==B&&HT[i].C==C) return i;
    int i=hn++; HT[i].A=A;HT[i].B=B;HT[i].C=C;HT[i].cnt=0;HT[i].nxt=Hhead[h];Hhead[h]=i;
    return i;
}
int main(int argc,char**argv){
    n=atoi(argv[1]);
    K=(ll)(3*sqrt(3.0)*n*n/2.0);
    np=n*n*n; P=malloc(np*sizeof*P);
    int t=0;
    for(int z=0;z<n;z++)for(int y=0;y<n;y++)for(int x=0;x<n;x++){P[t][0]=x;P[t][1]=y;P[t][2]=z;t++;}
    HT=malloc(HCAP*sizeof*HT); Hhead=malloc(HCAP*sizeof(int));
    memset(Hhead,-1,HCAP*sizeof(int));
    TCAP=1<<24; TL=malloc(TCAP*sizeof*TL);
    /* pass 1: triples -> EDM index */
    long ntri=0;
    for(int i=0;i<np;i++)for(int j=i+1;j<np;j++)for(int k=j+1;k<np;k++){
        ll *x1=P[i],*x2=P[j],*x3=P[k];
        ll e1[3]={x2[0]-x1[0],x2[1]-x1[1],x2[2]-x1[2]};
        ll e2[3]={x3[0]-x1[0],x3[1]-x1[1],x3[2]-x1[2]};
        ll cr[3]={e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]};
        if(!(cr[0]||cr[1]||cr[2])) continue;
        ll d12=e1[0]*e1[0]+e1[1]*e1[1]+e1[2]*e1[2];
        ll d13=e2[0]*e2[0]+e2[1]*e2[1]+e2[2]*e2[2];
        ll e3[3]={x3[0]-x2[0],x3[1]-x2[1],x3[2]-x2[2]};
        ll d23=e3[0]*e3[0]+e3[1]*e3[1]+e3[2]*e3[2];
        int ei=find(d23,d13,d12);
        HT[ei].cnt++;
        TL[tn].x1=i;TL[tn].x2=j;TL[tn].x3=k;TL[tn].nxt=-1; tn++;
        /* link triple to EDM bucket via chaining: reuse -1; simplest: store ei list later */
        TL[tn-1].nxt = -1;
        ntri++;
    }
    /* build per-EDM triple lists: second array head + chain */
    int *Ehead=malloc(hn*sizeof(int)); memset(Ehead,-1,hn*sizeof(int));
    /* redo insertion: we lost ei per triple; store it */
    /* simpler: re-loop is O(ntri); but tn has triples in order w/o ei tag.
       Instead re-run pass1 quickly? keep a parallel array ei_of_t */
    free(TL); free(Ehead); HCAP=1<<22; hn=0; memset(Hhead,-1,HCAP*sizeof(int));
    TL=malloc(TCAP*sizeof*TL); tn=0;
    int *ei_t=malloc(TCAP*sizeof(int));
    for(int i=0;i<np;i++)for(int j=i+1;j<np;j++)for(int k=j+1;k<np;k++){
        ll *x1=P[i],*x2=P[j],*x3=P[k];
        ll e1[3]={x2[0]-x1[0],x2[1]-x1[1],x2[2]-x1[2]};
        ll e2[3]={x3[0]-x1[0],x3[1]-x1[1],x3[2]-x1[2]};
        ll cr[3]={e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]};
        if(!(cr[0]||cr[1]||cr[2])) continue;
        ll d12=e1[0]*e1[0]+e1[1]*e1[1]+e1[2]*e1[2];
        ll d13=e2[0]*e2[0]+e2[1]*e2[1]+e2[2]*e2[2];
        ll e3[3]={x3[0]-x2[0],x3[1]-x2[1],x3[2]-x2[2]};
        ll d23=e3[0]*e3[0]+e3[1]*e3[1]+e3[2]*e3[2];
        int ei=find(d23,d13,d12); HT[ei].cnt++;
        TL[tn].x1=i;TL[tn].x2=j;TL[tn].x3=k; ei_t[tn]=ei; tn++;
    }
    /* per-EDM triple list heads */
    int *Eh=malloc(hn*sizeof(int)); memset(Eh,-1,hn*sizeof(int));
    int *tnx=malloc(tn*sizeof(int));
    for(int i=0;i<tn;i++){ int e=ei_t[i]; tnx[i]=Eh[e]; Eh[e]=i; }
    /* pass 2: per EDM enumerate conic pts; per triple test div+box */
    long totN=0; static long shellcnt[8192]; static long ntdist[64];
    long triplesN0=0;
    double invh=0; long hsum=0; long hnz=0;
    /* per-EDM work buffers */
    ll (*CL)[4]=malloc(65536*sizeof*CL); int cn;
    int *mmv=malloc(65536*sizeof(int));
    for(int e=0;e<hn;e++){
        ll A=HT[e].A, B=HT[e].B, C=HT[e].C;
        /* enumerate primitive conic points, |c|inf<=K; also compute h_T */
        cn=0; ll hmin=K+1;
        for(ll c1=-K;c1<=K;c1++){ if(!c1)continue;
          for(ll c2=-K;c2<=K;c2++){ if(!c2)continue;
            ll den=A*c2+B*c1; if(!den) continue;
            ll num=-C*c1*c2;
            if(num%den) continue;
            ll c3=num/den; if(!c3||llabs(c3)>K) continue;
            ll c4=-(c1+c2+c3); if(!c4||llabs(c4)>K) continue;
            ll g=gcdn_(gcdn_(c1,c2),gcdn_(c3,c4));
            ll r1=c1/g,r2=c2/g,r3=c3/g,r4=c4/g;
            if(r1<0){r1=-r1;r2=-r2;r3=-r3;r4=-r4;}
            /* dedupe: linear scan fine */
            int dup=0; for(int i=0;i<cn;i++) if(CL[i][0]==r1&&CL[i][1]==r2&&CL[i][2]==r3&&CL[i][3]==r4){dup=1;break;}
            if(dup) continue;
            CL[cn][0]=r1;CL[cn][1]=r2;CL[cn][2]=r3;CL[cn][3]=r4;
            int mm=0; ll aa[4]={llabs(r1),llabs(r2),llabs(r3),llabs(r4)};
            for(int u=0;u<4;u++) if(aa[u]>mm)mm=aa[u];
            mmv[cn]=mm; if(mm<hmin)hmin=mm;
            cn++;
          }
        }
        if(hmin>K){} /* no conic pts at all: hmin stays K+1 */
        /* per triple: test div+box for each conic pt */
        for(int ti=Eh[e];ti>=0;ti=tnx[ti]){
            int cnt=0;
            ll *x1=P[TL[ti].x1],*x2=P[TL[ti].x2],*x3=P[TL[ti].x3];
            for(int i=0;i<cn;i++){
                ll c1=CL[i][0],c2=CL[i][1],c3=CL[i][2],c4=CL[i][3];
                ll S0=c1*x1[0]+c2*x2[0]+c3*x3[0];
                ll S1=c1*x1[1]+c2*x2[1]+c3*x3[1];
                ll S2=c1*x1[2]+c2*x2[2]+c3*x3[2];
                if(S0%c4||S1%c4||S2%c4) continue;
                ll X=-S0/c4,Y=-S1/c4,Z=-S2/c4;
                if(X<0||X>=n||Y<0||Y>=n||Z<0||Z>=n) continue;
                if((X==x1[0]&&Y==x1[1]&&Z==x1[2])||(X==x2[0]&&Y==x2[1]&&Z==x2[2])||(X==x3[0]&&Y==x3[1]&&Z==x3[2])) continue;
                cnt++; shellcnt[mmv[i]]++;
            }
            totN+=cnt;
            int b=0; while((1<<b)<cnt&&b<62)b++; ntdist[b]++;
            if(cnt){ hnz++; if(hmin<=K){invh+=1.0/hmin; hsum+=hmin;} }
        }
        if(cn==0){ /* count triples with zero conic pts anyway for N_T dist */
            for(int ti=Eh[e];ti>=0;ti=tnx[ti]) ntdist[0]++;
        }
    }
    printf("n=%d K=%lld triples=%ld EDMs=%d  sum_T N_T=%ld (4*N_circ4 check)\n",n,K,ntri,hn,totN);
    printf("N_T log2-buckets: ");
    for(int b=0;b<20;b++) if(ntdist[b]) printf("[%ld-%ld]:%ld ",b>0?(1L<<(b-1)):0,(1L<<b)-1,ntdist[b]);
    printf("\ntriples with N_T>0: %ld  (frac %.4f)\n",hnz,(double)hnz/ntri);
    printf("shell |c|inf->sum_T #c: ");
    for(int m=1;m<=K&&m<400;m++) if(shellcnt[m]) printf("%d:%ld ",m,shellcnt[m]);
    printf("\n");
    return 0;
}
