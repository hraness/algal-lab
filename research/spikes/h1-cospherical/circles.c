/* circles.c - per-sphere circle census over an esamp extras file.
 * For each line "id tot | base x4 | pts x tot": enumerate all planes through
 * triples of sphere points; each plane gives a circle C with c = #pts on it.
 * Degenerate 5-subsets on this sphere split disjointly as:
 *   cop5 = sum_C C(c,5)            (all 5 on one circle: coplanar)
 *   cp   = sum_C C(c,4)*(t-c)      (4 on a circle + 1 off: "circle+point")
 *   irr  = C(t,5) - cop5 - cp      (no concyclic 4-subset; "genuine sphere 5")
 * (two distinct circles on a sphere share <=2 points -> classes disjoint).
 * Output: id tot nplanes cmax cop5 cp irr C4circ   (irr/cop5/cp are estimates
 * when np > LIM, flagged by negative nplanes)
 * Usage: circles n extras.tsv
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef long long ll;
typedef unsigned long long ull;

static ll gcdll(ll a, ll b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ll t=a%b;a=b;b=t;} return a; }
static ull mix(ull x){ x^=x>>33; x*=0xff51afd7ed558ccdULL; x^=x>>33; return x; }
static ll C(ll a,int r){ if(a<r)return 0; ll s=1; for(int i=0;i<r;i++)s*=a-i; for(int i=2;i<=r;i++)s/=i; return s; }

#define HBITS 22
#define HSIZE (1u<<HBITS)
static int hhead[HSIZE];
static int (*plist)[4];      /* plane coeffs */
static int *plnext;          /* chain */
static int npl;
static unsigned long long rs = 88172645463325252ULL;
static ull xr(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

static void hclear(void){ memset(hhead,0xFF,sizeof hhead); npl=0; }
static int hfind(ll nx,ll ny,ll nz,ll d){
    ull h=mix((ull)nx*0x9E3779B1ULL ^ (ull)ny*0x85EBCA77ULL ^ (ull)nz*0xC2B2AE3DULL ^ (ull)d*0x27D4EB2FULL)&(HSIZE-1);
    for(int i=hhead[h];i>=0;i=plnext[i])
        if(plist[i][0]==nx&&plist[i][1]==ny&&plist[i][2]==nz&&plist[i][3]==d) return i;
    return -1;
}
static int hadd(ll nx,ll ny,ll nz,ll d,int idx){
    ull h=mix((ull)nx*0x9E3779B1ULL ^ (ull)ny*0x85EBCA77ULL ^ (ull)nz*0xC2B2AE3DULL ^ (ull)d*0x27D4EB2FULL)&(HSIZE-1);
    plist[idx][0]=nx;plist[idx][1]=ny;plist[idx][2]=nz;plist[idx][3]=d;
    plnext[idx]=hhead[h]; hhead[h]=idx; return idx;
}
static void emit_triple(ll *pts,int i,int j,int l){
    ll ux=pts[3*j]-pts[3*i],uy=pts[3*j+1]-pts[3*i+1],uz=pts[3*j+2]-pts[3*i+2];
    ll vx=pts[3*l]-pts[3*i],vy=pts[3*l+1]-pts[3*i+1],vz=pts[3*l+2]-pts[3*i+2];
    ll nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
    ll dd=nx*pts[3*i]+ny*pts[3*i+1]+nz*pts[3*i+2];
    ll g=gcdll(nx,gcdll(ny,gcdll(nz,dd))); if(g){nx/=g;ny/=g;nz/=g;dd/=g;}
    if(nx<0||(nx==0&&(ny<0||(ny==0&&(nz<0||(nz==0&&dd<0)))))){nx=-nx;ny=-ny;nz=-nz;dd=-dd;}
    if(hfind(nx,ny,nz,dd)<0) hadd(nx,ny,nz,dd,npl++);
}

#define LIM 70          /* above this many sphere points, use random-triple mode */
#define SAMP 300000

int main(int argc, char **argv){
    int n = atoi(argv[1]);
    FILE *f = fopen(argv[2],"r"); if(!f){fprintf(stderr,"no extras\n");return 1;}
    plist=malloc(sizeof(*plist)*(1<<22)); plnext=malloc(sizeof(int)*(1<<22));
    char *line=NULL; size_t cap=0; ssize_t L;
    while ((L=getline(&line,&cap,f))>0){
        if(line[0]=='#') continue;
        char *p=line;
        ll id=strtoll(p,&p,10); ll tot=strtoll(p,&p,10);
        char *bar2=strchr(strchr(p,'|')+1,'|');
        ll *pts=malloc(sizeof(ll)*3*tot); ll np=0;
        p=bar2+1;
        while(*p && *p!='\n'){ while(*p==' ')p++; if(*p=='\n'||!*p||*p=='T')break;
            pts[np++]=strtoll(p,&p,10); }
        np/=3;
        if(np<5 || np!=tot){ free(pts); continue; }
        int sampled = np > LIM;
        hclear();
        if(!sampled){
            for(int i=0;i<np;i++)for(int j=i+1;j<np;j++)for(int l=j+1;l<np;l++)
                emit_triple(pts,i,j,l);
        } else {
            for(int t_=0;t_<SAMP;t_++){
                int i=xr()%np,j=xr()%np,l=xr()%np;
                if(i==j||j==l||i==l){t_--;continue;}
                emit_triple(pts,i,j,l);
            }
        }
        /* count points per plane */
        ll cop5=0,cp=0,C4c=0; int cmax=0, pmax=0;
        for(int pi=0;pi<npl;pi++){
            int c=0;
            for(int i=0;i<np;i++)
                if(plist[pi][0]*pts[3*i]+plist[pi][1]*pts[3*i+1]+plist[pi][2]*pts[3*i+2]==plist[pi][3]) c++;
            if(c>cmax){cmax=c;pmax=pi;}
            cop5+=C(c,5); cp+=C(c,4)*(np-c); C4c+=C(c,4);
        }
        ll C5=C(np,5);
        printf("%lld %lld %s%d %d %d %d %d %lld %lld %lld %lld\n", id, tot, sampled?"~":"", npl,
               cmax, plist[pmax][0], plist[pmax][1], plist[pmax][2], cop5, cp, C5-cop5-cp, C4c);
        free(pts);
    }
    return 0;
}
