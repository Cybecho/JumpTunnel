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

        title = QLabel("🤸🕳️ Jump Tunnel ! ! ! 🕳️🏃")
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
        key_btn = QPushButton("🔑 Generate master_id Key")
        key_btn.clicked.connect(self.generate_ssh_key)
        layout.addWidget(key_btn)

        # 별도 Public Key 출력
        self.pub_key_output = QTextEdit()
        self.pub_key_output.setReadOnly(True)
        layout.addWidget(QLabel("🔑 생성된 Public Key:"))
        layout.addWidget(self.pub_key_output)

        # curl 명령어 출력
        self.curl_command_output = QTextEdit()
        self.curl_command_output.setReadOnly(True)
        layout.addWidget(QLabel("👇 해당 명령어를 각 터널이 적용될 VM에 입력해주세요!"))
        layout.addWidget(self.curl_command_output)

        # Config 생성 버튼
        gen_btn = QPushButton("✅ Generate & Save SSH Config")
        gen_btn.clicked.connect(self.generate_config)
        layout.addWidget(gen_btn)

        # SSH 접속 명령어 출력 블록
        self.ssh_access_output = QTextEdit()
        self.ssh_access_output.setReadOnly(True)
        layout.addWidget(QLabel("🚪 SSH Config 생성 후, 호스트측 CLI에서 아래 명령어로 바로 터널에 접근할 수 있습니다!:"))
        layout.addWidget(self.ssh_access_output)

        self.setLayout(layout)

    def add_router(self):
        name, ip = QLineEdit(), QLineEdit()
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Router 이름"))
        h_layout.addWidget(name)
        h_layout.addWidget(QLabel("Router IP"))
        h_layout.addWidget(ip)
        
        delete_btn = QPushButton("🗑️ 삭제")
        delete_btn.clicked.connect(lambda: self.remove_router(h_layout, (name, ip, delete_btn)))
        h_layout.addWidget(delete_btn)

        self.router_layout.addLayout(h_layout)
        self.proxy_routers.append((name, ip, delete_btn))

    def remove_router(self, layout, router_data):
        self.proxy_routers.remove(router_data)
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        layout.deleteLater()

    def add_leafnode(self):
        name, ip, combo = QLineEdit(), QLineEdit(), QComboBox()
        combo.addItems([r[0].text() for r in self.proxy_routers])
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Leaf 이름"))
        h_layout.addWidget(name)
        h_layout.addWidget(QLabel("Leaf IP"))
        h_layout.addWidget(ip)
        h_layout.addWidget(QLabel("Attached Router"))
        h_layout.addWidget(combo)

        delete_btn = QPushButton("🗑️ 삭제")
        delete_btn.clicked.connect(lambda: self.remove_leafnode(h_layout, (name, ip, combo, delete_btn)))
        h_layout.addWidget(delete_btn)

        self.leaf_layout.addLayout(h_layout)
        self.leaf_nodes.append((name, ip, combo, delete_btn))

    def remove_leafnode(self, layout, leaf_data):
        self.leaf_nodes.remove(leaf_data)
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        layout.deleteLater()

    def generate_ssh_key(self):
        # 기존 키 삭제 후 키 재생성
        for ext in ['', '.pub']:
            path = self.key_path + ext
            if os.path.exists(path):
                os.remove(path)

        subprocess.run(['ssh-keygen', '-t', 'ed25519', '-f', self.key_path, '-C', 'master-key', '-N', ''], shell=True, check=True)

        with open(self.key_path + '.pub', 'r') as file:
            pub_key = file.read().strip()

        curl_cmd = f'sudo curl -sSL https://raw.githubusercontent.com/Cybecho/JumpTunnel/refs/heads/main/setup_jump_tunnel.sh | bash -s -- "{pub_key}"'

        self.pub_key_output.setPlainText(pub_key)
        self.curl_command_output.setPlainText(curl_cmd)

        QMessageBox.information(self, "✅ Key 생성 완료", "SSH 키와 설정 명령어가 준비되었습니다.")

    def generate_config(self):
        config = "Host *\n    StrictHostKeyChecking no\n\n"
        identity_path = os.path.expanduser("~/.ssh/master_id").replace('\\', '/')

        config += f"Host {self.bastion_name.text()}\n"
        config += f"    HostName {self.bastion_ip.text()}\n"
        config += f"    Port {self.bastion_port.value()}\n"
        config += f"    User master\n"
        config += f"    IdentityFile {identity_path}\n\n"

        prev_router = self.bastion_name.text()
        for rname, rip, _ in self.proxy_routers:
            config += (f"Host {rname.text()}\n    HostName {rip.text()}\n    User master\n"
                       f"    ProxyJump {prev_router}\n    IdentityFile {identity_path}\n\n")
            prev_router = rname.text()

        for lname, lip, combo, _ in self.leaf_nodes:
            attached_router = combo.currentText()
            config += (f"Host {lname.text()}\n    HostName {lip.text()}\n    User master\n"
                       f"    ProxyJump {attached_router}\n    IdentityFile {identity_path}\n\n")

        config_path = os.path.join(self.ssh_path, "config")
        with open(config_path, "w") as f:
            f.write(config)

        commands = "\n".join([f"ssh {h[0].text()}" for h in [(self.bastion_name,)] + self.proxy_routers + self.leaf_nodes])
        self.ssh_access_output.setPlainText(commands)

        QMessageBox.information(self, "✅ 완료", f"SSH Config가 생성되었습니다: {config_path}\n터널 접속 명령어를 확인하세요!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TunnelGUI()
    gui.resize(600, 800)
    gui.show()
    sys.exit(app.exec_())
