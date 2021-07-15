from __future__ import division #Ensure division returns float
from numpy import mean, std # version >= 1.7.1 && <= 1.9.1
from math import sqrt
import sys


def cohen_d(x,y):
        return (mean(x) - mean(y)) / sqrt((std(x, ddof=1) ** 2 + std(y, ddof=1) ** 2) / 2.0)
