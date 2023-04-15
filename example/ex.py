# %%
import plotly.figure_factory as ff
import plotly.graph_objs as go
from datetime import datetime, timedelta


tasks = [
    dict(Task='Task A', burst_time=4, arrival_time=0),
    dict(Task='Task B', burst_time=3, arrival_time=1),
    dict(Task='Task C', burst_time=5, arrival_time=3),
    dict(Task='Task D', burst_time=2, arrival_time=6),
]

tasks.sort(key=lambda x: x['arrival_time'])


current_time = 0
for task in tasks:
    task['Start'] = max(current_time, task['arrival_time'])
    task['Finish'] = task['Start'] + task['burst_time']
    task['Resource'] = 'CPU'
    current_time = task['Finish']

time_format = "2023-01-01 %H:%M:%S"
start_time = datetime.strptime("2023-01-01 00:00:00", time_format)

for task in tasks:
    task['Start'] = (start_time + timedelta(hours=task['Start'])
                     ).strftime(time_format)
    task['Finish'] = (
        start_time + timedelta(hours=task['Finish'])).strftime(time_format)

colors = {'CPU': 'rgb(58, 200, 225)'}

fig = ff.create_gantt(tasks, colors=colors, index_col='Resource',
                      show_colorbar=True, group_tasks=True)

# Customize the layout
fig.update_layout(
    title='Gantt Chart: Task Execution',
    xaxis=dict(title='Timeline', tickformat="%H:%M:%S"),
    yaxis=dict(title='CPU'),
    hovermode="x"
)

fig.show()

# %%
