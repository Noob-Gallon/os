from functools import wraps
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

# class Type(Enum):
#     TYPE_FCFS: 1
#     TYPE_SJF: 2
#     TYPE_PSJF: 3
#     TYPE_SRTF: 4
#     TYPE_PSRTF: 5
#     TYPE_Priority: 6
#     TYPE_PPriority: 7
#     TYPE_RR: 8
#     TYPE_PriorityRR: 9
#     TYPE_MultiLevelFeedbackQ: 10
#     TYPE_PriorityRealtime: 11
#     TYPE_RateMonotonic: 12
#     TYPE_EDFS: 13

# type = {
#     "FCFS": 1,
#     "SJF": 2,
#     "PSJF": 3,
#     "SRTF": 4,
#     "PSRTF": 5,
#     "Priority": 6,
#     "PPriority": 7,
#     "RR": 8,
#     "PriorityRR": 9,
#     "MultiLevelQ": 10,
#     "MultiLevelFeedbackQ": 11,
#     "PriorityRealtime": 12,
#     "RateMonotonic": 13,
#     "EDFS": 14
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

    # Add processes into readyQueue of FCFS from JSON file.
    # Select number of the file that you want to use.
    def addProcesses(self):
        # self.processList = processes

        while (True):
            userInputNnumber = input(
                "Select number of the file that you want to use. (1~3): ")

            try:
                intNumber = int(userInputNnumber)
                print("?")
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

            # second argument of yrange is the vertical width from first argument.
            # TODO 이후에 프로세스 이름 순대로 label 다는거 수정 필요?
            ax.broken_barh(xranges=process.executedTimeSection, yrange=(0.1, 0.8),
                           facecolors=(colors[colorIndex]), label=process.processName)
            # a index variable to set the color of each process.
            colorIndex += 1

        ax.set_xlim(0, self.currentUnitTime)
        ax.set_ylim(0, len(self.terminatedQueue))

        yticks = [0.5 + i for i in range(len(self.terminatedQueue))]
        yticksLabels = []
        for index in range(len(self.terminatedQueue)):
            # 추후에 스케쥴링 방법으로 변경, 하나에 그림 다 나타낼 거임.
            processName = "Algorithm " + str(index+1)
            yticksLabels.append(processName)

        ax.set_xticks(range((self.currentUnitTime)+1))
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


# MultiQueue with Round Robin
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

        for p in range(LOWEST_PRIORITY_LEVEL, HIGHEST_PRIORITY_LEVEL+1):
            length = len(self.readyQueue[p])

            for processNumber in range(0, length):
                if (self.readyQueue[p][processNumber].isRunning == True):
                    self.readyQueue[p][processNumber].runningTick(
                    )
                    print(self.readyQueue[p][processNumber].runningTime)
                else:
                    self.readyQueue[p][processNumber].waitingTick(
                    )

                if (self.readyQueue[p][processNumber].waitingTime % self.readyQueue[p][processNumber].burstTime == 0):
                    if (self.readyQueue[p][processNumber].priority != 0):
                        print("aging occurred!!!")
                        print(self.readyQueue[p][processNumber].processName)
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
        # 이 데이터를 바탕으로
        return (isAgingOccurred, priorityChange)

    # 프로세스 수행 과정에서 Aging이 발생했을 경우 이를 처리해주기 위한 메서드
    def handleAging(self, agingData, currentHighestPriority, currentExecutingProcessIndex):
        print("handleAging Executed...")
        length = len(agingData)
        addedValue = 0

        for processIndex in range(0, length):
            # aging이 발생한 queue가 현재 실행 중이 큐가 아닌 경우.
            if (agingData[processIndex][0] != currentHighestPriority):
                poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                    agingData[processIndex][2])
                self.readyQueue[agingData[processIndex]
                                [2]].append(poppedProcess)

            # aging이 발생한 queue가 현재 실행 중인 큐인 경우.
            else:
                if (agingData[processIndex][2] < currentExecutingProcessIndex):
                    if (agingData[processIndex][0] != currentHighestPriority):
                        poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                            agingData[processIndex][2])
                    addedValue = -1

                else:  # processData[2] > currentExecutingProcessIndex
                    poppedProcess = self.readyQueue[agingData[processIndex][0]].pop(
                        agingData[processIndex][2])
                    self.readyQueue[agingData[processIndex]
                                    [1]].append(poppedProcess)

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
