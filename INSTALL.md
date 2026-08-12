# Monad Market Noti 설치 가이드

## 1. 사전 준비물
- **지갑 주소:** 감시할 공개 지갑 주소 (개인키 불필요)
- **텔레그램 봇 토큰:** [@BotFather](https://t.me/botfather)에서 생성
- **텔레그램 채팅 ID:** [@userinfobot](https://t.me/userinfobot) 등에서 확인

RPC는 기본값(`https://rpc.monad.xyz`, 공개 RPC)을 그대로 쓰면 됩니다.

## 2. 설치 (Termux/Linux/Windows 공통)

```bash
# Termux의 경우
pkg update && pkg upgrade
pkg install python

pip install -r requirements.txt
```

## 3. 환경 변수 설정

`.env.example`을 복사해 `.env`로 만들고 값을 채우세요:

```bash
cp .env.example .env
```

```env
RPC_URL=https://rpc.monad.xyz
WALLET_ADDRESS=여기에_지갑_주소_입력
TELEGRAM_TOKEN=여기에_텔레그램_토큰_입력
TELEGRAM_CHAT_ID=여기에_채팅_ID_입력
REPORT_INTERVAL_MIN=10
```

`.env`는 `.gitignore`에 포함되어 있어 git에 커밋되지 않습니다.

## 4. 동작 확인

```bash
python test_monad_client.py
```

Net worth / Net APY / Health Factor / 자산별 목록이 출력되면 정상입니다.

## 5. 봇 실행

```bash
python main.py
```

**Tip:** Termux에서 상시 구동 시 `termux-wake-lock`으로 절전 모드를 방지하는 것을 권장합니다.
