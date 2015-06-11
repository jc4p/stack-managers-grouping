# stack-managers-grouping
Script to try to distribute Stack Exchange managers evenly across study groups

We currently have just under 60 "managers" at Stack Exchange. We want to distribute them into separate teams that can have routine meetings to discuss problems and help each other, but we want the groups to be evenly split across a series of criteria. Fun, right?

The criteria is as follows:

- Tenure
- Department
- Location
- Gender

`main.py` in this repository reads a private CSV, converts all the managers to models that have those fields (and a couple more), then tries to evenly spread them out.
