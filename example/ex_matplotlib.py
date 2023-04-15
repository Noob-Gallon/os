# %%
import matplotlib.pyplot as plt

tasks = [
    dict(Task='Task B', burst_time=3, arrival_time=1),
    dict(Task='Task C', burst_time=5, arrival_time=3),
    dict(Task='Task D', burst_time=2, arrival_time=6),
    dict(Task='Task A', burst_time=4, arrival_time=0),
]

tasks.sort(key=lambda x: x['arrival_time'])

# current_time을 currentUnitTime으로 설정한다.
current_time = 0

for task in tasks:
    task['Start'] = max(current_time, task['arrival_time'])
    task['Finish'] = task['Start'] + task['burst_time']
    task['Resource'] = 'CPU'
    current_time = task['Finish']
    print(task)

fig, ax = plt.subplots(figsize=(10, 4))

for index, task in enumerate(tasks):
    ax.barh(index, task['Finish'] - task['Start'],
            left=task['Start'], height=0.5, label=task['Task'])

ax.set_yticks(range(len(tasks)))
ax.set_yticklabels([task['Task'] for task in tasks])
ax.set_xlabel('Timeline')
ax.set_ylabel('CPU')
ax.set_title('Gantt Chart: Task Execution')

plt.legend()
plt.grid(axis='x')
plt.tight_layout()
plt.show()

# %%
