# Preemptive Shortest Job First
import json
from classes.Scheduler import PSJF
from classes.Process import Process


##################################################################
###                        execution                           ###
##################################################################


psjf = PSJF()

p = []
p.append(Process(7, 0, 0))
p.append(Process(2, 1, 0))
p.append(Process(8, 0, 0))
p.append(Process(4, 2, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
psjf.addProcesses(p)
psjf.startScheduling()
psjf.printEvaulation()
psjf.displayGanttChart()
