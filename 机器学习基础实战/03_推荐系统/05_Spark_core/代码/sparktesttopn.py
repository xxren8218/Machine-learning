import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
def func(x,y):
    result = x-y
    return result
if __name__ == '__main__':
    #创建spark context
    sc = SparkContext('local[2]','topncount')
    # rdd1 = sc.textFile('file:///root/tmp/access.log')
    # rdd2 = rdd1.map(lambda x:x.split()).filter(lambda x:len(x)>10).\
    #     map(lambda x:(x[10],1))
    # rdd3 = rdd2.reduceByKey(lambda a,b:a+b)\
    #     .sortBy(lambda x:x[1],ascending=False).filter(lambda x:len(x[0])>6)
    # result = rdd3.take(10)
    # print(result)
    rdd1 = sc.parallelize([1,2,3,4,5,6])
    result = rdd1.reduce(func)
    print(result)