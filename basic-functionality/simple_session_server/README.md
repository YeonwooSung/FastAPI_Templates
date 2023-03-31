# Session in FastAPI

FastAPI에서 세션을 사용하기 위해서는 일반적으로 `fastapi_session` 라이브러리를 사용합니다.

## fastapi_session

`fastapi_session` 라이브러리는 3가지 컴포넌트로 이루어져 있습니다:

- `SessionFrontend`: Session ID 저장하기 위한 기능을 포함하고 있습니다. (Cookie, Header 등)
- `SessionBackend`: Session ID에 대한 Session Data를 생성/저장/삭제/조회하는 기능을 포함하고 있습니다.
- `SessionMiddleware`: 주어진 Session ID가 유효한지 검사하는 기능을 제공합니다.

### Where does session memory store?

각 언어/프레임워크/라이브러리마다 세션 데이터를 저장하는 방법이 다릅니다.

가장 일반적인 방법으로는 in-memory 방식으로 세션 데이터를 저장하는 것이 있습니다.
Session-ID를 키로 하고, Session Data를 값으로 하는 key-value 저장 방식을 사용합니다.
fastapi_session 라이브러리에서는 이를 구현하기 위해 Python Dictionary를 사용합니다.

당연히 이러한 방식은 규모가 큰 서비스에서는 부하가 발생하기 쉽습니다.
그래서 대규모 트래픽을 감당하기 위한 서비스 개발 부서들 중에는 이러한 부하 문제를 해결하기 위해 Redis나 Memcached 같은 외부 저장소를 사용하기도 합니다.
