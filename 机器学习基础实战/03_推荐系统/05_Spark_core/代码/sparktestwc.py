import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
if __name__ == '__main__':
    #创建spark context
    sc = SparkContext('local[2]','wordcount')
    #通过spark context 获取rdd
    rdd1 = sc.textFile('file:///root/tmp/test.txt')
    rdd2 = rdd1.flatMap(lambda line:line.split())
    rdd3 = rdd2.map(lambda x:(x,1))
    rdd4 = rdd3.reduceByKey(lambda x,y:x+y)
    print(rdd4.collect())