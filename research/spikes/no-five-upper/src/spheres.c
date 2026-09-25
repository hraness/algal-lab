/* spheres.c - enumerate every sphere that contains at least MINPTS points of the grid
 * {0..n-1}^3, printing each sphere once as "m i1 ... im" (grid indices p = x*n*n+y*n+z).
 * Exact integer arithmetic (__int128).  A sphere is reported from the lexicographically
 * smallest non-coplanar 4-subset of its grid points.
 * Usage: spheres n [minpts]
 */
#include <stdio.h>
#include <stdlib.h>
typedef __int128 i128; typedef long long ll;
static int n, N; static int PX[4096], PY[4096], PZ[4096];
static int coplanar(int a,int b,int c,int d){
    ll u0=PX[b]-PX[a],u1=PY[b]-PY[a],u2=PZ[b]-PZ[a], v0=PX[c]-PX[a],v1=PY[c]-PY[a],v2=PZ[c]-PZ[a], w0=PX[d]-PX[a],w1=PY[d]-PY[a],w2=PZ[d]-PZ[a];
    ll det = u0*(v1*w2-v2*w1) - u1*(v0*w2-v2*w0) + u2*(v0*w1-v1*w0);
    return det==0;
}
/* circumsphere of a,b,c,d (non-coplanar): det>0, u = det*center, T = det^2*radius^2 */
static void circum(int a,int b,int c,int d, i128 *det, i128 u[3], i128 *T){
    ll M[3][3], r[3]; int q[3]={b,c,d};
    for (int i=0;i<3;i++){ int p=q[i];
        M[i][0]=2*(PX[p]-PX[a]); M[i][1]=2*(PY[p]-PY[a]); M[i][2]=2*(PZ[p]-PZ[a]);
        r[i]=(ll)PX[p]*PX[p]+(ll)PY[p]*PY[p]+(ll)PZ[p]*PZ[p]-((ll)PX[a]*PX[a]+(ll)PY[a]*PY[a]+(ll)PZ[a]*PZ[a]); }
    i128 D = (i128)M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - (i128)M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0]) + (i128)M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]);
    i128 adj[3][3] = {{(i128)M[1][1]*M[2][2]-(i128)M[1][2]*M[2][1], -((i128)M[0][1]*M[2][2]-(i128)M[0][2]*M[2][1]), (i128)M[0][1]*M[1][2]-(i128)M[0][2]*M[1][1]},
                      {-((i128)M[1][0]*M[2][2]-(i128)M[1][2]*M[2][0]), (i128)M[0][0]*M[2][2]-(i128)M[0][2]*M[2][0], -((i128)M[0][0]*M[1][2]-(i128)M[0][2]*M[1][0])},
                      {(i128)M[1][0]*M[2][1]-(i128)M[1][1]*M[2][0], -((i128)M[0][0]*M[2][1]-(i128)M[0][1]*M[2][0]), (i128)M[0][0]*M[1][1]-(i128)M[0][1]*M[1][0]}};
    for (int i=0;i<3;i++) u[i]=adj[i][0]*r[0]+adj[i][1]*r[1]+adj[i][2]*r[2];
    if (D<0){ D=-D; for(int i=0;i<3;i++) u[i]=-u[i]; }
    i128 t=0; i128 dx=D*PX[a]-u[0], dy=D*PY[a]-u[1], dz=D*PZ[a]-u[2]; t=dx*dx+dy*dy+dz*dz;
    *det=D; *T=t;
}
static int members[4096];
int main(int argc, char **argv){
    n=atoi(argv[1]); int minpts = argc>2 ? atoi(argv[2]) : 5; N=n*n*n;
    for (int p=0;p<N;p++){ PX[p]=p/(n*n); PY[p]=(p/n)%n; PZ[p]=p%n; }
    long nspheres=0, ninc=0;
    for (int a=0;a<N;a++) for (int b=a+1;b<N;b++) for (int c=b+1;c<N;c++) for (int d=c+1;d<N;d++){
        if (coplanar(a,b,c,d)) continue;
        i128 D,u[3],T; circum(a,b,c,d,&D,u,&T);
        int m=0;
        for (int p=0;p<N;p++){ i128 dx=D*PX[p]-u[0], dy=D*PY[p]-u[1], dz=D*PZ[p]-u[2]; if (dx*dx+dy*dy+dz*dz==T) members[m++]=p; }
        if (m<minpts) continue;
        ninc++;
        /* canonical representative: lexicographically first non-coplanar 4-subset of members */
        int found=0, ra=-1,rb=-1,rc=-1,rd=-1;
        for (int i=0;i<m&&!found;i++) for (int j=i+1;j<m&&!found;j++) for (int k=j+1;k<m&&!found;k++) for (int l=k+1;l<m&&!found;l++)
            if (!coplanar(members[i],members[j],members[k],members[l])){ ra=members[i];rb=members[j];rc=members[k];rd=members[l];found=1; }
        if (ra==a&&rb==b&&rc==c&&rd==d){ nspheres++; printf("%d",m); for(int i=0;i<m;i++) printf(" %d",members[i]); printf("\n"); }
    }
    fprintf(stderr,"n=%d spheres_with_ge_%d_points=%ld incidences(4-subsets)=%ld\n", n, minpts, nspheres, ninc);
    return 0;
}
