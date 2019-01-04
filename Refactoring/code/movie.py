#!/usr/bin/python3
# -*- coding:utf-8 –*-


"""
顾客租赁, 租了那些影片, 租期多长, 程序根据租赁时间和影片类型算出费用,
影片分类 普通, 儿童, 新片, 除了计算费用, 还要为常客累计积分(积分根据租片种类是否为新片而有不同)
"""


class AbcMovie(object):
    CHILDRENS = 2
    REGULAR = 0
    NEW_RELAEASE = 1


class Movie(AbcMovie):
    def __init__(self, title, priceCode):
        self._title = title
        self._priceCode = priceCode

    def getPriceCode(self):
        return self._priceCode

    def setPriceCode(self, price):
        self._priceCode = price

    def getTitle(self):
        return self._title


class Rental(object):
    def __init__(self, movie, daysRented):
        self._movie = movie
        self._daysRented = daysRented

    def getDaysRented(self):
        return self._daysRented

    def getMovie(self):
        return self._movie


class Customer(object):
    def __init__(self, name):
        self._name = name
        self._rentals = []

    def addRental(self, arg):
        self._rentals.append(arg)

    def getName(self):
        return self._name

    def statement(self):
        totalAmount = 0
        frequentRenterPoints = 0
        result = f'Rental Recora for {self.getName()} \n'
        for rental in self._rentals:
            thisAmount = 0
            moviePriceCode = rental.getMovie().getPriceCode()
            daysRented = rental.getDaysRented()
            movieTitle = rental.getMovie().getTitle()
            if moviePriceCode == AbcMovie.REGULAR:
                thisAmount += 2
                if daysRented > 2:
                    thisAmount += (daysRented - 2) * 1.5
            elif moviePriceCode == AbcMovie.NEW_RELAEASE:
                thisAmount += daysRented * 3
            elif moviePriceCode == AbcMovie.CHILDRENS:
                thisAmount += 1.5
                if daysRented > 3:
                    thisAmount += (daysRented - 3) * 1.5

            # add frequent renter points
            frequentRenterPoints += 1
            # add bonus for a two day new release rental
            if moviePriceCode == AbcMovie.NEW_RELAEASE and daysRented > 1:
                frequentRenterPoints += 1

            # show figures for this rental
            result += f'\t {movieTitle} \t {thisAmount} \n'
            totalAmount += thisAmount

        # add footer lines
        result += f'Amount owed is {totalAmount} \n'
        result += f'You earned {frequentRenterPoints} frequent renter points'
        return result


if __name__ == '__main__':
    print(AbcMovie.NEW_RELAEASE)
