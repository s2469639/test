"""부스 컨셉 / 기안서 자동 생성. scripts/classify/preprocess.py와 같은
OpenAI 클라이언트 설정을 재사용한다."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"


def generate_booth_concept(exhibition):
    """박람회 상세 데이터를 기반으로 부스 테마·슬로건·셀링포인트·이벤트 기획안 생성."""
    prompt = (
        f"박람회명: {exhibition.name}\n"
        f"국가: {exhibition.country}\n"
        f"규모: {exhibition.scale}\n"
        f"키워드: {exhibition.keywords}\n"
        f"참관대상: {exhibition.audience_note}\n"
        f"소개: {exhibition.intro}\n\n"
        "이 박람회에 맞는 부스 테마, 슬로건, 핵심 셀링포인트, 이벤트 기획안을 제안해줘."
    )
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    # TODO: response_format(json_schema)로 구조화된 필드(theme/slogan/selling_points/event_plan) 강제
    return {"raw_text": resp.choices[0].message.content}


def generate_proposal(exhibition, concept_draft):
    """컨셉 초안을 바탕으로 참가 기안서 초안 생성."""
    prompt = (
        f"박람회명: {exhibition.name}\n"
        f"부스 컨셉: {concept_draft.theme if concept_draft else '(미작성)'}\n\n"
        "이 정보를 바탕으로 사내 참가 기안서 초안을 작성해줘."
    )
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"content": resp.choices[0].message.content}
