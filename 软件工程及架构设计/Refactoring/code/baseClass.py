#!/usr/bin/python3
# -*- coding:utf-8 –*-


class AbcMovie(object):
    CHILDRENS = 2
    REGULAR = 0
    NEW_RELAEASE = 1


class AbstractPrice:
    def __init__(self):
        pass

    def getPriceCode(self):
        raise NotImplementedError

    def getCharge(self, daysRented):
        raise NotImplementedError

    def getFrequentRenterPoints(self, daysRented):
        return 1


class ChildrenPrice(AbstractPrice):
    def __init__(self):
        AbstractPrice.__init__(self)

    def getPriceCode(self):
        return AbcMovie.CHILDRENS

    def getCharge(self, daysRented):
        result = 1.5
        if daysRented > 3:
            result += (daysRented - 3) * 1.5
        return result


class NewReleasePrice(AbstractPrice):
    def __init__(self):
        AbstractPrice.__init__(self)

    def getPriceCode(self):
        return AbcMovie.NEW_RELAEASE

    def getCharge(self, daysRented):
        return daysRented * 3

    def getFrequentRenterPoints(self, daysRented):
        return 2 if daysRented > 1 else 1


class RegularPrice(AbstractPrice):
    def __init__(self):
        AbstractPrice.__init__(self)

    def getPriceCode(self):
        return AbcMovie.REGULAR

    def getCharge(self, daysRented):
        result = 2
        if daysRented > 2:
            result += (daysRented - 2) * 1.5
        return result
