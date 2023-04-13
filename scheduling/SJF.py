import json
from scheduler import SJF
from process import Process


##################################################################
###                        execution                           ###
##################################################################


sjf = SJF()

p = []
p.append(Process(7, 0))
p.append(Process(4, 2))
p.append(Process(1, 4))
p.append(Process(4, 5))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
for process in p:
    sjf.addProcess(process)

sjf.startScheduling()
# fcfs.printResult()

sjf.printEvaulation()
