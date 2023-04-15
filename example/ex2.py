# %%
import matplotlib.pyplot as plt

tasks = [
    dict(Task='Task A', burst_time=4, arrival_time=0),
    dict(Task='Task B', burst_time=3, arrival_time=1),
    dict(Task='Task C', burst_time=5, arrival_time=3),
    dict(Task='Task D', burst_time=2, arrival_time=6),
]

original_tasks = tasks.copy()
tasks.sort(key=lambda x: x['arrival_time'])

# Initialize task properties
for task in tasks:
    task['remaining_time'] = task['burst_time']
    task['execution_intervals'] = []

# PSJN algorithm
current_time = 0
while tasks:
    # Find the task with the smallest remaining burst time that has arrived
    next_task = None
    for task in tasks:
        if task['arrival_time'] <= current_time:
            # next_task가 is None이라면 바로 task를 선택하고,
            # 그게 아니라면 remaining_time을 비교하면서 남은 시간이 가장 짧은 것을 선택한다.
            if next_task is None or task['remaining_time'] < next_task['remaining_time']:
                next_task = task

    # task가 선택되었음.
    if next_task is not None:
        # Execute the task for one time unit
        next_task['execution_intervals'].append(
            (current_time, current_time + 1))
        next_task['remaining_time'] -= 1
        print(next_task)

        # 만약 task의 실행이 끝났다면 task를 tasks에서 제거한다.
        if next_task['remaining_time'] == 0:
            tasks.remove(next_task)

        # 한 번 실행이 끝났으므로, current_time += 1
        current_time += 1

    # 이 부분은 실행할 부분이 없을 경우 다음 실행할 task가 있는 곳까지
    # unit time을 jump해주는 부분이다. 필요할지 안필요할지 고민을 해보아야 할 것 같다.
    else:
        # Move to the next arriving task if no task is available to execute
        current_time = min(task['arrival_time'] for task in tasks)

fig, ax = plt.subplots(figsize=(15, 4))

# enumerate를 이용해 original_tasks를 index, task로 분리하며 탐색한다.
for index, task in enumerate(original_tasks):
    # 각각의 element에 대해서 interval을 가져온다.
    # interval이 여러 개일 경우 여러 개를 그리게 되는데,
    # 이 부분을 수정하여 하나처럼 그려지도록 만들어야 될 것 같다.

    # 길이를 얻음.
    length = len(task['execution_intervals'])
    startPoint = task['execution_intervals'][0][0]
    finishPoint = task['execution_intervals'][length-1][1]
    print(startPoint, finishPoint)
    ax.barh(y=index, width=(finishPoint - startPoint),
            left=startPoint, height=0.5)

    # for interval in task['execution_intervals']:
    #     ax.barh(index, interval[1] - interval[0],
    #             left=interval[0], height=0.5)

ax.set_yticks(range(len(original_tasks)))
print(original_tasks)

ax.set_yticklabels([task['Task'] for task in original_tasks])
ax.set_xlabel('Timeline')
ax.set_ylabel('CPU')
ax.set_title('Gantt Chart: Task Execution (PSJN)')

plt.legend()
plt.grid(axis='x')
plt.tight_layout()
plt.show()


# %%
