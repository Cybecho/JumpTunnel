#!/bin/bash

# ANSI 색상 코드 설정
GREEN="\e[32m"
CYAN="\e[36m"
RESET="\e[0m"

clear

# ASCII 아트 헤더
cat << "EOF"
      ██╗██╗   ██╗███╗   ███╗██████╗     ████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗     
      ██║██║   ██║████╗ ████║██╔══██╗    ╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║     
      ██║██║   ██║██╔████╔██║██████╔╝       ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║███████╗██║     
 ██   ██║██║   ██║██║╚██╔╝██║██╔═══╝        ██║   ██║   ██║██║╚██╗██║██║╚██╗██║╚════██║██║     
 ╚█████╔╝╚██████╔╝██║ ╚═╝ ██║██║            ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████║███████╗
  ╚════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝            ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚══════╝
EOF

echo -e "${GREEN}=========================================="
echo -e "  J U M P   T U N N E L   !  "
echo -e "==========================================${RESET}"
echo -e "이 스크립트는 다음 작업을 자동화합니다:"
echo -e "1. 'master' 사용자 생성"
echo -e "2. 'sudo' 권한 추가"
echo -e "3. SSH 키 등록 및 보안 설정"
echo -e "\n📌 SSH 키 생성 및 확인 방법:"
echo -e "  [Linux/Mac]"
echo -e "    키 생성: ${CYAN}ssh-keygen -t ed25519 -f ~/.ssh/master_id -C \"master-key\"${RESET}"
echo -e "    키 확인: ${CYAN}cat ~/.ssh/master_id.pub${RESET}"
echo -e "  [Windows]"
echo -e "    키 생성: ${CYAN}ssh-keygen -t ed25519 -f %USERPROFILE%\\.ssh\\master_id -C \"master-key\"${RESET}"
echo -e "    키 확인: ${CYAN}type %USERPROFILE%\\.ssh\\master_id.pub${RESET}"
echo -e "\n🔑 SSH 공개 키 등록 방법:"
echo -e "  1) 매개변수로 실행 시: ${CYAN}sudo ./setup_master_user.sh \"ssh-ed25519 AAAAC3... master-key\"${RESET}"
echo -e "  2) 매개변수 없이 실행하면 아래에서 직접 입력할 수 있습니다.\n"

# 매개변수가 없으면 CLI 입력 받기, 있으면 첫번째 매개변수를 사용
if [ -z "$1" ]; then
    echo -en "${GREEN}SSH 공개 키를 입력하세요 (엔터로 완료): ${RESET}"
    read -r SSH_KEY
else
    SSH_KEY="$1"
fi

if [[ -z "$SSH_KEY" ]]; then
    echo -e "${CYAN}❌ SSH 공개 키가 입력되지 않았습니다. 종료합니다.${RESET}"
    exit 1
fi

USERNAME="master"

# 1. 사용자 생성 및 패스워드 설정
echo -e "\n${GREEN}→ 'master' 사용자 생성 중...${RESET}"
sudo useradd -m "$USERNAME"
echo "$USERNAME:$USERNAME" | sudo chpasswd
sudo usermod -aG sudo "$USERNAME"

# 2. SSH 디렉토리 및 권한 설정
echo -e "${GREEN}→ SSH 디렉토리 생성 및 권한 설정 중...${RESET}"
sudo mkdir -p /home/$USERNAME/.ssh
sudo chmod 700 /home/$USERNAME/.ssh

# 3. SSH 키 등록
echo -e "${GREEN}→ SSH 키 등록 중...${RESET}"
echo "$SSH_KEY" | sudo tee -a /home/$USERNAME/.ssh/authorized_keys > /dev/null
sudo chmod 600 /home/$USERNAME/.ssh/authorized_keys
sudo chown -R "$USERNAME:$USERNAME" /home/$USERNAME/.ssh

echo -e "\n✅ ${GREEN}설정 완료!${RESET}"
echo -e "🔗 이제 SSH로 접속할 수 있습니다:"
echo -e "${CYAN}ssh $USERNAME@서버_IP${RESET}"
