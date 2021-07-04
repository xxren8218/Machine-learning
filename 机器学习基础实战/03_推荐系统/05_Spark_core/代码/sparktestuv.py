import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
if __name__ == '__main__':
    #创建spark context
    sc = SparkContext('local[2]','uvcount')
    rdd1 = sc.textFile('file:///root/tmp/access.log')
    rdd2 = rdd1.map(lambda x:x.split()).map(lambda x:x[0])
    rdd3 = rdd2.distinct().map(lambda x:('uv',1))
    rdd4 = rdd3.reduceByKey(lambda a,b:a+b)
    print(rdd4.collect())