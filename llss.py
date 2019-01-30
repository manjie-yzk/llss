import requests
from bs4 import BeautifulSoup
import re, threading, time
import queue as Queue


# 接收某篇具体文件的页面链接，把此页面内的动画磁力写入文件manjie_llss.txt
def get_magnets_from_detail_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
        #contents = soup.find('div', id="primary").find('article').find('div', class_="entry-content")
        contents = soup.find('div', class_="entry-content")
        text = contents.text
        aim_magnets = re.findall('[0-9a-zA-Z]{40}', text)
        with open('manjie_llss.txt', 'a+') as f:
            for m in aim_magnets:
                f.write(m+'\n')
                print(m)
    except:
        with open('errors_manjie.txt', 'a+') as f:
            f.write(url+'\n')

#base_url = 'http://www.llss.mx/wp/category/all/anime/page/' 原先是这个，后来改成了下面这个
base_url = 'http://www.llss.xyz/wp/category/all/anime/page/'
links = []
for i in range(1, 103):
    link = base_url + str(i) +'/'
    links.append(link)

# 得到点击“动画”目录后看到的99个列表页面之一，把此页每篇文章的url提取出来
def get_magnets_from_link_page(threadName, q):
    link = q.get(timeout=2)
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
    r = requests.get(link, headers=headers, timeout=30)
    r.encoding = r.apparent_encoding
    print(q.qsize, threadName, r.status_code, link)
    soup = BeautifulSoup(r.text, 'lxml')
    contents = soup.find_all('article')

    for c in contents:
        url = c.find('h1').a['href']
        get_magnets_from_detail_page(url)
    
start = time.time()

# 定义线程类
class myThread(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
    def run(self):
        print("Starting " + self.name)
        while True:
            try:
                get_magnets_from_link_page(self.name, self.q)
            except:
                break

# 把活跃的线程添加到线程列表待用
threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5"]
workQueue = Queue.Queue(103)
threads = []
for tName in threadList:
    thread = myThread(tName, workQueue)
    thread.start()
    threads.append(thread)

for link in links:
    workQueue.put(link)

# 等待至线程终止
for t in threads:
    t.join()

end = time.time()
print("Total time is: ", end-start)
print("Main Thread Exit!")
    
# 文件内磁力链接去重（想起来顺便补上）
with open('fxadm_llss.txt', 'r+') as f:
    contents = f.readlines()
    contents = list(set(contents))

# 去重后的磁力再写入另一个文件当中
for c in contents:
    with open('else_mj_llss.txt', 'a+') as f:
        f.write(c)
