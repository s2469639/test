"""박람회 상세 페이지의 실시간 환율 표시용. 외부 환율 API를 호출하고
짧은 TTL로 캐싱해 매 요청마다 API를 부르지 않도록 한다."""

import time

import requests

_CACHE = {}
_CACHE_TTL_SECONDS = 3600


def get_exchange_rate(base="USD", target="KRW"):
    key = (base, target)
    cached = _CACHE.get(key)
    if cached and time.time() - cached["fetched_at"] < _CACHE_TTL_SECONDS:
        return cached["rate"]

    try:
        rate = _fetch_exchange_rate(base, target)
    except requests.exceptions.RequestException:
        # 환율 API 장애로 상세 페이지 전체가 죽지 않도록, 실패 시 마지막 캐시값(있다면)을 반환
        return cached["rate"] if cached else None

    _CACHE[key] = {"rate": rate, "fetched_at": time.time()}
    return rate


def _fetch_exchange_rate(base, target):
    """TODO: 실제 환율 API(예: exchangerate-api.com, 한국수출입은행) 연동."""
    resp = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base}", timeout=5)
    resp.raise_for_status()
    return resp.json()["rates"][target]
