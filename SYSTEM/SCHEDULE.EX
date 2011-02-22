#  schedule.ex
#
#  This is a sample SCHEDULE file. If you want to run
#  the scheduler (or "cron" as it is called), modify this
#  to run jobs at the times you desire and rename it from
#  SCHEDULE.EX to SCHEDULE.
#
#     hr  dy  mo  dywk    command

#  These sample jobs are run hourly:

10    *   *   *   *       echo uucico -s system10
20    *   *   *   *       echo uucico -s system20
30    *   *   *   *       echo uucico -s system30
40    *   *   *   *       echo uucico -s system40
50    *   *   *   *       echo uucico -s system50

#  These sample jobs are run daily:

29   17   *   *   *       echo the 5:29 pm alarm!
29   18   *   *   *       echo the 6:29 pm alarm!
29   19   *   *   *       echo the 7:29 pm alarm!
29   20   *   *   *       echo the 8:29 pm alarm!
29   21   *   *   *       echo the 9:29 pm alarm!
