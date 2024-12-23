# grafmon

Monitor metrics in a real-time time-series line-graph

![screenshot](screenshots/grafmon1.png)

# Demonstration video

[![demo video](https://img.youtube.com/vi/o76IbERE7ec/0.jpg)](https://youtube.com/watch?v=o76IbERE7ec)

# Features

* Real-time time-series graph of metrics.
* Provide your own metric command.
* Several built-in metrics.
* Polished graph interface.
* Adjustable refresh rate.
* Pausable updates.
* Hide/show lines.
* Clickable/hoverable lines.
* Remembers window position/layout.

# Install

    pip install grafmon

# Usage

```
usage: grafmon [-h] [-m MONITOR | -c COMMAND] [-r REFRESHRATE] [-t MAXTICKS]
               [-l MAXLABELS] [--list-monitors]

Monitor metrics in a real-time time-series graph

options:
  -h, --help            show this help message and exit
  -m MONITOR, --monitor MONITOR
                        Select from builtin monitors to feed data into monitor
                        [default: pcpu]
  -c COMMAND, --command COMMAND
                        User command to feed data into monitor [example: ps
                        -eo rss,pid,comm --no-headers]
  -r REFRESHRATE, --refreshrate REFRESHRATE
                        Refresh rate in milliseconds [default: 1000]
  -t TICKS, --ticks TICKS
                        Count of ticks on X axis [default: 60]
  -l LABELS, --labels LABELS
                        Count of labels on X axis [default: 10]
  --list-monitors       List available builtin monitors
```

# Builtin monitors

```
avgpcpu    Average CPU% (using `ps`) over lifetime of all processes
cuc        CPU%, including dead children, in extended ##.### format of all processes
cuu        CPU% in extended ##.### format of all processes
drs        Data resident set size of all processes
pcpu       Immediate CPU% (using `top`) of all processes
pmem       Physical memory percentage of all processes
pss        Proportional share size of all processes
rbytes     Number of bytes really fetched from storage layer of all processes
rchars     Number of bytes read from storage of all processes
rops       Number of read I/O operations of all processes
rss        Resident set size (physical memory usage, in kilobytes) of all processes
sz         Physical pages used of all processes
thcount    Thread counts of all processes
trs        Text resident set (executable code memory usage) of all processes
vsz        Virtual memory usage of all processes
wbytes     Number of bytes really written to storage layer of all processes
wcbytes    Number of canceled write bytes of all processes
wchars     Number of bytes written to storage of all processes
wops       Number of write I/O operations of all processes
```

# Custom monitor

Grafmon is not limited to the builtin monitors. Grafmon also accepts user-provided
commands for monitoring. Grafmon can monitor smart plug metrics to track power usage of
appliances. Grafmon can monitor IoT sensors and more!

The command must output lines in the format of `<float> <string>` to STDOUT. The `<float>`
will be the value associated with `<string>`. The `<string>` may contain spaces. Grafmon will
invoke the command every refresh-rate tick; the command must start and terminate each tick.
It may be necessary to write a small wrapper script that read chunks of the input at a time
and terminates within a update tick.

I am planning to implement an `-s, --stream` option to continually read data from an open
stream, e.g. `grafmon -s 'tail -f log'` or `monitor_cmd | grafmon -` in the near future!

Examples:

    grafmon -c 'ps -eo pcpu,pid,comm --no-headers'

    grafmon -c 'cat file_regularly_overwritten'

    grafmon -c 'socat TCP-LISTEN:13510 -'

# Notes

This app is aimed at short-term use on personal laptops/desktops. For long-term monitoring of
servers, you should use something like sysstat logging along with grafana/kibana.

I needed an easy-to-install local app that requires no-to-minimal set-up to graph in real-time
various system metrics and custom IoT metrics, notably percentages of CPU usages for all active
processes and wattage usages of my home appliances. The KDE and Gnome system monitors/task
managers graph overall CPU usage rather than per-process usage.

Grafmon is inspired in part by Windows' perfmon.exe. The graph does not scroll, but instead
updates in a horizontally rolling blind. A vertical line will move from left-to-right as the
metrics are read each tick. When the line reaches the end, it resets back to the beginning.
This allows easy hovering over of graph elements to inspect the data. A moving scrolling graph
would be more difficult to hover over the lines and their peaks.

Lines may be clicked on to highlight them to more easily see them in the graph. Lines may
be hovered-over to see a tooltip of their values. Their values will also appear in the status
bar at the bottom of the window.

To zoom the graph in to inspect lower valued lines, you can untick the checkboxes in the list
on the left. Unticking checkboxes for lines with the highest peaks will hide the lines and
the graph will zoom in to fit the next highest peaks.
