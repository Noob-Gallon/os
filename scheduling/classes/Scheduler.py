from functools import wraps
import numpy as np
from matplotlib import cm
from abc import *  # import to implement interface(abstract class)
import matplotlib.pyplot as plt
import json
from pathlib import Path
from . import Process as p
# from enum import Enum

# Scheduling const variables
ROUND_ROBIN_TIME_QUANTUM = 5

# 해당 프로젝트에서는 프로세스의 우선 순위가
# 반드시 0보다는 크거나 같고 20보다는 작거나 같다고 가정한다.
# 숫자가 작을수록 높은 우선순위이다.
# 이에 따라 Level Bound 전역변수를 선언한다.
# 우선순위가 0~20 범위이고, Aging에 따라 상승하는 우선순위는
# 전체 범위의 약 10%인 2로 설정한다.
PRIORITY_AGING_VALUE = 2
HIGHEST_PRIORITY_LEVEL = 20
LOWEST_PRIORITY_LEVEL = 0

# MultiLevel Feedback Queue에서 사용되는
# Level의 수를 나타낸다.
# 현재 프로젝트에서는 총 세 개의 Level이 사용되므로
# 0 ~ 2라고 설정한다.
HIGHEST_FEEDBACK_LEVEL = 0
MIDDLE_FEEDBACK_LEVEL = 1
LOWEST_FEEDBACK_LEVEL = 2

HIGHEST_FEEDBACK_LEVEL_TIME_QUANTUM = 3
MIDDLE_FEEDBACK_LEVEL_TIME_QUANTUM = 6

# type = {
#     "FCFS": 1,
#     "SJF": 2,
#     "PSJF": 3,
#     "SRTF": 4,
#     "PSRTF": 5,
#     "Priority": 6,
#     "PPriority": 7,
#     "RR": 8,
#     "MultiLevelQ": 9,
#     "MultiLevelFeedbackQ": 10,
#     "PriorityRealtime": 11,
#     "RateMonotonic": 12,
#     "EDFS": 13
# }


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
        self.typeObject = None
        self.processChangedTime = []

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
                            process['burstTime'], process['arrivalTime'], process['priority'], process['processName'])
                        self.processList.append(newProcess)

                    # The arrival order of the equal arrivalTime processes is not broke
                    # because the sorted function is a stable sorting fuction.
                    self.processList = sorted(
                        self.processList, key=lambda process: process.arrivalTime)

                    # break the loop.
                    break
                else:
                    print(
                        "Wrong input. Please select a integer number between 1 and 3. flag-1")
            except:
                print(
                    "Wrong input. Please select a integer number between 1 and 3. flag-2")

    def increaseUnitTime(self):
        self.currentUnitTime += 1

    def checkNewProcessArrival(self):
        print("checkNewProcessArrival! : "+str(self.currentUnitTime))
        newProcessAdded = False

        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)
                newProcessAdded = True

        return newProcessAdded

    def isProcessRunningDone(self):
        print("current processName : "+self.readyQueue[0].processName)
        print("runningTime : "+str(self.readyQueue[0].runningTime))
        print("burstTime : "+str(self.readyQueue[0].burstTime))

        return (self.readyQueue[0].runningTime != self.readyQueue[0].burstTime)

    def isReadyQueueEmpty(self):
        return (len(self.readyQueue) == 0)

    def isSchedulingDone(self):
        return (len(self.processList) == len(self.terminatedQueue))

    def swapForPreempt(self, targetIndex):
        temp = self.readyQueue[0]
        self.readyQueue[0] = self.readyQueue[targetIndex]
        self.readyQueue[targetIndex] = temp

    def changeRunningProcess(self, targetIndex, startedTime):
        self.readyQueue[targetIndex].pauseProcessRunning(
            (startedTime, self.currentUnitTime - startedTime))
        startedTime = self.currentUnitTime
        self.readyQueue[0].startProcessRunning()

    def startScheduling(self, typeObject):

        type = typeObject['type']
        sortFunc = None
        checkNewProcessArrivalFunc = None
        checkPreemptConditionFunc = None
        newProcessAddedFlag = None
        isAgingOccurred = None

        if (type in [1,]):  # FCFS and Round Robin
            print("Nothing to do...")
        elif (type >= 2 and type <= 7):
            sortFunc = typeObject['sortFunc']
            checkNewProcessArrivalFunc = typeObject['checkNewProcessArrivalFunc']

            # For non-preemptive scheduling algorithms
            if (type in [2, 4, 6]):
                newProcessAddedFlag = False

            # For priority scheduling. Initialize the aging checking flag
            if (type in [6, 7]):
                isAgingOccurred = False

            # For preemptive scheduling algorithms
            if (type in [3, 5, 7]):
                checkPreemptConditionFunc = typeObject['checkPreemptConditionFunc']

        # Check the process arrival before executing the scheduling.
        # current unit time is 0.
        # Assert the processes into readyQueue. (and sort the readyQueue if it is required.)
        # checkNewProcessArrival method checks if the arrived processes on current time is exist.

        # FCFS and Round Robin no need to sort the readyQueue.
        if (type in [1,]):
            self.checkNewProcessArrival()
        elif (type >= 2 and type <= 7):
            if (checkNewProcessArrivalFunc() == True):
                sortFunc()  # 조건에 맞춰 정렬됨.

        ############################## Start the scheduling!!! ##############################
        while (True):
            # readyQueue is empty, so need to check if the scheduling is done.
            if (self.isReadyQueueEmpty()):
                print("1")
                # if scheduling is done, break the loop.
                if (self.isSchedulingDone()):
                    break

                # Process to be scheduled is remaining.
                # Increase the unitTime and continue looping to wait for the other processes.
                else:
                    self.increaseUnitTime()

                    # UnitTime is increased, so check the new arrival of process again.

                    # FCFS와 Round Robin은 자체적으로 sorting이 필요하지 않음.
                    if (type in [1,]):
                        self.checkNewProcessArrival()
                    elif (type in [2, 3, 4, 5, 6, 7, 9, 10, 11]):
                        if (checkNewProcessArrivalFunc() == True):
                            sortFunc()

            # readyQueue is not empty
            else:
                print("2")

                # The process located at the first of the readyQueue begins running in CPU(scheduling).
                # It could be changed by the scheduling algorithm such as preempting...

                # give the cpu controll to the 0's process.
                self.readyQueue[0].startProcessRunning()

                # startedTime give the information when a process started to be scheduled.
                # When a process is terminated to be scheduled or preempted,
                # the executedTimesection can be obtained through the difference of startedTime and currentUnitTime
                startedTime = self.currentUnitTime

                # Keep runs the scheduling until the job of a process is done.
                # On other preemptive scheduling algorithms,
                # the order could be changed by the other processes
                # by changing the first element of the readyQueue
                # (becuase the first element is the process currently being scheduled on my algorithm.)
                while (self.isProcessRunningDone()):
                    print("3")
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
                            print('process name running tick : ' +
                                  process.processName)

                        # Executed on only waiting processes.
                        else:
                            # Plus 1 to the waiting unitTime of these processes
                            process.waitingTick()

                            # implement 'Aging' on priority based scheduling algorithms
                            if (type in [6, 7]):
                                # 만약 한 프로세스가 자신의 burstTime만큼 실행되지 못하고 대기했다면
                                # 해당 프로세스의 우선순위를 2 높여준다. (숫자가 작을수록 높은 우선순위)
                                if (process.waitingTime % process.burstTime == 0):

                                    if (process.priority != 0):
                                        # 이걸로 인해서 prioriy의 순서가 바뀔 수 있으므로,
                                        # 여기서 뭔가 검사를 해줘야 함.
                                        # Aging에 따라 상승하는 우선순위 값은 전역변수로 선언되어 있음.
                                        process.priority -= PRIORITY_AGING_VALUE
                                        isAgingOccurred = True

                                        if (process.priority < 0):
                                            process.priority = 0

                    # UnitTime is increased, so check the new arrival of process again.
                    if (type in [1,]):  # FCFS
                        self.checkNewProcessArrival()

                    elif (type in [2, 4, 6]):  # non-preemptive
                        if (checkNewProcessArrivalFunc() == True):
                            newProcessAddedFlag = True

                    elif (type in [3, 5, 7]):  # preemptive

                        # 3, 5는 수행 중에 새로운 프로세스가 들어오는 것이 아닌 이상 순서가 바뀔 일이 없지만,
                        # 우선순위 스케쥴링은 Aging 또는 새로운 프로세스의 추가에 의해 선점이 발생할 수 있기 때문에
                        # 세부 조건을 아래와 같이 나누어 준다.
                        flag = checkNewProcessArrivalFunc()
                        if ((flag == True and type != 7) or
                                (type == 7 and (flag == True or isAgingOccurred == True))):
                            # tick을 한 번 했는데 새로운 프로세스가 도착한 경우.
                            # Preemptive이기 때문에, 현재 실행 중인 것과 비교해서
                            # 실행 순서를 교체해야 한다.
                            readyQueueLastIndex = len(self.readyQueue)-1
                            targetIndex = checkPreemptConditionFunc(
                                readyQueueLastIndex)

                            # targetIndex가 0이라면, 새롭게 들어온 process가 preempt되지 않는다는 뜻이며,
                            # targetIndex가 0이 아니라면 해당 index가 preempt될 process의 index가 된다.
                            if (targetIndex != 0):
                                # The scheduling of a process is done.
                                # Deque the process that is recently scheduled into terminated queue.
                                print("targetIndex : "+str(targetIndex))
                                # Swap two Processes
                                self.swapForPreempt(targetIndex)

                                # 스왑이 됐으므로, 실행되는 것이 바뀐다.
                                # 기존에 실행되던 것에 대해서 실행 시각을 저장,
                                # 새로운 것에도 추가되어야 하기 때문에 startedTime을 currentUnitTime으로 초기화한다.
                                self.changeRunningProcess(
                                    targetIndex, startedTime)
                                print("0번 : "+self.readyQueue[0].processName)

                # The scheduling of a process is done.
                # Deque the process that is recently scheduled into terminated queue.
                # Pass the executedTimeSection (start, end) through the terminatedProcess() method.
                self.readyQueue[0].terminateProcess(
                    (startedTime, self.currentUnitTime-startedTime))
                terminatedProcess = self.readyQueue.pop(0)
                # Pop the terminated Process from the readyQueue,
                # and push it into the terminatedProcess.
                self.terminatedQueue.append(terminatedProcess)

                if (type in [2, 4]):
                    if (newProcessAddedFlag == True):
                        sortFunc()
                        newProcessAddedFlag = False
                elif (type in [3, 5, 7]):
                    print("정렬합니다.")
                    for process in self.readyQueue:
                        print(process.processName+" "+str(process.priority))
                    sortFunc()
                elif (type in [6,]):  # priority scheduling...
                    if (newProcessAddedFlag == True or isAgingOccurred == True):
                        sortFunc()

    def displayGanttChart(self):

        # Colors list for dipslaying unique colors of each process.
        colors = cm.get_cmap('tab10', len(self.terminatedQueue)).colors

        # Draw the gantt chart by using matplotlib.pyplot
        fig, ax = plt.subplots()
        colorIndex = 0

        for process in self.terminatedQueue:
            print("process.executedTimeSection : ",
                  process.executedTimeSection)

            # 프로세스가 수행되기 시작한 지점을 추가함.
            for time in process.executedTimeSection:
                self.processChangedTime.append(
                    time[0])

            # second argument of yrange is the vertical width from first argument.
            # TODO 이후에 프로세스 이름 순대로 label 다는거 수정 필요?
            ax.broken_barh(xranges=process.executedTimeSection, yrange=(0.1, 0.8),
                           facecolors=(colors[colorIndex]), label=process.processName)
            # a index variable to set the color of each process.
            colorIndex += 1

        # 스케쥴링이 끝나는 지점의 시각 추가
        self.processChangedTime.append(self.currentUnitTime)

        self.processChangedTime = sorted(
            self.processChangedTime, key=lambda time: time)

        ax.set_xlim(0, self.currentUnitTime)
        ax.set_ylim(0, len(self.terminatedQueue))

        yticks = [0.5 + i for i in range(len(self.terminatedQueue))]
        yticksLabels = []
        for index in range(len(self.terminatedQueue)):
            # 추후에 스케쥴링 방법으로 변경, 하나에 그림 다 나타낼 거임.
            processName = "Algorithm " + str(index+1)
            yticksLabels.append(processName)

        print(self.processChangedTime)
        # ax.set_xticks(range((self.currentUnitTime)+1))
        ax.set_xticks(self.processChangedTime)
        ax.set_yticks(yticks, yticksLabels)

        ax.set_xlabel('Timeline')
        ax.set_ylabel('Processes')

        ax.set_title('Gantt Chart: Task Execution')
        ax.grid(True)

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
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

    @override(Scheduler)
    # Check if the new process has arrived every unit time.
    # This is FCFS, so, checks the unit time only.
    def checkNewProcessArrival(self):
        # Search the processList to check the arrivalTime of each Process.
        # If the arrivalTime of a process matches the current unit time,
        # and add it into readyQueue.
        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue.append(newProcess)


class SJF(Scheduler):

    # Sort the Processes list according to the burst time in ascending order.
    def sortByBurstTimeAsc(self):
        print("sortByBurstTimeAsc")
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: process.burstTime)


class PSJF(SJF):
    # Preemptive Shortest Job First
    # A Shortest Job can preempt the CPU from the executing Job.

    def checkPreemptCondition(self, readyQueueLastIndex):
        # 들어온 프로세스들 중 바꿔줄 인덱스.
        # 초기에 targetIndex를 0으로 설정해서
        # 0번째(현재 동작중인 process)로 비교하고,
        # 만약 0번째 process의 remianingTime보다 작은 프로세스가 있다면
        # targetIndex를 해당 index로 바꿔서 return한다.
        # 그러므로 0이 return된다면 false, 0보다 큰 양수라면 true라고 볼 수 있다.
        targetIndex = 0

        # 0번은 현재 수행되고 있는 process이고, 그것을 제외하고
        # currentUnitTime에 맞는 arrivalTime이 있다면 검사해준다.
        # 이후에는 현재 currentUnitTime에 들어온 개수에 맞게 for loop을 돌릴 수 있을듯.
        for index in range(readyQueueLastIndex, 0, -1):

            # 현재 들어온 process를 체크하는 구간이 지나면 break
            if (self.readyQueue[index].arrivalTime != self.currentUnitTime):
                break

            # 뭔가 이상하게 나눠짐. 나중에 수정하자...
            if (self.readyQueue[index].burstTime < self.readyQueue[targetIndex].burstTime and targetIndex == 0):
                targetIndex = index
            elif (self.readyQueue[index].burstTime <= self.readyQueue[targetIndex].burstTime and targetIndex != 0):
                targetIndex = index

        return targetIndex


class SRTF(Scheduler):
    # Shortest Remaining Time First
    # Thus, scheduling is proceeded according to the remaining time of processes.

    # Sort the processes according to the remaining time.
    def sortByRemainingTimeAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: (process.getRemainingTime()))


class PSRTF(SRTF):
    # Preemptive Shortest Remaining Time First
    # Thus, scheduling is proceeded according to the remaining time of processes
    # and a process could be preempted by other processes.

    ##### 중요 #####
    # 동일한 unitTime에 같은 process가 들어올 수 있으므로, 모두 체크해 주어야 한다.
    def checkPreemptCondition(self, readyQueueLastIndex):

        # 들어온 프로세스들 중 바꿔줄 인덱스.
        # 초기에 targetIndex를 0으로 설정해서
        # 0번째(현재 동작중인 process)로 비교하고,
        # 만약 0번째 process의 remianingTime보다 작은 프로세스가 있다면
        # targetIndex를 해당 index로 바꿔서 return한다.
        # 그러므로 0이 return된다면 false, 0보다 큰 양수라면 true라고 볼 수 있다.
        targetIndex = 0

        # 0번은 현재 수행되고 있는 process이고, 그것을 제외하고
        # currentUnitTime에 맞는 arrivalTime이 있다면 검사해준다.
        # 이후에는 현재 currentUnitTime에 들어온 개수에 맞게 for loop을 돌릴 수 있을듯.
        for index in range(readyQueueLastIndex, 0, -1):

            # 현재 들어온 process를 체크하는 구간이 지나면 break
            if (self.readyQueue[index].arrivalTime != self.currentUnitTime):
                break

            # 뭔가 이상하게 나눠짐. 나중에 수정하자...
            if (self.readyQueue[index].getRemainingTime() < self.readyQueue[targetIndex].getRemainingTime() and targetIndex == 0):
                targetIndex = index
            elif (self.readyQueue[index].getRemainingTime() <= self.readyQueue[targetIndex].getRemainingTime() and targetIndex != 0):
                targetIndex = index

        return targetIndex


class Priority(Scheduler):

    # Assume that the smaller the number, the higher the priority.
    def sortByPriorityAsc(self):
        self.readyQueue = sorted(
            self.readyQueue, key=lambda process: (process.priority))


class PPriority(Priority):

    def checkPreemptCondition(self, readyQueueLastIndex):

        targetIndex = 0

        for index in range(readyQueueLastIndex, 0, -1):

            if (self.readyQueue[index].priority < self.readyQueue[targetIndex].priority and targetIndex == 0):
                targetIndex = index
            # 만약 preempt될 process를 선정하는 과정에서 priority가 같은 것들이 있다면, 그 중에서 가장 먼저 도착한 것을
            # 고를 수 있도록 해준다. 만약 정확히 똑같은 시각에 똑같은 우선 순위의 것이 도착했다면, 해당 프로젝트에서는
            # 그것을 어떤 것을 먼저 처리해도 문제가 없다고 가정한다.
            elif (self.readyQueue[index].priority <= self.readyQueue[targetIndex].priority and targetIndex != 0):
                if (self.readyQueue[index].arrivalTime < self.readyQueue[targetIndex].arrivalTime):
                    targetIndex = index

        return targetIndex


# RoundRobin
class RoundRobin(Scheduler):

    @override(Scheduler)
    def isProcessRunningDone(self, currentExecutingProcessIndex, runningTimeOnStarted):

        # print("currentIndex : "+str(currentExecutingProcessIndex))
        # print("runningTimeOnStarted : "+str(runningTimeOnStarted))
        # print("runningTime : " +
        #       str(self.readyQueue[currentExecutingProcessIndex].runningTime))
        # print("burstTime : " +
        #       str(self.readyQueue[currentExecutingProcessIndex].burstTime))

        if (self.readyQueue[currentExecutingProcessIndex].runningTime == self.readyQueue[currentExecutingProcessIndex].burstTime):
            return False
        elif (self.readyQueue[currentExecutingProcessIndex].runningTime - runningTimeOnStarted == ROUND_ROBIN_TIME_QUANTUM):
            return False
        else:
            return True

    def runProcess(self, currentExecutingProcessIndex, runningTimeOnStarted):
        while (self.isProcessRunningDone(currentExecutingProcessIndex, runningTimeOnStarted)):

            self.increaseUnitTime()

            for process in self.readyQueue:

                # Executed on only running process.
                if (process.isRunning == True):
                    process.runningTick()
                    print(process.processName)

                # Executed on only waiting processes.
                else:
                    process.waitingTick()

            self.checkNewProcessArrival()

    @override(Scheduler)
    def startScheduling(self, typeObject):

        currentExecutingProcessIndex = 0

        self.checkNewProcessArrival()

        ############################## Start the scheduling!!! ##############################
        while (True):
            if (self.isReadyQueueEmpty()):

                if (self.isSchedulingDone()):
                    break

                else:
                    self.increaseUnitTime()
                    self.checkNewProcessArrival()

            else:
                self.readyQueue[currentExecutingProcessIndex].startProcessRunning()
                startedTime = self.currentUnitTime
                runningTimeOnStarted = self.readyQueue[currentExecutingProcessIndex].runningTime
                print("current process : " +
                      self.readyQueue[currentExecutingProcessIndex].processName)
                print("running time on started : " + str(runningTimeOnStarted))

                self.runProcess(currentExecutingProcessIndex,
                                runningTimeOnStarted)

                # while (self.isProcessRunningDone(currentExecutingProcessIndex, runningTimeOnStarted)):

                #     print("Check!")
                #     self.increaseUnitTime()

                #     for process in self.readyQueue:

                #         # Executed on only running process.
                #         if (process.isRunning == True):
                #             process.runningTick()
                #             print(process.processName)

                #         # Executed on only waiting processes.
                #         else:
                #             process.waitingTick()

                #     self.checkNewProcessArrival()

                # 하나의 수행이 종료된 경우
                if (self.readyQueue[currentExecutingProcessIndex].runningTime == self.readyQueue[currentExecutingProcessIndex].burstTime):
                    self.readyQueue[currentExecutingProcessIndex].terminateProcess(
                        (startedTime, self.currentUnitTime-startedTime))
                    terminatedProcess = self.readyQueue.pop(
                        currentExecutingProcessIndex)
                    # Pop the terminated Process from the readyQueue,
                    # and push it into the terminatedProcess.
                    self.terminatedQueue.append(terminatedProcess)

                    if (len(self.readyQueue) != 0):
                        currentExecutingProcessIndex = currentExecutingProcessIndex % len(
                            self.readyQueue)

                # 실행이 종료됐지만, 끝나지는 않은 경우
                else:
                    self.readyQueue[currentExecutingProcessIndex].pauseProcessRunning(
                        (startedTime, self.currentUnitTime - startedTime))
                    currentExecutingProcessIndex = (
                        currentExecutingProcessIndex + 1) % len(self.readyQueue)


# MultiQueue with Round Robin(Priority Round Robin)
class MultiQueue(Scheduler):

    @override(Scheduler)
    def __init__(self):
        super().__init__()

        # 우선순위의 범위가 LOWEST_PRIORITY_LEVEL ~ HIGHEST_PRIORITY_LEVEL이므로, 이에 맞게 readyQueue를 생성한다.
        for i in range(LOWEST_PRIORITY_LEVEL, HIGHEST_PRIORITY_LEVEL+1):
            self.readyQueue.append([])

    # 들어온 새로운 프로세스를 우선순위에 맞는 큐에 넣어준다.
    # Boolean이 필요할지 나중에 고민해보고 처리해야 할듯...
    @override(Scheduler)
    def checkNewProcessArrival(self):
        newProcessAdded = False

        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue[newProcess.priority].append(newProcess)
                newProcessAdded = True

        return newProcessAdded

    @override(Scheduler)
    def isProcessRunningDone(self, priorityLevel, currentExecutingProcessIndex, runningTimeOnStarted):

        print("runningTime : " +
              str(self.readyQueue[priorityLevel][currentExecutingProcessIndex].runningTime))
        print("burstTime : " +
              str(self.readyQueue[priorityLevel][currentExecutingProcessIndex].burstTime))
        if (self.readyQueue[priorityLevel][currentExecutingProcessIndex].runningTime == self.readyQueue[priorityLevel][currentExecutingProcessIndex].burstTime):
            return 1
        elif (self.readyQueue[priorityLevel][currentExecutingProcessIndex].runningTime - runningTimeOnStarted == ROUND_ROBIN_TIME_QUANTUM):
            return 2
        else:
            return 0

    @override(Scheduler)
    def isReadyQueueEmpty(self):
        flag = True

        for priorityLevel in range(LOWEST_PRIORITY_LEVEL, HIGHEST_PRIORITY_LEVEL+1):
            if (len(self.readyQueue[priorityLevel]) != 0):
                flag = False
                break

        return flag

    def clearExecutedFlag(self, priorityLevel):
        length = len(self.readyQueue[priorityLevel])

        for processNumber in range(0, length):
            self.readyQueue[priorityLevel][processNumber].alreadyExecuted = False

    def getHighestPriorityLevel(self):
        for p in range(LOWEST_PRIORITY_LEVEL, HIGHEST_PRIORITY_LEVEL):
            if (len(self.readyQueue[p]) == 0):
                continue
            else:
                return p

        return 999

    def tickProcesses(self):

        isAgingOccurred = False
        priorityChange = []
        print('current time unit!!! : '+str(self.currentUnitTime))

        print("in readyqueue 0")
        for process in self.readyQueue[0]:
            print(process.processName)

        for p in range(LOWEST_PRIORITY_LEVEL, HIGHEST_PRIORITY_LEVEL+1):
            length = len(self.readyQueue[p])

            for processNumber in range(0, length):
                if (self.readyQueue[p][processNumber].isRunning == True):
                    self.readyQueue[p][processNumber].runningTick(
                    )
                    print("running tick : " +
                          self.readyQueue[p][processNumber].processName)
                    print(str(self.readyQueue[p][processNumber].runningTime))
                else:
                    self.readyQueue[p][processNumber].waitingTick(
                    )
                    print("waiting tick : " +
                          self.readyQueue[p][processNumber].processName)
                    print(str(self.readyQueue[p][processNumber].waitingTime))

                if (self.readyQueue[p][processNumber].waitingTime % self.readyQueue[p][processNumber].burstTime == 0 and
                        self.readyQueue[p][processNumber].waitingTime != 0):
                    if (self.readyQueue[p][processNumber].priority != 0):

                        print("aging occurred!!!")
                        print(self.readyQueue[p][processNumber].processName)
                        print(self.readyQueue[p][processNumber].waitingTime)
                        print(self.readyQueue[p][processNumber].burstTime)
                        # 이걸로 인해서 prioriy의 순서가 바뀔 수 있으므로,
                        # 여기서 뭔가 검사를 해줘야 함.
                        # Aging에 따라 상승하는 우선순위 값은 전역변수로 선언되어 있음.
                        isAgingOccurred = True
                        temp = []

                        temp.append(p)
                        self.readyQueue[p][processNumber].priority -= PRIORITY_AGING_VALUE

                        if (self.readyQueue[p][processNumber].priority < 0):
                            self.readyQueue[p][processNumber].priority = 0

                        temp.append(self.readyQueue[p][processNumber].priority)
                        temp.append(processNumber)
                        print(temp)
                        priorityChange.append(temp)

        # isAgingOccurred : Aging이 일어났는가? 일어났다면, priorityChange에 데이터가 담기게 된다.
        # priorityChange에는 다음과 같은 순서로 데이터가 담긴다.
        # 1. 바뀌기 이전의 priority
        # 2. 바뀐 이후의 priority
        # 3. 해당 데이터가 queue에 위치한 index
        # 이 데이터를 바탕으로 Aging에 따른 Process 이동을 수행한다.
        return (isAgingOccurred, priorityChange)

    # 프로세스 수행 과정에서 Aging이 발생했을 경우 이를 처리해주기 위한 메서드
    def handleAging(self, agingData, currentHighestPriority, currentExecutingProcessIndex):
        print("handleAging Executed...")
        length = len(agingData)
        addedValue = 0

        for processIndex in range(0, length):
            # aging이 발생한 queue가 현재 실행 중인 큐가 아닌 경우.
            # 현재 실행 중인 큐에 들어오게 될 수도 있지만, 이것은 현재 포인터에 영향을 주지 않는다.
            # 왜냐하면, 반드시 뒤에서 들어오기 때문에, 현재 포인터의 숫자가 커지지는 않기 때문이다.
            # 또한, aging은 자체적으로 tickProcesses 메서드 자체에서 priority가 0인 큐에서는
            # 발생하지 않기 때문에 추가적인 block은 필요하지 않다.
            poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                agingData[processIndex][2])

            # aging은 한 번에 여러 개가 발생할 수 있다.
            # 그러므로, 만약 aging이 발생해서 빠진 프로세스가 있고
            # 또 다른 aging이 발생한 프로세스가 있는데, 만약 그것들의 큐가 같고
            # 아직 빠지지 않은 뒤의 것의 index가 더 크다면, 전자의 프로세스가 pop됨으로써
            # 전달 받은 index가 영향을 받게 된다. 따라서 이를 판별하고 만약 이러한 것이 있을 경우,
            # index를 1 빼주어야 올바른 계산이 될 수 있다.
            for comparedIndex in range(0, length):
                if ((comparedIndex > processIndex) and
                        (agingData[comparedIndex][0] == agingData[processIndex][0]) and
                        (agingData[comparedIndex][2]
                         > agingData[processIndex][2])
                    ):
                    agingData[comparedIndex][2] -= 1

            # 바뀐 priority queue에 popped process를 추가해준다.
            self.readyQueue[agingData[processIndex]
                            [1]].append(poppedProcess)

            # 만약 현재 aging이 발생한 큐가 기존에 실행 중이던 priority queue일 때는,
            # aging이 발생한 프로세스의 index가 현재 실행 중인 것보다 작은 경우에는
            # currentExecutingProcessIndex의 포인터를 1 감소시켜주어야
            # 이후에 올바르게 동작할 수 있게 된다.
            if (agingData[processIndex][2] < currentExecutingProcessIndex and agingData[processIndex][0] == currentHighestPriority):
                addedValue -= 1

        return addedValue

    @override(Scheduler)
    def startScheduling(self, typeObject):

        prevExecutingProcessIndex = 0
        currentExecutingProcessIndex = 0
        currentHighestPriority = 999
        newHighestPriority = 999

        startedTime = 0
        runningTimeOnStarted = 0
        agingData = None

        self.checkNewProcessArrival()

        ############################## Start the scheduling!!! ##############################
        while (True):
            print("1")
            # readyQueue가 비어있을 때
            if (self.isReadyQueueEmpty()):
                if (self.isSchedulingDone()):
                    break

                else:
                    self.increaseUnitTime()
                    self.checkNewProcessArrival()
            # readyQueue가 비어있지 않을 때
            else:
                while (True):
                    print("2")
                    # 현재 가장 높은 우선순위를 갖는 우선순위 큐를 찾아낸다.
                    newHighestPriority = self.getHighestPriorityLevel()
                    print("newHighestPriorirty : "+str(newHighestPriority))
                    # Queue가 빈 상태이므로 break.
                    # 이후에 더 들어올 프로세스가 남아있는지 체크해야 한다.
                    if (newHighestPriority == 999):
                        break

                    # Execute 1 : 선점이 일어나지 않고 이전에 실행되던 것이 계속해서 실행되는 경우
                    # 혹은 수행이 끝난 순간에 동일한 priority의 프로세스가 들어온 경우.
                    # 예컨대, priority 1을 수행하다가 checkNewProcessArival을 해보니, 다시 1이 들어왔을 수도 있음.
                    if (newHighestPriority == currentHighestPriority):
                        print("executed-1")

                        # if 조건 1
                        # 만약 alreadyExecuted가 True라면 이미 한 번 실행됐던 것이고 한 바퀴가 돌았다는 뜻.
                        # 다시 startProcessRunning을 해주어야 한다.

                        # if 조건 2
                        # 또는, 같은 priority이지만 수행 중이 아닌 경우. 즉, 수행이 끝나는 순간에 들어오게 된 프로세스가 있을 수도 있기 때문에
                        # startProcessRunning을 다시 해주어야 한다.
                        if (self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].alreadyExecuted == True):
                            self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].startProcessRunning(
                            )
                            print("No???-1")
                            print(str(self.currentUnitTime))
                            startedTime = self.currentUnitTime
                            print("startedTime : "+str(startedTime))
                            runningTimeOnStarted = self.readyQueue[currentHighestPriority][
                                currentExecutingProcessIndex].runningTime
                            self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].alreadyExecuted = False

                        if (self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].isRunning == False):
                            self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].startProcessRunning(
                            )
                            print("No???-2")
                            print(str(self.currentUnitTime))
                            startedTime = self.currentUnitTime
                            print("startedTime : "+str(startedTime))
                            runningTimeOnStarted = self.readyQueue[currentHighestPriority][
                                currentExecutingProcessIndex].runningTime

                        # 위의 경우가 아니라면, 이전에 수행되던 것이 다시 수행되는 것이라고 볼 수 있음.

                        self.increaseUnitTime()

                        agingData = self.tickProcesses()
                        print(agingData)
                        if (agingData[0] == True):
                            addedValue = self.handleAging(
                                agingData[1], currentHighestPriority, currentExecutingProcessIndex)
                            currentExecutingProcessIndex += addedValue

                        self.checkNewProcessArrival()

                    # Execute 2 : 선점이 일어나는 경우 또는 이전에는 실행되지 않다가 실행되기 시작한 경우.
                    # 혹은 수행이 끝난 즉시 높은 우선 순위의 프로세스가 들어와서 이걸 수행하게 된 경우.
                    elif (newHighestPriority < currentHighestPriority):
                        print("executed-2")
                        # 만약 선점이 일어났다면, 이전 Queue에 존재하는 process들의
                        # executed flag를 clear해주어야 한다.
                        # currentHighestPriority가 999가 아니라면,
                        # 이전에 어떠한 priorityLevel 상태에서 수행이 되던 것이므로
                        # 해당 level에 대하여 clear를 수행한 뒤, current를 갱신한다.
                        # 그리고 이전에 수행되던 프로세스의 수행을 중지시킨다.
                        if (currentHighestPriority != 999):
                            self.clearExecutedFlag(currentHighestPriority)

                            # pauseProcessRunning 자체에 수행 중이 아닐 경우에는 block되는 코드가 있으므로,
                            # 수행이 끝난 즉시 높은 우선 순위의 프로세스가 들어와서 이걸 수행하게 되는 경우는 block된다.
                            self.readyQueue[currentHighestPriority][prevExecutingProcessIndex].pauseProcessRunning(
                                (startedTime, self.currentUnitTime - startedTime))

                        # 여기서부터는 새로운 우선순위의 큐에서 수행이 시작되므로
                        # currentExecutingProcessIndex는 0으로 초기화한다.
                        # 그리고 currentHighestPriority를 newHighestPriority로 교체한다.
                        prevExecutingProcessIndex = currentExecutingProcessIndex
                        currentExecutingProcessIndex = 0
                        currentHighestPriority = newHighestPriority

                        self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].startProcessRunning(
                        )

                        startedTime = self.currentUnitTime
                        print("startedTime : "+str(startedTime))
                        runningTimeOnStarted = self.readyQueue[currentHighestPriority][
                            currentExecutingProcessIndex].runningTime

                        # print("current process : " +
                        #       self.readyQueue[priorityLevel][currentExecutingProcessIndex].processName)
                        # print("running time on started : " +
                        #       str(runningTimeOnStarted))

                        self.increaseUnitTime()

                        agingData = self.tickProcesses()
                        if (agingData[0] == True):
                            addedValue = self.handleAging(
                                agingData[1], currentHighestPriority, currentExecutingProcessIndex)
                            currentExecutingProcessIndex += addedValue

                        self.checkNewProcessArrival()

                    # Execute 3 : 한 Queue의 수행이 끝나고 낮은 우선순위 단계로 넘어가는 경우
                    # 이 경우에는 반드시 이전에 수행되던 것이 pause 혹은 terminate 되므로,
                    # prev pointer를 사용해서 pause/terminate 할 필요가 없다
                    # 하지만 새롭게 프로세스가 수행되어야 하므로, startProcessRunning을 수행해 주어야 한다.
                    elif (newHighestPriority > currentHighestPriority):
                        print("executed-3")

                        # 선점이 아니라 낮은 우선순위 단계로 넘어가더라도
                        # 이전 단계에서의 flag는 clear해주어야 한다.
                        # 여기서는 newHighestPriority가 999가 될 수도 있고,
                        # 0~20 내의 범위에서 나올 수도 있지만
                        # 선점이 발생하지 않고, 한 큐의 수행이 모두 끝난 것이기 때문에
                        # clear를 반드시 수행해준다.
                        self.clearExecutedFlag(currentHighestPriority)

                        prevExecutingProcessIndex = currentExecutingProcessIndex
                        currentExecutingProcessIndex = 0

                        currentHighestPriority = newHighestPriority

                        self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].startProcessRunning(
                        )

                        startedTime = self.currentUnitTime
                        print("startedTime : "+str(startedTime))
                        runningTimeOnStarted = self.readyQueue[currentHighestPriority][
                            currentExecutingProcessIndex].runningTime

                        self.increaseUnitTime()

                        agingData = self.tickProcesses()
                        if (agingData[0] == True):
                            addedValue = self.handleAging(
                                agingData[1], currentHighestPriority, currentExecutingProcessIndex)
                            currentExecutingProcessIndex += addedValue

                        self.checkNewProcessArrival()

                    # RoundRobin 수행에서 1 unitTime이 지났음.
                    # RoundRobin이 종료되었거나 Process의 수행 자체가 끝났는지 체크해야 함

                    # 1 unitTime이 지나갔음. 현재 수행 중인 프로세스의 수행이 끝났는지,
                    # 혹은 계속 수행해도 될 지를 판단함.
                    flag = self.isProcessRunningDone(
                        currentHighestPriority, currentExecutingProcessIndex, runningTimeOnStarted)

                    # 아래 if문은 현재 process의 수행이 종료될 경우를 구분한다.
                    # flag가 1 또는 2가 아닌 경우. 즉, 0인 경우에는
                    # 현재 프로세스가 계속해서 수행될 수 있음을 의미한다.

                    # flag == 1 : 실행되던 프로세스의 BurstTime이 모두 수행된 경우
                    if (flag == 1):
                        print("Process has been terminated!")
                        # 수행이 종료된 경우, priorityLevel Queue에서 pop되기 때문에 alreadyExecuted = True를 수행하지 않아도 된다.
                        self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].terminateProcess(
                            (startedTime, self.currentUnitTime-startedTime))
                        terminatedProcess = self.readyQueue[currentHighestPriority].pop(
                            currentExecutingProcessIndex)

                        # Pop the terminated Process from the readyQueue,
                        # and assert it into the terminatedProcess.
                        self.terminatedQueue.append(terminatedProcess)

                        if (len(self.readyQueue[currentHighestPriority]) != 0):
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = currentExecutingProcessIndex % len(
                                self.readyQueue[currentHighestPriority])
                        else:
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = 0

                    # flag == 2 : Time Quantum이 다 실행돼서 실행이 종료된 경우
                    elif (flag == 2):
                        print("Time Quantum Expired!")
                        self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].alreadyExecuted = True
                        self.readyQueue[currentHighestPriority][currentExecutingProcessIndex].pauseProcessRunning(
                            (startedTime, self.currentUnitTime - startedTime))
                        prevExecutingProcessIndex = currentExecutingProcessIndex
                        currentExecutingProcessIndex = (
                            currentExecutingProcessIndex + 1) % len(self.readyQueue[currentHighestPriority])

                    else:
                        print(self.readyQueue[currentHighestPriority]
                              [currentExecutingProcessIndex].processName+" is executing...")


# Multi Level Feedback Queue
class MultiLevelFeedbackQueue(Scheduler):

    @override(Scheduler)
    def __init__(self):
        super().__init__()

        # FEEDBACK LEVEL의 범위가 HIGHEST_FEEDBACK_LEVEL ~ LOWEST_FEEDBACK_LEVEL 이므로, 이에 맞게 readyQueue를 생성한다.
        # 처음 들어오는 프로세스는 반드시 HIGHEST_FEEDBACK_LEVEL에 들어가게 되며, 점차 낮은 레벨로 이동하게 된다.
        for i in range(HIGHEST_FEEDBACK_LEVEL, LOWEST_FEEDBACK_LEVEL+1):
            self.readyQueue.append([])

    # 들어온 새로운 프로세스를 우선순위에 맞는 큐에 넣어준다.
    # Boolean이 필요할지 나중에 고민해보고 처리해야 할듯...
    @override(Scheduler)
    def checkNewProcessArrival(self):
        newProcessAdded = False

        for newProcess in self.processList:
            if (newProcess.arrivalTime == self.currentUnitTime):
                self.readyQueue[HIGHEST_FEEDBACK_LEVEL].append(newProcess)
                newProcessAdded = True

        return newProcessAdded

    @override(Scheduler)
    def isProcessRunningDone(self, currentExecutingQueueLevel, currentExecutingProcessIndex, runningTimeOnStarted):

        # FCFS로 동작하는 부분.
        if (currentExecutingQueueLevel == LOWEST_FEEDBACK_LEVEL):
            print("FCFS?")
            print(self.readyQueue[currentExecutingQueueLevel]
                  [currentExecutingProcessIndex].runningTime)
            print(self.readyQueue[currentExecutingQueueLevel]
                  [currentExecutingProcessIndex].burstTime)
            if (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime == self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].burstTime):
                # FCFS의 수행이 종료된 경우.
                return 3

        # Round Robin으로 동작하는 부분.
        else:
            timeQuantum = HIGHEST_FEEDBACK_LEVEL_TIME_QUANTUM

            if (currentExecutingQueueLevel == MIDDLE_FEEDBACK_LEVEL):
                timeQuantum = MIDDLE_FEEDBACK_LEVEL_TIME_QUANTUM

            if (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime == self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].burstTime):
                return 1
            elif (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime - runningTimeOnStarted == timeQuantum):
                return 2

        # 수행이 종료되지 않은 경우.
        return 0

    # 세 개의 큐가 모두 비었는지 아닌지를 반환하는 메서드이다.

    @override(Scheduler)
    def isReadyQueueEmpty(self):
        flag = True

        for priorityLevel in range(HIGHEST_FEEDBACK_LEVEL, LOWEST_FEEDBACK_LEVEL+1):
            if (len(self.readyQueue[priorityLevel]) != 0):
                flag = False
                break

        return flag

    # 라운드 로빈을 돌릴 때 한 큐의 수행이 모두 끝났는지를 체크한다.
    def clearExecutedFlag(self, queueLevel):
        length = len(self.readyQueue[queueLevel])

        for processNumber in range(0, length):
            self.readyQueue[queueLevel][processNumber].alreadyExecuted = False

    # 다음에 수행할 큐를 고른다.
    # Level이 높은 큐를 시작으로, 하나의 프로세스라도 존재할 경우
    # 해당 큐가 실행된다.
    def getNextQueueLevel(self):

        for level in range(HIGHEST_FEEDBACK_LEVEL, LOWEST_FEEDBACK_LEVEL+1):
            # 큐가 비어있으면 다음 큐로 넘어가서 체크한다.
            if (len(self.readyQueue[level]) == 0):
                continue
            # 큐가 비어있지 않으면 실행할 것이 있는 것이므로,
            # 현재 level을 return한다.
            else:
                return level

        return 999

    # 현재 수행되고 있는 큐 내에서 수행되는 프로세스와
    # 수행 중이 아닌 프로세스의 runningTick(), waitingTick()을 수행하는 메서드.
    # 이 과정에서 만약 aging이 필요한 것이 있다면 윗 레벨의 큐로 올려줄 수 있게 되는데,
    # 이것은 Middle, Low 레벨에서만 적용하도록 한다.
    # TickProcesses를 단계 별로 구별하기?
    def tickProcesses(self, currentExecutingQueueLevel):

        isAgingOccurred = False
        priorityChange = []

        for p in range(HIGHEST_FEEDBACK_LEVEL, LOWEST_FEEDBACK_LEVEL+1):
            length = len(self.readyQueue[p])

            for processNumber in range(0, length):
                if (self.readyQueue[p][processNumber].isRunning == True):
                    self.readyQueue[p][processNumber].runningTick(
                    )
                    print(self.readyQueue[p][processNumber].processName)
                else:
                    self.readyQueue[p][processNumber].waitingTick(
                    )

                # Aging
                if (self.readyQueue[p][processNumber].waitingTime % self.readyQueue[p][processNumber].burstTime == 0):
                    if (currentExecutingQueueLevel in [MIDDLE_FEEDBACK_LEVEL, LOWEST_FEEDBACK_LEVEL]):
                        print(self.readyQueue[p][processNumber].processName)
                        # 이걸로 인해서 prioriy의 순서가 바뀔 수 있으므로,
                        # 여기서 뭔가 검사를 해줘야 함.
                        # Aging에 따라 상승하는 우선순위 값은 전역변수로 선언되어 있음.
                        isAgingOccurred = True
                        temp = []

                        temp.append(p)  # 현재 queue level
                        temp.append(processNumber)
                        print(temp)
                        priorityChange.append(temp)

        # isAgingOccurred : Aging이 일어났는가?를 의미함. 일어났다면, priorityChange에 데이터가 담기게 된다.
        # priorityChange에는 다음과 같은 순서로 데이터가 담긴다.
        # 1. 바뀌기 이전의 priority
        # 2. 바뀌기 이전에 위치한 큐에서의 index

        return (isAgingOccurred, priorityChange)

    # 프로세스 수행 과정에서 Aging이 발생했을 경우 이를 처리해주기 위한 메서드
    def handleAging(self, agingData, currentExecutingQueueLevel, currentExecutingProcessIndex):

        length = len(agingData)
        addedValue = 0

        # aging은 동시에 여러 프로세스에서 발생했을 수 있으므로,
        # 모두 조사해서 결과를 return해 주어야 한다.
        for processIndex in range(0, length):
            # aging이 발생한 queue가 현재 실행 중인 큐가 아닌 경우.
            # 즉, 현재 실행 중인 queue보다 레벨이 낮은 경우라고 할 수 있다.
            # 현재 실행중인 큐에 들어오게 되지만, 이것은 현재 포인터에 영향을 주지 않는다.
            # 왜냐하면, 반드시 뒤에서 들어오기 때문에, 현재 포인터의 숫자가 커지지는 않기 때문이다.
            if (agingData[processIndex][0] != currentExecutingQueueLevel):
                poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                    agingData[processIndex][1])
                self.readyQueue[agingData[processIndex]
                                [0]-1].append(poppedProcess)

            # aging이 발생한 queue가 현재 실행 중인 큐인 경우.
            else:
                # 현재 index를 기준으로 앞에서 빠지게 된다면, 포인터를 1 줄여줘야만 한다.
                if (agingData[processIndex][1] < currentExecutingQueueLevel):
                    poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                        agingData[processIndex][1])
                    addedValue -= 1

                # 현재 index를 기준으로 뒤에서 빠지게 되면, 포인터 자체에는 영향을 주지 않는다.
                else:  # processData[2] > currentExecutingProcessIndex
                    poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                        agingData[processIndex][1])
                    self.readyQueue[agingData[processIndex]
                                    [1]].append(poppedProcess)

        return addedValue

    # 스케쥴링 시작
    @override(Scheduler)
    def startScheduling(self, typeObject):

        prevExecutingProcessIndex = 0
        currentExecutingProcessIndex = 0

        prevExecutingQueueLevel = 999
        currentExecutingQueueLevel = 999

        startedTime = 0
        runningTimeOnStarted = 0

        self.checkNewProcessArrival()

        ############################## Start the scheduling!!! ##############################
        while (True):
            # readyQueue가 비어있을 때
            if (self.isReadyQueueEmpty()):
                if (self.isSchedulingDone()):
                    break

                else:
                    self.increaseUnitTime()
                    self.checkNewProcessArrival()
            # readyQueue가 비어있지 않을 때
            else:
                while (True):
                    # 다음에 실행할 Queue의 Level을 받아오기 전에
                    # 현재 값(current)을 이전 값(prev)에 저장한다.

                    # Queue Level은 반드시 이 곳에서만 바뀌기 때문에
                    # Prev를 적용하려면 이 곳에서 적용해야 함.

                    prevExecutingQueueLevel = currentExecutingQueueLevel

                    # 현재 멀티 레벨 피드백 큐에 존재하는 세 개의 큐에서
                    # 다음에 수행될 프로세스를 선택한다.
                    currentExecutingQueueLevel = self.getNextQueueLevel()
                    print("getNext! : "+str(currentExecutingQueueLevel))
                    if (currentExecutingQueueLevel != 999):
                        for p in self.readyQueue[currentExecutingQueueLevel]:
                            print(p.processName)

                    print('prev level : '+str(prevExecutingQueueLevel))
                    print('new level : '+str(currentExecutingQueueLevel))
                    # 세 개의 Queue가 빈 상태이므로 현재의 무한 loop를 break.
                    # 이후에 더 들어올 프로세스가 남아있는지 체크해야 한다.
                    if (currentExecutingQueueLevel == 999):
                        break

                    # 새롭게 전달받은 ExecutingQueueLevel이 이전의 ExecutingQueueLevel과 같은 경우.
                    # 기존에 수행되던 것이 계속해서 수행되거나, 하나의 프로세스가 종료(termination/expiration) 후에
                    # 계속 수행되는 것일 수도 있으며, 혹은 끝난 동시에 프로세스가 들어와 수행되는 것일 수도 있다.
                    if (currentExecutingQueueLevel == prevExecutingQueueLevel):
                        # Execute 1 : HIGHEST_FEEDBACK_LEVEL이 실행된다.
                        # HIGHEST_FEEDBACK_LEVEL은 Time Quantum을 HIGHEST_FEEDBACK_LEVEL_TIME_QUANTUM으로 설정한다. (3)
                        if (currentExecutingQueueLevel == 0):

                            # 연속으로 수행하는 경우. 기존에 수행되던 큐가 계속 수행되거나 종료되자마자 들어온 것일 수 있음.
                            # 그러면, 프로세스를 다시 시작시켜주어야 함. 이 단계에서는 반드시 한 바퀴만 돌기 때문에,
                            # alreadyExecuted flag를 만들어서 Round Robin이 한 바퀴를 체크하는 역할만 하게 됨.
                            if (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].alreadyExecuted == True):
                                print("한바퀴다돌았음!!!")
                                # 여기서 남은 것은 아래로 내려주어야 함.
                                for loop in range(0, len(self.readyQueue[currentExecutingQueueLevel])):
                                    # 1레벨 큐로 내려가게 되므로, 이전의 수행 상태를 False로 만들어야 함.
                                    self.readyQueue[currentExecutingQueueLevel][0].alreadyExecuted = False

                                    # 0레벨 큐에 존재하는 프로세스를 하나씩 빼서 1레벨 큐로 옮겨줌.
                                    # Python에서 pop은 맨 뒤에것 부터 제거한다.
                                    temp = self.readyQueue[currentExecutingQueueLevel].pop(
                                        0)
                                    print('popped! : '+temp.processName)
                                    self.readyQueue[MIDDLE_FEEDBACK_LEVEL].append(
                                        temp)

                                # 현재는 돌릴 것이 없으므로 continue.
                                # 다음에 돌릴 큐를 찾아야 한다.
                                continue

                            elif (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].isRunning == False):
                                # 이 경우는 이전의 level과 같은 경우이기 때문에, 수행되다가 종료가 되지 않은 채로 넘어오는 경우는 없음.
                                # 즉, 반드시 terminate되었거나 expired되어서 넘어오는 경우만 존재한다.
                                # 따라서 추가적으로 terminate나 pause는 해주지 않아도 된다.

                                # currentExecutingProcessIndex는 이미 바뀌고 난 이후이며,
                                # currentExecutingQueueLevel 또한 위에서 이미 바뀌었다.
                                # 따라서, 새로운 프로세스에 대한 시작만 처리해주면 됨.

                                self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                                )
                                startedTime = self.currentUnitTime
                                runningTimeOnStarted = self.readyQueue[
                                    currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime
                            else:
                                print("do nothing...!")
                                # 기본 동작. 이전에 실행되던 것이 그대로 실행될 경우.
                                # 딱히 뭘 할 필요 없이 그냥 수행해야 됨.

                            self.increaseUnitTime()
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue
                            self.checkNewProcessArrival()

                        # Execute 2 : MIDDLE_FEEDBACK_LEVEL이 실행된다.
                        # MIDDLE_FEEDBACK_LEVEL이 Time Quantum을 MIDDLE_FEEDBACK_LEVEL_TIME_QUANTUM으로 설정한다. (6)
                        elif (currentExecutingQueueLevel == 1):

                            # 연속으로 수행하는 경우. 기존에 수행되던 큐가 계속 수행되거나 종료되자마자 들어온 것일 수 있음.
                            # 그러면, 프로세스를 다시 시작시켜주어야 함. 이 단계에서는 반드시 한 바퀴만 돌기 때문에,
                            # alreadyExecuted flag를 만들어서 Round Robin이 한 바퀴를 체크하는 역할만 하게 됨.
                            if (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].alreadyExecuted == True):
                                print("한바퀴다돌았음!!!")
                                # 여기서 남은 것은 아래로 내려주어야 함.
                                for loop in range(0, len(self.readyQueue[currentExecutingQueueLevel])):
                                    # 2레벨 큐로 내려가게 되므로, 이전의 수행 상태를 False로 만들어야 함.
                                    self.readyQueue[currentExecutingQueueLevel][0].alreadyExecuted = False

                                    # 1레벨 큐에 존재하는 프로세스를 하나씩 빼서 2레벨 큐로 옮겨줌.
                                    # Python에서 pop은 맨 뒤에것 부터 제거한다.
                                    temp = self.readyQueue[currentExecutingQueueLevel].pop(
                                        0)
                                    print('popped! : '+temp.processName)
                                    self.readyQueue[LOWEST_FEEDBACK_LEVEL].append(
                                        temp)

                                # 현재는 돌릴 것이 없으므로 continue.
                                # 다음에 돌릴 큐를 찾아야 한다.
                                continue

                            elif (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].isRunning == False):
                                # 이 경우는 이전의 level과 같은 경우이기 때문에,
                                # 이전의 프로세스가 수행되다가 종료가 되지 않은 채로 넘어오는 경우는 없음.
                                # 즉, 반드시 terminate되었거나 expired되어서 넘어오는 경우만 존재한다.
                                # 따라서 추가적으로 terminate나 pause는 해주지 않아도 된다.

                                # currentExecutingProcessIndex는 이미 바뀌고 난 이후이며,
                                # currentExecutingQueueLevel 또한 위에서 이미 바뀌었다.
                                # 따라서, 새로운 프로세스에 대한 시작만 처리해주면 됨.

                                self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                                )
                                startedTime = self.currentUnitTime
                                runningTimeOnStarted = self.readyQueue[
                                    currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime
                            else:
                                print("do nothing...!")
                                # 기본 동작. 이전에 실행되던 것이 그대로 실행될 경우.
                                # 딱히 뭘 할 필요 없이 그냥 수행해야 됨.

                            # 이 부분은 들어가면 안됨. 왜냐면, 계속해서 수행되는 부분이기 때문에
                            # index는 정해진 대로 가야만 함.
                            # prevExecutingProcessIndex = currentExecutingProcessIndex
                            # currentExecutingProcessIndex = 0

                            self.increaseUnitTime()
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue
                            self.checkNewProcessArrival()
                            # Execute 3 : LOWEST_FEEDBACK_LEVEL이 실행된다.
                            # LOWEST_FEEDBACK_LEVEL FCFS를 수행한다.
                        elif (currentExecutingQueueLevel == 2):

                            if (self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].isRunning == False):
                                self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                                )
                                startedTime = self.currentUnitTime
                                runningTimeOnStarted = self.readyQueue[
                                    currentExecutingQueueLevel][currentExecutingProcessIndex].runningTime

                            self.increaseUnitTime()
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue
                            self.checkNewProcessArrival()

                    # 새롭게 전달받은 ExecutingQueueLevel이 이전의 ExecutingQueueLevel과 다른 경우.
                    # 선점, 비선점, 종료 등의 경우가 있을 수 있다.
                    # 중요한 것은, 현재 설정된 조건 하에서 Multilevel Feedback Queue의 선점은
                    # 반드시 0번으로 올라올 때만 나타난다는 것이다. 왜냐하면,
                    # 새로운 프로세스가 들어올 때 반드시 0번 큐에만 들어오기 때문이다.
                    # 따라서, 1번과 2번은 순차적으로 내려가며 실행이 되거나, 선점되었다가 다시 돌아가는 것을
                    # 제외하면 선점적 동작은 발생하지 않는다.
                    elif (currentExecutingQueueLevel != prevExecutingQueueLevel):
                        if (currentExecutingQueueLevel == 0):

                            # 0번을 수행하는데 이전에 1번을 수행하던 경우.
                            # 선점이 된 것이라고 볼 수 있음.
                            if (prevExecutingQueueLevel == 1):

                                # Round Robin을 수행하고 있었기 때문에,
                                # pause process 수행 및 alreadyExecuted flag의
                                # clear가 필요하다.
                                self.readyQueue[prevExecutingQueueLevel][prevExecutingProcessIndex].pauseProcessRunning(
                                    (startedTime, self.currentUnitTime - startedTime))
                                self.clearExecutedFlag(prevExecutingQueueLevel)

                            # 0번을 수행하는데 이전에 2번을 수행하던 경우.
                            # 선점이 된 것이라고 볼 수 있음.
                            elif (prevExecutingQueueLevel == 2):
                                # FCFS를 수행하던 것이기 때문에
                                # pause process만 수행해주면 됨.
                                self.readyQueue[prevExecutingQueueLevel][prevExecutingProcessIndex].pauseProcessRunning(
                                    (startedTime, self.currentUnitTime - startedTime))

                            # 처음 수행되기 시작한 경우 혹은 수행이 멈춰있다가
                            # 다시 수행되기 시작한 경우. 추가적으로 할 것은 없으므로
                            # 주석처리를 해두고, 분기가 존재할 수 있음을 기록한다.
                            # elif (prevExecutingQueueLevel == 999):

                            # 현재 index를 prev에 저장하고 현재 index를 0으로 만든다.
                            # 새로운 큐에서 시작되는 것이기 때문에 처음부터 수행이 될 것이고,
                            # 이에 따라 currentExecutingProcessIndex = 0이 된다.
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = 0

                            # 새롭게 시작되므로, 프로세스를 시작하고 시작 시각을 초기화한다.
                            # runningTime도 초기화해서 Round Robin을 체크할 수 있도록 한다.
                            self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                            )
                            startedTime = self.currentUnitTime
                            runningTimeOnStarted = self.readyQueue[currentExecutingQueueLevel][
                                currentExecutingProcessIndex].runningTime

                            # 실행 unitTime을 1 증가시킨다.
                            self.increaseUnitTime()

                            # 각 프로세스들에 대해서 runningTick()과 waitingTick()을 수행
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue

                            # 새롭게 도착한 프로세스 체크
                            self.checkNewProcessArrival()

                        elif (currentExecutingQueueLevel == 1):

                            # MultiLevel Feedback Queue의 논리상, 1번 레벨의 큐로 오게될 때
                            # 이전 프로세스가 종료되지 않고 선점되어 올 수는 없다. 왜냐하면,
                            # 반드시 높은 레벨부터 수행이 되어야만 하고, 그렇기 때문에 1번에서 2번으로 올 수는 있지만
                            # 반드시 1번이 비어있는 상황이기 때문에, 1번이 비지 않고 2번으로 올 수는 없기 때문이다.
                            # 또한, 2번에서 1번으로 선점되어 올 수는 없다. 왜냐하면, 2번은 1번이 반드시 비어야만 수행되고
                            # 2번이 수행되다가 1번에 프로세스가 들어오면, 그것이 쭉 수행되다가 내려오면서 다시 2번으로 오게 되기 때문에
                            # 이 경우에서는 반드시 이전의 프로세스의 수행이 종료되고 도달하게 된다.
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = 0

                            # 새롭게 시작되므로, 시작 시각을 초기화하고
                            # runningTime도 초기화해서 Round Robin을 체크할 수 있도록 한다.
                            startedTime = self.currentUnitTime
                            runningTimeOnStarted = self.readyQueue[currentExecutingQueueLevel][
                                currentExecutingProcessIndex].runningTime
                            self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                            )

                            self.increaseUnitTime()
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue
                            self.checkNewProcessArrival()

                        # FCFS인 경우.
                        elif (currentExecutingQueueLevel == 2):

                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = 0

                            # 새롭게 시작되므로, 시작 시각을 초기화하고
                            # runningTime도 초기화해서 FCFS를 체크할 수 있도록 한다.
                            startedTime = self.currentUnitTime
                            runningTimeOnStarted = self.readyQueue[currentExecutingQueueLevel][
                                currentExecutingProcessIndex].runningTime
                            self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].startProcessRunning(
                            )

                            self.increaseUnitTime()
                            agingData = self.tickProcesses(
                                currentExecutingQueueLevel)
                            if (agingData[0] == True):
                                addedValue = self.handleAging(
                                    agingData[1], currentExecutingQueueLevel, currentExecutingProcessIndex)
                                currentExecutingProcessIndex += addedValue
                            self.checkNewProcessArrival()

                    # 현재 수행되던 것의 수행이 종료되었는지 체크함.
                    flag = self.isProcessRunningDone(
                        currentExecutingQueueLevel, currentExecutingProcessIndex, runningTimeOnStarted)
                    print("flag : "+str(flag))

                    # flag == 1 : 실행되던 프로세스의 BurstTime이 모두 수행된 경우
                    if (flag == 1):
                        print("Process has been terminated!")
                        # 수행이 종료된 경우, priorityLevel Queue에서 pop되기 때문에 alreadyExecuted = True를 수행하지 않아도 된다.
                        self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].terminateProcess(
                            (startedTime, self.currentUnitTime-startedTime))
                        terminatedProcess = self.readyQueue[currentExecutingQueueLevel].pop(
                            currentExecutingProcessIndex)

                        # Pop the terminated Process from the readyQueue,
                        # and assert it into the terminatedProcess.
                        self.terminatedQueue.append(terminatedProcess)

                        # readyQueue가 비어있지 않기 때문에 수행할 것이 더 남았다고 판단,
                        # 이에 따라 currentExecutingProcessIndex를 증가시켜줌.
                        if (len(self.readyQueue[currentExecutingQueueLevel]) != 0):
                            # index가 바뀌기 전에 기억해주어야 한다. 중복되는거 같은데 이후에 확인 필요.
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = currentExecutingProcessIndex % len(
                                self.readyQueue[currentExecutingQueueLevel])
                        # readyQueue가 비어있으므로 수행할 것이 없다고 판단,
                        # 이에 따라 currentExecutingProcessIndex를 0으로 만들어 줌.
                        else:
                            prevExecutingProcessIndex = currentExecutingProcessIndex
                            currentExecutingProcessIndex = 0

                    # flag == 2 : Time Quantum이 다 실행돼서 실행이 종료된 경우
                    elif (flag == 2):
                        print("Time Quantum Expired!")
                        self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].alreadyExecuted = True
                        self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].pauseProcessRunning(
                            (startedTime, self.currentUnitTime - startedTime))
                        # index가 바뀌기 전에 기억해주어야 하므로, currentIndex를 prev에 저장해준 뒤에 값을 바꿔준다.
                        prevExecutingProcessIndex = currentExecutingProcessIndex
                        currentExecutingProcessIndex = (
                            currentExecutingProcessIndex + 1) % len(self.readyQueue[currentExecutingQueueLevel])

                    # flag == 3 : FCFS 수행이 종료된 경우
                    elif (flag == 3):
                        # FCFS에서는 Round Robin에서 한 바퀴를 돌았음을 체크하는 변수인 alreadyExecuted가 필요하지 않음.
                        # 따라서 해당 변수는 건드리지 않는다.
                        print("FCFS done!")
                        self.readyQueue[currentExecutingQueueLevel][currentExecutingProcessIndex].terminateProcess(
                            (startedTime, self.currentUnitTime-startedTime))
                        terminatedProcess = self.readyQueue[currentExecutingQueueLevel].pop(
                            currentExecutingProcessIndex)

                        # Pop the terminated Process from the readyQueue,
                        # and assert it into the terminatedProcess.
                        self.terminatedQueue.append(terminatedProcess)

                    # flag == 0 : termination되거나 expiration되지 않고 계속해서 process가 수행됨.
                    else:
                        print(self.readyQueue[currentExecutingQueueLevel]
                              [currentExecutingProcessIndex].processName+" is executing...")
