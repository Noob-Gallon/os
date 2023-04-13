class Process:
    # Process class
    # Process that will be scheduled.
    # It contains information about scheduling.

    def __init__(self, burstTime, arrivalTime):
        self.burstTime = burstTime
        self.arrivalTime = arrivalTime

        self.runningTime = 0
        self.waitingTime = 0
        self.responseTime = 0
        self.turnAroundTime = 0

        self.isRunning = False
        self.isTerminated = False

    def runningTick(self):
        if (self.isRunning == False):
            return

        self.runningTime += 1

    def waitingTick(self):
        if (self.isRunning == True):
            return

        self.waitingTime += 1

    def startRunning(self):
        if (self.isRunning == True):
            return

        self.isRunning = True
        self.responseTime = self.waitingTime

    def stopRunning(self):
        if (self.isRunning == False):
            return

        # Stop running in CPU and alculates the scheduling evaluation factors.
        self.isRunning = False
        self.isTerminated = True
        self.turnAroundTime = self.runningTime + self.waitingTime
