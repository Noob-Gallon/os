class Process:
    # Process class
    # Process that will be scheduled.
    # It contains the process scheduling information.

    def __init__(self, burstTime, arrivalTime, priority):
        self.burstTime = burstTime
        self.arrivalTime = arrivalTime
        self.priority = priority

        self.executedTimeSection = []

        self.runningTime = 0
        self.waitingTime = 0
        self.responseTime = 0
        self.turnAroundTime = 0

        self.isRunning = False
        self.isTerminated = False

    # For process that is executing,
    # increase the runningTime.
    def runningTick(self):
        # Append the timeSection for displaying gantt-chart.
        self.runningTime += 1

    # For processes that are waiting in the readyQueue,
    # increase the waitingTime.
    def waitingTick(self):
        self.waitingTime += 1

    def getRemainingTime(self):
        return self.burstTime - self.runningTime

    # Make this process to be executed on CPU.
    # Note that he calculating manner of responseTime could be changed
    # for preemptive scheduling algorithms.
    def startProcess(self):
        if (self.isRunning == True):
            return

        self.isRunning = True
        self.responseTime = self.waitingTime

    # Stop
    def pauseProcess(self, timeSection):
        if (self.isRunning == False):
            return

        self.executedTimeSection.append(timeSection)
        self.isRunning = False

    # Make this process to be terminated.
    # Calculate the turnAroundTime.
    def terminateProcess(self, timeSection):
        if (self.isRunning == False):
            return

        # Stop running in CPU and alculates the scheduling evaluation factors.
        self.executedTimeSection.append(timeSection)
        self.isRunning = False
        self.isTerminated = True
        self.turnAroundTime = self.runningTime + self.waitingTime
