class Solution:
    def __init__(self):
        self.value = -1
        self.rst = []

    def get_path(self,matrix, i, j, n, m, flag, path, s):
        if i == 0 and j == m - 1 and s >= 0 and s > self.value:
            path.append([i, j])
            self.value = s
            self.rst = path[:]
            return 1

        if not (i >= 0 and i < n and j >= 0 and j < m and flag[i][j] == 1 and matrix[i][j] == 1):
            return -1

        if s <= 0:
            if i == 0 and j == m - 1:

                return 1
            else:
                return -1

        flag[i][j] = 0
        path.append([i, j])

        left, right, top, bottom = 1, 1, 1, 1
        if s >= 1:
            left = self.get_path(matrix, i - 1, j, n, m, flag, path, s - 1)
            right = self.get_path(matrix, i + 1, j, n, m, flag, path, s - 1)
        if s >= 3:
            top = self.get_path(matrix, i, j - 1, n, m, flag, path, s - 3)
        bottom = self.get_path(matrix, i, j + 1, n, m, flag, path, s)

        if not (left or right or top or bottom):
            return -1

        path.pop()
        flag[i][j] = 1

        return 1


if __name__ == "__main__":
    input = [int(x) for x in raw_input().split()]
    n, m, s = input[0], input[1], input[2]
    matrix = []
    flag = [[1 for x in xrange(m)] for i in xrange(n)]

    for i in xrange(n):
        input = [int(x) for x in raw_input().split()]
        matrix.append(input)



    path = []
    so = Solution()
    f = so.get_path(matrix, 0, 0, n, m, flag, path, s)

    if f == 1:
        lenth = len(so.rst)
        out =""
        for index in xrange(lenth-1):
            out = out +  str(so.rst[index]) + ","
        print out + str(so.rst[lenth -1])
    else:
        print "Can not escape!"
