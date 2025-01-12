import os
from ortools.sat.python import cp_model
import datetime
from matrix2ascii import matrix2ascii

# 以下参数会算至年底
isLeapYear = 0  # 是否闰年
isWeek = True  # 是否带星期

year = 2025  # 仅作为输出使用
startMonth = 1  # 第一天是几月
startDay = 1  # 第一天是几号
startWeekday = 3  # 第一天是星期几

maxSolNum = 10  # 最大解数量

startTime = datetime.datetime.now()


def solve(day, month, weekday, isWeek, maxSolNum, outfileName):
    # 参数
    num_col = 7  # 列数
    if isWeek:
        num_row = 8  # 行数
        num_pieces = 10  # 拼图片数
        num_piece = 5  # 每片拼图包含的方块数（最大值）
    else:
        num_row = 7
        num_pieces = 8
        num_piece = 6

    model = cp_model.CpModel()
    work = {}
    # 创建【拼图块型号，方块号，拼图块排布形态，行号，列号】的五维0-1数组
    for p in range(num_pieces):
        for n in range(num_piece):
            for s in range(8):
                for r in range(num_row):
                    for c in range(num_col):
                        work[p, n, s, r, c] = model.NewBoolVar(
                            "work_%i_%i_%i_%i_%i" % (p, n, s, r, c)
                        )

    # 输入条件以及
    # 每个行号、列号只有一种方块的一种形态的一个号(个别位置没有)
    def addRowColConstraint(r, c):
        model.Add(
            sum(
                work[p, n, s, r, c]
                for p in range(num_pieces)
                for n in range(num_piece)
                for s in range(8)
            )
            == 0
        )

    def addRowColConstraints():
        rowDay = int((day - 1) / 7) + 2
        colDay = (day - 1) % 7
        rowMonth = int((month - 1) / 6)
        colMonth = (month - 1) % 6
        if isWeek:
            rowWeek = int(weekday / 4) + 6
            colWeek = weekday % 4 + 3 + rowWeek - 6
        # print(rowWeek, colWeek)

        for r in range(num_row):
            for c in range(num_col):
                if (
                    (r == 0 and c == 6)
                    or (r == 1 and c == 6)
                    or (r == 6 and c > 2 and (not isWeek))
                    or (r == 7 and c < 4 and isWeek)
                ):
                    """不可选择的位置"""
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for p in range(num_pieces)
                            for n in range(num_piece)
                            for s in range(8)
                        )
                        == 0
                    )
                elif r == rowDay and c == colDay:
                    addRowColConstraint(r, c)
                elif r == rowMonth and c == colMonth:
                    addRowColConstraint(r, c)
                elif r == rowWeek and c == colWeek and isWeek:
                    addRowColConstraint(r, c)
                else:
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for p in range(num_pieces)
                            for n in range(num_piece)
                            for s in range(8)
                        )
                        == 1
                    )
    addRowColConstraints()
    
    # 每种拼图块的每个方块号只有1个行号、列号、形态（含不可选择的方块号）
    def addPieceConstraint():
        if not isWeek:
            for p in range(num_pieces):
                for n in range(num_piece):
                    if p < 7 and n == 5:
                        "不可选择的方块号"
                        model.Add(
                            sum(
                                work[p, n, s, r, c]
                                for r in range(num_row)
                                for c in range(num_col)
                                for s in range(8)
                            )
                            == 0
                        )
                    else:
                        model.Add(
                            sum(
                                work[p, n, s, r, c]
                                for r in range(num_row)
                                for c in range(num_col)
                                for s in range(8)
                            )
                            == 1
                        )
        else:
            for p in range(num_pieces):
                for n in range(num_piece):
                    if p > 6 and n == 4:
                        "不可选择的方块号"
                        model.Add(
                            sum(
                                work[p, n, s, r, c]
                                for r in range(num_row)
                                for c in range(num_col)
                                for s in range(8)
                            )
                            == 0
                        )
                    else:
                        model.Add(
                            sum(
                                work[p, n, s, r, c]
                                for r in range(num_row)
                                for c in range(num_col)
                                for s in range(8)
                            )
                            == 1
                        )

    addPieceConstraint()
    # 每种型号的所有方块的形态号统一
    if not isWeek:
        for p in range(num_pieces):
            for s in range(8):
                if p == 7:
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        <= 6
                    )
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        != 5
                    )
                else:
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        <= 5
                    )
                model.Add(
                    sum(
                        work[p, n, s, r, c]
                        for r in range(num_row)
                        for c in range(num_col)
                        for n in range(num_piece)
                    )
                    != 4
                )
    else:
        for p in range(num_pieces):
            for s in range(8):
                if p >= 7:
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        <= 4
                    )
                else:
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        <= 5
                    )
                    model.Add(
                        sum(
                            work[p, n, s, r, c]
                            for r in range(num_row)
                            for c in range(num_col)
                            for n in range(num_piece)
                        )
                        != 4
                    )
    for p in range(num_pieces):
        for s in range(8):
            model.Add(
                sum(
                    work[p, n, s, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                != 3
            )
            model.Add(
                sum(
                    work[p, n, s, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                != 2
            )
            model.Add(
                sum(
                    work[p, n, s, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                != 1
            )
    """不要求日期时使用                
    # 前两行空的必须为1(月份)
    model.Add(
        sum(work[p, n, s, r, c] for p in range(num_pieces)
            for n in range(num_piece) for s in range(8) for r in range(2)
            for c in range(num_col)) == 11)
    """

    # 拼图块内距离约束
    def addDistance(di, dj, pnum, nnum, nnum2):
        """
        nnum：源方块序号
        nnum2：目标方块序号
        """
        d = [di, dj]
        for r in range(num_row):
            for c in range(num_col):
                s = 0
                """
                if r==0 and c==0:
                    print()
                """
                for i in [1, -1]:
                    for j in [1, -1]:
                        for k in [0, 1]:
                            row = r + i * d[k]
                            col = c + j * d[1 - k]
                            """#for print
                            if r==0 and c==0:
                                strk=['i','j'][k]
                                strk2=['i','j'][1-k]
                                stri=['','+','-'][i]
                                strj=['','+','-'][j]
                                print("(r{}{},c{}{})".format(stri,strk,strj,strk2),end='')
                            """
                            if (
                                row < num_row
                                and col < num_col
                                and row >= 0
                                and col >= 0
                            ):
                                # print([pnum, nnum, s, r, c])
                                # print([pnum, nnum2, s, row, col])
                                model.Add(
                                    (
                                        work[pnum, nnum, s, r, c]
                                        + work[pnum, nnum2, s, row, col]
                                        != 1
                                    )
                                )
                            else:
                                # 该形态不能出现在该位置
                                model.Add(work[pnum, nnum, s, r, c] == 0)
                            s = s + 1

    def addDistances():
        # 禁用形态
        """
        0:原始
        1:逆时针旋转90后左右翻转（左下右上45°翻转）
        2:左右翻转-
        3:逆时针旋转90
        4:上下翻转
        5:顺时针旋转90-
        6:旋转180-
        7:顺时针旋转90后左右翻转（左上右下45°翻转）-
        """

        # 0号拼图(两种都有)
        """
        012
        34
        """
        addDistance(1, 1, 0, 0, 4)
        addDistance(1, 0, 0, 0, 3)
        addDistance(0, 2, 0, 0, 2)
        addDistance(0, 1, 0, 0, 1)
        # 1号拼图（两种都有）
        """
        0
        1
        234
        """
        addDistance(2, 2, 1, 0, 4)
        addDistance(2, 1, 1, 0, 3)
        addDistance(2, 0, 1, 0, 2)
        addDistance(1, 0, 1, 0, 1)
        model.Add(
            sum(
                work[1, n, 1, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[1, n, 3, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[1, n, 5, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[1, n, 7, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        # 2号拼图（两种都有）
        """
        01
        2
        34
        """
        addDistance(2, 2, 2, 0, 4)
        addDistance(2, 1, 2, 0, 3)
        addDistance(1, 1, 2, 0, 2)
        addDistance(0, 1, 2, 0, 1)
        model.Add(
            sum(
                work[2, n, 4, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[2, n, 5, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[2, n, 6, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[2, n, 7, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        # 3号拼图（两种都有）
        """
        0
        1
        23
        4
        """
        addDistance(3, 1, 3, 0, 4)
        addDistance(2, 1, 3, 0, 3)
        addDistance(2, 0, 3, 0, 2)
        addDistance(1, 0, 3, 0, 1)

        # 4号拼图（两种都有）
        """
        0
        1
        2
        34
        """
        addDistance(3, 1, 4, 0, 4)
        addDistance(3, 0, 4, 0, 3)
        addDistance(2, 0, 4, 0, 2)
        addDistance(1, 0, 4, 0, 1)
        # 5号拼图（两种都有）
        """
        0 1
        234
        """
        addDistance(1, 2, 5, 0, 4)
        addDistance(1, 1, 5, 0, 3)
        addDistance(1, 0, 5, 0, 2)
        addDistance(0, 2, 5, 0, 1)
        model.Add(
            sum(
                work[5, n, 2, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[5, n, 5, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[5, n, 6, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        model.Add(
            sum(
                work[5, n, 7, r, c]
                for r in range(num_row)
                for c in range(num_col)
                for n in range(num_piece)
            )
            == 0
        )
        if not isWeek:
            # 6号拼图
            """
            0
            1
            23
            4
            """
            addDistance(3, 0, 6, 0, 4)
            addDistance(2, 1, 6, 0, 3)
            addDistance(2, 0, 6, 0, 2)
            addDistance(1, 0, 6, 0, 1)
            # 7号拼图
            """
            012  
            345
            """
            addDistance(1, 2, 7, 0, 5)
            addDistance(1, 1, 7, 0, 4)
            addDistance(1, 0, 7, 0, 3)
            addDistance(0, 2, 7, 0, 2)
            addDistance(0, 1, 7, 0, 1)
            for s in range(2, 8):
                model.Add(
                    sum(
                        work[7, n, s, r, c]
                        for r in range(num_row)
                        for c in range(num_col)
                        for n in range(num_piece)
                    )
                    == 0
                )
        else:
            # 6号拼图
            """
            0
            123
            4
            """
            addDistance(2, 0, 6, 0, 4)
            addDistance(1, 2, 6, 0, 3)
            addDistance(1, 1, 6, 0, 2)
            addDistance(1, 0, 6, 0, 1)
            model.Add(
                sum(
                    work[6, n, 3, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                == 0
            )
            model.Add(
                sum(
                    work[6, n, 4, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                == 0
            )
            model.Add(
                sum(
                    work[6, n, 6, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                == 0
            )
            model.Add(
                sum(
                    work[6, n, 7, r, c]
                    for r in range(num_row)
                    for c in range(num_col)
                    for n in range(num_piece)
                )
                == 0
            )

            # 7号拼图
            """
            0
            1
            2
            3
            """
            addDistance(3, 0, 7, 0, 3)
            addDistance(2, 0, 7, 0, 2)
            addDistance(1, 0, 7, 0, 1)
            for s in range(2, 8):
                model.Add(
                    sum(
                        work[7, n, s, r, c]
                        for r in range(num_row)
                        for c in range(num_col)
                        for n in range(num_piece)
                    )
                    == 0
                )

            # 8号拼图
            """
            0
            1
            23
            """
            addDistance(2, 1, 8, 0, 3)
            addDistance(2, 0, 8, 0, 2)
            addDistance(1, 0, 8, 0, 1)

            # 9号拼图
            """
            01
            23
            """
            addDistance(1, 2, 9, 0, 3)
            addDistance(1, 1, 9, 0, 2)
            addDistance(0, 1, 9, 0, 1)
            for s in range(4, 8):
                model.Add(
                    sum(
                        work[9, n, s, r, c]
                        for r in range(num_row)
                        for c in range(num_col)
                        for n in range(num_piece)
                    )
                    == 0
                )

    addDistances()
    # 求解
    solver = cp_model.CpSolver()
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    # solver.parameters.num_search_workers = 4
    # solver.parameters.interleave_search = False
    class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, variables, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__variables = variables
            self.__solution_count = 0
            self.__solution_limit = limit

        def on_solution_callback(self):
            self.__solution_count += 1
            print方案 = "第%i种方案：\n" % self.__solution_count
            print(print方案)
            endTime = datetime.datetime.now()
            # 输出结果到文件
            matrix = []
            for r in range(num_row):
                matrix.append([])
                for c in range(num_col):
                    matrix[r].append([])
                    isprint = False
                    for p in range(num_pieces):
                        for s in range(8):
                            for n in range(num_piece):
                                if self.BooleanValue(self.__variables[p, n, s, r, c]):
                                    isprint = True
                                    matrix[r][c] = p + 1
                    if not isprint:
                        matrix[r][c] = 0

            ascii = matrix2ascii(matrix, 1)
            ascii2 = matrix2ascii(matrix, 2)
            print(ascii2)
            with open(outfileName, "a+", encoding="utf-8") as f:
                f.write(print方案)
                f.write(ascii)
                f.close()
            print(endTime - startTime)
            print()
            with open("print.log", "a+", encoding="utf-8") as f2:
                timeSingle = endTime - startTime
                seconds = timeSingle.total_seconds()
                if isWeek:
                    f2.write(
                        "{}|月|{}|日|星期|{}|方案|{}|程序已运行|{}|{}|秒\n".format(
                            month,
                            day,
                            weekday,
                            self.__solution_count,
                            endTime - startTime,
                            seconds,
                        )
                    )
                else:
                    f2.write(
                        "{}|月|{}|日|    |  |方案|{}|程序已运行|{}|{}|秒\n".format(
                            month,
                            day,
                            self.__solution_count,
                            endTime - startTime,
                            seconds,
                        )
                    )
                f2.close()
            if self.__solution_count >= self.__solution_limit:
                self.StopSearch()

        def solution_count(self):
            return self.__solution_count

    solution_printer = VarArraySolutionPrinter(work, maxSolNum)  # 修改以改变解数量
    status = solver.Solve(model, solution_printer)
    assert solution_printer.solution_count() == maxSolNum  # 修改以改变解数量
    # 统计结果
    print("统计数据")
    # print('  - 状态       : %s' % solver.StatusName(status))
    print("  - 状态       : ", end="")
    if solver.StatusName(status) == "OPTIMAL":
        print("最优解")
    elif solver.StatusName(status) == "FEASIBLE":
        print("可行解")
    elif solver.StatusName(status) == "INFEASIBLE":
        print("无解")
    else:
        print(solver.StatusName(status))
    print("  - 冲突       : %i" % solver.NumConflicts())
    print("  - 分支       : %i" % solver.NumBranches())
    print("  - 运行时长   : %f s" % solver.WallTime())
    with open("print2.log", "a+", encoding="utf-8") as f3:
        f3.write(
            "月|{}|日|{}|星期|{}|状态|{}|冲突|{}|分支|{}|运行时长|{}|方案数|{}\n".format(
                month,
                day,
                weekday,
                solver.StatusName(status),
                solver.NumConflicts(),
                solver.NumBranches(),
                solver.WallTime(),
                maxSolNum,
            )
        )


# from csv2html import csv2md
def makeOutFile(year, month, day, weekday, isWeek):
    if isWeek:
        outfileName = "./已完成结果/{}/{}月{}日星期{}.md".format(
            year, month, day, weekday
        )
    else:
        outfileName = "./已完成结果/{}/{}月{}日无星期.md".format(year, month, day)
    if not os.path.exists("./已完成结果/{}".format(year)):
        os.makedirs("./已完成结果/{}".format(year))
    with open(outfileName, "w+", encoding="utf-8") as f:
        if isWeek:
            f.write("{}年{}月{}日星期{}\n".format(year, month, day, weekday))
        else:
            f.write("{}年{}月{}日\n".format(year, month, day))
        f.close()
    return outfileName


def main(isLeapYear, isWeek, startMonth, startDay, startWeekday, maxSolNum):
    # day = 29  #日，均从1开始
    # month = 8  #月
    # weekday = 2  #星期,0表示星期天
    """isLeapYear = 0 #是否闰年
    isWeek = True  #是否带星期
    startMonth = 9  #第一天是几月
    startDay = 10  #第一天是几号
    startWeekday = 0  #第一天是星期几
    maxSolNum = 50  #最大解数量"""

    # for month in range(8, 13):#月范围
    for month in range(startMonth, 13):  # 月范围
        list31 = [1, 3, 5, 7, 8, 10, 12]
        if month in list31:
            maxDay = 31
        else:
            maxDay = 30
        for day in range(1, maxDay + 1):
            if day < startDay and month == startMonth:
                continue
            if month == 2 and day >= 29 + isLeapYear:
                continue
            weekday = startWeekday % 7
            startWeekday += 1
            print("{}月{}日星期{}".format(month, day, weekday))
            print("开始计算")
            outfileName = makeOutFile(year, month, day, weekday, isWeek)
            newfileName = outfileName.replace(".md", "-完成.md")
            if os.path.isfile(newfileName):
                print("已计算过")
                os.remove(outfileName)
                continue
            solve(day, month, weekday, isWeek, maxSolNum, outfileName)
            os.rename(outfileName, newfileName)

if __name__ == "__main__":
    main(isLeapYear, isWeek, startMonth, startDay, startWeekday, maxSolNum)
