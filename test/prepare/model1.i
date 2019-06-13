Simple test model
c cells
1 1 -7.8  1 -2 5 -8 12 -13 imp:n=1
2 2 -1.0  1 -2 7 -8 11 -12 imp:n=1
3 0       1 -2 3 -7 10 -12 imp:n=1 FILL=1
4 0       1 -2 8 -9 10 -12 imp:n=1 FILL=2 (8 3 1.5)
10 2 -1.0 1 -2 5 -6 11 -14 imp:n=1 U=1
11 2 -1.0 1 -2 3 -4 11 -13 imp:n=1 U=1
12 0      #10 #11 imp:n=1 U=1
21 1 -7.8 -15 imp:n=1 U=2
22 0       15 imp:n=1 U=2

c surfaces
1 PZ 0
2 PZ 3
3 PX -1
4 PX  1
5 PX  3
6 PX  4.5
7 PX  5
8 PX  7
9 PX  9
10 PY 0
11 PY 2
12 PY 4
13 PY 6
14 PY 8
15 SO 1

c data
M1 26056.31c 1
M2 1001.31c 2 8016.31c 1
