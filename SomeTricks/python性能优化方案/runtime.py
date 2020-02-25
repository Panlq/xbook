##

import timeit


lon1,lat1,lon2,lat2=-72.345,34.323,-61.823,54.826
num=500000 #调用50万次

# version1
t=timeit.Timer("v1.great_circle(%f,%f,%f,%f)"%(lon1,lat1,lon2,lat2),
            "import version1 as v1")
print('纯python版本用时:'+str(t.timeit(num))+'sec')

# version2
t=timeit.Timer("v2.great_circle(%f,%f,%f,%f)"%(lon1,lat1,lon2,lat2),
            "import version2 as v2")
print('python+c版本使用:'+str(t.timeit(num))+'sec')

# version3
t=timeit.Timer("v3.great_circle(%f,%f,%f,%f)"%(lon1,lat1,lon2,lat2),
            "import version3 as v3")
print('纯c版本(python函数调用)使用:'+str(t.timeit(num))+'sec')

# version2
t=timeit.Timer("v4.great_circle(%f,%f,%f,%f,%i)"%(lon1,lat1,lon2,lat2,num),
            "import version4 as v4")
print('纯c版本(C函数调用)使用:'+str(t.timeit(1))+'sec')