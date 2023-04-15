from functools import wraps
from matplotlib import cm
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
        self.processList = []
        self.readyQueue = []
        self.terminatedQueue = []
        self.currentUnitTime = 0

    # Add processes into readyQueue of FCFS from JSON file.
    def addProcess(self, process):
        self.processList.append(process)

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
            ax.broken_barh(xranges=process.executedTimeSection, yrange=(yrange+0.1, 0.8),
                           facecolors=(colors[yrange]))
            yrange += 1

        ax.set_xlim(0, self.currentUnitTime)
        ax.set_ylim(0, len(self.terminatedQueue))

        yticks = [0.5 + i for i in range(len(self.terminatedQueue))]
        yticksLabels = []
        for index in range(len(self.terminatedQueue)):
            processName = "Process " + str(index)
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
        # I assume that at least there one process arrives at first. #
        ##############################################################
        # If not, I must use infinity loop to check the process arrival.
        # It's an example assignment, so I made a rule.
        self.checkNewProcessArrival()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located in the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startRunning()
            startedTime = self.currentUnitTime

            # Keep runs the scheduling until the job of a process is done.
            # It'non-preemptive, so, doesn't matter when the other's arrive.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):

                # plus 1 to the unitTime.
                # unitTime presents the total running time to date.
                self.increaseUnitTime()

                for process in self.readyQueue:
                    process.runningTick()

                    if (process.isRunning == False):
                        process.waitingTick()

                # UnitTime is increased, so check the new arrival of process again.
                # Checking for new process arrivals must be executed here,
                # because otherwise, the loop might stop even though a new process has arrived.
                self.checkNewProcessArrival()

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].stopRunning(
                (startedTime, self.currentUnitTime-startedTime))
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)


class SJF(Scheduler):

    @override(Scheduler)
    # Use the 'override' decorator to modify the method so that it returns a boolean value
    # that determines whether the 'readyQueue' should be sorted or not.
    def checkNewProcessArrival(self):
        flag = False

        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                flag = True

        return flag

    # Sort the Processes list according to burst time in ascending order.
    def sortByBurstTimeAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: process.burstTime)

    # SJF
    def startScheduling(self):
        arrivalFlag = False

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        if (self.checkNewProcessArrival() == True):
            # Sort the readyQueue to pick out the shortest process.
            self.sortByBurstTimeAsc()

        # If readyQueue is not empty, keep schedule the processes.
        while (len(self.readyQueue)):
            # The process located in the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startRunning()

            # Keep runs the scheduling until the job of a process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):
                for process in self.readyQueue:
                    process.runningTick()

                    if (process.isRunning == False):
                        process.waitingTick()

                # plus 1 to the unitTime.
                # unitTime presents the totla running time to date.
                self.increaseUnitTime()

                # Check for new process arrivals.
                # If any new process has arrived, sort the readyQueue again according to the burstTime.
                # 문제 발생, 여기서 정렬해버리면 preemptive가 된다.
                # 이걸 약간 수정해서 끝나면 바뀌도록 해야할 듯.
                if (self.checkNewProcessArrival() == True):
                    arrivalFlag = True

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].stopRunning()
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)

            if (arrivalFlag == True):
                self.sortByBurstTimeAsc()
                arrivalFlag = False
