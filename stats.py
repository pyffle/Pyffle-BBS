import pstats
import sys
args = sys.argv
p = pstats.Stats(args[1])
p.sort_stats("cumulative")
p.print_stats()