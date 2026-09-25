/* zero5: exact count of 5-subsets of a point set in Z^3 whose lifted 5x5
 * determinant (rows x,y,z,x^2+y^2+z^2,1) vanishes.  Uses the 4x4 determinant
 * of lifted differences in __int128 (safe for coordinates below 2^20).
 * Input: lines "x y z".  Output: "zeros=<count> subsets=<count>" and up to
 * MAXPRINT zero subsets as index lists.  Usage: zero5 [maxprint] < points */
#include <stdio.h>
#include <stdlib.h>
typedef __int128 i128; typedef long long ll;
static ll X[8192][4]; static int m;
static i128 det4(i128 a[4][4]){
  i128 s=0;
  for(int c=0;c<4;c++){
    i128 sub[3][3]; for(int r=1;r<4;r++){int cc=0; for(int j=0;j<4;j++) if(j!=c) sub[r-1][cc++]=a[r][j];}
    i128 d=sub[0][0]*(sub[1][1]*sub[2][2]-sub[1][2]*sub[2][1])-sub[0][1]*(sub[1][0]*sub[2][2]-sub[1][2]*sub[2][0])+sub[0][2]*(sub[1][0]*sub[2][1]-sub[1][1]*sub[2][0]);
    i128 t=a[0][c]*d; s+=(c&1)?-t:t; }
  return s; }
int main(int argc,char**argv){
  long maxprint=argc>1?atol(argv[1]):20; ll x,y,z;
  while(scanf("%lld %lld %lld",&x,&y,&z)==3){
    if(m>=8192){ fprintf(stderr,"zero5: more than 8192 points\n"); return 2; }
    X[m][0]=x;X[m][1]=y;X[m][2]=z;X[m][3]=x*x+y*y+z*z; m++; }
  long long zeros=0, subsets=0;
  for(int a=0;a<m;a++)for(int b=a+1;b<m;b++)for(int c=b+1;c<m;c++)for(int d=c+1;d<m;d++)for(int e=d+1;e<m;e++){
    int R[4]={b,c,d,e}; i128 M[4][4]; for(int r=0;r<4;r++)for(int j=0;j<4;j++) M[r][j]=(i128)(X[R[r]][j]-X[a][j]);
    subsets++; if(det4(M)==0){ zeros++; if(zeros<=maxprint) printf("zero %d %d %d %d %d\n",a,b,c,d,e); } }
  printf("zeros=%lld subsets=%lld\n",zeros,subsets); return 0; }
