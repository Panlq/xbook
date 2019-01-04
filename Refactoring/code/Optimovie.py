#!/usr/bin/python3
# -*- coding:utf-8 –*-


"""
顾客租赁, 租了那些影片, 租期多长, 程序根据租赁时间和影片类型算出费用,
影片分类 普通, 儿童, 新片, 除了计算费用, 还要为常客累计积分(积分根据租片种类是否为新片而有不同)
"""

"""
1. 功能归属明确
    Move Method, Move Field, Extract Class 抽离/封装
2. Replace Temp with Query() 以查询取代临时变量
3. Inline Temp   临时变量内联化
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

    def getCharge(self):
        result = 0
        moviePriceCode = self._movie.getPriceCode()
        daysRented = self._daysRented
        if moviePriceCode == AbcMovie.REGULAR:
            result += 2
            if daysRented > 2:
                result += (daysRented - 2) * 1.5
        elif moviePriceCode == AbcMovie.NEW_RELAEASE:
            result += daysRented * 3
        elif moviePriceCode == AbcMovie.CHILDRENS:
            result += 1.5
            if daysRented > 3:
                result += (daysRented - 3) * 1.5
        return result

    def getFrequentRenterPoints(self):
        # add bonus for a two day new release rental
        if self._movie.getPriceCode() == AbcMovie.NEW_RELAEASE and self._daysRented > 1:
            return 2
        return 1


class Customer(object):
    def __init__(self, name):
        self._name = name
        self._totalCharge = 0
        self._frequentRenterPoints = 0
        self._rentals = []

    def addRental(self, arg):
        self._rentals.append(arg)

    def getName(self):
        return self._name

    def getTotalCharge(self):
        pass

    def getTotalFrequentRenterPoints(self):
        pass

    def statement(self):
        result = f'Rental Recora for {self.getName()} \n'
        for rental in self._rentals:
            thisAmount = rental.getCharge()
            movieTitle = rental.getMovie().getTitle()
            self._frequentRenterPoints += rental.getFrequentRenterPoints()
            # show figures for this rental
            result += f'\t {movieTitle} \t {thisAmount} \n'
            self._totalCharge += thisAmount
        # add footer lines
        result += f'Amount owed is {self._totalCharge} \n'
        result += f'You earned {self._frequentRenterPoints} frequent renter points'
        return result

    def htmlStatement(self):
        result = f'<H1>Rental for <EM> {self.getName()} </EM></H1><P>\n;'
        for rental in self._rentals:
            result += rental.getMovie().getTitle() + ': ' + str(rental.getCharge()) + '<BR>\n'
            result += f'<P>You own <EM>{self._totalCharge}</EM><P>\n'
            result += f'On this rental you earned <EM>{self._frequentRenterPoints}</EM> frequent renter points<P>' 
        return result


if __name__ == '__main__':
    ha = Movie('Dream1', AbcMovie.CHILDRENS)
    hb = Movie('Dream2', AbcMovie.NEW_RELAEASE)
    hc = Movie('Dream3', AbcMovie.CHILDRENS)
    hd = Movie('Dream4', AbcMovie.REGULAR)
    he = Movie('Dream5', AbcMovie.REGULAR)
    hf = Movie('Dream6', AbcMovie.NEW_RELAEASE)
    a = Customer('Mark')
    b = Customer('Jon')
    c = Customer('Jack')
    a.addRental(Rental(ha, 3))
    a.addRental(Rental(hb, 5))
    c.addRental(Rental(hd, 1))

    res = a.statement()
    # b.statement()
    # c.statement()
    print(res)