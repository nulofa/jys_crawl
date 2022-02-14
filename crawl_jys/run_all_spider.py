import datetime
import os
import time
from subprocess import PIPE, Popen

if __name__ == '__main__':
    assert os.getcwd()== "/home/hadoop/jys_crawl/jys_crawl/crawl_jys"
    spiders = os.listdir("./crawl_jys/spiders")
    skips = {'gx_gzw.py','zg_czb.py', "gx_fgw.py"}

    print(len(spiders))
    for spider in spiders[2:]:
        start = time.time()
        if spider.startswith("__") or spider in skips:
            continue
        print(spider)
        p = Popen("scrapy crawl %s" % spider.replace(".py",""), shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        output = "err = %s, \nout = %s" % (stderr.decode('utf-8'), stdout.decode("utf-8"))

        os.system("ps axu | grep 'firefox --marionette' | grep -v grep | awk '{print $2}' | xargs kill")
        end = time.time()

        with open("crawl_out/%s.out" % (spider), 'w') as f:
            f.write(datetime.datetime.today().ctime()+": runing time = %s\n"% round(end-start, 2))
            f.write(output)
