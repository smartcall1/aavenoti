# Monad Market Noti (Aave Monad 대시보드 감시 봇)

Aave V3 Monad Market(체인 143, `rpc.monad.xyz`)의 포지션 현황을 주기적으로 텔레그램으로 보고하는 봇입니다.
[aave_noti](../aave_noti)와 동일한 구조를 재사용했으며, 감시 대상만 이더리움 메인넷 Aave에서 Monad Market으로 교체했습니다.

## 주요 기능
- **정기 대시보드 리포트:** 기본 2분마다(설정 가능) Net worth, Net APY, Health Factor, 자산별 공급/대출 잔액과 APY를 텔레그램으로 전송합니다. 자산별 조회를 병렬 RPC 호출로 처리해 12개 자산 기준 약 8초 내에 끝납니다(2분 주기 기준 부하율 ~7%).
- **HF 긴급 알림:** 기본 1분마다(설정 가능) Health Factor만 가볍게 체크해, 임계값(기본 1.1) 밑으로 떨어지면 즉시 경보를 보냅니다. 임계값 아래에 머무는 동안은 재알림 없이 1회만 발송하고, 회복 시 회복 알림을 보냅니다.
- **무음 정기 리포트:** 정기 대시보드 리포트는 기본적으로 무음(`disable_notification`)으로 전송되어 폰이 울리지 않고, HF·순APY 긴급/회복 알림만 평소처럼 소리·진동으로 옵니다. `REPORT_SILENT=false`로 바꾸면 정기 리포트도 알림이 뜨게 할 수 있습니다.
- **순APY 경고:** 정기 리포트 조회 시점마다 순APY가 임계값(기본 10%) 아래로 떨어지면 별도 알림을 보냅니다. HF와 마찬가지로 임계값 아래에 머무는 동안은 1회만 발송하고, 회복 시 회복 알림을 보냅니다.
- **알림 채널 분리(선택):** `TELEGRAM_EMERGENCY_TOKEN`/`TELEGRAM_EMERGENCY_CHAT_ID`를 채우면 HF/순APY 긴급알림이 별도 봇/채팅방으로 갑니다. 정기 리포트 채팅방은 마음 편히 뮤트해두고, 긴급알림 채팅방만 알림 켜두면 됩니다. 비워두면 기존처럼 한 채팅방으로 다 옵니다.
- **잔존 메뉴 자동 제거:** 봇 시작 시 emergency 채팅방에 남아있을 수 있는 예전 봇의 커스텀 키보드(Status/Funding/Stop/Kill 같은)를 자동으로 지웁니다.
- **Net worth 증감 표시:** 정기 리포트마다 직전 조회 대비 Net worth 변화량을 `(+$1.86)` 형태로 함께 보여줍니다 (첫 리포트는 비교 대상이 없어 생략).
- **개인키 불필요:** 지갑 주소만으로 온체인 데이터를 읽어옵니다 (읽기 전용 RPC 호출).
- **초경량:** Python 기반, Termux에서도 가볍게 상시 구동 가능합니다.

## 컨트랙트 (Monad 메인넷, chain 143)
- Pool: `0x69a5F9AD4f96ebf0a0C792dD42a01cC5C0102fef`
- AaveProtocolDataProvider: `0xB65A68B98274ef7D9a60E0C0747dD1BEc3D32fad`
- AaveOracle: `0x0c02b2c2038066C10Eab8fe1D5Cdb73d5a78A1Bf`

## 파일 구성
- `main.py`: 스케줄 관리 및 메인 루프
- `monad_client.py`: Monad Market 온체인 데이터 조회
- `formatter.py`: 텔레그램 메시지 포맷팅
- `notifier.py`: 텔레그램 Bot API 전송
- `test_monad_client.py`: 연결/데이터 조회 테스트 스크립트
- `.env`: 개인 설정 (지갑 주소, 텔레그램 토큰 등) — **절대 커밋 금지**

## 빠른 시작
1. `.env.example`을 복사해 `.env`로 만들고 값을 채웁니다.
2. `pip install -r requirements.txt`
3. `python test_monad_client.py`로 데이터 조회를 확인합니다.
4. `python main.py`로 봇을 실행합니다.

자세한 설치 방법은 [INSTALL.md](./INSTALL.md)를 참고하세요.
