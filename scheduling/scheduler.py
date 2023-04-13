from functools import wraps


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
        print("increase!")
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

    def printEvaulation(self):

        print("##### Evaulation of Scheduling... #####")
        print("Total unitTime : ", self.currentUnitTime)
        print("Process List : ", end='')
        for process in self.terminatedQueue:
            print("%d " % process.burstTime, end='')
        print('\n\n')

        totalRunningTime = 0
        for process in self.terminatedQueue:
            totalRunningTime += process.runningTime
        print("CPU utilization : ", totalRunningTime/self.currentUnitTime)

        print("Throughput : ", len(self.terminatedQueue)/self.currentUnitTime)

        print("Turnaround Time : [", end=' ')
        for process in self.terminatedQueue:
            print("%d " % process.turnAroundTime, end=' ')
        print("]")

        print("Waiting Time : [", end=' ')

        for process in self.terminatedQueue:
            print("%d " % process.waitingTime, end=' ')
        print("]")

        print("Response Time : [", end=' ')

        for process in self.terminatedQueue:
            print("%d " % process.responseTime, end=' ')
        print("]")


class FCFS(Scheduler):

    def startScheduling(self):
        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # I assume that at least there one process arrives at first.
        # If not, I must use infinity loop. it's an example, so I made a rule.
        self.checkNewProcessArrival()

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

                # UnitTime is increased, so check the new arrival of process again.
                # Checking for new process arrivals must be executed here,
                # because otherwise, the loop might stop even though a new process has arrived.
                self.checkNewProcessArrival()

            # The scheduling of a process is done.
            # Deque the process that is recently scheduled into terminated queue.
            self.readyQueue[0].stopRunning()
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
