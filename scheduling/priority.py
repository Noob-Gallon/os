# Preemptive Shortest Remaining Time First
import json
from classes.Scheduler import Priority
from classes.Process import Process


##################################################################
###                        execution                           ###
##################################################################


priority = Priority()

p = []
p.append(Process(7, 0, 0))
p.append(Process(2, 1, 0))
p.append(Process(8, 0, 0))
p.append(Process(4, 4, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
priority.addProcesses(p)
priority.startScheduling()
priority.printEvaulation()
priority.displayGanttChart()
