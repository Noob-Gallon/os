from functools import wraps
from matplotlib import cm
from abc import *  # import to implement interface(abstract class)
import matplotlib.pyplot as plt


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
    def addProcesses(self, processes):
        self.processList = processes

        # Sort the readyQueue according to the burstTime in ascending order
        # to find the matching processes on every unit time.
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: process.burstTime)

    def increaseUnitTime(self):
        self.currentUnitTime += 1

    # Check if the new process has arrived every unit time.
    # This is FCFS, so, checks the unit time only.
    def checkNewProcessArrival(self):
        # Search the processList to check the arrivalTime of each Process.
        # If the arrivalTime of a process matches the current unit time,
        # add the process into readyQueue.
        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                # self.processList.remove(newProcess)

    def displayGanttChart(self):

        # Colors list for dipslaying unique colors of each process.
        colors = cm.get_cmap('tab10', len(self.terminatedQueue)).colors

        fig, ax = plt.subplots()
        yrange = 0

        for process in self.terminatedQueue:
            print("process.executedTimeSection : ",
                  process.executedTimeSection)
            ax.broken_barh(xranges=process.executedTimeSection, yrange=(yrange+0.1, 0.8),
                           facecolors=(colors[yrange]))
            yrange += 1

        ax.set_xlim(0, self.currentUnitTime)
        ax.set_ylim(0, len(self.terminatedQueue))

        yticks = [0.5 + i for i in range(len(self.terminatedQueue))]
        yticksLabels = []
        for index in range(len(self.terminatedQueue)):
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
        print(totalRunningTime/self.currentUnitTime)
        print("\n")
        ########################################################################

        ### Throughput ###
        print("- Throughput")
        print(len(self.terminatedQueue)/self.currentUnitTime)
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

    def startScheduling(self):
        # Check the process arrival before executing the scheduling.
        # current unit time is 0.

        ##############################################################
        # I assume that at least one process arrives at unit time 0. #
        ##############################################################
        # If not, I must use infinity loop to check the process arrival.
        # It's an example assignment, so I made a rule.
        self.checkNewProcessArrival()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located at the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startProcess()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            # It'non-preemptive, so, doesn't matter when the other's arrive.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    if (process.isRunning == True):
                        process.runningTick()
                    else:
                        process.waitingTick()

                # UnitTime is increased, so check the new arrival of process again.
                # Checking for new process arrivals must be executed here,
                # because otherwise, the loop might stop even though a new process has arrived.
                self.checkNewProcessArrival()

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].terminateProcess(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)


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
