# financial transactions

## 주요 기능

1. **분산락(Distributed Lock)** - Redis를 사용하여 여러 서버에서 동시에 같은 계좌에 접근하는 경우를 안전하게 처리
2. **Compare-and-Set 알고리즘** - 낙관적 락(Optimistic Lock)으로 데이터 일관성 보장
3. **원자적 트랜잭션 처리** - 송금, 입금, 출금 처리 중 오류 발생 시 롤백
4. **계좌 이체** - 분산락과 CAS 알고리즘을 결합한 안전한 계좌 이체 구현

## 기술 설명

1. **분산락 구현**
   - Redis의 `SET NX EX` 명령어를 사용하여 원자적 락 획득
   - compare-and-delete 패턴 기반 원자적 락 해제
   - 재시도 정책(retry policy) 설정을 통한 락 획득 신뢰성 향상

2. **Compare-and-Set 알고리즘**
   - 각 계좌에 버전 번호 유지
   - 트랜잭션 시 버전 확인 후 업데이트 (버전이 일치할 때만)
   - 버전 불일치 시 재시도 로직

3. **동시성 제어**
   - 분산락으로 인스턴스간 동시성 제어
   - 낙관적 락으로 DB 수준 동시성 제어
   - 송금 시 데드락 방지를 위해 정렬된 순서로 락 획득

## API 엔드포인트

- `POST /api/v1/accounts` - 계좌 생성
- `GET /api/v1/accounts/{account_number}` - 계좌 조회
- `POST /api/v1/transactions` - 입금/출금 트랜잭션 생성
- `POST /api/v1/transfers` - 계좌 이체 처리
