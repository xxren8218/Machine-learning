import happybase
hostname = '192.168.19.137'
table_name = 'users'
column_family = 'cf'
row_key = 'row_1'

# 获取和服务端之间的链接
conn = happybase.Connection(hostname)
#封装函数
def show_rows(table, row_keys=None):
    if row_keys:
        print('show value of row named %s' % row_keys)
        if len(row_keys) == 1:
            print(table.row(row_keys[0]))
        else:
            print(table.rows(row_keys))
    else:
        print('show all row values of table named %s' % table.name)
        for key, value in table.scan():
            print(key, value)

def put_row(table, column_family, row_key, value):
    print('insert one row to hbase')
    table.put(row_key, {'%s:name' % column_family:'name_%s' % value})
def put_rows(table, column_family, row_lines=30):
    print('insert rows to hbase now')
    for i in range(row_lines):
        put_row(table, column_family, 'row_%s' % i, i)
#函数封装
def delete_table(table_name):
    print('delete table %s now.' % table_name)
    conn.delete_table(table_name, True)
def delete_row(table, row_key, column_family=None, keys=None):
    if keys:
        print('delete keys:%s from row_key:%s' % (keys, row_key))
        key_list = ['%s:%s' % (column_family, key) for key in keys]
        table.delete(row_key, key_list)
    else:
        print('delete row(column_family:) from hbase')
        table.delete(row_key)


def main():
    #print(conn.tables())
    #创建表
    #conn.create_table('user5',{'cf1': dict()})
    table = conn.table('user5')
    # put_row(table,'cf1','rowkey_10','user1')
    # put_rows(table,'cf1',row_lines=10)

    #show_rows(table,['row_5','row_6'])
    # delete_row(table,'row_5')
    # for key, value in table.scan():
    #     print(key, value)
    # delete_row(table,'row_6', column_family='cf1')
    # show_rows(table)
    delete_table('user5')
    pass


if __name__ == '__main__':
    main()