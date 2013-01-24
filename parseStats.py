#!/usr/bin/env python
#
# parseStats
#
# parse profiling stats
#

import pstats

p = pstats.Stats('profiling.prof')

p.sort_stats('cumulative').print_stats()
