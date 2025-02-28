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
                             QStatusBar, QCheckBox, QProgressBar)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import sys
import psutil
from datetime import datetime
from typing import List, Optional


# Uygulama dizini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DEFAULT_DB = os.path.join(BASE_DIR, "PubKeys.db")
DEFAULT_FOUND_FILE = os.path.join(BASE_DIR, "found.txt")
COIN_SYMBOLS = {
    BTC: "₿ BTC",
    ETH: "Ξ ETH",
    TRX: "TRX",
    DOGE: "Ð DOGE",
    BCH: "BCH",
    DASH: "Đ DASH",
    ZEC: "ⓩ ZEC",
    LTC: "Ł LTC",
    "ALL": "ALL"
}
SUPPORTED_COINS = list(COIN_SYMBOLS.keys())[:-1]  # "ALL" hariç

# Çözülmemiş Puzzle Adresleri
UNSOLVED_PUZZLES = {
    68: "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    76: "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    77: "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    78: "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    79: "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
    81: "15qsCm78whspNQFydGJQk5rexzxTQopnHZ",
    82: "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",
    83: "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2",
    84: "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",
    86: "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",
    87: "1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq",
    88: "16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",
    89: "19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt",
    91: "1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74",
    92: "1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",
    93: "17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad",
    94: "1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",
    96: "15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",
    97: "18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8",
    98: "1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",
    99: "1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL",
    101: "1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n",
    102: "1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",
    103: "1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf",
    104: "1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",
    106: "18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",
    107: "15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc",
    108: "1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",
    109: "1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL",
    111: "1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3",
    112: "18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",
    113: "1NeGn21dUDDeqFQ63LUFC9uDcVdGjqkxKyh",
    114: "174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy",
    116: "1MnJ6hdhvK37VLmqcdEwqC3iFxyWH2PHUV",
    117: "1KNRfGWw7Q9Rmwsc6NT5zsdvEb9M2Wkj5Z",
    118: "1PJZPzvGX19a7twf5HyD2VvNiPdprrfDx",
    119: "1GuBBhf61rnvRe4K8zu8vdQB3kHzwFqSy7",
    121: "1GDSuiThEV64c166LUFC9uDcVdGjqkxKyh",
    122: "1Me3ASYt5JCTAK2XaC32RMeH34PdprrfDx",
    123: "1CdufMQL892A69KXgv6UNBD17ywWqYpKut",
    124: "1BkkGsX9ZM6iwL3zbqs7HWBV7SvosR6m8N",
    126: "1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz",
    127: "1G6EFyBRU86sThN3SSt3GrHu1sA7w7nzi4",
    128: "1MZ2L1gFrCtkkn6DnTT2e4PFUTHw9gNwaj",
    129: "1Hz3uv3nNZzBVMXLGadCucgjiCs5W9vaGz",
    131: "16zRPnT8znwq42q7XeMkZUhb1bKqgRogyy",
    132: "1KrU4dHE5WrW8rhWDsTRjR21r8t3dsrS3R",
    133: "17uDfp5r4n441xkgLFmhNoSW1KWp6xVLD",
    134: "13A3JrvXmvg5w9XGvyyR4JEJqiLz8ZySY3",
    135: "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v",
    136: "1UDHPdovvR985NrWSkdWQDEQ1xuRiTALq",
    137: "15nf31J46iLuK1ZkTnqHo7WgN5cARFK3RA",
    138: "1Ab4vzG6wEQBDNQM1B2bvUz4fqXXdFk2WT",
    139: "1Fz63c775VV9fNyj25d9Xfw3YHE6sKCxbt",
    140: "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo",
    141: "1CD91Vm97mLQvXhrnoMChhJx4TP9MaQkJo",
    142: "15MnK2jXPqTMURX4xC3h4mAZxyCcaWWEDD",
    143: "13N66gCzWWHEZBxhVxG18P8wyjEWF9Yoi1",
    144: "1NevxKDYuDcCh1ZMMi6ftmWwGrZKC6j7Ux",
    145: "19GpszRNUej5yYqxXoLnbZWKew3KdVLkXg",
    146: "1M7ipcdYHey2Y5RZM34MBbpugghmjaV89P",
    147: "18aNhurEAJsw6BAgtANpexk5ob1aGTwSeL",
    148: "1FwZXt6EpRT7Fkndzv6K4b4DFoT4trbMrV",
    149: "1CXvTzR6qv8wJ7eprzUKeWxyGcHwDYP1i2",
    150: "1MUJSJYtGPVGkBCTqGspnxyHahpt5Te8jy",
    151: "13Q84TNNvgcL3HJiqQPvyBb9m4hxjS3jkV",
    152: "1LuUHyrQr8PKSvbcY1v1PiuGuqFjWpDumN",
    153: "18192XpzzdDi2K11QVHR7td2HcPS6Qs5vg",
    154: "1NgVmsCCJaKLzGyKLFJfVequnFW9ZvnMLN",
    155: "1AoeP37TmHdFh8uN72fu9AqgtLrUwcv2wJ",
    156: "1FTpAbQa4h8trvhQXjXnmNhqdiGBd1oraE",
    157: "14JHoRAdmJg3XR4RjMDh6Wed6ft6hzbQe9",
    158: "19z6waranEf8CcP8FqNgdwUe1QRxvUNKBG",
    159: "14u4nA5sugaswb6SZgn5av2vuChdMnD9E5",
    160: "1NBC8uXJy1GiJ6drkiZa1WuKn51ps7EPTv"
}

# Dil desteği
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
        "puzzle_tab": "Puzzle",
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
        "test_fail": "Test başarısız. Private Key ile eşleşme bulunamadı.",
        "test_address_found": "Test adresi bulundu: {0}",
        "test_address_not_found": "Test adresi bulunamadı.",
        "test_result_saved": "Test sonucu {0} dosyasına kaydedildi.",
        "new_db_created": "Yeni veritabanı oluşturuldu: {0}",
        "addresses_added": "{0} dosyasından {1} adres eklendi.",
        "processes_started": "Cüzdan kontrol süreçleri başlatıldı.",
        "processes_paused": "Cüzdan kontrol süreçleri duraklatıldı.",
        "processes_resumed": "Cüzdan kontrol süreçleri devam ettirildi.",
        "processes_stopped": "Cüzdan kontrol süreçleri durduruldu.",
        "db_optimized": "Veritabanı başarıyla optimize edildi.",
        "db_backup": "Veritabanı {0} yoluna yedeklendi.",
        "db_restored": "Veritabanı {0} yolundan geri yüklendi.",
        "selected_coins": "Seçilen kripto para birimleri: {0}",
        "puzzle_select": "Puzzle Seçimi:",
        "puzzle_address": "Puzzle Adresi:",
        "puzzle_range": "Private Key Aralığı (Hex):",
        "puzzle_status": "Durum:",
        "puzzle_found": "Bulunan Private Keyler:",
        "progress": "İlerleme:",
        "current_key": "Geçerli Anahtar:",
        "elapsed_time": "Geçen Süre: {0}",
        "remaining_time": "Tahmini Kalan Süre: {0}",
        "invalid_puzzle": "Geçersiz puzzle numarası! Çözülmemiş bir puzzle seçin."
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
        "puzzle_tab": "Puzzle",
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
        "test_fail": "Test failed. No match found with Private Key.",
        "test_address_found": "Test address found: {0}",
        "test_address_not_found": "Test address not found.",
        "test_result_saved": "Test result saved to {0}.",
        "new_db_created": "New database created: {0}",
        "addresses_added": "Added {1} addresses from {0}.",
        "processes_started": "Started wallet checking processes.",
        "processes_paused": "Paused wallet checking processes.",
        "processes_resumed": "Resumed wallet checking processes.",
        "processes_stopped": "Stopped wallet checking processes.",
        "db_optimized": "Database optimized successfully.",
        "db_backup": "Database backed up to {0}.",
        "db_restored": "Database restored from {0}.",
        "selected_coins": "Selected cryptocurrencies: {0}",
        "puzzle_select": "Puzzle Selection:",
        "puzzle_address": "Puzzle Address:",
        "puzzle_range": "Private Key Range (Hex):",
        "puzzle_status": "Status:",
        "puzzle_found": "Found Private Keys:",
        "progress": "Progress:",
        "current_key": "Current Key:",
        "elapsed_time": "Elapsed Time: {0}",
        "remaining_time": "Estimated Remaining Time: {0}",
        "invalid_puzzle": "Invalid puzzle number! Select an unsolved puzzle."
    }
}

ABOUT_TEXT = {
    "Türkçe": """
----------------------------------------
        Çoklu Para Birimi Zengin Adres Bulucu v2.0
----------------------------------------

**Mustafa AKBAL tarafından oluşturuldu**

BTC, ETH, TRX, DOGE, BCH, DASH, ZEC ve LTC için adres tarama ve Bitcoin Puzzle desteği ile.

----------------------------------------
Geliştirici Bilgisi
----------------------------------------
Ad: Mustafa AKBAL  
E-posta: mstf.akbal@gmail.com  
Telegram: @chawresho  
Instagram: mstf.akbal  

Blockchain tutkunu bir разработчик. Fikirleriniz için bana ulaşın!

----------------------------------------
Özellikler
----------------------------------------
- Çoklu coin desteği  
- Çözülmemiş Bitcoin Puzzle tarama (ayrı sekmede)  
- Hızlı, çok iş parçacıklı kontrol  
""",
    "English": """
----------------------------------------
        Multi Currency Rich Address Finder v2.0
----------------------------------------

**Created by Mustafa AKBAL**

Address scanning for BTC, ETH, TRX, DOGE, BCH, DASH, ZEC, LTC with unsolved Bitcoin Puzzle support.

----------------------------------------
Developer Info
----------------------------------------
Name: Mustafa AKBAL  
Email: mstf.akbal@gmail.com  
Telegram: @chawresho  
Instagram: mstf.akbal  

Blockchain enthusiast. Contact me for ideas!

----------------------------------------
Features
----------------------------------------
- Multi-coin support  
- Unsolved Bitcoin Puzzle scanning (in a separate tab)  
- Fast, multithreaded checking  
"""
}

class QueueHandler(logging.Handler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        self.queue.put(self.format(record))

class WalletGenerator:
    def __init__(self, selected_coins: List[str], puzzle_mode: bool = False, puzzle_number: int = None):
        self.selected_coins = selected_coins if "ALL" not in selected_coins else SUPPORTED_COINS
        self.puzzle_mode = puzzle_mode
        self.puzzle_number = puzzle_number
        if puzzle_mode and puzzle_number:
            self.puzzle_start = 2 ** (puzzle_number - 1)
            self.puzzle_end = (2 ** puzzle_number) - 1
            self.checked_keys = set()  # Rastgele anahtarların tekrarını önlemek için
            self.target_address = self.get_puzzle_address()

    def get_puzzle_address(self) -> str:
        if not self.puzzle_mode or not self.puzzle_number:
            return None
        return UNSOLVED_PUZZLES.get(self.puzzle_number, None)

    def get_puzzle_range(self) -> str:
        if not self.puzzle_mode or not self.puzzle_number:
            return "N/A"
        start_hex = hex(self.puzzle_start)[2:].zfill(64)
        end_hex = hex(self.puzzle_end)[2:].zfill(64)
        return f"{start_hex} - {end_hex}"

    def get_total_keys(self) -> int:
        if not self.puzzle_mode or not self.puzzle_number:
            return 0
        return self.puzzle_end - self.puzzle_start + 1

    @staticmethod
    def generate_private_key() -> str:
        return "".join(random.choice("0123456789abcdef") for _ in range(64))

    def generate_next_puzzle_key(self) -> str:
        if len(self.checked_keys) >= self.get_total_keys():
            return None  # Tüm anahtarlar kontrol edildiğinde dur
        while True:
            random_key = random.randint(self.puzzle_start, self.puzzle_end)
            if random_key not in self.checked_keys:
                self.checked_keys.add(random_key)
                return hex(random_key)[2:].zfill(64)

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
                    if delimiter == "None":
                        for line in f:
                            address = line.strip()
                            if address and len(address) > 20:
                                cursor.execute("INSERT OR IGNORE INTO DataBase (PubKeys) VALUES (?)", (address,))
                                added_count += conn.total_changes
                    else:
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
          log_queue: Queue, running_flag, found_queue: Queue, selected_coins: List[str],
          puzzle_mode: bool = False, puzzle_number: int = None):
    logging.info(f"{current_process().name}: Worker başlatıldı.")
    wallet_gen = WalletGenerator(selected_coins, puzzle_mode, puzzle_number)
    worker_name = current_process().name
    target_address = wallet_gen.target_address if puzzle_mode else None

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
            if puzzle_mode:
                private_key = wallet_gen.generate_next_puzzle_key()
                if not private_key:
                    log_queue.put(f"{worker_name}: Puzzle {puzzle_number} aralığı tamamlandı.")
                    return
            else:
                private_key = wallet_gen.generate_private_key()
            
            addresses = wallet_gen.generate_addresses(private_key)
            if addresses:
                if puzzle_mode:
                    if target_address in addresses:
                        addresses_to_check = [target_address]
                        private_keys = [private_key]
                        break
                else:
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

def puzzle_worker(db_filename: str, found_file: str, total_checked, lock, batch_size: int,
                  log_queue: Queue, running_flag, found_queue: Queue, puzzle_number: int,
                  current_key_queue: Queue):
    logging.info(f"{current_process().name}: Puzzle Worker başlatıldı.")
    wallet_gen = WalletGenerator([BTC], True, puzzle_number)
    worker_name = current_process().name
    target_address = wallet_gen.target_address

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
            private_key = wallet_gen.generate_next_puzzle_key()
            if not private_key:
                log_queue.put(f"{worker_name}: Puzzle {puzzle_number} aralığı tamamlandı.")
                return
            
            current_key_queue.put(private_key)  # Geçerli anahtarı kuyruğa ekle
            addresses = wallet_gen.generate_addresses(private_key)
            if addresses and target_address in addresses:
                addresses_to_check = [target_address]
                private_keys = [private_key]
                break

        if not addresses_to_check:
            with lock:
                total_checked.value += dynamic_batch
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
        self.puzzle_total_checked = self.manager.Value('i', 0)
        self.lock = self.manager.Lock()
        self.running_flag = self.manager.Value('b', False)
        self.puzzle_running_flag = self.manager.Value('b', False)
        self.puzzle_paused = self.manager.Value('b', False)
        self.log_queue = self.manager.Queue()
        self.found_queue = self.manager.Queue()
        self.puzzle_found_queue = self.manager.Queue()
        self.current_key_queue = self.manager.Queue()  # Geçerli anahtar için kuyruk
        self.processes: List[Process] = []
        self.puzzle_processes: List[Process] = []

        self.db_manager = DatabaseManager()
        self.total_addresses = 0
        self.start_time = None
        self.puzzle_start_time = None
        self.db_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_DB)
        self.found_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_FOUND_FILE)
        self.selected_coins = SUPPORTED_COINS
        self.coin_checkboxes = {}
        self.current_language = "Türkçe"
        self.puzzle_number = None

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

        puzzle_tab = self.create_puzzle_tab()
        tabs.addTab(puzzle_tab, "Puzzle")

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

        self.optimize_db_btn = QPushButton("Optimize Database", clicked=self.optimize_database)
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

    def create_puzzle_tab(self) -> QWidget:
        puzzle_tab = QWidget()
        puzzle_layout = QVBoxLayout(puzzle_tab)

        # Puzzle Seçimi
        select_layout = QHBoxLayout()
        self.puzzle_select_label = QLabel("Puzzle Seçimi:")
        self.puzzle_number_combo = QComboBox()
        self.puzzle_number_combo.addItems([str(num) for num in UNSOLVED_PUZZLES.keys()])
        self.puzzle_number_combo.currentTextChanged.connect(self.update_puzzle_info)
        select_layout.addWidget(self.puzzle_select_label)
        select_layout.addWidget(self.puzzle_number_combo)
        puzzle_layout.addLayout(select_layout)

        # Puzzle Adresi
        address_layout = QHBoxLayout()
        self.puzzle_address_label = QLabel("Puzzle Adresi:")
        self.puzzle_address_display = QLineEdit(readOnly=True)
        address_layout.addWidget(self.puzzle_address_label)
        address_layout.addWidget(self.puzzle_address_display)
        puzzle_layout.addLayout(address_layout)

        # Private Key Aralığı
        range_layout = QVBoxLayout()
        self.puzzle_range_label = QLabel("Private Key Aralığı (Hex):")
        self.puzzle_range_display = QTextEdit(readOnly=True)
        self.puzzle_range_display.setMaximumHeight(50)
        range_layout.addWidget(self.puzzle_range_label)
        range_layout.addWidget(self.puzzle_range_display)
        puzzle_layout.addLayout(range_layout)

        # Kontrol Düğmeleri
        btn_layout = QHBoxLayout()
        self.puzzle_start_btn = QPushButton("Başlat", clicked=self.start_puzzle_workers)
        self.puzzle_pause_btn = QPushButton("Duraklat", clicked=self.pause_puzzle_workers, enabled=False)
        self.puzzle_stop_btn = QPushButton("Durdur", clicked=self.stop_puzzle_workers, enabled=False)
        btn_layout.addWidget(self.puzzle_start_btn)
        btn_layout.addWidget(self.puzzle_pause_btn)
        btn_layout.addWidget(self.puzzle_stop_btn)
        puzzle_layout.addLayout(btn_layout)

        # Durum
        status_layout = QHBoxLayout()
        self.puzzle_status_label = QLabel("Durum:")
        self.puzzle_status_display = QLabel("Durduruldu" if self.current_language == "Türkçe" else "Stopped")
        status_layout.addWidget(self.puzzle_status_label)
        status_layout.addWidget(self.puzzle_status_display)
        puzzle_layout.addLayout(status_layout)

        # İlerleme Çubuğu
        progress_layout = QHBoxLayout()
        self.puzzle_progress_label = QLabel("İlerleme:")
        self.puzzle_progress_bar = QProgressBar()
        self.puzzle_progress_bar.setMaximum(100)
        self.puzzle_progress_bar.setValue(0)
        progress_layout.addWidget(self.puzzle_progress_label)
        progress_layout.addWidget(self.puzzle_progress_bar)
        puzzle_layout.addLayout(progress_layout)

        # Geçerli Anahtar
        current_key_layout = QHBoxLayout()
        self.puzzle_current_key_label = QLabel("Geçerli Anahtar:")
        self.puzzle_current_key_display = QLineEdit(readOnly=True)
        current_key_layout.addWidget(self.puzzle_current_key_label)
        current_key_layout.addWidget(self.puzzle_current_key_display)
        puzzle_layout.addLayout(current_key_layout)

        # İstatistikler
        stats_layout = QVBoxLayout()
        self.puzzle_stats_label = QLabel("", alignment=Qt.AlignCenter)
        self.puzzle_time_elapsed_label = QLabel("", alignment=Qt.AlignCenter)
        self.puzzle_time_remaining_label = QLabel("", alignment=Qt.AlignCenter)
        stats_layout.addWidget(self.puzzle_stats_label)
        stats_layout.addWidget(self.puzzle_time_elapsed_label)
        stats_layout.addWidget(self.puzzle_time_remaining_label)
        puzzle_layout.addLayout(stats_layout)

        # Bulunan Private Keyler
        found_layout = QVBoxLayout()
        self.puzzle_found_label = QLabel("Bulunan Private Keyler:")
        self.puzzle_found_table = QTableWidget(0, 2)
        self.puzzle_found_table.setHorizontalHeaderLabels(["Private Key", "Address"])
        self.puzzle_found_table.horizontalHeader().setStretchLastSection(True)
        found_layout.addWidget(self.puzzle_found_label)
        found_layout.addWidget(self.puzzle_found_table)
        puzzle_layout.addLayout(found_layout)

        return puzzle_tab

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
        self.update_puzzle_info()

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
        self.puzzle_select_label.setText(tr["puzzle_select"])
        self.puzzle_address_label.setText(tr["puzzle_address"])
        self.puzzle_range_label.setText(tr["puzzle_range"])
        self.puzzle_status_label.setText(tr["puzzle_status"])
        self.puzzle_found_label.setText(tr["puzzle_found"])
        self.puzzle_progress_label.setText(tr["progress"])
        self.puzzle_current_key_label.setText(tr["current_key"])
        self.puzzle_start_btn.setText(tr["start"])
        self.puzzle_pause_btn.setText(tr["pause"])
        self.puzzle_stop_btn.setText(tr["stop"])
        self.about_text.setText(ABOUT_TEXT[self.current_language])
        tabs = self.centralWidget().layout().itemAt(0).widget()
        tabs.setTabText(0, tr["control_tab"])
        tabs.setTabText(1, tr["logs_tab"])
        tabs.setTabText(2, tr["found_tab"])
        tabs.setTabText(3, tr["settings_tab"])
        tabs.setTabText(4, tr["puzzle_tab"])
        tabs.setTabText(5, tr["about_tab"])
        self.update_stats()

    def test_database(self):
        tr = TRANSLATIONS[self.current_language]
        if not os.path.exists(self.db_filename):
            self.create_new_db()
        
        DatabaseManager.add_test_addresses(self.db_filename)
        test_private_key = "1111111111111111111111111111111111111111111111111111111111111111"
        wallet_gen = WalletGenerator([BTC])
        addresses = wallet_gen.generate_addresses(test_private_key)
        
        if not addresses:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Test private key ile adres oluşturulamadı!")
            return

        found_addresses = DatabaseManager.check_addresses(self.db_filename, addresses)
        
        if found_addresses:
            for addr in found_addresses:
                self.append_log(tr["test_address_found"].format(addr))
                with open(self.found_file, "a", encoding="utf-8") as f:
                    f.write(f"Private Key: {test_private_key}, Adres: {addr}\n")
                self.append_log(tr["test_result_saved"].format(self.found_file))
                QMessageBox.information(self, "Test Sonucu" if self.current_language == "Türkçe" else "Test Result",
                                       tr["test_success"].format(addr))
        else:
            self.append_log(tr["test_address_not_found"])
            QMessageBox.warning(self, "Test Sonucu" if self.current_language == "Türkçe" else "Test Result",
                               tr["test_fail"])

    def change_language(self, lang: str):
        self.current_language = lang
        self.retranslate_ui()
        self.save_config()

    def update_puzzle_info(self):
        puzzle_number = int(self.puzzle_number_combo.currentText())
        wallet_gen = WalletGenerator([BTC], True, puzzle_number)
        self.puzzle_address_display.setText(wallet_gen.target_address or "Bilinmeyen Puzzle")
        self.puzzle_range_display.setText(wallet_gen.get_puzzle_range())
        self.puzzle_progress_bar.setValue(0)
        self.puzzle_current_key_display.setText("")

    def start_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if not self.running_flag.value:
            if not self.selected_coins:
                QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                                   "Lütfen en az bir kripto para birimi seçin!")
                return
            if not os.path.exists(self.db_filename):
                reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                            "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?",
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
            self.append_log(tr["processes_started"])

    def pause_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if self.running_flag.value:
            self.running_flag.value = False
            self.pause_btn.setText(tr["resume"])
            self.append_log(tr["processes_paused"])
        else:
            self.running_flag.value = True
            self.pause_btn.setText(tr["pause"])
            self.append_log(tr["processes_resumed"])

    def stop_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if self.processes:
            for p in self.processes:
                p.terminate()
            for p in self.processes:
                p.join()
            self.processes.clear()
            self.running_flag.value = False
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setText(tr["pause"])
            self.stop_btn.setEnabled(False)
            self.append_log(tr["processes_stopped"])
            self.start_time = None

    def start_puzzle_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if not self.puzzle_running_flag.value:
            if not os.path.exists(self.db_filename):
                reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                            "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not self.create_new_db():
                        return
                else:
                    return
            
            self.puzzle_number = int(self.puzzle_number_combo.currentText())
            if self.puzzle_number not in UNSOLVED_PUZZLES:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    tr["invalid_puzzle"])
                return
            
            num_workers = os.cpu_count() or 4
            for _ in range(num_workers):
                p = Process(target=puzzle_worker, args=(self.db_filename, self.found_file, self.puzzle_total_checked,
                                                       self.lock, self.batch_size_spin.value(), self.log_queue,
                                                       self.puzzle_running_flag, self.puzzle_found_queue, self.puzzle_number,
                                                       self.current_key_queue))
                p.start()
                self.puzzle_processes.append(p)
            self.puzzle_running_flag.value = True
            self.puzzle_paused.value = False
            self.puzzle_start_time = datetime.now()
            self.puzzle_start_btn.setEnabled(False)
            self.puzzle_pause_btn.setEnabled(True)
            self.puzzle_stop_btn.setEnabled(True)
            self.puzzle_status_display.setText("Çalışıyor..." if self.current_language == "Türkçe" else "Running...")
            self.append_log(f"Puzzle {self.puzzle_number} tarama süreçleri başlatıldı.")

    def pause_puzzle_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if self.puzzle_running_flag.value:
            if not self.puzzle_paused.value:
                self.puzzle_running_flag.value = False
                self.puzzle_paused.value = True
                self.puzzle_pause_btn.setText(tr["resume"])
                self.puzzle_status_display.setText("Duraklatıldı" if self.current_language == "Türkçe" else "Paused")
                self.append_log(f"Puzzle {self.puzzle_number} tarama süreçleri duraklatıldı.")
            else:
                self.puzzle_running_flag.value = True
                self.puzzle_paused.value = False
                self.puzzle_pause_btn.setText(tr["pause"])
                self.puzzle_status_display.setText("Çalışıyor..." if self.current_language == "Türkçe" else "Running...")
                self.append_log(f"Puzzle {self.puzzle_number} tarama süreçleri devam ettirildi.")

    def stop_puzzle_workers(self):
        tr = TRANSLATIONS[self.current_language]
        if self.puzzle_processes:
            for p in self.puzzle_processes:
                p.terminate()
            for p in self.puzzle_processes:
                p.join()
            self.puzzle_processes.clear()
            self.puzzle_running_flag.value = False
            self.puzzle_paused.value = False
            self.puzzle_start_btn.setEnabled(True)
            self.puzzle_pause_btn.setEnabled(False)
            self.puzzle_pause_btn.setText(tr["pause"])
            self.puzzle_stop_btn.setEnabled(False)
            self.puzzle_status_display.setText("Durduruldu" if self.current_language == "Türkçe" else "Stopped")
            self.append_log(f"Puzzle {self.puzzle_number} tarama süreçleri durduruldu.")
            self.puzzle_start_time = None
            self.puzzle_progress_bar.setValue(0)

    def update_stats(self):
        tr = TRANSLATIONS[self.current_language]
        
        # Genel tarama istatistikleri
        if self.running_flag.value and self.start_time:
            elapsed_time_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            speed = self.total_checked.value / max(elapsed_time_minutes, 0.0167)
            status_msg = f"Çalışıyor... ({len(self.processes)} worker aktif)"
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

        # Puzzle tarama istatistikleri
        if self.puzzle_running_flag.value and self.puzzle_start_time and not self.puzzle_paused.value:
            wallet_gen = WalletGenerator([BTC], True, self.puzzle_number)
            total_keys = wallet_gen.get_total_keys()
            elapsed_time_seconds = (datetime.now() - self.puzzle_start_time).total_seconds()
            elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time_seconds))
            puzzle_speed = self.puzzle_total_checked.value / max(elapsed_time_seconds / 60, 0.0167)
            progress = (self.puzzle_total_checked.value / total_keys) * 100 if total_keys > 0 else 0
            remaining_keys = total_keys - self.puzzle_total_checked.value
            remaining_time_seconds = remaining_keys / (puzzle_speed * 60) if puzzle_speed > 0 else 0
            remaining_time_str = time.strftime("%H:%M:%S", time.gmtime(remaining_time_seconds))
            puzzle_status_msg = f"Çalışıyor... ({len(self.puzzle_processes)} worker aktif)"
            self.puzzle_progress_bar.setValue(int(progress))
            self.puzzle_stats_label.setText(f"{tr['total_checked'].format(self.puzzle_total_checked.value)}\n"
                                            f"{tr['speed'].format(puzzle_speed)}")
            self.puzzle_time_elapsed_label.setText(tr["elapsed_time"].format(elapsed_time_str))
            self.puzzle_time_remaining_label.setText(tr["remaining_time"].format(remaining_time_str))
        else:
            puzzle_speed = 0
            puzzle_status_msg = ("Duraklatıldı" if self.current_language == "Türkçe" else "Paused") if self.puzzle_paused.value else ("Durduruldu" if self.current_language == "Türkçe" else "Stopped")
            self.puzzle_stats_label.setText(f"{tr['total_checked'].format(self.puzzle_total_checked.value)}\n"
                                            f"{tr['speed'].format(puzzle_speed)}")
            if not self.puzzle_running_flag.value:
                self.puzzle_time_elapsed_label.setText("")
                self.puzzle_time_remaining_label.setText("")

        self.puzzle_status_display.setText(puzzle_status_msg)

        while not self.puzzle_found_queue.empty():
            private_key, addr = self.puzzle_found_queue.get()
            row = self.puzzle_found_table.rowCount()
            self.puzzle_found_table.insertRow(row)
            self.puzzle_found_table.setItem(row, 0, QTableWidgetItem(private_key))
            self.puzzle_found_table.setItem(row, 1, QTableWidgetItem(addr))

        # Geçerli anahtarı güncelle
        while not self.current_key_queue.empty():
            current_key = self.current_key_queue.get()
            self.puzzle_current_key_display.setText(current_key)

    def append_log(self, message: str):
        self.logs_text.append(message)

    def filter_logs(self, text):
        full_text = self.logs_text.toPlainText()
        filtered_lines = [line for line in full_text.split('\n') if text.lower() in line.lower()]
        self.logs_text.setText('\n'.join(filtered_lines))

    def browse_db(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Veritabanı Dosyası Seç", "", "SQLite Files (*.db);;All Files (*)")
        if file_name:
            self.db_path_input.setText(file_name)
            self.db_filename = file_name
            self.save_config()

    def browse_found_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Bulunan Dosyayı Seç", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.found_file_input.setText(file_name)
            self.found_file = file_name
            self.save_config()

    def create_new_db(self) -> bool:
        tr = TRANSLATIONS[self.current_language]
        self.db_filename = self.db_path_input.text()
        if not self.db_filename:
            QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                               "Lütfen önce bir veritabanı yolu belirtin!")
            return False
        if os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Dosya Var" if self.current_language == "Türkçe" else "File Exists",
                                        "Bu dosyada zaten bir veritabanı var. Üzerine yazılsın mı?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return False
        if DatabaseManager.create_new_database(self.db_filename):
            self.append_log(tr["new_db_created"].format(self.db_filename))
            self.status_bar.showMessage(tr["new_db_created"].format(self.db_filename))
            self.total_addresses = 0
            self.save_config()
            return True
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Yeni veritabanı oluşturulamadı!")
            return False

    def add_addresses_from_file(self):
        tr = TRANSLATIONS[self.current_language]
        file_path, _ = QFileDialog.getOpenFileName(self, "Adres Dosyası Seç", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return
        
        self.db_filename = self.db_path_input.text()
        if not os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                        "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?",
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
        self.status_bar.showMessage("Dosyadan adresler ekleniyor...")

        added_count = self.db_manager.add_addresses_from_file(self.db_filename, file_path, column_index, delimiter)
        if added_count >= 0:
            self.append_log(tr["addresses_added"].format(file_path, added_count))
            self.status_bar.showMessage(f"{added_count} adres eklendi")
            self.update_address_count()
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Dosyadan adresler eklenemedi!")
            self.status_bar.showMessage("Adres ekleme başarısız")

    def update_address_count(self):
        tr = TRANSLATIONS[self.current_language]
        self.db_filename = self.db_path_input.text()
        if not os.path.exists(self.db_filename):
            reply = QMessageBox.question(self, "Veritabanı Bulunamadı" if self.current_language == "Türkçe" else "Database Not Found",
                                        "Veritabanı bulunamadı. Yeni bir veritabanı oluşturmak ister misiniz?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not self.create_new_db():
                    return
            else:
                return
        self.status_bar.showMessage("Veritabanı kontrol ediliyor...")
        self.loading_dialog = QMessageBox(self)
        self.loading_dialog.setWindowTitle("Veritabanı Kontrolü")
        self.loading_dialog.setText("Veritabanı kontrol ediliyor...")
        self.loading_dialog.setStandardButtons(QMessageBox.NoButton)
        self.loading_dialog.show()

        self.db_check_thread = DbCheckThread(self.db_filename)
        self.db_check_thread.finished.connect(self.on_update_address_count_finished)
        self.db_check_thread.error.connect(self.on_db_check_error)
        self.db_check_thread.start()

    def on_update_address_count_finished(self, total: int):
        tr = TRANSLATIONS[self.current_language]
        self.total_addresses = total
        self.loading_dialog.accept()
        self.save_config()
        self.update_stats()
        self.status_bar.showMessage(f"Adres sayısı güncellendi: {total}")

    def on_db_check_error(self, error_message: str):
        self.loading_dialog.accept()
        QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error", error_message)
        self.status_bar.showMessage("Veritabanı kontrolü başarısız")

    def optimize_database(self):
        tr = TRANSLATIONS[self.current_language]
        if DatabaseManager.optimize_database(self.db_filename):
            self.append_log(tr["db_optimized"])
            self.update_address_count()
        else:
            QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                "Veritabanı optimizasyonu başarısız!")

    def backup_database(self):
        tr = TRANSLATIONS[self.current_language]
        if not os.path.exists(self.db_filename):
            QMessageBox.warning(self, "Uyarı" if self.current_language == "Türkçe" else "Warning",
                               "Yedeklenecek bir veritabanı yok!")
            return
        backup_path, _ = QFileDialog.getSaveFileName(self, "Yedeği Kaydet", "", "SQLite Files (*.db);;All Files (*)")
        if backup_path:
            try:
                shutil.copy(self.db_filename, backup_path)
                self.append_log(tr["db_backup"].format(backup_path))
                self.status_bar.showMessage(tr["db_backup"].format(backup_path))
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Veritabanı yedeklenemedi: {str(e)}")

    def restore_database(self):
        tr = TRANSLATIONS[self.current_language]
        restore_path, _ = QFileDialog.getOpenFileName(self, "Yedek Dosyası Seç", "", "SQLite Files (*.db);;All Files (*)")
        if restore_path:
            try:
                shutil.copy(restore_path, self.db_filename)
                self.update_address_count()
                self.append_log(tr["db_restored"].format(restore_path))
                self.status_bar.showMessage(tr["db_restored"].format(restore_path))
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Veritabanı geri yüklenemedi: {str(e)}")

    def export_found_addresses(self):
        tr = TRANSLATIONS[self.current_language]
        if self.found_table.rowCount() == 0:
            QMessageBox.information(self, "Dışa Aktar" if self.current_language == "Türkçe" else "Export",
                                   "Dışa aktarılacak adres yok.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Bulunan Adresleri Kaydet", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    for row in range(self.found_table.rowCount()):
                        private_key = self.found_table.item(row, 0).text()
                        addr = self.found_table.item(row, 1).text()
                        f.write(f"Private Key: {private_key}, Address: {addr}\n")
                self.status_bar.showMessage(f"{file_name} yoluna dışa aktarıldı")
            except Exception as e:
                QMessageBox.critical(self, "Hata" if self.current_language == "Türkçe" else "Error",
                                    f"Dışa aktarma başarısız: {str(e)}")

    def toggle_workers_spin(self, state: int):
        self.workers_spin.setEnabled(not state)

    def on_all_coins_changed(self, state: int):
        tr = TRANSLATIONS[self.current_language]
        if state == Qt.Checked:
            self.selected_coins = SUPPORTED_COINS
            for coin in SUPPORTED_COINS:
                self.coin_checkboxes[coin].setChecked(True)
        else:
            self.selected_coins = []
            for coin in SUPPORTED_COINS:
                self.coin_checkboxes[coin].setChecked(False)
        self.append_log(tr["selected_coins"].format([COIN_SYMBOLS[coin] for coin in self.selected_coins]))
        self.save_config()

    def on_coin_changed(self, coin: str, state: int):
        tr = TRANSLATIONS[self.current_language]
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
        self.append_log(tr["selected_coins"].format([COIN_SYMBOLS[coin] for coin in self.selected_coins]))
        self.save_config()

    def closeEvent(self, event):
        if self.processes or self.puzzle_processes:
            reply = QMessageBox.question(self, "Çıkış" if self.current_language == "Türkçe" else "Exit",
                                        "Süreçler çalışıyor. Durdurup çıkmak ister misiniz?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_workers()
                self.stop_puzzle_workers()
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
