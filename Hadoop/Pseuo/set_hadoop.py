#coding=utf-8

import os
import tarfile
import time
import shutil
import sys

#tar -zxvf .gz
def un_tar(file_name):
	#
	tar = tarfile.open(file_name)
	names = tar.getnames()
	for name in names:
		 tar.extract(name,"./")
	tar.close()
#移动文件/目录
def moveDir(source_Dir,targetDir):	
	shutil.move(source_Dir,targetDir)
#追加文件内容
def add_oldfile(old_file,set_file):	
	fpoint_set = os.open(set_file,os.O_RDONLY)
	for line in os.read(fpoint_set,1024):
		f = open(old_file,"a")
		f.write(line)
		f.close()
	os.close(fpoint_set)
if __name__ == '__main__':
	print("Start");
	start = time.clock()
	#创建hadoop文件夹
	un_tar("hadoop.tar.gz")
	moveDir("./hadoop","/usr/local/")
	print('hadoop dir is OK!')
	#创建Java文件夹
	un_tar("java.tar.gz")
	moveDir("./java","/home/hadoop/Downloads/")
	print('java dir is OK!')	
	#修改环境变量
	add_oldfile("/home/hadoop/.bashrc","bashrc")
	add_oldfile("/etc/profile","profile")
	print('bashrc and profile is ok!')
	end = time.clock()
	print('Running time: %s Seconds'% (end - start))
	print("successful!")
	print('run source,chown,delete logs and tmp')


