"""
Multi Currency Rich Address Finder v2.0

Developed by Mustafa AKBAL 
                                             ██████╗██╗  ██╗ █████╗ ██╗    ██╗██████╗ ███████╗███████╗██╗  ██╗
                                            ██╔════╝██║  ██║██╔══██╗██║    ██║██╔══██╗██╔════╝██╔════╝██║  ██║
                                            ██║     ███████║███████║██║ █╗ ██║██████╔╝█████╗  ███████╗███████║
                                            ██║     ██╔══██║██╔══██║██║███╗██║██╔══██╗██╔══╝  ╚════██║██╔══██║
                                            ╚██████╗██║  ██║██║  ██║╚███╔███╔╝██║  ██║███████╗███████║██║  ██║
                                             ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
                                            AUTHOR : Mustafa AKBAL e-mail: mstf.akbal@gmail.com 
                                            Telegram: @chawresho   Instagram: mstf.akbal
                                             ================= DONATE ADDRESSES ========================
                                            BTC p2pkh                : 191QB72rS77vP8NC1EC11wWqKtkfbm5SM8
                                            BTC p2wpkh               : bc1q2l29nc6puvuk0rn449wf6l8rm62wuxst7uvjeu
                                            BTC p2wpkh_in_p2sh       : 3AkjfoQn494K5FBdqMrnQRr4UsWji7Az62
                                            BTC p2wsh_in_p2sh        : 3Cf3J2jw4xx8DVuwHDiQuVrsRoroUgzd7M
                                            BTC p2sh                 : 3LPo8JHFdXZxvyZDQiWxiWCvPYU4oUhyHz
                                            BTC p2wsh                : bc1q47rduwq76v4fteqvxm8p9axq39nq25kurgwlyaefmyqz3nhyc8rscuhwwq
                                            ETH/BSC/AVAX/POLYGON     : 0x279f020A74BfE5Ba6a539B0f523D491A4122d18D
                                            TRX                      : TDahqcDTkM2qnfoCPfed1YhcB5Eocc2Cwe
                                            DOGE                     : DD9ViMyVjX2Cv8YnjpBZZhgSD2Uy1NQVbk
                                            DASH dash_p2pkh          : XihF1MgkPpLWY4xms7WDsUCdAELMiBXCFZ
                                            ZEC zec_p2pkh            : t1Rt1BSSzQRuWymR5wf189kckaYwkSSQAb1
                                            LTC ltc_p2pkh            : LTEMSKLgWmMydw4MBNBJHxabY77wp1zyZ6
                                            LTC ltc_p2sh             : MSbwSBhDaeRPjUq7WbWJY9TKiF4WpZbBd8
                                            LTC ltc_p2wsh            : ltc1q47rduwq76v4fteqvxm8p9axq39nq25kurgwlyaefmyqz3nhyc8rsmce759
                                            LTC ltc_p2wpkh           : ltc1q2l29nc6puvuk0rn449wf6l8rm62wuxst6qkkpv


License: MIT License  
Note: This application is the result of hard work and dedication. Please do not distribute it without permission and respect the effort put into its development.

Legal Disclaimer and Warning for Unlawful Use

THE USE OF THIS SOFTWARE FOR ANY ILLEGAL ACTIVITY IS STRICTLY PROHIBITED. THE AUTHORS AND COPYRIGHT HOLDERS OF THIS SOFTWARE DISCLAIM ANY LEGAL RESPONSIBILITY FOR UNLAWFUL USE OR ENGAGEMENT IN ILLEGAL ACTIVITIES USING THIS SOFTWARE.

USERS ARE SOLELY RESPONSIBLE FOR ENSURING THAT THEIR USE OF THIS SOFTWARE COMPLIES WITH APPLICABLE LAWS AND REGULATIONS. ANY UNLAWFUL ACTIVITIES UNDERTAKEN USING THIS SOFTWARE ARE AT THE USER'S OWN RISK.

THIS SOFTWARE IS INTENDED FOR LEGAL AND ETHICAL USE ONLY. ANY USE CONTRARY TO LOCAL, NATIONAL, OR INTERNATIONAL LAWS IS EXPRESSLY PROHIBITED. THE AUTHORS AND COPYRIGHT HOLDERS DO NOT SUPPORT OR CONDONE ILLEGAL ACTIVITIES.

BY USING THIS SOFTWARE, YOU ACKNOWLEDGE AND AGREE THAT UNLAWFUL USE MAY RESULT IN LEGAL CONSEQUENCES, INCLUDING BUT NOT LIMITED TO CRIMINAL PROSECUTION AND CIVIL LIABILITY.

IF YOU ENGAGE IN ILLEGAL ACTIVITIES, YOU DO SO AT YOUR OWN PERIL, AND THE AUTHORS AND COPYRIGHT HOLDERS SHALL NOT BE HELD LIABLE FOR ANY SUCH ACTIONS.

IT IS STRONGLY ADVISED TO USE THIS SOFTWARE RESPONSIBLY AND LEGALLY. IF YOU CANNOT COMPLY WITH THESE TERMS, YOU SHOULD IMMEDIATELY CEASE THE USE OF THIS SOFTWARE.


Disclaimer of Liability

THE USE OF THIS SOFTWARE AND ANY ACTIONS RESULTING FROM IT ARE THE SOLE RESPONSIBILITY OF THE USER. THE AUTHORS AND COPYRIGHT HOLDERS OF THIS SOFTWARE ARE NOT LIABLE FOR ANY DAMAGES, LOSSES, OR RESPONSIBILITIES ARISING OUT OF THE USE OF THIS SOFTWARE.

THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT ANY WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. NO WARRANTIES ARE PROVIDED FOR THE USE OF THIS SOFTWARE.

THE USE OF THIS SOFTWARE MAY INVOLVE RISKS OF DAMAGE TO COMPUTER SYSTEMS OR DATA. USERS SHOULD TAKE NECESSARY SECURITY PRECAUTIONS BEFORE USING THE SOFTWARE AND SHOULD BE SURE TO BACK UP THEIR DATA BEFORE CONTINUING TO USE THE SOFTWARE.

THE USE OF THE SOFTWARE IMPLIES THAT YOU UNDERSTAND AND ACCEPT THIS DISCLAIMER OF LIABILITY IN ITS ENTIRETY. IF YOU DO NOT AGREE TO THESE TERMS, YOU SHOULD NOT USE THE SOFTWARE.


"""
import os
import sqlite3
import random
import time
import logging
import json
import csv
import shutil
from multiprocessing import Process, Manager, current_process, Queue
from hdwallet import HDWallet
from hdwallet.symbols import BTC, ETH, TRX, DOGE, BCH, DASH, ZEC, LTC
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QSpinBox, QTabWidget, QMessageBox,
                             QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog, QComboBox,
                             QStatusBar, QCheckBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QTranslator
import sys
import psutil
from datetime import datetime
from typing import List, Optional

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Sabitler
CONFIG_FILE = "config.json"
DEFAULT_DB = "PubKeys.db"
DEFAULT_FOUND_FILE = "found.txt"
COIN_SYMBOLS = {
    BTC: "₿ BTC",
    ETH: "Ξ ETH",
    TRX: "TRX",
    DOGE: "Ð DOGE",
    BCH: "BCH",
    DASH: "Đ DASH",
    ZEC: "ⓩ ZEC",
    LTC: "Ł LTC",
    "ALL": "Hepsi"
}
SUPPORTED_COINS = list(COIN_SYMBOLS.keys())[:-1]  # "ALL" hariç

# Dil desteği için sözlük
TRANSLATIONS = {
    "Türkçe": {
        "window_title": "Çoklu Para Birimi Zengin Adres Bulucu v2.0",
        "start": "Başlat",
        "pause": "Duraklat",
        "resume": "Devam Et",
        "stop": "Durdur",
        "test_db": "Veritabanı Test Et",
        "total_checked": "Toplam Kontrol Edilen: {0}",
        "total_in_db": "Veritabanındaki Toplam: {0}",
        "speed": "Hız: {0:.2f} adres/dk",
        "control_tab": "Kontrol",
        "logs_tab": "Günlükler",
        "found_tab": "Bulunan Adresler",
        "settings_tab": "Ayarlar",
        "about_tab": "Hakkında",
        "select_coins": "Kontrol Edilecek Kripto Paraları Seçin:",
        "database_path": "Veritabanı Yolu:",
        "found_file_path": "Bulunan Dosya Yolu:",
        "browse": "Gözat",
        "create_new_db": "Yeni Veritabanı Oluştur",
        "optimize_db": "Veritabanını Optimize Et",
        "performance_settings": "Performans Ayarları:",
        "batch_size": "Toplu İşlem Boyutu:",
        "num_workers": "Çalışan Sayısı:",
        "auto": "Otomatik",
        "add_addresses": "Dosyadan Adres Ekle:",
        "select_file": "Dosya Seç",
        "column": "Sütun:",
        "delimiter": "Ayraç:",
        "no_delimiter": "Ayraç Yok",
        "filter_logs": "Filtre:",
        "db_management": "Veritabanı Yönetimi:",
        "backup_db": "Veritabanını Yedekle",
        "restore_db": "Veritabanını Geri Yükle",
        "update_count": "Adres Sayısını Güncelle",
        "export_found": "Bulunan Adresleri Dışa Aktar",
        "language": "Dil:",
        "test_success": "Test başarılı! Private Key ile eşleşme bulundu: {0}",
        "test_fail": "Test başarısız. Private Key ile eşleşme bulunamadı."
    },
    "English": {
        "window_title": "Multi Currency Rich Address Finder v2.0",
        "start": "Start",
        "pause": "Pause",
        "resume": "Resume",
        "stop": "Stop",
        "test_db": "Test Database",
        "total_checked": "Total Checked: {0}",
        "total_in_db": "Total in DB: {0}",
        "speed": "Speed: {0:.2f} addr/min",
        "control_tab": "Control",
        "logs_tab": "Logs",
        "found_tab": "Found Addresses",
        "settings_tab": "Settings",
        "about_tab": "About",
        "select_coins": "Select Cryptocurrencies to Check:",
        "database_path": "Database Path:",
        "found_file_path": "Found File Path:",
        "browse": "Browse",
        "create_new_db": "Create New DB",
        "optimize_db": "Optimize Database",
        "performance_settings": "Performance Settings:",
        "batch_size": "Batch Size:",
        "num_workers": "Number of Workers:",
        "auto": "Auto",
        "add_addresses": "Add Addresses from File:",
        "select_file": "Select File",
        "column": "Column:",
        "delimiter": "Delimiter:",
        "no_delimiter": "No Delimiter",
        "filter_logs": "Filter:",
        "db_management": "Database Management:",
        "backup_db": "Backup Database",
        "restore_db": "Restore Database",
        "update_count": "Update Address Count",
        "export_found": "Export Found Addresses",
        "language": "Language:",
        "test_success": "Test successful! Match found with Private Key: {0}",
        "test_fail": "Test failed. No match found with Private Key."
    }
}

ABOUT_TEXT = {
    "Türkçe": """
----------------------------------------
        Çoklu Para Birimi Zengin Adres Bulucu v2.0
----------------------------------------

**Mustafa AKBAL tarafından oluşturuldu**

BTC, ETH, TRX, DOGE, BCH, DASH, ZEC ve LTC için kripto para adreslerini oluşturup kontrol eden basit, güçlü bir araç.

----------------------------------------
Geliştirici Bilgisi
----------------------------------------
Ad: Mustafa AKBAL  
E-posta: mstf.akbal@gmail.com  
Telegram: @chawresho  
Instagram: mstf.akbal  

Blockchain tutkunu olarak, bunu kripto hayranları ve araştırmacılar için yaptım. Fikirleriniz mi var? Bana ulaşın!

----------------------------------------
Özellikler
----------------------------------------
- Çoklu coin desteği (çeşitli adres türleri)  
- Hızlı, çok iş parçacıklı kontrol  
- Veritabanlarını kolayca yönetin ve dışa aktarın  

----------------------------------------
Beni Destekleyin
----------------------------------------
Bağışlar güncellemeleri teşvik eder!  
BTC: 191QB72rS77vP8NC1EC11wWqKtkfbm5SM8  
ETH: 0x279f020A74BfE5Ba6a539B0f523D491A4122d18D  
TRX: TDahqcDTkM2qnfoCPfed1YhcB5Eocc2Cwe  
DOGE: DD9ViMyVjX2Cv8YnjpBZZhgSD2Uy1NQVbk  
DASH: XihF1MgkPpLWY4xms7WDsUCdAELMiBXCFZ  
ZEC: t1Rt1BSSzQRuWymR5wf189kckaYwkSSQAb1  
LTC: LTEMSKLgWmMydw4MBNBJHxabY77wp1zyZ6  
*(E-posta ile daha fazla adres isteyebilirsiniz)*  
Desteğiniz için teşekkürler!

----------------------------------------
Lisans
----------------------------------------
MIT Lisansı – Kullanımı ve düzenlemesi ücretsiz. Telif hakkını koruyun ve izinsiz paylaşmayın.

----------------------------------------
Yasal Uyarı
----------------------------------------
**Yasadışı kullanım yasaktır.** Kötüye kullanımdan sorumlu değilim.  
- Sadece yasal kullanım için (örneğin, araştırma, test).  
- Tüm yasalara uyun – sorumluluk size aittir!

----------------------------------------
Sorumluluk
----------------------------------------
"OLDUĞU GİBİ" sağlanır – garanti yoktur. Risk size aittir.
""",
    "English": """
----------------------------------------
        Multi Currency Rich Address Finder v2.0
----------------------------------------

**Created by Mustafa AKBAL**

A simple, powerful tool to generate and check cryptocurrency addresses for BTC, ETH, TRX, DOGE, BCH, DASH, ZEC, and LTC.

----------------------------------------
Developer Info
----------------------------------------
Name: Mustafa AKBAL  
Email: mstf.akbal@gmail.com  
Telegram: @chawresho  
Instagram: mstf.akbal  

Passionate about blockchain, I built this for crypto fans and researchers. Got ideas? Contact me!

----------------------------------------
Features
----------------------------------------
- Multi-coin support (various address types)  
- Fast, multithreaded checking  
- Manage and export databases easily  

----------------------------------------
Support Me
----------------------------------------
Donations fuel updates!  
BTC: 191QB72rS77vP8NC1EC11wWqKtkfbm5SM8  
ETH: 0x279f020A74BfE5Ba6a539B0f523D491A4122d18D  
TRX: TDahqcDTkM2qnfoCPfed1YhcB5Eocc2Cwe  
DOGE: DD9ViMyVjX2Cv8YnjpBZZhgSD2Uy1NQVbk  
DASH: XihF1MgkPpLWY4xms7WDsUCdAELMiBXCFZ  
ZEC: t1Rt1BSSzQRuWymR5wf189kckaYwkSSQAb1  
LTC: LTEMSKLgWmMydw4MBNBJHxabY77wp1zyZ6  
*(More addresses on request via email)*  
Thanks for your support!

----------------------------------------
License
----------------------------------------
MIT License – Free to use/modify. Keep the copyright and don’t share without permission.

----------------------------------------
Legal Notice
----------------------------------------
**No illegal use allowed.** I’m not liable for misuse.  
- For legal use only (e.g., research, testing).  
- Follow all laws – your responsibility!

----------------------------------------
Liability
----------------------------------------
Provided "AS IS" – no warranties. Use at your own risk.
"""
}

class QueueHandler(logging.Handler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        self.queue.put(self.format(record))

class WalletGenerator:
    def __init__(self, selected_coins: List[str]):
        self.selected_coins = selected_coins if "ALL" not in selected_coins else SUPPORTED_COINS

    @staticmethod
    def generate_private_key() -> str:
        return "".join(random.choice("0123456789abcdef") for _ in range(64))

    def generate_addresses(self, private_key: str) -> Optional[List[str]]:
        try:
            addresses = []
            for symbol in self.selected_coins:
                wallet = HDWallet(symbol)
                wallet.from_private_key(private_key)
                if symbol == BTC:
                    addresses.extend([
                        wallet.p2pkh_address(), wallet.p2wpkh_address(),
                        wallet.p2wpkh_in_p2sh_address(), wallet.p2wsh_in_p2sh_address(),
                        wallet.p2sh_address(), wallet.p2wsh_address()
                    ])
                elif symbol == LTC:
                    addresses.extend([
                        wallet.p2pkh_address(), wallet.p2sh_address(),
                        wallet.p2wsh_address(), wallet.p2wpkh_address()
                    ])
                elif symbol in [BCH, DASH, ZEC]:
                    addresses.extend([wallet.p2pkh_address(), wallet.p2sh_address()])
                elif symbol in [ETH, TRX, DOGE]:
                    addresses.append(wallet.p2pkh_address())
            return [addr for addr in addresses if addr]
        except Exception as e:
            logging.error(f"Cüzdan oluşturulurken hata: {e}")
            return None

class DatabaseManager:
    @staticmethod
    def check_addresses(db_filename: str, addresses: List[str]) -> set:
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' for _ in addresses)
                cursor.execute(f"SELECT PubKeys FROM DataBase WHERE PubKeys IN ({placeholders})", addresses)
                return {row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logging.error(f"Adres kontrolünde hata: {e}")
            return set()

    @staticmethod
    def get_total_addresses(db_filename: str) -> int:
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM DataBase")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Toplam adres sayısında hata: {e}")
            return -1

    @staticmethod
    def add_addresses_from_file(db_filename: str, file_path: str, column_index: int, delimiter: str) -> int:
        added_count = 0
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS DataBase (PubKeys TEXT UNIQUE)")
                with open(file_path, "r", encoding="utf-8") as f:
                    if delimiter == "None":  # Ayraç yoksa satır satır oku
                        for line in f:
                            address = line.strip()
                            if address and len(address) > 20:
                                cursor.execute("INSERT OR IGNORE INTO DataBase (PubKeys) VALUES (?)", (address,))
                                added_count += conn.total_changes
                    else:  # Ayraç varsa CSV olarak oku
                        reader = csv.reader(f, delimiter=delimiter)
                        for row in reader:
                            if len(row) > column_index:
                                address = row[column_index].strip()
                                if address and len(address) > 20:
                                    cursor.execute("INSERT OR IGNORE INTO DataBase (PubKeys) VALUES (?)", (address,))
                                    added_count += conn.total_changes
                conn.commit()
            return added_count
        except Exception as e:
            logging.error(f"Dosyadan adres eklenirken hata: {e}")
            return -1

    @staticmethod
    def create_new_database(db_filename: str) -> bool:
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS DataBase (PubKeys TEXT UNIQUE)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubkeys ON DataBase (PubKeys)")
                conn.commit()
            logging.info(f"Yeni veritabanı oluşturuldu: {db_filename}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Yeni veritabanı oluşturulurken hata: {e}")
            return False

    @staticmethod
    def add_test_addresses(db_filename: str):
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS DataBase (PubKeys TEXT UNIQUE)")
                test_addresses = ["1Q1pE5vPGEEMqRcVRMbtBK842Y6Pzo6nK9", "1MsHWS1BnwMc3tLE8G35UXsS58fKipzB7a"]
                for addr in test_addresses:
                    cursor.execute("INSERT OR IGNORE INTO DataBase (PubKeys) VALUES (?)", (addr,))
                conn.commit()
            logging.info("Test adresleri veritabanına eklendi.")
        except sqlite3.Error as e:
            logging.error(f"Test adresleri eklenirken hata: {e}")

    @staticmethod
    def optimize_database(db_filename: str) -> bool:
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("REINDEX idx_pubkeys")
                cursor.execute("DELETE FROM DataBase WHERE PubKeys IN (SELECT PubKeys FROM DataBase GROUP BY PubKeys HAVING COUNT(*) > 1)")
                conn.commit()
            logging.info(f"Veritabanı optimize edildi: {db_filename}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanı optimizasyonu sırasında hata: {e}")
            return False

def worker(db_filename: str, found_file: str, total_checked, lock, batch_size: int,
          log_queue: Queue, running_flag, found_queue: Queue, selected_coins: List[str]):
    logging.info(f"{current_process().name}: Worker başlatıldı.")
    wallet_gen = WalletGenerator(selected_coins)
    worker_name = current_process().name

    while True:
        with lock:
            if not running_flag.value:
                time.sleep(1)
                continue

        cpu_usage = psutil.cpu_percent()
        dynamic_batch = max(50, min(batch_size, int(1000 / (cpu_usage + 1))))

        addresses_to_check = []
        private_keys = []
        for _ in range(dynamic_batch):
            private_key = wallet_gen.generate_private_key()
            addresses = wallet_gen.generate_addresses(private_key)
            if addresses:
                addresses_to_check.extend(addresses)
                private_keys.extend([private_key] * len(addresses))

        if not addresses_to_check:
            continue

        with lock:
            total_checked.value += len(addresses_to_check)
            found_addresses = DatabaseManager.check_addresses(db_filename, addresses_to_check)
            for addr in found_addresses:
                index = addresses_to_check.index(addr)
                private_key = private_keys[index]
                with open(found_file, "a", encoding="utf-8") as f:
                    f.write(f"Eşleşme bulundu! Private Key: {private_key}, Adres: {addr}\n")
                found_queue.put((private_key, addr))
                log_queue.put(f"{worker_name} eşleşme buldu: {addr}")
                # Worker burada durmuyor, devam ediyor

class LogThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, log_queue: Queue):
        super().__init__()
        self.log_queue = log_queue

    def run(self):
        while True:
            try:
                log_message = self.log_queue.get(timeout=1)
                self.log_signal.emit(log_message)
            except:
                time.sleep(0.1)

class DbCheckThread(QThread):
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, db_filename: str):
        super().__init__()
        self.db_filename = db_filename

    def run(self):
        total = DatabaseManager.get_total_addresses(self.db_filename)
        if total == -1:
            self.error.emit("Veritabanı adres sayısı alınamadı. Dosya yolunu kontrol edin.")
        else:
            self.finished.emit(total)

class WalletCheckerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = Manager()
        self.total_checked = self.manager.Value('i', 0)
        self.lock = self.manager.Lock()
        self.running_flag = self.manager.Value('b', False)
        self.log_queue = self.manager.Queue()
        self.found_queue = self.manager.Queue()
        self.processes: List[Process] = []

        self.db_manager = DatabaseManager()
        self.total_addresses = 0
        self.start_time = None
        self.db_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_DB)
        self.found_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_FOUND_FILE)
        self.selected_coins = SUPPORTED_COINS
        self.coin_checkboxes = {}
        self.current_language = "Türkçe"

        self.init_ui()
        self.load_config()
        self.setup_logging()
        self.setup_timer()
        self.retranslate_ui()

    def init_ui(self):
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        tabs = QTabWidget()
        layout.addWidget(tabs)

        control_tab = self.create_control_tab()
        tabs.addTab(control_tab, "Control")

        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "Logs")

        found_tab = self.create_found_tab()
        tabs.addTab(found_tab, "Found Addresses")

        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Settings")

        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "About")

    def create_control_tab(self) -> QWidget:
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start", clicked=self.start_workers)
        self.pause_btn = QPushButton("Pause", clicked=self.pause_workers, enabled=False)
        self.stop_btn = QPushButton("Stop", clicked=self.stop_workers, enabled=False)
        self.test_db_btn = QPushButton("Test Database", clicked=self.test_database)
        for btn in (self.start_btn, self.pause_btn, self.stop_btn, self.test_db_btn):
            btn_layout.addWidget(btn)
        control_layout.addLayout(btn_layout)

        self.stats_label = QLabel("", alignment=Qt.AlignCenter)
        control_layout.addWidget(self.stats_label)

        coin_selection_layout = QVBoxLayout()
        self.select_coins_label = QLabel("Select Cryptocurrencies to Check:")
        coin_selection_layout.addWidget(self.select_coins_label)
        coins_inner_layout = QHBoxLayout()
        self.coin_checkboxes["ALL"] = QCheckBox(COIN_SYMBOLS["ALL"], checked=True, stateChanged=self.on_all_coins_changed)
        coins_inner_layout.addWidget(self.coin_checkboxes["ALL"])
        for coin in SUPPORTED_COINS:
            checkbox = QCheckBox(COIN_SYMBOLS[coin], checked=True, stateChanged=lambda state, c=coin: self.on_coin_changed(c, state))
            self.coin_checkboxes[coin] = checkbox
            coins_inner_layout.addWidget(checkbox)
        coin_selection_layout.addLayout(coins_inner_layout)
        control_layout.addLayout(coin_selection_layout)

        return control_tab

    def create_logs_tab(self) -> QWidget:
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel("Filtre:" if self.current_language == "Türkçe" else "Filter:")
        filter_layout.addWidget(self.filter_label)
        self.filter_input = QLineEdit()
        self.filter_input.textChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.filter_input)
        logs_layout.addLayout(filter_layout)
        
        self.logs_text = QTextEdit(readOnly=True)
        logs_layout.addWidget(self.logs_text)
        return logs_tab

    def create_found_tab(self) -> QWidget:
        found_tab = QWidget()
        found_layout = QVBoxLayout(found_tab)
        self.found_table = QTableWidget(0, 2)
        self.found_table.setHorizontalHeaderLabels(["Private Key", "Address"])
        self.found_table.horizontalHeader().setStretchLastSection(True)
        found_layout.addWidget(self.found_table)
        self.export_btn = QPushButton("Export Found Addresses", clicked=self.export_found_addresses)
        found_layout.addWidget(self.export_btn)
        return found_tab

    def create_settings_tab(self) -> QWidget:
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        db_layout = QHBoxLayout()
        self.db_path_label = QLabel("Database Path:")
        db_layout.addWidget(self.db_path_label)
        self.db_path_input = QLineEdit(text=self.db_filename)
        db_layout.addWidget(self.db_path_input)
        self.browse_db_btn = QPushButton("Browse", clicked=self.browse_db)
        db_layout.addWidget(self.browse_db_btn)
        self.create_db_btn = QPushButton("Create New DB", clicked=self.create_new_db)
        db_layout.addWidget(self.create_db_btn)
        settings_layout.addLayout(db_layout)

        found_file_layout = QHBoxLayout()
        self.found_file_label = QLabel("Found File Path:")
        found_file_layout.addWidget(self.found_file_label)
        self.found_file_input = QLineEdit(text=self.found_file)
        found_file_layout.addWidget(self.found_file_input)
        self.browse_found_btn = QPushButton("Browse", clicked=self.browse_found_file)
        found_file_layout.addWidget(self.browse_found_btn)
        settings_layout.addLayout(found_file_layout)

        perf_layout = QVBoxLayout()
        self.perf_label = QLabel("Performance Settings:")
        perf_layout.addWidget(self.perf_label)
        batch_layout = QHBoxLayout()
        self.batch_size_label = QLabel("Batch Size:")
        batch_layout.addWidget(self.batch_size_label)
        self.batch_size_spin = QSpinBox(minimum=1, maximum=1000, value=100)
        batch_layout.addWidget(self.batch_size_spin)
        perf_layout.addLayout(batch_layout)

        workers_layout = QHBoxLayout()
        self.workers_label = QLabel("Number of Workers:")
        workers_layout.addWidget(self.workers_label)
        self.workers_spin = QSpinBox(minimum=1, maximum=os.cpu_count() * 2 or 8, value=os.cpu_count() or 4)
        self.auto_workers_check = QCheckBox("Auto", checked=True, stateChanged=self.toggle_workers_spin)
        workers_layout.addWidget(self.workers_spin)
        workers_layout.addWidget(self.auto_workers_check)
        perf_layout.addLayout(workers_layout)
        settings_layout.addLayout(perf_layout)

        add_file_layout = QVBoxLayout()
        self.add_file_label = QLabel("Add Addresses from File:")
        add_file_layout.addWidget(self.add_file_label)
        file_select_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("Select File", clicked=self.add_addresses_from_file)
        file_select_layout.addWidget(self.add_file_btn)
        self.column_label = QLabel("Column:")
        file_select_layout.addWidget(self.column_label)
        self.column_spin = QSpinBox(maximum=9, value=0)
        file_select_layout.addWidget(self.column_spin)
        self.delimiter_label = QLabel("Delimiter:")
        file_select_layout.addWidget(self.delimiter_label)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["Ayraç Yok" if self.current_language == "Türkçe" else "No Delimiter", ", (Comma)", "\t (Tab)", "  (Space)"])
        file_select_layout.addWidget(self.delimiter_combo)
        add_file_layout.addLayout(file_select_layout)
        settings_layout.addLayout(add_file_layout)

        db_mgmt_layout = QVBoxLayout()
        self.db_mgmt_label = QLabel("Database Management:")
        db_mgmt_layout.addWidget(self.db_mgmt_label)
        backup_layout = QHBoxLayout()
        self.backup_db_btn = QPushButton("Backup Database", clicked=self.backup_database)
        self.restore_db_btn = QPushButton("Restore Database", clicked=self.restore_database)
        backup_layout.addWidget(self.backup_db_btn)
        backup_layout.addWidget(self.restore_db_btn)
        db_mgmt_layout.addLayout(backup_layout)
        settings_layout.addLayout(db_mgmt_layout)

        self.update_count_btn = QPushButton("Update Address Count", clicked=self.update_address_count)
        settings_layout.addWidget(self.update_count_btn)

        self.optimize_db_btn = QPushButton("Veritabanını Optimize Et" if self.current_language == "Türkçe" else "Optimize Database", clicked=self.optimize_database)
        settings_layout.addWidget(self.optimize_db_btn)

        lang_layout = QHBoxLayout()
        self.lang_label = QLabel("Language:")
        lang_layout.addWidget(self.lang_label)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English"])
        self.language_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.language_combo)
        settings_layout.addLayout(lang_layout)

        return settings_tab

    def create_about_tab(self) -> QWidget:
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        self.about_text = QTextEdit(readOnly=True)
        self.about_text.setText(ABOUT_TEXT[self.current_language])
        about_layout.addWidget(self.about_text)
        return about_tab

    def setup_logging(self):
        self.log_thread = LogThread(self.log_queue)
        self.log_thread.log_signal.connect(self.append_log)
        self.log_thread.start()

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.total_addresses = config.get("total_addresses", 0)
                self.db_filename = config.get("db_filename", self.db_filename)
                self.found_file = config.get("found_file", self.found_file)
                self.selected_coins = config.get("selected_coins", SUPPORTED_COINS)
                self.current_language = config.get("language", "Türkçe")
                self.db_path_input.setText(self.db_filename)
                self.found_file_input.setText(self.found_file)
                for coin, checkbox in self.coin_checkboxes.items():
                    if coin == "ALL":
                        checkbox.setChecked("ALL" in self.selected_coins or len(self.selected_coins) == len(SUPPORTED_COINS))
                    else:
                        checkbox.setChecked(coin in self.selected_coins)
                self.language_combo.setCurrentText(self.current_language)
        except (FileNotFoundError, json.JSONDecodeError):
            self.total_addresses = 0
            self.selected_coins = SUPPORTED_COINS
            self.current_language = "Türkçe"
        self.update_stats()

    def save_config(self):
        config = {
            "total_addresses": self.total_addresses,
            "db_filename": self.db_filename,
            "found_file": self.found_file,
            "selected_coins": self.selected_coins if "ALL" not in self.selected_coins else SUPPORTED_COINS,
            "language": self.current_language
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def retranslate_ui(self):
        tr = TRANSLATIONS[self.current_language]
        self.setWindowTitle(tr["window_title"])
        self.start_btn.setText(tr["start"])
        self.pause_btn.setText(tr["pause"])
        self.stop_btn.setText(tr["stop"])
        self.test_db_btn.setText(tr["test_db"])
        self.select_coins_label.setText(tr["select_coins"])
        self.db_path_label.setText(tr["database_path"])
        self.found_file_label.setText(tr["found_file_path"])
        self.browse_db_btn.setText(tr["browse"])
        self.browse_found_btn.setText(tr["browse"])
        self.create_db_btn.setText(tr["create_new_db"])
        self.optimize_db_btn.setText(tr["optimize_db"])
        self.perf_label.setText(tr["performance_settings"])
        self.batch_size_label.setText(tr["batch_size"])
        self.workers_label.setText(tr["num_workers"])
        self.auto_workers_check.setText(tr["auto"])
        self.add_file_label.setText(tr["add_addresses"])
        self.add_file_btn.setText(tr["select_file"])
        self.column_label.setText(tr["column"])
        self.delimiter_label.setText(tr["delimiter"])
        self.filter_label.setText(tr["filter_logs"])
        self.delimiter_combo.clear()
        self.delimiter_combo.addItems([tr["no_delimiter"], ", (Comma)", "\t (Tab)", "  (Space)"])
        self.db_mgmt_label.setText(tr["db_management"])
        self.backup_db_btn.setText(tr["backup_db"])
        self.restore_db_btn.setText(tr["restore_db"])
        self.update_count_btn.setText(tr["update_count"])
        self.export_btn.setText(tr["export_found"])
        self.lang_label.setText(tr["language"])
        self.about_text.setText(ABOUT_TEXT[self.current_language])
        self.centralWidget().layout().itemAt(0).widget().setTabText(0, tr["control_tab"])
        self.centralWidget().layout().itemAt(0).widget().setTabText(1, tr["logs_tab"])
        self.centralWidget().layout().itemAt(0).widget().setTabText(2, tr["found_tab"])
        self.centralWidget().layout().itemAt(0).widget().setTabText(3, tr["settings_tab"])
        self.centralWidget().layout().itemAt(0).widget().setTabText(4, tr["about_tab"])
        self.update_stats()

    def test_database(self):
        if not os.path.exists(self.db_filename):
            self.create_new_db()
        
        DatabaseManager.add_test_addresses(self.db_filename)
        test_private_key = "1111111111111111111111111111111111111111111111111111111111111111"
        wallet_gen = WalletGenerator([BTC])
        addresses = wallet_gen.generate_addresses(test_private_key)
        
        if not addresses:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Test private key ile adres oluşturulamadı!" if self.current_language == "Türkçe" else "Could not generate addresses with test private key!")
            return

        found_addresses = DatabaseManager.check_addresses(self.db_filename, addresses)
        tr = TRANSLATIONS[self.current_language]
        
        if found_addresses:
            for addr in found_addresses:
                self.append_log(f"Test adresi bulundu: {addr}")
                QMessageBox.information(self, "Test Sonucu" if self.current_language == "Türkçe" else "Test Result",
                                       tr["test_success"].format(addr))
        else:
            self.append_log("Test adresi bulunamadı.")
            QMessageBox.warning(self, "Test Sonucu" if self.current_language == "Türkçe" else "Test Result",
                               tr["test_fail"])

    def change_language(self, lang: str):
        self.current_language = lang
        self.retranslate_ui()
        self.save_config()

    def start_workers(self):
        if not self.running_flag.value:
            if not self.selected_coins:
                QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                                   "Lütfen en az bir kripto para birimi seçin!" if self.current_language == "Türkçe" else "Please select at least one cryptocurrency!")
                return
            if not os.path.exists(self.db_filename):
                reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                            "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?" if self.current_language == "Türkçe" else "Database not found. Would you like to create a new one?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not self.create_new_db():
                        return
                else:
                    return
            self.db_filename = self.db_path_input.text()
            num_workers = os.cpu_count() if self.auto_workers_check.isChecked() else self.workers_spin.value()
            for _ in range(num_workers):
                p = Process(target=worker, args=(self.db_filename, self.found_file, self.total_checked,
                                                self.lock, self.batch_size_spin.value(), self.log_queue, self.running_flag,
                                                self.found_queue, self.selected_coins))
                p.start()
                self.processes.append(p)
            self.running_flag.value = True
            self.start_time = datetime.now()
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.append_log("Cüzdan kontrol süreçleri başlatıldı." if self.current_language == "Türkçe" else "Started wallet checking processes.")

    def pause_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if self.running_flag.value:
            self.running_flag.value = False
            self.pause_btn.setText(tr["resume"])
            self.append_log("Cüzdan kontrol süreçleri duraklatıldı." if self.current_language == "Türkçe" else "Paused wallet checking processes.")
        else:
            self.running_flag.value = True
            self.pause_btn.setText(tr["pause"])
            self.append_log("Cüzdan kontrol süreçleri devam ettirildi." if self.current_language == "Türkçe" else "Resumed wallet checking processes.")

    def stop_workers(self):
        if self.processes:
            for p in self.processes:
                p.terminate()
            for p in self.processes:
                p.join()
            self.processes.clear()
            self.running_flag.value = False
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setText(TRANSLATIONS[self.current_language]["pause"])
            self.stop_btn.setEnabled(False)
            self.append_log("Cüzdan kontrol süreçleri durduruldu." if self.current_language == "Türkçe" else "Stopped wallet checking processes.")
            self.start_time = None

    def update_stats(self):
        tr = TRANSLATIONS[self.current_language]
        if self.running_flag.value and self.start_time:
            elapsed_time_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            speed = self.total_checked.value / max(elapsed_time_minutes, 0.0167)
            status_msg = f"Çalışıyor... ({len(self.processes)} worker aktif)" if self.current_language == "Türkçe" else f"Running... ({len(self.processes)} workers active)"
        else:
            speed = 0
            status_msg = "Durduruldu" if self.current_language == "Türkçe" else "Stopped"
        
        self.stats_label.setText(f"{tr['total_checked'].format(self.total_checked.value)}\n"
                                 f"{tr['total_in_db'].format(self.total_addresses)}\n"
                                 f"{tr['speed'].format(speed)}")
        self.status_bar.showMessage(status_msg)

        while not self.found_queue.empty():
            private_key, addr = self.found_queue.get()
            row = self.found_table.rowCount()
            self.found_table.insertRow(row)
            self.found_table.setItem(row, 0, QTableWidgetItem(private_key))
            self.found_table.setItem(row, 1, QTableWidgetItem(addr))

    def append_log(self, message: str):
        self.logs_text.append(message)

    def filter_logs(self, text):
        full_text = self.logs_text.toPlainText()
        filtered_lines = [line for line in full_text.split('\n') if text.lower() in line.lower()]
        self.logs_text.setText('\n'.join(filtered_lines))

    def browse_db(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Veritabanı Dosyası Seç" if self.current_language == "Türkçe" else "Select Database File", "", "SQLite Files (*.db);;All Files (*)")
        if file_name:
            self.db_path_input.setText(file_name)
            self.db_filename = file_name
            self.save_config()

    def browse_found_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Bulunan Dosyayı Seç" if self.current_language == "Türkçe" else "Select Found File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.found_file_input.setText(file_name)
            self.found_file = file_name
            self.save_config()

    def create_new_db(self) -> bool:
        self.db_filename = self.db_path_input.text()
        if not self.db_filename:
            QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                               "Lütfen önce bir veritabanı yolu belirtin!" if self.current_language == "Türkçe" else "Please specify a database path first!")
            return False
        if os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Dosya Var" if self.current_language == "Türkçe" else "File Exists",
                                        "Bu dosyada zaten bir veritabanı var. Üzerine yazılsın mı?" if self.current_language == "Türkçe" else "A database already exists in this file. Overwrite it?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return False
        if DatabaseManager.create_new_database(self.db_filename):
            self.append_log(f"Yeni veritabanı oluşturuldu: {self.db_filename}")
            self.status_bar.showMessage("Yeni veritabanı oluşturuldu" if self.current_language == "Türkçe" else "New database created")
            self.total_addresses = 0
            self.save_config()
            return True
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Yeni veritabanı oluşturulamadı!" if self.current_language == "Türkçe" else "Failed to create new database!")
            return False

    def add_addresses_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Adres Dosyası Seç" if self.current_language == "Türkçe" else "Select Address File", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return
        
        self.db_filename = self.db_path_input.text()
        if not os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                        "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?" if self.current_language == "Türkçe" else "Database not found. Would you like to create a new one?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not self.create_new_db():
                    return
            else:
                return
        
        column_index = self.column_spin.value()
        delimiter_map = {
            ", (Comma)": ",",
            "\t (Tab)": "\t",
            "  (Space)": " ",
            TRANSLATIONS[self.current_language]["no_delimiter"]: "None"
        }
        delimiter = delimiter_map[self.delimiter_combo.currentText()]
        self.status_bar.showMessage("Dosyadan adresler ekleniyor..." if self.current_language == "Türkçe" else "Adding addresses from file...")

        added_count = self.db_manager.add_addresses_from_file(self.db_filename, file_path, column_index, delimiter)
        if added_count >= 0:
            self.append_log(f"{file_path} dosyasından {added_count} adres eklendi." if self.current_language == "Türkçe" else f"Added {added_count} addresses from {file_path}")
            self.status_bar.showMessage(f"{added_count} adres eklendi" if self.current_language == "Türkçe" else f"Added {added_count} addresses")
            self.update_address_count()
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Dosyadan adresler eklenemedi!" if self.current_language == "Türkçe" else "Failed to add addresses from file.")
            self.status_bar.showMessage("Adres ekleme başarısız" if self.current_language == "Türkçe" else "Failed to add addresses")

    def update_address_count(self):
        self.db_filename = self.db_path_input.text()
        if not os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                        "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?" if self.current_language == "Türkçe" else "Database not found. Would you like to create a new one?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not self.create_new_db():
                    return
            else:
                return
        self.status_bar.showMessage("Veritabanı kontrol ediliyor..." if self.current_language == "Türkçe" else "Checking database...")
        self.loading_dialog = QMessageBox(self, windowTitle="Veritabanı Kontrolü" if self.current_language == "Türkçe" else "Checking Database",
                                        text="Veritabanı kontrol ediliyor..." if self.current_language == "Türkçe" else "Checking database...",
                                        standardButtons=QMessageBox.NoButton)
        self.loading_dialog.show()

        self.db_check_thread = DbCheckThread(self.db_filename)
        self.db_check_thread.finished.connect(self.on_update_address_count_finished)
        self.db_check_thread.error.connect(self.on_db_check_error)
        self.db_check_thread.start()

    def on_update_address_count_finished(self, total: int):
        self.total_addresses = total
        self.loading_dialog.accept()
        self.save_config()
        self.update_stats()
        self.status_bar.showMessage(f"Adres sayısı güncellendi: {total}" if self.current_language == "Türkçe" else f"Address count updated: {total}")

    def on_db_check_error(self, error_message: str):
        self.loading_dialog.accept()
        QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error", error_message)
        self.status_bar.showMessage("Veritabanı kontrolü başarısız" if self.current_language == "Türkçe" else "Database check failed")

    def optimize_database(self):
        if DatabaseManager.optimize_database(self.db_filename):
            self.append_log("Veritabanı başarıyla optimize edildi." if self.current_language == "Türkçe" else "Database optimized successfully.")
            self.update_address_count()
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Veritabanı optimizasyonu başarısız!" if self.current_language == "Türkçe" else "Database optimization failed!")

    def backup_database(self):
        if not os.path.exists(self.db_filename):
            QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                               "Yedeklenecek bir veritabanı yok!" if self.current_language == "Türkçe" else "No database to backup!")
            return
        backup_path, _ = QFileDialog.getSaveFileName(self, "Yedeği Kaydet" if self.current_language == "Türkçe" else "Save Backup", "", "SQLite Files (*.db);;All Files (*)")
        if backup_path:
            try:
                shutil.copy(self.db_filename, backup_path)
                self.append_log(f"Veritabanı {backup_path} yoluna yedeklendi." if self.current_language == "Türkçe" else f"Database backed up to {backup_path}")
                self.status_bar.showMessage(f"{backup_path} yoluna yedeklendi" if self.current_language == "Türkçe" else f"Backup saved to {backup_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Veritabanı yedeklenemedi: {str(e)}" if self.current_language == "Türkçe" else f"Failed to backup database: {str(e)}")

    def restore_database(self):
        restore_path, _ = QFileDialog.getOpenFileName(self, "Yedek Dosyası Seç" if self.current_language == "Türkçe" else "Select Backup File", "", "SQLite Files (*.db);;All Files (*)")
        if restore_path:
            try:
                shutil.copy(restore_path, self.db_filename)
                self.update_address_count()
                self.append_log(f"Veritabanı {restore_path} yolundan geri yüklendi." if self.current_language == "Türkçe" else f"Database restored from {restore_path}")
                self.status_bar.showMessage(f"{restore_path} yolundan geri yüklendi" if self.current_language == "Türkçe" else f"Restored from {restore_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Veritabanı geri yüklenemedi: {str(e)}" if self.current_language == "Türkçe" else f"Failed to restore database: {str(e)}")

    def export_found_addresses(self):
        if self.found_table.rowCount() == 0:
            QMessageBox.information(self, "Dışa Aktar" if self.current_language == "Türkçe" else "Export",
                                   "Dışa aktarılacak adres yok." if self.current_language == "Türkçe" else "No addresses to export.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Bulunan Adresleri Kaydet" if self.current_language == "Türkçe" else "Save Found Addresses", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    for row in range(self.found_table.rowCount()):
                        private_key = self.found_table.item(row, 0).text()
                        addr = self.found_table.item(row, 1).text()
                        f.write(f"Private Key: {private_key}, Address: {addr}\n")
                self.status_bar.showMessage(f"{file_name} yoluna dışa aktarıldı" if self.current_language == "Türkçe" else f"Exported to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Dışa aktarma başarısız: {str(e)}" if self.current_language == "Türkçe" else f"Failed to export: {str(e)}")

    def toggle_workers_spin(self, state: int):
        self.workers_spin.setEnabled(not state)

    def on_all_coins_changed(self, state: int):
        if state == Qt.Checked:
            self.selected_coins = SUPPORTED_COINS
            for coin in SUPPORTED_COINS:
                self.coin_checkboxes[coin].setChecked(True)
        else:
            self.selected_coins = []
            for coin in SUPPORTED_COINS:
                self.coin_checkboxes[coin].setChecked(False)
        self.append_log(f"Seçilen kripto para birimleri: {[COIN_SYMBOLS[coin] for coin in self.selected_coins]}")
        self.save_config()

    def on_coin_changed(self, coin: str, state: int):
        if state == Qt.Checked:
            if coin not in self.selected_coins:
                self.selected_coins.append(coin)
        else:
            if coin in self.selected_coins:
                self.selected_coins.remove(coin)
        
        all_checked = len(self.selected_coins) == len(SUPPORTED_COINS)
        self.coin_checkboxes["ALL"].blockSignals(True)
        self.coin_checkboxes["ALL"].setChecked(all_checked)
        self.coin_checkboxes["ALL"].blockSignals(False)

        self.append_log(f"Seçilen kripto para birimleri: {[COIN_SYMBOLS[coin] for coin in self.selected_coins]}")
        self.save_config()

    def closeEvent(self, event):
        if self.processes:
            reply = QMessageBox.question(self, "Çıkış" if self.current_language == "Türkçe" else "Exit",
                                        "Süreçler çalışıyor. Durdurup çıkmak ister misiniz?" if self.current_language == "Türkçe" else "Processes are running. Stop and exit?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_workers()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    global app
    app = QApplication(sys.argv)
    window = WalletCheckerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
