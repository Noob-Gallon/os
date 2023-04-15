# Shortest Job First
import json
from classes.Scheduler import SJF
from classes.Process import Process

##################################################################
###                        execution                           ###
##################################################################

sjf = SJF()

p = []
# p.append(Process(7, 0))
# p.append(Process(8, 4))
# p.append(Process(4, 5))
# p.append(Process(4, 2))

p.append(Process(7, 0, 0))
p.append(Process(8, 4, 0))
p.append(Process(5, 5, 0))
p.append(Process(4, 2, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
sjf.addProcesses(p)
sjf.startScheduling()
sjf.printEvaulation()
sjf.displayGanttChart()
