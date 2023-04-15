import json
import plotly.figure_factory as ff
import plotly.graph_objs as go
from Scheduler import FCFS
from Process import Process

##################################################################
###                        execution                           ###
##################################################################

# Make a instance of FCFS
# 나중에 json으로 바꿔야 함.
fcfs = FCFS()

p = []
p.append(Process(6, 0))
p.append(Process(8, 0))
p.append(Process(7, 0))
p.append(Process(3, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
fcfs.addProcesses(p)

fcfs.startScheduling()
fcfs.printEvaulation()
fcfs.displayGanttChart()

# fcfs.printResult()
