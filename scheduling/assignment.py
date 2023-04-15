# %%
import json
import plotly.figure_factory as ff
import plotly.graph_objs as go
from scheduling.Scheduler import *
from Process import Process

##################################################################
###                        execution                           ###
##################################################################

# Make a instance of FCFS
# 나중에 json으로 바꿔야 함.
fcfs = FCFS()
sjf = SJF()
psjf = PSJF()

# 문제 발견
# 동시에 p를 주면 오류가 발생함
# 이것은 deep copy와 shallow copy에 관련있는 것으로 보임.
# 조금 더 생각해 보아야 할 듯.
p = []
p.append(Process(7, 0))
p.append(Process(2, 1))
p.append(Process(8, 0))
p.append(Process(4, 2))

p2 = []
p2.append(Process(7, 0))
p2.append(Process(2, 1))
p2.append(Process(8, 0))
p2.append(Process(4, 2))

p3 = []
p3.append(Process(7, 0))
p3.append(Process(2, 1))
p3.append(Process(8, 0))
p3.append(Process(4, 2))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
fcfs.addProcesses(p)
sjf.addProcesses(p2)
psjf.addProcesses(p3)

fcfs.startScheduling()
sjf.startScheduling()
psjf.startScheduling()

fcfs.printEvaulation()
fcfs.displayGanttChart()

sjf.printEvaulation()
sjf.displayGanttChart()

psjf.printEvaulation()
psjf.displayGanttChart()

# %%
