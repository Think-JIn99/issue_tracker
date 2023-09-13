from requests import Request, Response, PreparedRequest, Session
from collections import namedtuple
import json
import time

from database import bulk_insert
from models import Newses

url = "https://news.naver.com/main/mainNews.naver"
headers = {"Host": "news.naver.com", "User-Agent": "curl/7.64.1", "Accept": "*/*"}  # 통신 헤더. 필수요소

Category = namedtuple("Category", ["정치", "경제", "사회", "과학", "세계"])  # 뉴스 카테고리
categories = Category(정치=100, 경제=101, 사회=102, 과학=103, 세계=104)

News = namedtuple(
    "News", ["id", "category", "title", "summary", "office_name", "service_time", "url"]
)  # DB에 저장할 뉴스 탬플릿


def create_request(category_number: int, page: int) -> PreparedRequest:
    """
    전송할 리퀘스트를 생성합니다.

    Args:
        category_number (int): 카테고리 번호
        page (int): 페이지 번호

    Returns:
        PreparedRequest: 인코딩된  HTTP 리퀘스트 객체
    """
    params = {"sid1": category_number, "page": page}  # api콜을 위한 파라미터
    req = Request(method="POST", headers=headers, url=url, params=params)  # request 생성
    prepared_request = req.prepare()  # request 정보 encoding 처리된 전송 가능한 리퀘스트 생성
    return prepared_request


def send_request(req: PreparedRequest | list[PreparedRequest]) -> list[Response]:
    """
    리퀘스트 전송

    Args:
        req (PreparedRequest | list[PreparedRequest]): HTTP 리퀘스트 객체 혹은 리퀘스트 리스트

    Returns:
        list[Response]: HTTP 응답 리스트
    """

    if not isinstance(req, list):
        req = [req]  # list로 변환

    responses = []
    with Session() as session:  # 세션을 통한 커넥션 생성
        for r in req:
            try:
                res = session.send(r, timeout=3000)  # HTTP 전송
                responses.append(res)
                print(f">> Send {r.url} is completed")
                time.sleep(0.1)  # block을 위한 sleep

            except Exception as e:
                print(">> Send Request Failed", r.url)
                print(e)

    return responses


def parse_response(response: Response, category: str) -> list[News]:
    """
    HTTP 응답 데이터를 파싱해 필요한 데이터만 추출합니다.

    Args:
        response (Response): HTTP 응답 객체
        category (str): 카테고리 (정치, 경제, 사회, ...)

    Raises:
        ValueError: 파싱 에러

    Returns:
        list[News]: 파싱한 뉴스 템플릿 데이터
    """
    newses = []
    get_url = (
        lambda office_id, article_id: f"https://n.news.naver.com/article/{office_id}/{article_id}"
    )  # 상세 url 생성 함수

    json_res = response.json()  # api 정보 파싱
    airs_result = json.loads(json_res["airsResult"])  # TODO nested json이 희한하게 안풀려서. 번거롭게 2번 풀어줘야함.
    category_number = str(getattr(categories, category))

    for news in airs_result["result"][category_number]:
        try:
            article_id = news["articleId"]  # 뉴스 아이디
            title = news["title"]
            summary = news["summary"]
            office_id = news["officeId"]  # 언론사 아이디
            office_name = news["officeName"]  # 언론사 이름
            service_time = news["serviceTime"]  # 기사 작성일
            url = get_url(office_id, article_id)

            news = News(
                id=article_id,
                category=category,
                title=title,
                summary=summary,
                office_name=office_name,
                service_time=service_time,
                url=url,
            )

            newses.append(news)

        except Exception as e:
            raise ValueError(">> Can't Parse Data. Response Data is not correct")  # 파싱 에러

    return newses


def scrap(category: str):
    """
    10 페이지씩 순회하며 네이버로 부터 뉴스를 추출합니다.

    Args:
        category (str): 카테고리

    Returns:
        list|none: 추출한 뉴스 데이터 혹은 None

    Yields:
        list|none: 추출한 뉴스 데이터 혹은 None
    """
    category_number = getattr(categories, category)
    print(f"category_numebr: {category_number} is running")
    page: int = 1  # 스크래핑 진행할 페이지 번호

    while True:
        req_list = [
            create_request(category_number, i) for i in range(page, page + 10)
        ]  # 100페이지에 대해서 요청생성
        res = send_request(req_list)  # HTTP 리퀘스트 송신
        article_id_set = set()  # 중복 체크를 위한 아이디 집합
        total_newses = []  # 전체 뉴스
        for r in res:
            try:
                page_newses = []  # 단일 페이지 뉴스
                for n in parse_response(r, category):
                    if n.id not in article_id_set:
                        page_newses.append(n)  # 중복이 아닐 경우
                        article_id_set.add(n.id)  # 중복이 아닐 경우

                if len(page_newses):
                    total_newses.extend(page_newses)

                else:
                    print(
                        f"category: {category} is ended in page:{page} ~ {page + 10}"
                    )  # 중복이 아닌 뉴스가 없다면 반복문 종료한다
                    yield None

            except Exception as e:
                print(e)

        page += 10

        yield total_newses


def main():
    for category in categories._fields:
        news_gen = scrap(category)
        if category in ("정치", "경제", "사회"):
            while True:
                try:
                    newses = next(news_gen)
                    if newses:
                        print(newses[0], " is completed")  # 파싱 샘플 확인
                        bulk_insert(Newses, [n._asdict() for n in newses])  # DB에 입력
                        print(f"News inserted  {newses[:3]}")

                    else:
                        break

                except StopIteration as e:
                    break #제네레이터 종료시

                except Exception as e:
                    print(e)


# print(newses[0], " is completed")  # 파싱 샘플 확인
# bulk_insert(Newses, [n._asdict() for n in newses])  # DB에 입력

if __name__ == "__main__":
    main()
