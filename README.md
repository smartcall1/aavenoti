# Monad Market Noti (Aave Monad 대시보드 감시 봇)

Aave V3 Monad Market(체인 143, `rpc.monad.xyz`)의 포지션 현황을 주기적으로 텔레그램으로 보고하는 봇입니다.
[aave_noti](../aave_noti)와 동일한 구조를 재사용했으며, 감시 대상만 이더리움 메인넷 Aave에서 Monad Market으로 교체했습니다.

## 주요 기능
- **정기 대시보드 리포트:** 기본 10분마다(설정 가능) Net worth, Net APY, Health Factor, 자산별 공급/대출 잔액과 APY를 텔레그램으로 전송합니다.
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
