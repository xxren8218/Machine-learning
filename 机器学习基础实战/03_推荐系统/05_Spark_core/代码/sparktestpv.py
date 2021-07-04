import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
if __name__ == '__main__':
    #创建spark context
    sc = SparkContext('local[2]','pvcount')
    rdd1 = sc.textFile('file:///root/tmp/access.log')
    result = rdd1.map(lambda x:('pv',1))\
        .reduceByKey(lambda a,b:a+b)\
        .collect()
    print(result)