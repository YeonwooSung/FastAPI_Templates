# client_example.py - 마이크로서비스에서 Ingestion API 사용 예시

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
import uuid
import time


class IngestionClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_batch(
        self, 
        events: List[Dict[str, Any]], 
        batch_id: str = None,
        priority: int = 0
    ) -> Dict[str, Any]:
        """배치 이벤트 전송"""
        
        # 이벤트 데이터 포맷팅
        formatted_events = []
        for event in events:
            formatted_event = {
                "event_id": event.get("event_id", str(uuid.uuid4())),
                "service_name": event["service_name"],
                "event_type": event["event_type"],
                "payload": event["payload"],
                "timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
                "metadata": event.get("metadata", {})
            }
            formatted_events.append(formatted_event)
        
        payload = {
            "events": formatted_events,
            "batch_id": batch_id,
            "priority": priority
        }
        
        async with self.session.post(
            f"{self.base_url}/v1/ingest/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to send batch: {response.status}")
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """배치 상태 조회"""
        async with self.session.get(
            f"{self.base_url}/v1/batch/{batch_id}/status"
        ) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return {"error": "Batch not found"}
            else:
                raise Exception(f"Failed to get batch status: {response.status}")


# 예시 1: 사용자 서비스에서 이벤트 전송
async def user_service_example():
    """사용자 서비스에서 로그인/가입 이벤트 전송 예시"""
    
    async with IngestionClient() as client:
        # 사용자 이벤트 데이터
        user_events = [
            {
                "service_name": "user-service",
                "event_type": "user_login",
                "payload": {
                    "user_id": "user_123",
                    "login_method": "email",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0...",
                    "success": True
                },
                "metadata": {
                    "region": "us-west-2",
                    "version": "1.2.3"
                }
            },
            {
                "service_name": "user-service",
                "event_type": "user_signup",
                "payload": {
                    "user_id": "user_124",
                    "email": "user@example.com",
                    "signup_method": "google_oauth",
                    "referrer": "https://example.com"
                },
                "metadata": {
                    "ab_test_group": "signup_flow_v2",
                    "campaign_id": "summer_2024"
                }
            }
        ]
        
        # 배치 전송
        response = await client.send_batch(
            events=user_events,
            batch_id=f"user_batch_{int(time.time())}",
            priority=5
        )
        
        print("User service batch response:", response)
        
        # 상태 확인
        await asyncio.sleep(2)
        status = await client.get_batch_status(response["batch_id"])
        print("Batch status:", status)


# 예시 2: 주문 서비스에서 대량 이벤트 전송
async def order_service_example():
    """주문 서비스에서 주문 처리 이벤트 대량 전송 예시"""
    
    async with IngestionClient() as client:
        # 대량 주문 이벤트 생성 (1000개)
        order_events = []
        for i in range(1000):
            event = {
                "service_name": "order-service",
                "event_type": "order_created" if i % 3 == 0 else "order_updated",
                "payload": {
                    "order_id": f"order_{i:06d}",
                    "customer_id": f"customer_{i % 100}",
                    "total_amount": round(50.0 + (i % 500), 2),
                    "items_count": 1 + (i % 5),
                    "status": "pending" if i % 4 == 0 else "confirmed"
                },
                "metadata": {
                    "source": "api",
                    "channel": "web" if i % 2 == 0 else "mobile"
                }
            }
            order_events.append(event)
        
        # 배치를 500개씩 나누어 전송
        batch_size = 500
        for i in range(0, len(order_events), batch_size):
            batch = order_events[i:i + batch_size]
            
            response = await client.send_batch(
                events=batch,
                batch_id=f"order_batch_{i//batch_size}_{int(time.time())}",
                priority=3
            )
            
            print(f"Order batch {i//batch_size + 1} response:", response)


# 예시 3: 결제 서비스에서 고우선순위 이벤트 전송
async def payment_service_example():
    """결제 서비스에서 결제 이벤트 전송 예시"""
    
    async with IngestionClient() as client:
        payment_events = [
            {
                "service_name": "payment-service",
                "event_type": "payment_processed",
                "payload": {
                    "payment_id": "pay_abc123",
                    "order_id": "order_456789",
                    "amount": 99.99,
                    "currency": "USD",
                    "payment_method": "credit_card",
                    "gateway": "stripe",
                    "status": "success",
                    "transaction_id": "txn_xyz789"
                },
                "metadata": {
                    "risk_score": 0.1,
                    "processing_time_ms": 1250,
                    "gateway_fee": 2.89
                }
            },
            {
                "service_name": "payment-service",
                "event_type": "payment_failed",
                "payload": {
                    "payment_id": "pay_def456",
                    "order_id": "order_789012",
                    "amount": 149.99,
                    "currency": "USD",
                    "payment_method": "credit_card",
                    "gateway": "stripe",
                    "status": "failed",
                    "error_code": "insufficient_funds",
                    "error_message": "Your card has insufficient funds"
                },
                "metadata": {
                    "retry_count": 2,
                    "risk_score": 0.8
                }
            }
        ]
        
        # 고우선순위로 전송 (결제는 중요한 이벤트)
        response = await client.send_batch(
            events=payment_events,
            priority=8  # 높은 우선순위
        )
        
        print("Payment batch response:", response)


# 예시 4: 배치 처리 모니터링
async def monitoring_example():
    """배치 처리 상태 모니터링 예시"""
    
    async with IngestionClient() as client:
        # 테스트 이벤트 전송
        test_events = [
            {
                "service_name": "monitoring-service",
                "event_type": "system_health_check",
                "payload": {
                    "service": "api-gateway",
                    "status": "healthy",
                    "response_time_ms": 45,
                    "memory_usage_mb": 512,
                    "cpu_usage_percent": 23.5
                }
            }
        ]
        
        response = await client.send_batch(
            events=test_events,
            batch_id="monitoring_test_batch"
        )
        
        batch_id = response["batch_id"]
        print(f"Monitoring batch sent: {batch_id}")
        
        # 상태를 주기적으로 확인
        for i in range(10):
            await asyncio.sleep(2)
            status = await client.get_batch_status(batch_id)
            print(f"Status check {i+1}: {status}")
            
            if status.get("status") == "completed":
                print("Batch processing completed!")
                break
            elif status.get("status") == "failed":
                print("Batch processing failed!")
                break


# 예시 5: 에러 처리 및 재시도 로직
async def error_handling_example():
    """에러 처리 및 재시도 로직 예시"""
    
    async def send_with_retry(client, events, max_retries=3):
        """재시도 로직이 포함된 전송 함수"""
        for attempt in range(max_retries):
            try:
                response = await client.send_batch(events=events)
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 지수 백오프
    
    async with IngestionClient() as client:
        error_events = [
            {
                "service_name": "error-test-service",
                "event_type": "test_event",
                "payload": {"test": "data"}
            }
        ]
        
        try:
            response = await send_with_retry(client, error_events)
            print("Successfully sent with retry:", response)
        except Exception as e:
            print(f"Failed after all retries: {e}")


# 메인 실행 함수
async def main():
    """모든 예시 실행"""
    print("=== User Service Example ===")
    await user_service_example()
    
    print("\n=== Order Service Example ===")
    await order_service_example()
    
    print("\n=== Payment Service Example ===")
    await payment_service_example()
    
    print("\n=== Monitoring Example ===")
    await monitoring_example()
    
    print("\n=== Error Handling Example ===")
    await error_handling_example()


if __name__ == "__main__":
    asyncio.run(main())


# 추가 유틸리티 함수들

class EventBuilder:
    """이벤트 생성을 위한 헬퍼 클래스"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        event_id: str = None
    ) -> Dict[str, Any]:
        """표준화된 이벤트 생성"""
        return {
            "event_id": event_id or str(uuid.uuid4()),
            "service_name": self.service_name,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }


# Django/Flask 통합 예시
class DjangoIngestionMixin:
    """Django 프로젝트에서 사용할 수 있는 믹스인"""
    
    @staticmethod
    async def send_user_event(user_id: int, event_type: str, payload: Dict[str, Any]):
        """Django 사용자 이벤트 전송"""
        async with IngestionClient() as client:
            event = {
                "service_name": "django-app",
                "event_type": event_type,
                "payload": {
                    "user_id": user_id,
                    **payload
                },
                "metadata": {
                    "framework": "django",
                    "version": "4.2"
                }
            }
            
            return await client.send_batch([event])


# FastAPI 통합 예시  
from fastapi import BackgroundTasks

class FastAPIIngestionService:
    """FastAPI 서비스에서 사용할 백그라운드 이벤트 전송"""
    
    def __init__(self):
        self.client = None
    
    async def initialize(self):
        self.client = IngestionClient()
        await self.client.__aenter__()
    
    async def cleanup(self):
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    def send_event_background(
        self, 
        background_tasks: BackgroundTasks,
        service_name: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """백그라운드에서 이벤트 전송"""
        background_tasks.add_task(
            self._send_event,
            service_name,
            event_type,
            payload
        )
    
    async def _send_event(
        self,
        service_name: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """실제 이벤트 전송 로직"""
        try:
            async with IngestionClient() as client:
                event = {
                    "service_name": service_name,
                    "event_type": event_type,
                    "payload": payload
                }
                await client.send_batch([event])
        except Exception as e:
            print(f"Failed to send event: {e}")
            # 로깅 또는 데드레터 큐로 전송
