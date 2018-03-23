# some_spider

wipo.int的小爬虫

#### 部署及依赖

1、运行环境 python2.7
2、python依赖

	pip install requests
	pip install gevent
	pip install PyExecJS
3、nodejs依赖
	centos:
		yum -y install nodejs
	Ubuntu:
		apt-get install -y nodejs
4、爬虫脚本启动
	 python brand_crawl.py -s 1 -e 20 -p /data/brand
	 -s 起始爬取页面
	 -e 结束爬取页面
	 -w 并发数
	 -p 输出json保存目录
