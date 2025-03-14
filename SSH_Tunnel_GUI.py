import sys, os, subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QComboBox, QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt

class TunnelGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSH Jump Tunnel ! ! !")
        self.proxy_routers = []
        self.leaf_nodes = []
        self.ssh_path = os.path.expanduser("~/.ssh")
        if not os.path.exists(self.ssh_path):
            os.makedirs(self.ssh_path)
        self.key_path = os.path.join(self.ssh_path, "master_id")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("��️ Jump Tunnel ! ! ! �️�")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Bastion 설정 (Port 포함)
        bastion_group = QGroupBox("Bastion 설정 (필수)")
        bastion_layout = QHBoxLayout()
        self.bastion_name = QLineEdit("Bastion_master")
        self.bastion_ip = QLineEdit("127.0.0.1")
        self.bastion_port = QSpinBox()
        self.bastion_port.setMaximum(65535)
        self.bastion_port.setValue(22222)
        bastion_layout.addWidget(QLabel("이름"))
        bastion_layout.addWidget(self.bastion_name)
        bastion_layout.addWidget(QLabel("IP"))
        bastion_layout.addWidget(self.bastion_ip)
        bastion_layout.addWidget(QLabel("포트"))
        bastion_layout.addWidget(self.bastion_port)
        bastion_group.setLayout(bastion_layout)
        layout.addWidget(bastion_group)

        # Proxy Routers 추가 버튼
        self.router_layout = QVBoxLayout()
        router_btn = QPushButton("➕ Add ProxyRouter")
        router_btn.clicked.connect(self.add_router)
        layout.addWidget(router_btn)
        layout.addLayout(self.router_layout)

        # Leaf Nodes 추가 버튼
        self.leaf_layout = QVBoxLayout()
        leaf_btn = QPushButton("➕ Add LeafNode")
        leaf_btn.clicked.connect(self.add_leafnode)
        layout.addWidget(leaf_btn)
        layout.addLayout(self.leaf_layout)

        # SSH 키 생성 버튼
        key_btn = QPushButton("� Generate master_id Key")
        key_btn.clicked.connect(self.generate_ssh_key)
        layout.addWidget(key_btn)

        # 별도 Public Key 출력
        self.pub_key_output = QTextEdit()
        self.pub_key_output.setReadOnly(True)
        layout.addWidget(QLabel("� 생성된 Public Key:"))
        layout.addWidget(self.pub_key_output)

        # curl 명령어 출력
        self.curl_command_output = QTextEdit()
        self.curl_command_output.setReadOnly(True)
        layout.addWidget(QLabel("� 해당 명령어를 각 터널이 적용될 VM에 입력해주세요!"))
        layout.addWidget(self.curl_command_output)

        # Config 생성 버튼
        gen_btn = QPushButton("✅ Generate & Save SSH Config")
        gen_btn.clicked.connect(self.generate_config)
        layout.addWidget(gen_btn)

        # SSH 접속 명령어 출력 블록
        self.ssh_access_output = QTextEdit()
        self.ssh_access_output.setReadOnly(True)
        layout.addWidget(QLabel("� SSH Config 생성 후, 호스트측 CLI에서 아래 명령어로 바로 터널에 접근할 수 있습니다!:"))
        layout.addWidget(self.ssh_access_output)

        self.setLayout(layout)

    def add_router(self):
        """
        Proxy Router(중간 라우터)를 추가하는 레이아웃.
        """
        name_edit = QLineEdit()
        ip_edit = QLineEdit()

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Proxy Jump Name"))
        h_layout.addWidget(name_edit)
        h_layout.addWidget(QLabel("Proxy Jump IP"))
        h_layout.addWidget(ip_edit)
        
        delete_btn = QPushButton("�️ 삭제")
        delete_btn.clicked.connect(
            lambda: self.remove_router(h_layout, (name_edit, ip_edit, delete_btn))
        )
        h_layout.addWidget(delete_btn)

        self.router_layout.addLayout(h_layout)
        self.proxy_routers.append((name_edit, ip_edit, delete_btn))

    def remove_router(self, layout, router_data):
        """
        Proxy Router(중간 라우터) 삭제 처리
        """
        self.proxy_routers.remove(router_data)
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        layout.deleteLater()

    def add_leafnode(self):
        """
        Leaf Node(최종 노드)를 추가하는 레이아웃.
        - 포트(기본 22)도 입력받도록 수정
        """
        name_edit = QLineEdit()
        ip_edit = QLineEdit()
        router_combo = QComboBox()
        router_combo.addItems([r[0].text() for r in self.proxy_routers])

        # LeafNode 별 Port 지정 가능
        port_spinbox = QSpinBox()
        port_spinbox.setMaximum(65535)
        port_spinbox.setValue(22)  # 기본 22로 설정

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Leaf 이름"))
        h_layout.addWidget(name_edit)
        h_layout.addWidget(QLabel("Leaf IP"))
        h_layout.addWidget(ip_edit)
        h_layout.addWidget(QLabel("Attached Router"))
        h_layout.addWidget(router_combo)
        h_layout.addWidget(QLabel("Leaf Port"))
        h_layout.addWidget(port_spinbox)

        delete_btn = QPushButton("�️ 삭제")
        delete_btn.clicked.connect(
            lambda: self.remove_leafnode(h_layout, (name_edit, ip_edit, router_combo, port_spinbox, delete_btn))
        )
        h_layout.addWidget(delete_btn)

        self.leaf_layout.addLayout(h_layout)
        # leaf_nodes 배열에 port_spinbox도 함께 저장
        self.leaf_nodes.append((name_edit, ip_edit, router_combo, port_spinbox, delete_btn))

    def remove_leafnode(self, layout, leaf_data):
        self.leaf_nodes.remove(leaf_data)
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        layout.deleteLater()

    def generate_ssh_key(self):
        """
        기존 SSH 키를 삭제하고 새로 생성한 뒤,
        공개키와 curl 명령어를 화면에 표시
        """
        for ext in ['', '.pub']:
            path = self.key_path + ext
            if os.path.exists(path):
                os.remove(path)

        subprocess.run(
            ['ssh-keygen', '-t', 'ed25519', '-f', self.key_path, '-C', 'master-key', '-N', ''],
            shell=True, check=True
        )

        with open(self.key_path + '.pub', 'r') as file:
            pub_key = file.read().strip()

        curl_cmd = f'sudo curl -sSL https://raw.githubusercontent.com/Cybecho/JumpTunnel/refs/heads/main/setup_jump_tunnel.sh | bash -s -- "{pub_key}"'

        self.pub_key_output.setPlainText(pub_key)
        self.curl_command_output.setPlainText(curl_cmd)

        QMessageBox.information(self, "✅ Key 생성 완료", "SSH 키와 설정 명령어가 준비되었습니다.")

    def generate_config(self):
        """
        Bastion/Proxy Router/LeafNode 를 활용해
        ~/.ssh/config 파일을 생성
        """
        config = "Host *\n    StrictHostKeyChecking no\n\n"
        identity_path = os.path.expanduser("~/.ssh/master_id").replace('\\', '/')

        # 1) Bastion Host 설정
        config += f"Host {self.bastion_name.text()}\n"
        config += f"    HostName {self.bastion_ip.text()}\n"
        config += f"    Port {self.bastion_port.value()}\n"
        config += f"    User master\n"
        config += f"    IdentityFile {identity_path}\n\n"

        # 2) Proxy Routers 설정
        prev_router = self.bastion_name.text()
        for rname, rip, _ in self.proxy_routers:
            config += (f"Host {rname.text()}\n"
                       f"    HostName {rip.text()}\n"
                       f"    User master\n"
                       f"    ProxyJump {prev_router}\n"
                       f"    IdentityFile {identity_path}\n\n")
            prev_router = rname.text()

        # 3) Leaf Nodes 설정 (포트 직접 입력)
        for lname, lip, combo, port_spinbox, _ in self.leaf_nodes:
            attached_router = combo.currentText()
            config += (
                f"Host {lname.text()}\n"
                f"    HostName {lip.text()}\n"
                f"    Port {port_spinbox.value()}\n"
                f"    User master\n"
                f"    ProxyJump {attached_router}\n"
                f"    IdentityFile {identity_path}\n\n"
            )

        # 생성된 config 파일 저장
        config_path = os.path.join(self.ssh_path, "config")
        with open(config_path, "w") as f:
            f.write(config)

        # SSH 명령어 안내: bastion, router, leaf 순서대로
        commands_list = [f"ssh {self.bastion_name.text()}"]
        commands_list += [f"ssh {r[0].text()}" for r in self.proxy_routers]
        commands_list += [f"ssh {l[0].text()}" for l in self.leaf_nodes]
        commands = "\n".join(commands_list)
        self.ssh_access_output.setPlainText(commands)

        QMessageBox.information(
            self, "✅ 완료",
            f"SSH Config가 생성되었습니다: {config_path}\n터널 접속 명령어를 확인하세요!"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TunnelGUI()
    gui.resize(600, 800)
    gui.show()
    sys.exit(app.exec_())
