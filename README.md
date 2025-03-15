# J U M P   T U N N E L   !

[튜토리얼 글](https://cybecho.notion.site/1b21bab9e3f880b5b550cb614005e951?pvs=4)

## Windows Tunnel Client Program

해당 코드는 Python 3.13.x 버전으로 작성되었습니다.

빌드 전, 아래 패키지를 설치해주세요

```
py -m pip install PyQt5
py -m pip install pyinstaller

```

그 후, [SSH_Tunnel_GUI.py](https://github.com/Cybecho/JumpTunnel/blob/main/SSH_Tunnel_GUI.py) 이 위치하는 디렉토리로 이동하여, 아래 명령어로 직접 빌드하여 사용하세요.

`./dict/` 디렉토리에 `SSH_Tunnel_GUI.exe` 실행시켜주시면 됩니다.

```
pyinstaller --onefile --windowed SSH_Tunnel_GUI.py

```



# Linux Tunnel Host Script

이 스크립트는 다음 작업을 자동화합니다:
1. 'master' 사용자 생성
2. 'sudo' 권한 추가
3. SSH 키 등록 및 보안 설정

📌 SSH 키 생성 및 확인 방법:
  [Linux/Mac]
    키 생성: ssh-keygen -t ed25519 -f ~/.ssh/master_id -C "master-key"
    키 확인: cat ~/.ssh/master_id.pub
  [Windows]
    키 생성: ssh-keygen -t ed25519 -f %USERPROFILE%\.ssh\master_id -C "master-key"
    키 확인: type %USERPROFILE%\.ssh\master_id.pub

🔑 SSH 공개 키 등록 방법:
  1) 매개변수로 실행 시: sudo ./setup_master_user.sh "ssh-ed25519 AAAAC3... master-key"
  2) 매개변수 없이 실행하면 아래에서 직접 입력할 수 있습니다.

  ---

### 사용법
 `setup_jump_tunnel.sh` 를 각 터널 구간 클라이언트에 설치 및 설정해주세요

```
sudo curl -sSL https://raw.githubusercontent.com/your_github_username/your_repo/main/setup_master_user.sh | bash

```
