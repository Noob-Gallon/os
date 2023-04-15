import json
from scheduler import PSJF
from process import Process


##################################################################
###                        execution                           ###
##################################################################


psjf = PSJF()

p = []
p.append(Process(7, 0))
p.append(Process(2, 1))
p.append(Process(8, 0))
p.append(Process(4, 2))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
psjf.addProcesses(p)

psjf.startScheduling()
psjf.printEvaulation()
psjf.displayGanttChart()
