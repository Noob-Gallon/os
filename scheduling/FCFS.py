import json
from scheduler import FCFS
from process import Process

##################################################################
###                        execution                           ###
##################################################################

# Make a instance of FCFS
fcfs = FCFS()

p = []
p.append(Process(6, 0))
p.append(Process(8, 0))
p.append(Process(7, 17))
p.append(Process(3, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.
for process in p:
    fcfs.addProcess(process)

fcfs.startScheduling()
# fcfs.printResult()

fcfs.printEvaulation()
