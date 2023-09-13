import requests
from requests import Response

# import asyncio


HEADER = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

DEFAULT_REQUEST_TIMEOUT = 8


def send_request(url: str, header: dict[str, str] = HEADER, query: dict[str, str] = {}) -> Response:
    """
    엔드 포인트로 http 요청을 전송합니다.

    Args:
        url (string): url
        query (dict): 요청 전송을 위한 파라미터를 의미한다.
        header (dict): 요청 전송을 위한 헤더를 의미한다.

    Raises:
        requests.exceptions.ConnectTimeout: 커넥션 타임 아웃 에러

    Returns:
        requests.Response: 엔드 포인트 요청 응답결과
    """

    for _ in range(3):
        try:
            res = requests.get(url, headers=header, params=query)
            res.raise_for_status()  # 200번 응답인 경우에만 pass
            return res

        except Exception as e:
            print(e)
    else:
        raise TimeoutError(f">>> {url}, {query} exceeded max retry!")


# async def async_send_request(url: str, headers: dict = {}, query: dict = {}, type="text") -> tuple:
#     """
#     aiohttp를 활용해 비동기로 요청을 전송한다.
#     """
#     tiemout = aiohttp.ClientTimeout(total=5)  # 타임아웃 설정
#     connector = aiohttp.TCPConnector(limit=50)

#     async with aiohttp.ClientSession(
#         timeout=tiemout, connector=connector
#     ) as session:  # 세션 성립에 4초이상 소요되면 종료한다.
#         for i in range(3):
#             try:
#                 async with session.get(url, headers=headers, params=query) as response:
#                     is_redirect = False
#                     assert response.status in [200, 302, 301], f"Response Error {response.status}"
#                     if type == "json":
#                         res = await response.json()
#                     else:
#                         res = await response.text()  # page html을 가져온다.

#                     if response.history:  # history가 1보다 크면 리다이렉트가 된 것
#                         is_redirect = True

#                     return is_redirect, res

#             except asyncio.TimeoutError:
#                 print(f"{query}: Connection delayed: {i}")

#             except AssertionError as e:
#                 print(e, "is occured wait 5 secs..")
#                 await asyncio.sleep(5)

#     await asyncio.sleep(30)
#     raise aiohttp.ClientConnectionError(f"{url} is not respond")
