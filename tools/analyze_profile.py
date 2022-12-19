import pstats
import sys
from pstats import SortKey

profile = 'profile.txt'
if len(sys.argv) > 1:
	profile = sys.argv[1]

print("Reading profile from", profile)
p = pstats.Stats(profile)
p.sort_stats(SortKey.TIME).print_stats(10)
