Build Stats
===========

We might like to keep track of how long we spend waiting for the build. 
This script assumes you're using a tool like Android Studio which produces a log.
It uses regular expressions to pick out interesting entries from the log. 
A second script then converts these interesting entries into a csv file for further statistical analysis.

Usage
-----
If your idea.log is in the standard place on a mac and you're happy for it to write new files in subfolders under
the current working directory then this is the workflow:

Run this as often as you restart your IDE, perhaps twice a day:

    $ gather_build_data.py

That should produce a new log file under a subfolder 'data' named with today's date and your username.
Once a week, process all the statistics into a csv file you can share with your team:

    $ process_to_csv.py

It should produce a new csv file under a subfolder 'processed_data' named with today's date and your username.
Send the csv file to whoever on your team is collating this data for further analysis. 
Then you should clean up the processed log files so they won't be processed again next week:

    $ clean.py

If your idea.log is not in the standard place, you can tell gather_build_data.py where to find it:

    $ buildstats.py /path/to/idea.log


Tests
-----
The self-tests use 
[pytest](https://docs.pytest.org/) 
and 
[approvaltests](https://github.com/approvals/approvaltests.Python).