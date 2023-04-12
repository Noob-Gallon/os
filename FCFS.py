import collections
import json

# Process class
# Process that will be scheduled.
# It contains information about scheduling informations.


class Process:
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

    def printProcessInformation(self):
        print("Process Information\n")
        print("burstTime : %d" % self.burstTime)
        print("runningTime : %d" % self.runningTime)
        print("arrivalTime : %d" % self.arrivalTime)
        print("waitingTime : %d" % self.waitingTime)
        print("responseTime : %d" % self.responseTime)
        print("trunAroundTime : %d" % self.turnAroundTime)
        print("\n\n")


class FCFS:
    def __init__(self):
        self.readyQueue = []
        self.terminatedQueue = []

    # add processes into readyQueue of FCFS from JSON file.
    def addProcess(self, process):
        self.readyQueue.append(process)

    def startScheduling(self):
        # if readyQueue is not empty,
        # keep schedule processes.
        while (len(self.readyQueue)):
            # The process located in the first of the readyQueue begins running in CPU(scheduling).
            self.readyQueue[0].startRunning()

            # Keep runs the scheduling until the job of the process is done.
            while (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime):
                for process in self.readyQueue:
                    process.runningTick()

                    if (process.isRunning == False):
                        process.waitingTick()

            # A scheduling is done.
            # Deque the process that is recently scheduled in to terminated queue.
            self.readyQueue[0].stopRunning()
            terminatedProcess = self.readyQueue.pop(0)
            self.terminatedQueue.append(terminatedProcess)

    def printResult(self):
        for process in self.terminatedQueue:
            process.printProcessInformation()

##################################################################
###                        execution                           ###
##################################################################


fcfs = FCFS()

p = []
p.append(Process(6, 0))
p.append(Process(8, 0))
p.append(Process(7, 0))
p.append(Process(3, 0))

for process in p:
    fcfs.addProcess(process)

fcfs.startScheduling()
fcfs.printResult()
