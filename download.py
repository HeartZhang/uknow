import requests
from tqdm import tqdm
import os
import aiohttp
import asyncio

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


async def fetch(session, url, dst, pbar=None, headers=None):
    if headers:
        async with session.get(url, headers=headers) as req:
            with(open(dst, 'ab')) as f:
                while True:
                    chunk = await req.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(1024)
            pbar.close()
    else:
        async with session.get(url) as req:
            return req


async def async_download_from_url(url, dst):
    '''异步'''
    async with aiohttp.ClientSession() as session:
        req = await fetch(session, url, dst)

        file_size = int(req.headers['content-length'])
        print(f"get file size:{file_size}")
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size
        header = {"Range": f"bytes={first_byte}-{file_size}"}
        pbar = tqdm(
            total=file_size, initial=first_byte,
            unit='B', unit_scale=True, desc=dst)
        await fetch(session, url, dst, pbar=pbar, headers=header)


def download_from_url(url, dst):
    '''同步'''
    response = requests.get(url, stream=True)
    file_size = int(response.headers['content-length'])
    print(f"get file size:{file_size}")
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": f"bytes={first_byte}-{file_size}"}
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=dst)
    req = requests.get(url, headers=header, timeout=60, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


# 异步方式下载
def async_exec():
    url = "http://185.38.13.130//mp43/288480.mp4?st=sTT_s7ocvoWtG1DffBbMTQ&e=1555454272"
    task = [asyncio.ensure_future(async_download_from_url(url, f"temp/{i}.mp4")) for i in range(1, 3)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(task))
    loop.close()


# 同步方式下载
def sync_exec():
    url = "http://192.240.120.34//mp43/219718.mp4?st=bmftKonmYBBhGooEY0NoOA&e=1555035414"
    download_from_url(url, "夏目友人帐第一集.mp4")

def main():
    sync_exec()


if __name__ == '__main__':
    main()