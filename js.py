import js2py
import random
from download import download_from_url

uas = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.96 Chrome/58.0.3029.96 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0; Baiduspider-ads) Gecko/17.0 Firefox/17.0",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9b4) Gecko/2008030317 Firefox/3.0b4",
    "Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; BIDUBrowser 7.6)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
]

def setHeader():
    randomIP = str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)) + '.' + str(
        random.randint(0, 255)) + '.' + str(random.randint(0, 255))
    headers = {
        'User-Agent': random.choice(uas),
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        'X-Forwarded-For': randomIP,
    }
    return headers

def get_source(p1, p2):
    jsc, _ = js2py.run_file('md5.js')
    return jsc.encrypt(p1,p2)

# strencode(
# "Y3x9E1E7BQcdfCQbJVoaAA5EWXccBA5EBRteIhsECh1iDTZJKA4rNg9aUhQmNgwCCDA6OSpCDxgvDj5OOgd8PTpxK3sHf2ANBSYZCAZvFykqGToeCTYAGmBIDTthdC12Fx8dFjI7EwAgBAYCLwxmDX0XDmQediodAyMzAzs9fk46UjtIGSpmJwJxAg19d1BO",
# "343e5cOmG/faF7W9Dv1GxLOrIbfZTPmh/gcxddLOC09cjO5vktkCf8Jobds4wTIIY5zTdL14JpSxT7YnHtlPlq1U92iW41w9YrWYVBIlpPC3aX780mmQQ2gsJka6Xz+wpaa8Cm0QNC3z",
# "Y3x9E1E7BQcdfCQbJVoaAA5EWXccBA5EBRteIhsECh1iDTZJKA4rNg9aUhQmNgwCCDA6OSpCDxgvDj5OOgd8PTpxK3sHf2ANBSYZCAZvFykqGToeCTYAGmBIDTthdC12Fx8dFjI7EwAgBAYCLwxmDX0XDmQediodAyMzAzs9fk46UjtIGSpmJwJxAg19d1BO"));
def main():
    str = get_source('Y3x9E1E7BQcdfCQbJVoaAA5EWXccBA5EBRteIhsECh1iDTZJKA4rNg9aUhQmNgwCCDA6OSpCDxgvDj5OOgd8PTpxK3sHf2ANBSYZCAZvFykqGToeCTYAGmBIDTthdC12Fx8dFjI7EwAgBAYCLwxmDX0XDmQediodAyMzAzs9fk46UjtIGSpmJwJxAg19d1BO','343e5cOmG/faF7W9Dv1GxLOrIbfZTPmh/gcxddLOC09cjO5vktkCf8Jobds4wTIIY5zTdL14JpSxT7YnHtlPlq1U92iW41w9YrWYVBIlpPC3aX780mmQQ2gsJka6Xz+wpaa8Cm0QNC3z')
    print(str)



if __name__ == '__main__':
    download_from_url('http://198.255.82.90//mp43/102331.mp4?st=9RiEsFneMxmNc7ePFN6bNw&e=1554937983','./temp/test.mp4')