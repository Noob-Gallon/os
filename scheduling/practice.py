# %%
# First Come First Serverd
from classes.Scheduler import FCFS
from classes.Scheduler import SJF
from classes.Scheduler import PSJF
from classes.Scheduler import SRTF
from classes.Scheduler import PSRTF
from classes.Scheduler import Priority
from classes.Scheduler import PPriority
from classes.Scheduler import RoundRobin
# from classes.Scheduler import PriorityRoundRobin
from classes.Scheduler import MultiQueue

##################################################################
###                        execution                           ###
##################################################################

# Make a instance of FCFS
# 나중에 json으로 바꿔야 함.
fcfs = FCFS()
sjf = SJF()
psjf = PSJF()
srtf = SRTF()
psrtf = PSRTF()
priority = Priority()
ppriority = PPriority()
roundRobin = RoundRobin()
# priorityRoundRobin = PriorityRoundRobin()
multiQueue = MultiQueue()

# p = []
# p.append(Process(6, 0, 0))
# p.append(Process(8, 0, 0))
# p.append(Process(7, 0, 0))
# p.append(Process(3, 0, 0))

# First, Insert the processes inforamtion in the scheduler.
# Check the arrival of the process every unit time.

# fcfs.addProcesses()
# fcfs.startScheduling({'type': 1})
# fcfs.printEvaulation()
# fcfs.displayGanttChart()

# sjf.addProcesses()
# sjf.startScheduling(typeObject={'type': 2,
#                                 'sortFunc': sjf.sortByBurstTimeAsc,
#                                 'checkNewProcessArrivalFunc': sjf.checkNewProcessArrival})
# # psjf.printEvaulation()
# sjf.displayGanttChart()

# psjf.addProcesses()
# psjf.startScheduling(typeObject={'type': 3,
#                                  'sortFunc': psjf.sortByBurstTimeAsc,
#                                  'checkNewProcessArrivalFunc': psjf.checkNewProcessArrival,
#                                  'checkPreemptConditionFunc': psjf.checkPreemptCondition})
# # psjf.printEvaulation()
# psjf.displayGanttChart()

# srtf.addProcesses()
# srtf.startScheduling(typeObject={'type': 4,
#                                  'sortFunc': srtf.sortByRemainingTimeAsc,
#                                  'checkNewProcessArrivalFunc': srtf.checkNewProcessArrival})
# # srtf.printEvaulation()
# srtf.displayGanttChart()

# psrtf.addProcesses()
# psrtf.startScheduling(typeObject={'type': 5,
#                                   'sortFunc': psrtf.sortByRemainingTimeAsc,
#                                   'checkNewProcessArrivalFunc': psrtf.checkNewProcessArrival,
#                                   'checkPreemptConditionFunc': psrtf.checkPreemptCondition})
# # psrtf.printEvaulation()
# psrtf.displayGanttChart()

# priority.addProcesses()
# priority.startScheduling(typeObject={'type': 6,
#                                      'sortFunc': priority.sortByPriorityAsc,
#                                      'checkNewProcessArrivalFunc': priority.checkNewProcessArrival})
# # priority.printEvaulation()
# priority.displayGanttChart()

# ppriority.addProcesses()
# ppriority.startScheduling(typeObject={'type': 7,
#                                       'sortFunc': ppriority.sortByPriorityAsc,
#                                       'checkNewProcessArrivalFunc': ppriority.checkNewProcessArrival,
#                                       'checkPreemptConditionFunc': ppriority.checkPreemptCondition})
# # ppriority.printEvaulation()
# ppriority.displayGanttChart()

# roundRobin.addProcesses()
# roundRobin.startScheduling(typeObject={'type': 8})
# # roundRobin.printEvaulation()
# roundRobin.displayGanttChart()

# priorityRoundRobin.addProcesses()
# priorityRoundRobin.startScheduling(typeObject={'type': 9})
# # priorityRoundRobin.printEvaulation()
# priorityRoundRobin.displayGanttChart()

multiQueue.addProcesses()
multiQueue.startScheduling(typeObject={'type': 10})
# priorityRoundRobin.printEvaulation()
multiQueue.displayGanttChart()

# %%
