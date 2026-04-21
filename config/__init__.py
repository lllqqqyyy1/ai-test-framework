# Django config package
import pymysql

# 使用 pymysql 替代 mysqlclient
pymysql.install_as_MySQLdb()
