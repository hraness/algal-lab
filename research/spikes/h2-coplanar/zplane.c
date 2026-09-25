/* Brute-force count of coplanar 5-subsets of [0,n)^3.
 * Usage: ./zplane n
 * Prints: n, Z_plane (= all coplanar 5-subsets, collinear included).
 * Coplanarity: 5 points p1..p5 are coplanar iff the four difference
 * vectors u_i = p_i - p_1 (i=2..5) have rank <= 2, iff all four
 * 3x3 minors det[u_a u_b u_c] vanish.
 */
#include <stdio.h>
#include <stdlib.h>

static long long det3(const long long a[3], const long long b[3], const long long c[3]) {
    return a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]);
}

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    long long m = (long long)n*n*n;
    long long (*p)[3] = malloc(m*3*sizeof(long long));
    long long i = 0;
    for (long long x=0;x<n;x++) for (long long y=0;y<n;y++) for (long long z=0;z<n;z++) {
        p[i][0]=x; p[i][1]=y; p[i][2]=z; i++;
    }
    long long zplane = 0, zcoll = 0;
    for (long long a=0;a<m-4;a++)
    for (long long b=a+1;b<m-3;b++)
    for (long long c=b+1;c<m-2;c++)
    for (long long d=c+1;d<m-1;d++)
    for (long long e=d+1;e<m;e++) {
        long long u[4][3];
        long long base[3] = {p[a][0],p[a][1],p[a][2]};
        long long idx[4] = {b,c,d,e};
        for (int r=0;r<4;r++) for (int j=0;j<3;j++) u[r][j] = p[idx[r]][j]-base[j];
        if (det3(u[0],u[1],u[2])==0 && det3(u[0],u[1],u[3])==0 &&
            det3(u[0],u[2],u[3])==0 && det3(u[1],u[2],u[3])==0) {
            zplane++;
            /* collinear iff all u_i parallel to u_2 (rank <= 1): check the
               four pair-cross products u_i x u_j == 0 */
            int coll = 1;
            for (int r=0;r<4 && coll;r++) for (int s=r+1;s<4 && coll;s++) {
                long long cr[3] = {
                    u[r][1]*u[s][2]-u[r][2]*u[s][1],
                    u[r][2]*u[s][0]-u[r][0]*u[s][2],
                    u[r][0]*u[s][1]-u[r][1]*u[s][0]};
                if (cr[0]||cr[1]||cr[2]) coll = 0;
            }
            if (coll) zcoll++;
        }
    }
    printf("n=%d Z_plane=%lld Z_coll=%lld\n", n, zplane, zcoll);
    return 0;
}
