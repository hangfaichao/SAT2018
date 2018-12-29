from bs4 import BeautifulSoup
import requests
import re
import sys

def check(url):
    head = {'contentType':'text/html;charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.4 Safari/537.36'}
    try:
        r = requests.get(url, headers = head)
    except:
        return False, None
    if r.status_code == 200:
        return True, r.content
    return False, None

def findLinks(html, baseurl):
    if baseurl[-1] == '/':
        baseurl = baseurl[:-1]
    urlparse = baseurl.split('/')
    rooturl = urlparse[0] + '//' + urlparse[2]
    linktypes = {"a":'href','iframe':'src','img':'src','script':'src','link':'href'}
    urls = []
    soup = BeautifulSoup(html, "html.parser")#, from_encoding = "utf-8")
    for k, v in linktypes.items():
        for item in soup.find_all(k):
            link = item.get(v)
            if link is not None and link != '' and link != '/' and not link.find('t_=') > 0:
                if re.search(r'^(\\\'|\\")',link):
                    link = link[2:-2]
                if re.search(r'/$',link):
                    link = link[:-1]

                if re.search(r'^(http://.|https://.)',link):
                    urls.append(link)
                elif re.search(r'^(//)',link):
                    link = urlparse[0] + link
                    urls.append(link)
                elif re.search(r'^/',link):
                    link = rooturl + link
                    urls.append(link)
                elif re.search(r'^(../)',link):
                    step = link.count('../')
                    link = link.replace('../','')
                    upStep = step - (len(urlparse)-4)
                    if upStep >= 0:
                        link = rooturl  + '/' + link
                    else:
                        upStep = (len(urlparse)-4) - step
                        linkTemp = ''
                        for linkTmp in urlparse[3:-(upStep+1)]:
                            linkTemp = linkTemp + '/' + linkTmp
                        link = rooturl + linkTemp + '/' + link
                    urls.append(link)
                elif not re.search(r'(:|#)',link):
                    link = baseurl + '/' + link
                    urls.append(link)
    return urls

def main():
    maxlevel = 5
    homeurl = sys.argv[1]
    if homeurl[:4] != "http":
        homeurl = "http://" + homeurl
    currentlevel, nextlevel, checked, invalid = set(), set(), set(), set()
    currentlevel.add(homeurl)
    f = open("result.txt", 'w')
    f.write("# HomeUrl: " + homeurl + "\n# MaxLevel = 5\n\n\n")
    level = 1
    while level <= maxlevel and len(currentlevel):
        f.write("-----Check level: " + str(level) + ", Link number: " + str(len(currentlevel)) + "-----\n")
        print("-----Check level: " + str(level) + "  Link number: " + str(len(currentlevel)) + "-----")
        
        print("Invalid link:")
        for url in currentlevel:
            success, content = check(url)
            if not success:
                invalid.add(url)
                print(url)
            elif url.startswith(homeurl):
                urls = findLinks(content, url)
                nextlevel.update(urls)
            checked.add(url)

        currentlevel = nextlevel - checked
        nextlevel.clear()
        if len(invalid):
            f.write("Find " + str(len(invalid)) + " invalid links:\n")
            for item in invalid:
                f.write(item + "\n")
            invalid.clear()
        level += 1
    print("Total checked number: ", len(checked))
    f.write("\n\nTotal checked number: " + str(len(checked)))
    f.close()
    


if __name__ == "__main__":
    main()
