import time
import uuid
import logging

# custom modules
from app.config import settings
from app.db import redis_client


logger = logging.getLogger(__name__)


class LockAcquisitionError(Exception):
    """락 획득 실패 예외"""
    pass


class DistributedLock:
    """Redis 기반 분산락 구현"""
    
    def __init__(self, resource_key: str, timeout: int = None, retry_count: int = None, retry_delay: float = None):
        """
        분산락 초기화
        
        Args:
            resource_key: 락을 획득할 리소스 키
            timeout: 락 만료 시간(초)
            retry_count: 락 획득 재시도 횟수
            retry_delay: 재시도 간 대기 시간(초)
        """
        self.resource_key = f"lock:{resource_key}"
        self.lock_id = str(uuid.uuid4())
        self.timeout = timeout or settings.LOCK_TIMEOUT
        self.retry_count = retry_count or settings.LOCK_RETRY_COUNT
        self.retry_delay = retry_delay or settings.LOCK_RETRY_DELAY
        self.redis = redis_client
        self._locked = False

    async def acquire(self) -> bool:
        """락 획득 시도"""
        retry = 0
        
        while retry < self.retry_count:
            # SET NX (Not eXists): 키가 없을 때만 설정 (원자적 연산)
            # EX: 만료 시간 설정(초)
            acquired = self.redis.set(
                self.resource_key, 
                self.lock_id, 
                nx=True, 
                ex=self.timeout
            )
            
            if acquired:
                self._locked = True
                logger.debug(f"Lock acquired: {self.resource_key}")
                return True
                
            logger.debug(f"Lock acquisition failed, retrying {retry+1}/{self.retry_count}")
            retry += 1
            time.sleep(self.retry_delay)
            
        logger.warning(f"Failed to acquire lock after {self.retry_count} attempts: {self.resource_key}")
        return False

    async def release(self) -> bool:
        """락 해제 (compare-and-delete 패턴 사용)"""
        if not self._locked:
            return True
            
        # Lua 스크립트로 원자적 연산 구현: 키가 우리 것일 때만 삭제
        release_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(
            release_script, 
            1,  # keys 개수 
            self.resource_key,  # KEYS[1]
            self.lock_id  # ARGV[1]
        )
        
        if result:
            self._locked = False
            logger.debug(f"Lock released: {self.resource_key}")
            return True
        else:
            logger.warning(f"Failed to release lock or lock already expired: {self.resource_key}")
            return False

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        if not await self.acquire():
            raise LockAcquisitionError(f"Failed to acquire lock: {self.resource_key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.release()
