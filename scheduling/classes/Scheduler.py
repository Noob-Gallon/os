from functools import wraps
from matplotlib import cm
from abc import *  # import to implement interface(abstract class)
import matplotlib.pyplot as plt
import json
from pathlib import Path
from . import Process as p

type = {
    "FCFS": 1,
    "SJF": 2,
    "PSJF": 3,
    "SRTF": 4,
    "PSRTF": 5,
    "Priority": 6,
    "PPriority": 7,
    "RR": 8,
    "PriorityRR": 9,
    "MultiLevelQ": 10,
    "MultiLevelFeedbackQ": 11,
}


def override(superclass):
    # This function is used to present the explicit annotation of override.
    def overrider(method):
        assert method.__name__ in dir(
            superclass), f"{method.__name__} not found in {superclass.__name__}"

        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        return wrapper
    return overrider


class Scheduler:
    # Scheduler class
    # Basically, it is FCFS(First-Come-First-Server)
    # Implement another scheduling algorithm by inheriting this class.

    # This class ontains the instances of process class.
    # Each process class means the job need to be executed.

    def __init__(self):
        # processList는 새로운 프로세스의 도착을 확인하기 위하여 도입되었음.
        self.processList = []
        self.readyQueue = []
        self.terminatedQueue = []
        self.currentUnitTime = 0

    # Add processes into readyQueue of FCFS from JSON file.
    # Select number of the file that you want to use.
    def addProcesses(self):
        # self.processList = processes

        while (True):
            userInputNnumber = input(
                "Select number of the file that you want to use. (1~3): ")

            try:
                intNumber = int(userInputNnumber)

                if (intNumber >= 1 and intNumber <= 3):

                    fileName = "example" + userInputNnumber + ".json"

                    currentDir = Path(__file__).resolve().parent
                    jsonFilePath = currentDir / fileName

                    with open(jsonFilePath, 'r') as file:
                        processesFromJson = json.load(file)

                    for process in processesFromJson:
                        newProcess = p.Process(
                            process['burstTime'], process['arrivalTime'], process['priority'])
                        self.processList.append(newProcess)

                    # The arrival order of the equal arrivalTime processes is not broke
                    # because the sorted function is a stable sorting fuction.
                    self.processList = sorted(
                        self.processList, key=lambda process: process.arrivalTime)

                    break
                else:
                    print("Wrong input. Please select a integer number between 1 and 3")
            except:
                print("Wrong input. Please select a integer number between 1 and 3")

    def increaseUnitTime(self):
        self.currentUnitTime += 1

    # Check if the new process has arrived every unit time.
    # This is FCFS, so, checks the unit time only.
    def checkNewProcessArrival(self):
        # Search the processList to check the arrivalTime of each Process.
        # If the arrivalTime of a process matches the current unit time,
        # and add it into readyQueue.
        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                # self.processList.remove(newProcess)

    def displayGanttChart(self):

        # Colors list for dipslaying unique colors of each process.
        colors = cm.get_cmap('tab10', len(self.terminatedQueue)).colors

        # Draw the gantt chart by using matplotlib.pyplot
        fig, ax = plt.subplots()
        colorIndex = 0

        for process in self.terminatedQueue:
            print("process.executedTimeSection : ",
                  process.executedTimeSection)

            # second argument of yrange is the vertical width from first argument.
            ax.broken_barh(xranges=process.executedTimeSection, yrange=(0.1, 0.8),
                           facecolors=(colors[colorIndex]))
            # a index variable to set the color of each process.
            colorIndex += 1

        ax.set_xlim(0, self.currentUnitTime)
        ax.set_ylim(0, len(self.terminatedQueue))

        yticks = [0.5 + i for i in range(len(self.terminatedQueue))]
        yticksLabels = []
        for index in range(len(self.terminatedQueue)):
            # 추후에 스케쥴링 방법으로 변경, 하나에 그림 다 나타낼 거임.
            processName = "Process " + str(index+1)
            yticksLabels.append(processName)

        ax.set_xticks(range((self.currentUnitTime)+1))
        ax.set_yticks(yticks, yticksLabels)

        ax.set_xlabel('Timeline')
        ax.set_ylabel('Processes')

        ax.set_title('Gantt Chart: Task Execution')
        ax.grid(True)

        # plt.legend()
        # plt.grid(axis='x')
        # plt.tight_layout()
        plt.show()

    def printEvaulation(self):

        print("\n")
        print("### Evaulation of Scheduling... ###")
        print("\n")

        ### Total Executing Time ###
        print("- Total Executing Time")
        print(self.currentUnitTime)
        print("\n")
        ########################################################################

        ### CPU Utilization ###
        totalRunningTime = 0
        for process in self.terminatedQueue:
            totalRunningTime += process.runningTime
        print("- CPU utilization")
        print(round(totalRunningTime/self.currentUnitTime, 2))
        print("\n")
        ########################################################################

        ### Throughput ###
        print("- Throughput")
        print(round(len(self.terminatedQueue)/self.currentUnitTime, 2))
        print("\n")
        ########################################################################

        ### Turnaround Time ###
        count = 1
        print("- Turnaround Time")
        for process in self.terminatedQueue:
            print("Process %d : %d " % (count, process.turnAroundTime))
            count += 1
        print("\n")
        ########################################################################

        ### Waiting Time ###
        count = 1
        print("- Waiting Time")
        for process in self.terminatedQueue:
            print("Process %d : %d " % (count, process.waitingTime))
            count += 1
        print("\n")
        ########################################################################

        ### Response Time ###
        count = 1
        print("- Response Time")
        for process in self.terminatedQueue:
            print("Process %d : %d " % (count, process.responseTime))
            count += 1
        print("\n")
        ########################################################################


class FCFS(Scheduler):

    def startScheduling(self, typeObject):

        type = typeObject['type']
        sortFunc = None
        checkNewProcessArrivalFunc = None
        checkingConditionFunc = None
        newProcessAddedFlag = None

        if (type == 1):
            print("Nothing to do...")
        elif (type >= 2 and type <= 6):
            sortFunc = typeObject['sortFunc']
            checkNewProcessArrivalFunc = typeObject['checkNewProcessArrivalFunc']

            # For non-preemptive algorithms
            if (type == 2 or type == 4):
                newProcessAddedFlag = False

            if (type >= 3 and type <= 6):
                checkingConditionFunc = typeObject['checkingConditionFunc']

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assert the processes into readyQueue. (and sort if it is required.)
        # checkNewProcessArrival method checks if the arrived processes on current time is exist.
        if (type == 1):  # FCFS, no need to sort the readyQueue.
            self.checkNewProcessArrival()
        elif (type >= 2 and type <= 6):
            if (checkNewProcessArrivalFunc() == True):
                sortFunc()

        ############################## Start the scheduling!!! ##############################
        while (True):
            # readyQueue is empty, need to check if the scheduling is done.
            if (len(self.readyQueue) == 0):

                # if scheduling is done, break the loop.
                if (len(self.processList) == len(self.terminatedQueue)):
                    break

                # Process to be scheduled is remaining.
                # Increase the unitTime and continue loop to wait for the process.
                else:
                    self.increaseUnitTime()

                    # UnitTime is increased, so check the new arrival of process again.

                    ### 중요!!! 넣기만 하고 sort 안하므로 다른 것들은 조정 필요함. type 구분 ###
                    if (type == 1):
                        self.checkNewProcessArrival()
                    else:
                        print("need to be modified...")
                    continue

            # readyQueue is not empty
            else:
                # The process located at the first of the readyQueue begins running in CPU(scheduling).
                # It could be changed by the scheduling algorithm such as preempting...

                # give the cpu controll to the 0's process.
                self.readyQueue[0].startProcess()

                # startedTime give the information when a process started to be scheduled.
                # When a process is terminated to be scheduled or preempted,
                # the executedTimesection can be obtained through the difference of startedTime and currentUnitTime
                startedTime = self.currentUnitTime

                # Keep runs the scheduling until the job of a process is done.
                # On other preemptive scheduling algorithms,
                # the order could be changed by the other processes
                # by changing the first element of the readyQueue
                # (becuase the first element is the process currently being scheduled on my algorithm.)
                while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                    # plus 1 to the unitTime.
                    # currentUnitTime presents the total running time to date.
                    # And 1 unitTime is passed due to scheduling on every loop.
                    self.increaseUnitTime()

                    # Set the properties of each process included in readyQueue.
                    for process in self.readyQueue:

                        # Executed on only running process.
                        if (process.isRunning == True):
                            # Plus 1 to the running unitTime of this process.
                            process.runningTick()

                        # Executed on only waiting processes.
                        else:
                            # Plus 1 to the waiting unitTime of these processes
                            process.waitingTick()

                            # implement 'Aging' on priority based scheduling algorithms
                            if (type == 6):
                                process.priority -= 1

                    # UnitTime is increased, so check the new arrival of process again.
                    if (type == 1):  # FCFS
                        self.checkNewProcessArrival()

                    ###### checkNewProcessArrivalFunc 조건 구분 고려 #####
                    elif (type == 2 or type == 4):  # SJF, SRTF
                        if (checkNewProcessArrivalFunc() == True):
                            newProcessAddedFlag = True
                    elif (type == 3 or type == 5 or type == 6):  # PSJF, PSRTF
                        if (checkNewProcessArrivalFunc() == True):
                            # tick을 한 번 했는데 새로운 프로세스가 도착한 경우.
                            # Preemptive이기 때문에, 현재 실행 중인 것과 비교해서
                            # 실행 순서를 교체해야 한다.
                            readyQueueLastIndex = len(self.readyQueue)-1
                            if (checkingConditionFunc()):
                                # The scheduling of a process is done.
                                # Deque the process that is recently scheduled into terminated queue.

                                # Swap two Processes
                                temp = self.readyQueue[0]
                                self.readyQueue[0] = self.readyQueue[readyQueueLastIndex]
                                self.readyQueue[readyQueueLastIndex] = temp

                                # 스왑이 됐으므로, 실행되는 것이 바뀐다.
                                # 기존에 실행되던 것에 대해서 실행 시각을 저장,
                                # 새로운 것에도 추가되어야 하기 때문에 startedTime을 currentUnitTime으로 초기화한다.
                                self.readyQueue[readyQueueLastIndex].pauseProcess(
                                    (startedTime, self.currentUnitTime - startedTime))
                                startedTime = self.currentUnitTime
                                self.readyQueue[0].startProcess()

                        # The scheduling of a process is done.
                        # Deque the process that is recently scheduled into terminated queue.
                        # Pass the executedTimeSection (start, end) through the terminatedProcess() method.
                self.readyQueue[0].terminateProcess(
                    (startedTime, self.currentUnitTime-startedTime))
                terminatedProcess = self.readyQueue.pop(0)
                # Pop the terminated Process from the readyQueue,
                # and push it into the terminatedProcess.
                self.terminatedQueue.append(terminatedProcess)

                if (type == 2 or type == 4):
                    if (newProcessAdded == True):
                        sortFunc()
                        newProcessAdded = False
                elif (type == 3 or type == 5 or type == 6):
                    sortFunc()

###############################################
###############################################
###############################################
### 아래쪽은 추후에 FCFS로 모두 합병될 코드임. ###
###############################################
###############################################
###############################################


class SJF(Scheduler):

    @override(Scheduler)
    def checkNewProcessArrival(self):
        newProcessAdded = False

        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                newProcessAdded = True

        return newProcessAdded

    # Sort the Processes list according to the burst time in ascending order.
    def sortByBurstTimeAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: process.burstTime)

    # SJF
    def startScheduling(self):

        newProcessAdded = False

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assume that at least one process arrives at unit time 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the shortest process.
            self.sortByBurstTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        process.waitingTick()

                # Check for new process arrivals.
                if (self.checkNewProcessArrival() == True):
                    newProcessAdded = True

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)

            if (newProcessAdded == True):
                self.sortByBurstTimeAsc()
                newProcessAdded = False


class PSJF(SJF):
    # Preemptive Shortest Job First
    # A Shortest Job can preempt the CPU from the executing Job.

    # SJF
    @override(SJF)
    def startScheduling(self):

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assume that at least one process arrives at unit time 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the shortest process.
            self.sortByBurstTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        process.waitingTick()

                # Check for new process arrivals.
                # If any new process has arrived, sort the readyQueue again according to the burstTime.
                if (self.checkNewProcessArrival() == True):
                    # tick을 한 번 했는데 새로운 프로세스가 도착한 경우.
                    # Preemptive이기 때문에, 현재 실행 중인 것과 비교해서
                    # 실행 순서를 교체해야 한다.
                    readyQueueLastIndex = len(self.readyQueue)-1
                    if (self.readyQueue[readyQueueLastIndex].burstTime < self.readyQueue[0].burstTime):
                        # The scheduling of a process is done.
                        # Deque the process that is recently scheduled into terminated queue.

                        # Swap two Processes
                        temp = self.readyQueue[0]
                        self.readyQueue[0] = self.readyQueue[readyQueueLastIndex]
                        self.readyQueue[readyQueueLastIndex] = temp

                        # 스왑이 됐으므로, 실행되는 것이 바뀐다.
                        # 기존에 실행되던 것에 대해서 실행 시각을 저장,
                        # 새로운 것에도 추가되어야 하기 때문에 startedTime을 currentUnitTime으로 초기화한다.
                        self.readyQueue[readyQueueLastIndex].pauseProcess(
                            (startedTime, self.currentUnitTime - startedTime))
                        startedTime = self.currentUnitTime
                        self.readyQueue[0].startProcess()

            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)
            self.sortByBurstTimeAsc()


class SRTF(Scheduler):
    # Shortest Remaining Time First
    # Thus, scheduling is proceeded according to the remaining time of processes.

    # FCFS가 아닌 것들은 모두 추가가 되었는지 아닌지를 체크하게 되는데,
    # 그 이유는 모두 조건이 새롭게 생기기 때문에...
    @override(Scheduler)
    def checkNewProcessArrival(self):
        newProcessAdded = False

        for newProcess in self.processList:
            # Add a new arrived process on currentUnitTime into readyQueue.
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                newProcessAdded = True

        return newProcessAdded

    # Sort the processes according to the remaining time.
    def sortByRemainingTimeAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: (process.getRemainingTime()))

    # SRTF
    def startScheduling(self):

        newProcessAdded = False

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assume that at least one process arrives at unit time 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the process that has shortese remaining time.
            self.sortByRemainingTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        process.waitingTick()

                # Check for new process arrivals.
                if (self.checkNewProcessArrival() == True):
                    newProcessAdded = True

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)

            if (newProcessAdded == True):
                self.sortByRemainingTimeAsc()
                newProcessAdded = False


class PSRTF(SRTF):
    # Preemptive Shortest Remaining Time First
    # Thus, scheduling is proceeded according to the remaining time of processes
    # and a process could be preempted by other processes.

    # SRTF
    @override(SRTF)
    def startScheduling(self):

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assume that at least one process arrives at unit time 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the process that has shortese remaining time.
            self.sortByRemainingTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        process.waitingTick()

                # Check for new process arrivals.
                if (self.checkNewProcessArrival() == True):

                    readyQueueLastIndex = len(self.readyQueue)-1
                    if (self.readyQueue[readyQueueLastIndex].getRemainingTime() < self.readyQueue[0].getRemainingTime()):
                        # Swap two Processes

                        temp = self.readyQueue[0]
                        self.readyQueue[0] = self.readyQueue[readyQueueLastIndex]
                        self.readyQueue[readyQueueLastIndex] = temp

                        self.readyQueue[readyQueueLastIndex].pauseProcess(
                            (startedTime, self.currentUnitTime - startedTime))
                        startedTime = self.currentUnitTime
                        self.readyQueue[0].startProcess()

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)
            self.sortByRemainingTimeAsc()


# 현재 코드가 Non-Preemptive가 아닌 Preemptive로 짜여 있는듯. 확인이 필요해 보임.
class Priority(Scheduler):

    # Assume that the smaller the number, the higher the priority.
    def sortByPriorityAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: (process.priority))

    def startScheduling(self):

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assume that at least one process arrives at unit time 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the process that has shortese remaining time.
            self.sortByRemainingTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        # Low priority processes may never execute,
                        # so there need to be Aging on Priority Scheduling.
                        # So, implement 'Aging'.
                        # on every waitingTick, decrease the priority of the processes.
                        process.waitingTick()
                        process.priority -= 1

                # Check for new process arrivals.
                if (self.checkNewProcessArrival() == True):

                    readyQueueLastIndex = len(self.readyQueue)-1
                    if (self.readyQueue[readyQueueLastIndex].priority < self.readyQueue[0].priority):
                        # Swap two Processes

                        temp = self.readyQueue[0]
                        self.readyQueue[0] = self.readyQueue[readyQueueLastIndex]
                        self.readyQueue[readyQueueLastIndex] = temp

                        self.readyQueue[readyQueueLastIndex].pauseProcess(
                            (startedTime, self.currentUnitTime - startedTime))
                        startedTime = self.currentUnitTime
                        self.readyQueue[0].startProcess()

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)
            self.sortByPriorityAsc()


# class RoundRobin():
