import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
def ip_transform(ip):
    ips = ip.split(".")#[223,243,0,0]
    ip_num = 0
    for i in ips:
        ip_num = int(i) | ip_num << 8
    return ip_num

#二分法查找ip对应的行的索引
def binary_search(ip_num, broadcast_value):
    start = 0
    end = len(broadcast_value) - 1
    while (start <= end):
        mid = int((start + end) / 2)
        if ip_num >= int(broadcast_value[mid][0]) and ip_num <= int(broadcast_value[mid][1]):
            return mid
        if ip_num < int(broadcast_value[mid][0]):
            end = mid
        if ip_num > int(broadcast_value[mid][1]):
            start = mid
if __name__ == '__main__':
    #创建spark context
    sc = SparkContext('local[2]','iptopN')
    city_id_rdd = sc.textFile('file:///root/tmp/ip.txt')\
        .map(lambda x:x.split('|')).map(lambda x:(x[2],x[3],x[13],x[14]))
    temp = city_id_rdd.collect()
    #创建广播变量
    city_broadcast = sc.broadcast(temp)
    dest_data = sc.textFile('file:///root/tmp/20090121000132.394251.http.format')\
        .map(lambda x:x.split('|')[1])
    def get_pos(x):
        #print(list(x))
        #从广播变量中 获取ip地址库
        cbv = city_broadcast.value
        def get_result(ip):
            ip_num = ip_transform(ip)
            index = binary_search(ip_num,cbv)
            return ((cbv[index][2],cbv[index][3]),1)
        result = map(tuple,[get_result(ip) for ip in x])
        return result
    dest_rdd = dest_data.mapPartitions(lambda x:get_pos(x))#((经度，纬度），1）
    result_rdd = dest_rdd.reduceByKey(lambda a,b:a+b).sortBy(lambda x:x[1],ascending=False)
    print(result_rdd.collect())
