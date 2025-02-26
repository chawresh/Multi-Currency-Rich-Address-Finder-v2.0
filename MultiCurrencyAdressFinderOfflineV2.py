import sys
import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
import csv
import smtplib
from email.mime.text import MIMEText
from PyQt5.QtGui import QIcon, QColor, QFont, QTextCharFormat, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QTimeEdit, QDateEdit, QTableWidget, QCheckBox, QComboBox, QSpinBox, QHBoxLayout, QScrollArea,
    QGroupBox, QGridLayout, QTextEdit, QInputDialog, QTabWidget, QFileDialog, QStatusBar, QListWidget, QHeaderView, QDialog,
    QCalendarWidget, QFormLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QTimer, Qt, QTime, QDate, QLocale, QThread, QByteArray
import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
import pyperclip
import platform
import requests
import shutil
import pyautogui
import tempfile

app_path = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(app_path, 'data.db')
default_icon_file = os.path.join(app_path, 'lhe.png')
log_file = os.path.join(app_path, 'app.log')

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SchedulerThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.stop_flag = True

class TaskEditDialog(QDialog):
    def __init__(self, task, patients, parent=None):
        super().__init__(parent)
        self.task = task
        self.patients = patients
        self.setWindowTitle("Görev Bilgileri")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F7F9FC, stop:1 #E8ECEF); 
                border-radius: 15px; 
            }
            QLabel { 
                font-size: 14px; 
                color: #2C3E50; 
                font-weight: bold; 
            }
            QLineEdit, QTextEdit { 
                padding: 8px; 
                border: 2px solid #BDC3C7; 
                border-radius: 6px; 
                background: #FFFFFF; 
                font-size: 14px; 
                color: #2C3E50; 
            }
            QComboBox, QDateEdit, QTimeEdit { 
                padding: 8px; 
                border: 2px solid #BDC3C7; 
                border-radius: 6px; 
                background: #FFFFFF; 
                font-size: 14px; 
            }
            QPushButton { 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 8px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD); 
                color: white; 
                border: none; 
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #357ABD, stop:1 #2A6399); 
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(task["description"])
        self.description_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(QLabel("Görev Açıklaması:"))
        layout.addWidget(self.description_edit)

        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(task.get("note", ""))
        self.note_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(QLabel("Not:"))
        layout.addWidget(self.note_edit)

        self.time_list = QListWidget()
        for time_str in task["time"]:
            self.time_list.addItem(time_str)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_list)
        time_buttons = QVBoxLayout()
        self.add_time_btn = QPushButton("Saat Ekle")
        self.add_time_btn.clicked.connect(self.add_time)
        self.remove_time_btn = QPushButton("Saat Sil")
        self.remove_time_btn.clicked.connect(self.remove_time)
        time_buttons.addWidget(self.add_time_btn)
        time_buttons.addWidget(self.remove_time_btn)
        time_layout.addLayout(time_buttons)
        layout.addWidget(QLabel("Saatler:"))
        layout.addLayout(time_layout)

        self.repeat_group = QGroupBox("Tekrar Günleri")
        repeat_layout = QHBoxLayout()
        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar", "Hergün"]
        self.day_checkboxes = {day: QCheckBox(day) for day in self.days}
        for day in task["repeat"]:
            if day in self.day_checkboxes:
                self.day_checkboxes[day].setChecked(True)
        for checkbox in self.day_checkboxes.values():
            repeat_layout.addWidget(checkbox)
        self.repeat_group.setLayout(repeat_layout)
        layout.addWidget(self.repeat_group)

        self.patient_combo = QComboBox()
        self.patient_combo.addItem("Hasta Yok")
        self.patient_combo.addItems(self.patients)
        self.patient_combo.setCurrentText(task.get("patient", "Hasta Yok"))
        layout.addWidget(QLabel("Hasta:"))
        layout.addWidget(self.patient_combo)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.save_task)
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_time(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Saat Seç")
        layout = QVBoxLayout()
        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        layout.addWidget(time_edit)
        ok_button = QPushButton("Tamam")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            time_str = time_edit.time().toString("HH:mm")
            if time_str not in [self.time_list.item(i).text() for i in range(self.time_list.count())]:
                self.time_list.addItem(time_str)

    def remove_time(self):
        selected_items = self.time_list.selectedItems()
        for item in selected_items:
            self.time_list.takeItem(self.time_list.row(item))

    def save_task(self):
        self.task["description"] = self.description_edit.toPlainText()
        self.task["note"] = self.note_edit.toPlainText()
        self.task["time"] = [self.time_list.item(i).text() for i in range(self.time_list.count())]
        self.task["repeat"] = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        patient = self.patient_combo.currentText() if self.patient_combo.currentText() != "Hasta Yok" else None
        self.task["patient"] = patient
        if not self.task["time"]:
            QMessageBox.warning(self, "Hata", "En az bir saat eklemelisiniz!")
            return
        self.accept()

class WhatsAppSchedulerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.themes = {
            "Açık Mod": """
                QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E6ECEF, stop:1 #D1DCE2); }
                QLabel { color: #2C3E50; font-weight: bold; }
                QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD); color: white; border-radius: 8px; padding: 8px; border: none; }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #357ABD, stop:1 #2A6399); }
                QTableWidget { background-color: #FFFFFF; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 8px; }
                QHeaderView::section { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F0F4F8, stop:1 #DDE4E9); color: #2C3E50; padding: 5px; border: none; }
                QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QListWidget { background-color: #FFFFFF; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 5px; padding: 5px; }
                QComboBox::drop-down { border-left: 1px solid #BDC3C7; width: 20px; }
                QComboBox::down-arrow { border: 2px solid #2C3E50; border-radius: 3px; width: 8px; height: 8px; background: #2C3E50; }
                QGroupBox { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F0F4F8, stop:1 #DDE4E9); border: 1px solid #BDC3C7; border-radius: 8px; padding: 10px; color: #2C3E50; }
                QCheckBox { color: #2C3E50; }
                QCalendarWidget { background-color: #FFFFFF; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 5px; }
                QTabWidget::pane { border: 1px solid #BDC3C7; background: #FFFFFF; }
                QTabBar::tab { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F0F4F8, stop:1 #DDE4E9); color: #2C3E50; padding: 5px; border: 1px solid #BDC3C7; border-bottom: none; }
                QTabBar::tab:selected { background: #FFFFFF; color: #2C3E50; }
            """,
            "Koyu Mod": """
                QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #263238, stop:1 #37474F); }
                QLabel { color: #CFD8DC; font-weight: bold; }
                QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #607D8B, stop:1 #78909C); color: #CFD8DC; border-radius: 8px; padding: 8px; border: none; }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #78909C, stop:1 #90A4AE); }
                QTableWidget { background-color: #37474F; color: #CFD8DC; border: 1px solid #455A64; border-radius: 8px; }
                QHeaderView::section { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #455A64, stop:1 #607D8B); color: #CFD8DC; padding: 5px; border: none; }
                QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QListWidget { background-color: #455A64; color: #CFD8DC; border: 1px solid #607D8B; border-radius: 5px; padding: 5px; }
                QComboBox::item { color: #CFD8DC; }
                QComboBox::item:selected { background-color: #607D8B; color: #CFD8DC; }
                QComboBox::drop-down { border-left: 1px solid #607D8B; width: 20px; }
                QComboBox::down-arrow { border: 2px solid #CFD8DC; border-radius: 3px; width: 8px; height: 8px; background: #CFD8DC; }
                QGroupBox { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #37474F, stop:1 #455A64); border: 1px solid #607D8B; border-radius: 8px; padding: 10px; color: #CFD8DC; }
                QCheckBox { color: #CFD8DC; }
                QCalendarWidget { background-color: #455A64; color: #CFD8DC; border: 1px solid #607D8B; border-radius: 5px; }
                QTabWidget::pane { border: 1px solid #607D8B; background: #37474F; }
                QTabBar::tab { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #455A64, stop:1 #607D8B); color: #CFD8DC; padding: 5px; border: 1px solid #607D8B; border-bottom: none; }
                QTabBar::tab:selected { background: #37474F; color: #CFD8DC; }
            """
        }

        logging.info("Veritabanı başlatılıyor")
        try:
            self.init_db()
            logging.info("Veritabanı başlatma tamamlandı")
        except Exception as e:
            logging.error(f"Veritabanı başlatılamadı: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Veritabanı başlatılamadı: {str(e)}")
            sys.exit(1)

        try:
            self.config, self.logo_data = self.load_config_and_logo()
        except Exception as e:
            logging.error(f"Yapılandırma ve logo yüklenemedi: {str(e)}")
            QMessageBox.warning(self, "Uyarı", "Yapılandırma ve logo yüklenemedi, varsayılan ayarlar kullanılıyor.")
            self.config = self.get_default_config()
            self.logo_data = None
            with open(default_icon_file, 'rb') as f:
                self.logo_data = f.read()

        self.temp_logo_file = None
        if self.logo_data:
            self.temp_logo_file = os.path.join(tempfile.gettempdir(), 'temp_logo.png')
            with open(self.temp_logo_file, 'wb') as f:
                f.write(self.logo_data)
            self.icon_file = self.temp_logo_file
        else:
            self.icon_file = default_icon_file

        self.users = self.load_users()
        self.current_user = None

        if self.is_first_setup:
            if not self.show_login_dialog(developer_only=True):
                sys.exit(0)
            if not self.show_first_setup_dialog():
                sys.exit(0)
        else:
            if not self.show_login_dialog():
                sys.exit(0)

        self.setWindowTitle(self.config.get("app_name", "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi"))
        self.setWindowIcon(QIcon(self.icon_file))

        screen = QApplication.primaryScreen().availableGeometry()
        max_width = screen.width()
        max_height = screen.height()
        window_width = min(int(max_width * 0.8), max_width)
        window_height = min(int(max_height * 0.9), max_height)
        window_x = screen.left() + (max_width - window_width) // 2
        window_y = screen.top() + (max_height - window_height) // 2
        self.setGeometry(window_x, window_y, window_width, window_height)
        self.setMinimumSize(800, 600)

        self.categories = ["Acil", "İlaç", "Uyarı", "Eğitim", "Hatırlatma", "Diğer"]
        self.priorities = ["Normal", "Düşük", "Orta", "Yüksek"]
        self.emojis = ["⏰", "📋", "⚠️", "📒", "🚨", "✅", "❌", "⭐", "📅"]

        self.load_groups()
        self.patients = self.load_patients()
        self.tasks = self.load_tasks()
        self.archived_tasks = self.load_archived_tasks()
        self.task_history = self.load_task_history()

        self.driver = None
        self.init_ui()
        self.schedule_tasks()
        self.start_scheduler()
        self.reset_colors_daily()
        logging.info("Uygulama başlatıldı.")

    def init_db(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            logging.info(f"Veritabanına bağlanıldı: {db_file}")

            c.execute('''CREATE TABLE IF NOT EXISTS users (
                         username TEXT PRIMARY KEY,
                         password TEXT NOT NULL,
                         email TEXT,
                         added_date TEXT DEFAULT (datetime('now')))''')
            c.execute('''CREATE TABLE IF NOT EXISTS groups (
                         group_name TEXT PRIMARY KEY)''')
            c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         description TEXT NOT NULL,
                         note TEXT,
                         time TEXT NOT NULL,
                         repeat TEXT NOT NULL,
                         duration_type TEXT,
                         duration_value INTEGER,
                         end_date TEXT,
                         group_name TEXT,
                         status TEXT NOT NULL,
                         category TEXT,
                         priority TEXT,
                         start_date TEXT DEFAULT (date('now')),
                         files TEXT,
                         patient TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS archived_tasks (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         description TEXT NOT NULL,
                         note TEXT,
                         time TEXT NOT NULL,
                         repeat TEXT NOT NULL,
                         duration_type TEXT,
                         duration_value INTEGER,
                         end_date TEXT,
                         group_name TEXT,
                         status TEXT NOT NULL,
                         category TEXT,
                         priority TEXT,
                         start_date TEXT,
                         files TEXT,
                         patient TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS config (
                         key TEXT PRIMARY KEY,
                         value TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS app_settings (
                         id INTEGER PRIMARY KEY CHECK (id = 1),
                         logo BLOB,
                         app_name TEXT,
                         other_info TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS task_history (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         task_description TEXT NOT NULL,
                         action TEXT NOT NULL,
                         timestamp TEXT NOT NULL,
                         user TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS task_templates (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL,
                         description TEXT NOT NULL,
                         note TEXT,
                         time TEXT NOT NULL,
                         repeat TEXT NOT NULL,
                         duration_type TEXT,
                         duration_value INTEGER,
                         category TEXT,
                         priority TEXT,
                         files TEXT,
                         patient TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS patients (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL)''')

            c.execute("PRAGMA table_info(tasks)")
            columns = {col[1] for col in c.fetchall()}
            if "files" not in columns:
                c.execute("ALTER TABLE tasks ADD COLUMN files TEXT")
            if "start_date" not in columns:
                c.execute("ALTER TABLE tasks ADD COLUMN start_date TEXT DEFAULT (date('now'))")
            if "patient" not in columns:
                c.execute("ALTER TABLE tasks ADD COLUMN patient TEXT")

            c.execute("PRAGMA table_info(archived_tasks)")
            columns = {col[1] for col in c.fetchall()}
            if "files" not in columns:
                c.execute("ALTER TABLE archived_tasks ADD COLUMN files TEXT")
            if "start_date" not in columns:
                c.execute("ALTER TABLE archived_tasks ADD COLUMN start_date TEXT")
            if "patient" not in columns:
                c.execute("ALTER TABLE archived_tasks ADD COLUMN patient TEXT")

            c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("atlantis", "maestro"))

            default_configs = {
                "search_box_xpath": '//div[@contenteditable="true"][@data-tab="3"]',
                "message_box_xpath": '//div[@contenteditable="true"][@data-tab="10"]',
                "default_message_template": """⏰ GÖREV ZAMANI ⏰\n\n📋 {description}\n⚠️ Not: {note}\n\n📒 Kategori: {category}\n🚨 Öncelik: {priority}""",
                "browser_timeout": "30",
                "post_send_delay": "10",
                "qr_scan_delay": "20",
                "chrome_profile_dir": os.path.join(os.path.expanduser("~"), "WhatsAppProfile"),
                "theme": "Açık Mod",
                "message_method": "Selenium",
                "whatsapp_api_key": "",
                "whatsapp_api_phone": "",
                "headless": False,
                "window_width": 1024,
                "window_height": 768,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "proxy": "",
                "disable_notifications": True,
                "page_load_strategy": "normal",
                "element_wait_time": 10,
                "retry_count": 3,
                "caption_box_xpath": '//div[@aria-label="Başlık ekleyin"]',
                "document_menu_xpath": '//span[text()="Belge"]',
                "media_menu_xpath": '//span[text()="Fotoğraflar ve Videolar"]',
                "attachment_button_xpath": '//button[@title="Ekle"]//span[@data-icon="plus"]',
                "file_input_xpath": '//input[@type="file"]',
                "pre_send_delay": 10,
                "smtp_server": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "notification_email": ""
            }
            for key, value in default_configs.items():
                c.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))

            c.execute("SELECT COUNT(*) FROM app_settings")
            if c.fetchone()[0] == 0:
                with open(default_icon_file, 'rb') as f:
                    default_logo = f.read()
                c.execute("INSERT INTO app_settings (id, logo, app_name, other_info) VALUES (1, ?, ?, ?)",
                          (sqlite3.Binary(default_logo), "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi", ""))

            c.execute("SELECT COUNT(*) FROM users")
            self.is_first_setup = c.fetchone()[0] == 1

            conn.commit()
            logging.info("Veritabanı tabloları oluşturuldu ve yapılandırma eklendi.")
        except sqlite3.Error as e:
            logging.error(f"Veritabanı oluşturulurken hata: {str(e)}")
            raise
        finally:
            conn.close()

    def get_default_config(self):
        return {
            "search_box_xpath": '//div[@contenteditable="true"][@data-tab="3"]',
            "message_box_xpath": '//div[@contenteditable="true"][@data-tab="10"]',
            "default_message_template": """⏰ GÖREV ZAMANI ⏰\n\n📋 {description}\n⚠️ Not: {note}\n\n📒 Kategori: {category}\n🚨 Öncelik: {priority}""",
            "browser_timeout": "30",
            "post_send_delay": "10",
            "qr_scan_delay": "20",
            "chrome_profile_dir": os.path.join(os.path.expanduser("~"), "WhatsAppProfile"),
            "theme": "Açık Mod",
            "message_method": "Selenium",
            "whatsapp_api_key": "",
            "whatsapp_api_phone": "",
            "headless": False,
            "window_width": 1024,
            "window_height": 768,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "proxy": "",
            "disable_notifications": True,
            "page_load_strategy": "normal",
            "element_wait_time": 10,
            "retry_count": 3,
            "caption_box_xpath": '//div[@aria-label="Başlık ekleyin"]',
            "document_menu_xpath": '//span[text()="Belge"]',
            "media_menu_xpath": '//span[text()="Fotoğraflar ve Videolar"]',
            "attachment_button_xpath": '//button[@title="Ekle"]//span[@data-icon="plus"]',
            "file_input_xpath": '//input[@type="file"]',
            "pre_send_delay": 10,
            "smtp_server": "",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "notification_email": ""
        }

    def load_config_and_logo(self):
        default_config = self.get_default_config()
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT key, value FROM config")
            config_data = {row[0]: json.loads(row[1]) for row in c.fetchall()}
            config = default_config.copy()
            config.update(config_data)

            c.execute("SELECT logo, app_name, other_info FROM app_settings WHERE id = 1")
            row = c.fetchone()
            logo_data = row[0] if row else None
            if row:
                config["app_name"] = row[1]
                config["other_info"] = row[2]
            conn.close()
            logging.info("Yapılandırma ve logo başarıyla yüklendi.")
            return config, logo_data
        except sqlite3.OperationalError as e:
            logging.warning(f"Yapılandırma veya logo tablosu bulunamadı: {str(e)}. Varsayılan yapılandırma kullanılıyor.")
            self.init_db()
            return default_config, None
        except Exception as e:
            logging.error(f"Yapılandırma ve logo yüklenirken hata: {str(e)}")
            return default_config, None

    def save_config_and_logo(self, config=None, logo_data=None, app_name=None, other_info=None):
        if config is None:
            config = self.config
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM config")
            for key, value in config.items():
                if key not in ["app_name", "other_info"]:
                    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))

            c.execute("DELETE FROM app_settings WHERE id = 1")
            logo_to_save = logo_data if logo_data is not None else self.logo_data
            app_name_to_save = app_name if app_name is not None else config.get("app_name", "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi")
            other_info_to_save = other_info if other_info is not None else config.get("other_info", "")
            c.execute("INSERT INTO app_settings (id, logo, app_name, other_info) VALUES (1, ?, ?, ?)",
                      (sqlite3.Binary(logo_to_save), app_name_to_save, other_info_to_save))
            conn.commit()
            logging.info("Yapılandırma ve logo kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Yapılandırma ve logo kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_users(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT username, password, email, added_date FROM users")
            users = {row[0]: {"password": row[1], "email": row[2], "added_date": row[3]} for row in c.fetchall()}
            conn.close()
            return users
        except sqlite3.Error as e:
            logging.error(f"Kullanıcılar yüklenemedi: {str(e)}")
            return {}

    def save_users(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM users")
            for username, data in self.users.items():
                c.execute("INSERT OR REPLACE INTO users (username, password, email, added_date) VALUES (?, ?, ?, ?)",
                          (username, data["password"], data.get("email", ""), data.get("added_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
            conn.commit()
            logging.info("Kullanıcılar kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Kullanıcılar kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_groups(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT group_name FROM groups")
            self.groups = [row[0] for row in c.fetchall()]
            conn.close()
        except sqlite3.Error as e:
            logging.error(f"Gruplar yüklenemedi: {str(e)}")
            self.groups = []

    def save_groups(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM groups")
            for group in self.groups:
                c.execute("INSERT OR REPLACE INTO groups (group_name) VALUES (?)", (group,))
            conn.commit()
            logging.info("Gruplar kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Gruplar kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_patients(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT name FROM patients")
            patients = [row[0] for row in c.fetchall()]
            conn.close()
            return patients
        except sqlite3.Error as e:
            logging.error(f"Hastalar yüklenemedi: {str(e)}")
            return []

    def save_patients(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM patients")
            for patient in self.patients:
                c.execute("INSERT OR REPLACE INTO patients (name) VALUES (?)", (patient,))
            conn.commit()
            logging.info("Hastalar kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Hastalar kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_tasks(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT description, note, time, repeat, duration_type, duration_value, end_date, group_name, status, category, priority, start_date, files, patient FROM tasks")
            tasks = []
            for row in c.fetchall():
                time_value = row[2]
                times = json.loads(time_value) if time_value else ["09:00"]
                if not isinstance(times, list):
                    times = [times]
                files = json.loads(row[12]) if row[12] else []
                patient = row[13] if row[13] else None
                tasks.append({
                    "description": row[0],
                    "note": row[1],
                    "time": times,
                    "repeat": json.loads(row[3]),
                    "duration_type": row[4],
                    "duration_value": row[5],
                    "end_date": row[6],
                    "group_name": row[7],
                    "status": row[8],
                    "category": row[9],
                    "priority": row[10],
                    "start_date": row[11] if row[11] else datetime.now().strftime("%Y-%m-%d"),
                    "files": files,
                    "patient": patient
                })
            conn.close()
            return tasks
        except sqlite3.Error as e:
            logging.error(f"Görevler yüklenemedi: {str(e)}")
            return []

    def save_tasks(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM tasks")
            for task in self.tasks:
                c.execute("INSERT INTO tasks (description, note, time, repeat, duration_type, duration_value, end_date, group_name, status, category, priority, start_date, files, patient) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (task["description"], task.get("note", ""), json.dumps(task["time"]), json.dumps(task["repeat"]), task["duration_type"],
                           task["duration_value"], task["end_date"], task["group_name"], task["status"],
                           task["category"], task["priority"], task.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                           json.dumps(task["files"]), task.get("patient", None)))
            conn.commit()
            logging.info("Görevler kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Görevler kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_archived_tasks(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT description, note, time, repeat, duration_type, duration_value, end_date, group_name, status, category, priority, start_date, files, patient FROM archived_tasks")
            archived_tasks = []
            for row in c.fetchall():
                time_value = row[2]
                times = json.loads(time_value) if time_value else ["09:00"]
                if not isinstance(times, list):
                    times = [times]
                files = json.loads(row[12]) if row[12] else []
                patient = row[13] if row[13] else None
                archived_tasks.append({
                    "description": row[0],
                    "note": row[1],
                    "time": times,
                    "repeat": json.loads(row[3]),
                    "duration_type": row[4],
                    "duration_value": row[5],
                    "end_date": row[6],
                    "group_name": row[7],
                    "status": row[8],
                    "category": row[9],
                    "priority": row[10],
                    "start_date": row[11] if row[11] else datetime.now().strftime("%Y-%m-%d"),
                    "files": files,
                    "patient": patient
                })
            conn.close()
            return archived_tasks
        except sqlite3.Error as e:
            logging.error(f"Arşivlenmiş görevler yüklenemedi: {str(e)}")
            return []

    def save_archived_tasks(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM archived_tasks")
            for task in self.archived_tasks:
                c.execute("INSERT INTO archived_tasks (description, note, time, repeat, duration_type, duration_value, end_date, group_name, status, category, priority, start_date, files, patient) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (task["description"], task.get("note", ""), json.dumps(task["time"]), json.dumps(task["repeat"]), task["duration_type"],
                           task["duration_value"], task["end_date"], task["group_name"], task["status"],
                           task["category"], task["priority"], task.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                           json.dumps(task["files"]), task.get("patient", None)))
            conn.commit()
            logging.info("Arşivlenmiş görevler kaydedildi.")
        except sqlite3.Error as e:
            logging.error(f"Arşivlenmiş görevler kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_task_history(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT task_description, action, timestamp, user FROM task_history")
            history = [{"description": row[0], "action": row[1], "timestamp": row[2], "user": row[3]} for row in c.fetchall()]
            conn.close()
            return history
        except sqlite3.Error as e:
            logging.error(f"Görev geçmişi yüklenemedi: {str(e)}")
            return []

    def save_task_history(self, description, action, user):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("INSERT INTO task_history (task_description, action, timestamp, user) VALUES (?, ?, ?, ?)",
                      (description, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Görev geçmişi kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def load_task_templates(self):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("SELECT name, description, note, time, repeat, duration_type, duration_value, category, priority, files, patient FROM task_templates")
            templates = []
            for row in c.fetchall():
                time_value = row[3]
                times = json.loads(time_value) if time_value else ["09:00"]
                if not isinstance(times, list):
                    times = [times]
                files = json.loads(row[9]) if row[9] else []
                patient = row[10] if row[10] else None
                templates.append({
                    "name": row[0],
                    "description": row[1],
                    "note": row[2],
                    "time": times,
                    "repeat": json.loads(row[4]),
                    "duration_type": row[5],
                    "duration_value": row[6],
                    "category": row[7],
                    "priority": row[8],
                    "files": files,
                    "patient": patient
                })
            conn.close()
            return templates
        except sqlite3.Error as e:
            logging.error(f"Görev şablonları yüklenemedi: {str(e)}")
            return []

    def save_task_templates(self, templates):
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM task_templates")
            for template in templates:
                c.execute("INSERT INTO task_templates (name, description, note, time, repeat, duration_type, duration_value, category, priority, files, patient) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (template["name"], template["description"], template.get("note", ""), json.dumps(template["time"]),
                           json.dumps(template["repeat"]), template["duration_type"], template["duration_value"],
                           template["category"], template["priority"], json.dumps(template["files"]),
                           template.get("patient", None)))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Görev şablonları kaydedilemedi: {str(e)}")
        finally:
            conn.close()

    def show_login_dialog(self, developer_only=False):
        dialog = QDialog(self)
        dialog.setWindowTitle("Giriş Yap")
        dialog.setFixedSize(450, 650)
        dialog.setStyleSheet(self.themes[self.config["theme"]] + """
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F7F9FC, stop:1 #E8ECEF); 
                border-radius: 15px; 
            }
            QLineEdit { 
                padding: 8px; 
                border: 2px solid #BDC3C7; 
                border-radius: 6px; 
                background: #FFFFFF; 
                font-size: 14px; 
                color: #2C3E50; 
            }
            QLineEdit:focus { 
                border: 2px solid #4A90E2; 
            }
            QPushButton { 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 8px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD); 
                color: white; 
                border: none; 
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #357ABD, stop:1 #2A6399); 
            }
            QLabel { 
                font-size: 12px; 
                color: #2C3E50; 
            }
            QGroupBox { 
                font-size: 12px; 
                font-weight: bold; 
                border: 1px solid #BDC3C7; 
                border-radius: 8px; 
                padding: 10px; 
                margin-top: 10px; 
                background: #FFFFFF; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top center; 
                padding: 0 5px; 
                background: #FFFFFF; 
                color: #2C3E50; 
            }
            QTabWidget::pane { 
                border: 1px solid #BDC3C7; 
                background: #FFFFFF; 
            }
            QTabBar::tab { 
                background: #F0F4F8; 
                color: #2C3E50; 
                padding: 5px; 
                border: 1px solid #BDC3C7; 
                border-bottom: none; 
                border-top-left-radius: 5px; 
                border-top-right-radius: 5px; 
            }
            QTabBar::tab:selected { 
                background: #FFFFFF; 
                color: #4A90E2; 
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        dialog.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD);
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            padding: 10px;
        """)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(self.icon_file).pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)

        title_label = QLabel(f"{self.config.get('app_name', 'LİMAN HUZUR ve HASTA BAKIM EVİ')}\nYönetim Sistemine Giriş")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)

        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)

        form_group = QGroupBox("Giriş")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        username = QLineEdit()
        username.setPlaceholderText("Kullanıcı Adı")
        username.setMinimumHeight(35)
        username.setToolTip("Kullanıcı adınızı girin")
        form_layout.addRow("Kullanıcı Adı:", username)

        password = QLineEdit()
        password.setPlaceholderText("Şifre")
        password.setEchoMode(QLineEdit.Password)
        password.setMinimumHeight(35)
        password.setToolTip("Şifrenizi girin")
        password.returnPressed.connect(lambda: self.validate_login_and_close(username.text(), password.text(), dialog, developer_only))
        form_layout.addRow("Şifre:", password)

        show_password = QCheckBox("Şifreyi Göster")
        show_password.setStyleSheet("color: #2C3E50; font-size: 12px; margin-left: 5px;")
        show_password.stateChanged.connect(lambda state: password.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password))
        form_layout.addRow("", show_password)

        if not developer_only:
            forgot_password = QLabel('<a href="#" style="color: #3498DB; text-decoration: none;">Şifremi Unuttum?</a>')
            forgot_password.setFont(QFont("Arial", 10))
            forgot_password.setAlignment(Qt.AlignRight)
            forgot_password.setOpenExternalLinks(False)
            forgot_password.setToolTip("Şifre sıfırlama henüz uygulanmadı")
            forgot_password.linkActivated.connect(lambda: QMessageBox.information(dialog, "Bilgi", "Şifre sıfırlama özelliği henüz eklenmedi."))
            form_layout.addRow("", forgot_password)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        login_button = QPushButton("Giriş Yap")
        login_button.clicked.connect(lambda: self.validate_login_and_close(username.text(), password.text(), dialog, developer_only))
        login_button.setToolTip("Giriş yapmak için tıklayın")
        main_layout.addWidget(login_button)

        dialog.status_bar = QStatusBar()
        dialog.status_bar.setStyleSheet("color: #E74C3C; font-size: 12px; background: transparent;")
        main_layout.addWidget(dialog.status_bar)

        if not developer_only:
            info_tabs = QTabWidget()

            about_tab = QWidget()
            about_layout = QVBoxLayout()
            about_layout.setSpacing(8)

            about_title_label = QLabel(f"{self.config.get('app_name', 'LİMAN HUZUR ve HASTA BAKIM EVİ')}\nPersonel Görev Yöneticisi")
            about_title_label.setFont(QFont("Arial", 13, QFont.Bold))
            about_title_label.setAlignment(Qt.AlignCenter)
            about_layout.addWidget(about_title_label)

            about_version_label = QLabel("Sürüm: 1.0.0 • Şubat 2025")
            about_version_label.setFont(QFont("Arial", 10))
            about_version_label.setAlignment(Qt.AlignCenter)
            about_layout.addWidget(about_version_label)

            about_description_label = QLabel(
                "Hasta bakım evi personeli için görev planlama ve WhatsApp üzerinden "
                "otomatik bildirim gönderme uygulaması."
            )
            about_description_label.setFont(QFont("Arial", 11))
            about_description_label.setWordWrap(True)
            about_description_label.setAlignment(Qt.AlignCenter)
            about_layout.addWidget(about_description_label)

            about_tab.setLayout(about_layout)
            info_tabs.addTab(about_tab, "Hakkında")

            dev_tab = QWidget()
            dev_layout = QFormLayout()
            dev_layout.setSpacing(8)
            dev_layout.setLabelAlignment(Qt.AlignLeft)

            developer_label = QLabel("Mustafa AKBAL")
            developer_label.setFont(QFont("Arial", 11))
            dev_layout.addRow("Ad:", developer_label)

            email_label = QLabel('<a href="mailto:mstf.akbal@gmail.com" style="color: #3498DB; text-decoration: none;">mstf.akbal@gmail.com</a>')
            email_label.setFont(QFont("Arial", 11))
            email_label.setOpenExternalLinks(True)
            dev_layout.addRow("E-posta:", email_label)

            phone_label = QLabel("+90 544 748 59 59")
            phone_label.setFont(QFont("Arial", 11))
            dev_layout.addRow("Telefon:", phone_label)

            instagram_label = QLabel('<a href="https://instagram.com/mstf.akbal" style="color: #3498DB; text-decoration: none;">@mstf.akbal</a>')
            instagram_label.setFont(QFont("Arial", 11))
            instagram_label.setOpenExternalLinks(True)
            dev_layout.addRow("Instagram:", instagram_label)

            dev_tab.setLayout(dev_layout)
            info_tabs.addTab(dev_tab, "Geliştirici")

            main_layout.addWidget(info_tabs)

            copyright_label = QLabel("© 2025 Mustafa AKBAL. Tüm hakları saklıdır.")
            copyright_label.setFont(QFont("Arial", 9))
            copyright_label.setAlignment(Qt.AlignCenter)
            copyright_label.setStyleSheet("color: #7F8C8D; margin-top: 10px;")
            main_layout.addWidget(copyright_label)

        main_layout.addStretch()
        dialog.setLayout(main_layout)
        return dialog.exec_() == QDialog.Accepted

    def validate_login_and_close(self, username, password, dialog, developer_only=False):
        if developer_only:
            if username == "atlantis" and password == "maestro":
                self.current_user = "atlantis"
                dialog.accept()
            else:
                dialog.status_bar.showMessage("Geçersiz geliştirici kimlik bilgileri!", 3000)
        else:
            if self.validate_login(username, password):
                self.current_user = username
                dialog.accept()
            else:
                dialog.status_bar.showMessage("Geçersiz kullanıcı adı veya şifre!", 3000)

    def validate_login(self, username, password):
        return username in self.users and self.users[username]["password"] == password

    def show_first_setup_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("İlk Kurulum - Yönetici Hesabı Oluştur ve Kişiselleştir")
        dialog.setFixedSize(450, 700)
        dialog.setStyleSheet(self.themes[self.config["theme"]] + """
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F7F9FC, stop:1 #E8ECEF); 
                border-radius: 15px; 
            }
            QLabel { 
                font-size: 14px; 
                color: #2C3E50; 
                font-weight: bold; 
            }
            QLineEdit, QTextEdit { 
                padding: 8px; 
                border: 2px solid #BDC3C7; 
                border-radius: 6px; 
                background: #FFFFFF; 
                font-size: 14px; 
                color: #2C3E50; 
            }
            QPushButton { 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 8px; 
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.logo_path = QLineEdit()
        self.logo_path.setPlaceholderText("Logo Dosyasını Seçin")
        self.logo_path.setReadOnly(True)
        logo_button = QPushButton("Logo Seç")
        logo_button.clicked.connect(self.select_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path)
        logo_layout.addWidget(logo_button)
        layout.addWidget(QLabel("Logo:"))
        layout.addLayout(logo_layout)

        self.app_name = QLineEdit()
        self.app_name.setPlaceholderText("Ör: X Hasta Bakım Evi")
        layout.addWidget(QLabel("Uygulama Adı:"))
        layout.addWidget(self.app_name)

        self.other_info = QTextEdit()
        self.other_info.setPlaceholderText("Ör: X Hasta Bakım Evi için özel notlar")
        layout.addWidget(QLabel("Diğer Özel Bilgiler:"))
        layout.addWidget(self.other_info)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Yönetici Kullanıcı Adı")
        layout.addWidget(QLabel("Yönetici Kullanıcı Adı:"))
        layout.addWidget(self.username)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Yönetici E-posta")
        layout.addWidget(QLabel("Yönetici E-posta:"))
        layout.addWidget(self.email)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Yönetici Şifre")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Yönetici Şifre:"))
        layout.addWidget(self.password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Şifreyi Onayla")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Şifreyi Onayla:"))
        layout.addWidget(self.confirm_password)

        self.show_password = QCheckBox("Şifreyi Göster")
        self.show_password.stateChanged.connect(lambda state: (
            self.password.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password),
            self.confirm_password.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password)
        ))
        layout.addWidget(self.show_password)

        self.save_button = QPushButton("Hesabı Oluştur ve Kaydet")
        self.save_button.clicked.connect(lambda: self.create_first_user_and_save(
            self.username.text(), 
            self.password.text(), 
            self.confirm_password.text(), 
            self.logo_path.text(), 
            self.app_name.text(), 
            self.other_info.toPlainText(), 
            self.email.text(),
            dialog
        ))
        layout.addWidget(self.save_button)

        dialog.status_bar = QStatusBar()
        dialog.status_bar.setStyleSheet("color: #E74C3C; font-size: 12px;")
        layout.addWidget(dialog.status_bar)

        layout.addStretch()
        dialog.setLayout(layout)
        return dialog.exec_() == QDialog.Accepted

    def select_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Logo Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_path.setText(file_path)

    def create_first_user_and_save(self, username, password, confirm_password, logo_path, app_name, other_info, email, dialog):
        if not username or not password or not confirm_password or not logo_path or not app_name:
            dialog.status_bar.showMessage("Tüm alanlar doldurulmalı!", 3000)
            return
        if password != confirm_password:
            dialog.status_bar.showMessage("Şifreler eşleşmiyor!", 3000)
            return
        if username == "atlantis":
            dialog.status_bar.showMessage("Bu kullanıcı adı kullanılamaz!", 3000)
            return
        try:
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
        except Exception as e:
            dialog.status_bar.showMessage(f"Logo dosyası okunamadı: {str(e)}", 3000)
            return

        if "atlantis" in self.users:
            del self.users["atlantis"]
        self.users[username] = {"password": password, "email": email}
        self.save_users()
        self.save_config_and_logo(self.config, logo_data, app_name, other_info)
        self.logo_data = logo_data
        self.config["app_name"] = app_name
        self.config["other_info"] = other_info
        if self.temp_logo_file:
            os.remove(self.temp_logo_file)
        self.temp_logo_file = os.path.join(tempfile.gettempdir(), 'temp_logo.png')
        with open(self.temp_logo_file, 'wb') as f:
            f.write(self.logo_data)
        self.icon_file = self.temp_logo_file
        dialog.accept()

    def manage_users_dialog(self):
        if self.current_user != "atlantis" and len(self.users) > 1 and list(self.users.keys())[0] != self.current_user:
            QMessageBox.warning(self, "Yetki Hatası", "Sadece geliştirici veya ilk yönetici kullanıcılar bu işlemi yapabilir!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Kullanıcıları Yönet")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet(self.themes[self.config["theme"]])
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        user_table = QTableWidget()
        user_table.setColumnCount(4)
        user_table.setHorizontalHeaderLabels(["Kullanıcı Adı", "Tür", "E-posta", "Ekleme Tarihi"])
        user_table.setRowCount(len(self.users))

        for i, (username, data) in enumerate(self.users.items()):
            item0 = QTableWidgetItem(username)
            item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)
            user_table.setItem(i, 0, item0)

            user_type = "Geliştirici" if username == "atlantis" else "İlk Yönetici" if i == 0 else "Kurum"
            item1 = QTableWidgetItem(user_type)
            item1.setFlags(item1.flags() & ~Qt.ItemIsEditable)
            user_table.setItem(i, 1, item1)

            item2 = QTableWidgetItem(data.get("email", ""))
            item2.setFlags(item2.flags() & ~Qt.ItemIsEditable)
            user_table.setItem(i, 2, item2)

            added_date = data["added_date"] if data.get("added_date") else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item3 = QTableWidgetItem(added_date)
            item3.setFlags(item3.flags() & ~Qt.ItemIsEditable)
            user_table.setItem(i, 3, item3)

        user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        user_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(user_table)

        add_group = QGroupBox("Yeni Kullanıcı Ekle")
        add_layout = QHBoxLayout()
        new_username = QLineEdit()
        new_username.setPlaceholderText("Kullanıcı Adı")
        new_password = QLineEdit()
        new_password.setPlaceholderText("Şifre")
        new_password.setEchoMode(QLineEdit.Password)
        new_email = QLineEdit()
        new_email.setPlaceholderText("E-posta")
        show_password = QCheckBox("Şifreyi Göster")
        show_password.stateChanged.connect(lambda state: new_password.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password))
        add_button = QPushButton("Ekle")
        add_button.clicked.connect(lambda: self.add_user(new_username.text(), new_password.text(), new_email.text(), dialog, user_table))
        add_layout.addWidget(QLabel("Kullanıcı Adı:"))
        add_layout.addWidget(new_username)
        add_layout.addWidget(QLabel("Şifre:"))
        add_layout.addWidget(new_password)
        add_layout.addWidget(QLabel("E-posta:"))
        add_layout.addWidget(new_email)
        add_layout.addWidget(show_password)
        add_layout.addWidget(add_button)
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        delete_button = QPushButton("Seçili Kullanıcıyı Sil")
        delete_button.clicked.connect(lambda: self.delete_user(user_table, dialog))
        layout.addWidget(delete_button)

        close_button = QPushButton("Kapat")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        layout.addStretch()
        dialog.setLayout(layout)
        dialog.exec_()

    def add_user(self, username, password, email, dialog, user_table):
        if not username or not password:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı ve şifre boş olamaz!")
            return
        if username in self.users:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten mevcut!")
            return
        if username == "atlantis":
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı kullanılamaz!")
            return

        self.users[username] = {"password": password, "email": email}
        self.save_users()

        row = user_table.rowCount()
        user_table.insertRow(row)
        user_table.setItem(row, 0, QTableWidgetItem(username))
        user_table.setItem(row, 1, QTableWidgetItem("Kurum"))
        user_table.setItem(row, 2, QTableWidgetItem(email))
        user_table.setItem(row, 3, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        QMessageBox.information(self, "Başarılı", f"{username} başarıyla eklendi!")

    def delete_user(self, table, dialog):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silmek için bir kullanıcı seçin!")
            return
        username = table.item(selected_row, 0).text()
        if username == "atlantis" or (selected_row == 0 and len(self.users) > 1):
            QMessageBox.warning(self, "Hata", "Geliştirici veya ilk yönetici kullanıcısı silinemez!")
            return

        reply = QMessageBox.question(self, "Onay", f"'{username}' kullanıcısını silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.users[username]
            self.save_users()
            table.removeRow(selected_row)
            QMessageBox.information(self, "Başarılı", f"'{username}' başarıyla silindi!")

    def add_patient(self, patient_name):
        if not patient_name:
            QMessageBox.warning(self, "Hata", "Hasta adı boş olamaz!")
            return
        if patient_name in self.patients:
            QMessageBox.warning(self, "Hata", "Bu hasta zaten mevcut!")
            return
        self.patients.append(patient_name)
        self.save_patients()
        self.patient_list.addItem(patient_name)
        self.task_patient_combo.clear()
        self.task_patient_combo.addItem("Hasta Yok")
        self.task_patient_combo.addItems(self.patients)
        QMessageBox.information(self, "Başarılı", f"{patient_name} başarıyla eklendi!")

    def delete_patient(self):
        selected_items = self.patient_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hata", "Lütfen silmek için bir hasta seçin!")
            return
        patient_name = selected_items[0].text()
        reply = QMessageBox.question(self, "Onay", f"'{patient_name}' hastasını silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.patients.remove(patient_name)
            self.save_patients()
            self.patient_list.takeItem(self.patient_list.row(selected_items[0]))
            self.task_patient_combo.clear()
            self.task_patient_combo.addItem("Hasta Yok")
            self.task_patient_combo.addItems(self.patients)
            self.update_patient_task_table(None)  # Clear patient task table after deletion
            QMessageBox.information(self, "Başarılı", f"'{patient_name}' başarıyla silindi!")

    def init_ui(self):
        main_layout = QVBoxLayout()

        top_widget = QWidget()
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setPixmap(QIcon(self.icon_file).pixmap(190, 105))
        top_layout.addWidget(logo_label)

        clock_container = QWidget()
        clock_layout = QVBoxLayout()
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("""
            background-color: #4A90E2; 
            color: white; 
            padding: 10px; 
            border-radius: 8px; 
            margin: 5px;
        """ if self.config["theme"] == "Açık Mod" else """
            background-color: #607D8B; 
            color: #CFD8DC; 
            padding: 10px; 
            border-radius: 8px; 
            margin: 5px;
        """)

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 14))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("""
            background-color: #ECF0F1; 
            color: #2C3E50; 
            padding: 8px; 
            border-radius: 8px; 
            margin: 5px;
        """ if self.config["theme"] == "Açık Mod" else """
            background-color: #455A64; 
            color: #CFD8DC; 
            padding: 8px; 
            border-radius: 8px; 
            margin: 5px;
        """)

        clock_layout.addWidget(self.clock_label)
        clock_layout.addWidget(self.date_label)
        clock_container.setLayout(clock_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(clock_container)
        top_layout.addStretch(1)

        right_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.setCurrentText(self.config["theme"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        theme_layout.addWidget(self.theme_combo)
        right_layout.addLayout(theme_layout)

        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)
        self.group_combo.addItems(self.groups)
        self.add_group_button = QPushButton("➕")
        self.add_group_button.clicked.connect(self.add_group)
        self.delete_group_button = QPushButton("🗑️")
        self.delete_group_button.clicked.connect(self.delete_group)
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Kurum:"))
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(self.add_group_button)
        group_layout.addWidget(self.delete_group_button)
        right_layout.addLayout(group_layout)

        self.status_label = QLabel(f"Bugün Gönderilen: {len([t for t in self.tasks if t['status'] == 'Gönderildi'])}")
        right_layout.addWidget(self.status_label)

        top_layout.addLayout(right_layout)
        top_widget.setLayout(top_layout)
        main_layout.addWidget(top_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)

        self.tabs = QTabWidget()
        self.task_tab = QWidget()
        self.patients_tab = QWidget()
        self.calendar_tab = QWidget()
        self.stats_tab = QWidget()
        self.settings_tab = QWidget()
        self.instructions_tab = QWidget()
        self.about_tab = QWidget()
        self.history_tab = QWidget()

        self.tabs.addTab(self.task_tab, "Görevler")
        self.tabs.addTab(self.patients_tab, "Hastalar")
        self.tabs.addTab(self.calendar_tab, "Takvim")
        self.tabs.addTab(self.stats_tab, "İstatistik")
        self.tabs.addTab(self.settings_tab, "Ayarlar")
        self.tabs.addTab(self.instructions_tab, "Kullanım Talimatları")
        self.tabs.addTab(self.about_tab, "Hakkında")
        self.tabs.addTab(self.history_tab, "Görev Geçmişi")
        main_layout.addWidget(self.tabs)

        # Task Tab
        task_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        form_group = QGroupBox("Görev Bilgileri")
        form_layout = QGridLayout()

        self.task_template_combo = QComboBox()
        self.task_template_combo.addItem("Şablon Seçiniz")
        templates = self.load_task_templates()
        for template in templates:
            self.task_template_combo.addItem(template["name"])
        self.task_template_combo.currentTextChanged.connect(self.load_template)
        form_layout.addWidget(QLabel("Görev Şablonu:"), 0, 0)
        form_layout.addWidget(self.task_template_combo, 0, 1, 1, 2)

        self.task_description_input = QTextEdit()
        form_layout.addWidget(QLabel("Görev Açıklaması:"), 1, 0)
        form_layout.addWidget(self.task_description_input, 1, 1, 1, 2)

        self.task_note_input = QTextEdit()
        form_layout.addWidget(QLabel("Not:"), 2, 0)
        form_layout.addWidget(self.task_note_input, 2, 1, 1, 2)

        message_layout = QHBoxLayout()
        for emoji in self.emojis:
            emoji_button = QPushButton(emoji)
            emoji_button.setFixedSize(40, 40)
            emoji_button.clicked.connect(lambda checked, e=emoji: self.add_emoji(e))
            message_layout.addWidget(emoji_button)
        form_layout.addWidget(QLabel("Emojiler:"), 3, 0)
        form_layout.addLayout(message_layout, 3, 1, 1, 2)

        self.task_time_list = QListWidget()
        self.add_time_button = QPushButton("Saat Ekle")
        self.add_time_button.clicked.connect(self.add_time)
        self.remove_time_button = QPushButton("Saat Sil")
        self.remove_time_button.clicked.connect(self.remove_time)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.task_time_list)
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_time_button)
        buttons_layout.addWidget(self.remove_time_button)
        time_layout.addLayout(buttons_layout)
        form_layout.addWidget(QLabel("Saatler:"), 4, 0)
        form_layout.addLayout(time_layout, 4, 1, 1, 2)

        self.repeat_days_group = QGroupBox("Tekrar Günleri")
        self.repeat_days_layout = QHBoxLayout()
        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar", "Hergün"]
        self.day_checkboxes = {day: QCheckBox(day) for day in self.days}
        for checkbox in self.day_checkboxes.values():
            self.repeat_days_layout.addWidget(checkbox)
        self.repeat_days_group.setLayout(self.repeat_days_layout)
        form_layout.addWidget(self.repeat_days_group, 5, 0, 1, 3)

        self.task_duration_input = QComboBox()
        self.task_duration_input.addItems(["Sürekli", "Günlük", "Haftalık", "Aylık"])
        self.task_duration_spinbox = QSpinBox()
        self.task_duration_spinbox.setRange(1, 365)
        self.task_duration_input.currentTextChanged.connect(self.update_duration_spinbox)
        form_layout.addWidget(QLabel("Görev Süresi:"), 6, 0)
        form_layout.addWidget(self.task_duration_input, 6, 1)
        form_layout.addWidget(self.task_duration_spinbox, 6, 2)

        self.task_start_date_input = QDateEdit()
        self.task_start_date_input.setDate(datetime.now())
        form_layout.addWidget(QLabel("Başlangıç Tarihi:"), 7, 0)
        form_layout.addWidget(self.task_start_date_input, 7, 1)

        self.task_end_date_input = QDateEdit()
        self.task_end_date_input.setDate(datetime.now())
        self.task_end_date_checkbox = QCheckBox("Bitiş Tarihi Belirle")
        self.task_end_date_checkbox.stateChanged.connect(self.toggle_end_date_input)
        form_layout.addWidget(QLabel("Bitiş Tarihi:"), 8, 0)
        form_layout.addWidget(self.task_end_date_input, 8, 1)
        form_layout.addWidget(self.task_end_date_checkbox, 8, 2)

        self.task_category_combo = QComboBox()
        self.task_category_combo.addItems(self.categories)
        self.task_priority_combo = QComboBox()
        self.task_priority_combo.addItems(self.priorities)
        form_layout.addWidget(QLabel("Kategori:"), 9, 0)
        form_layout.addWidget(self.task_category_combo, 9, 1)
        form_layout.addWidget(QLabel("Öncelik:"), 9, 2)
        form_layout.addWidget(self.task_priority_combo, 9, 3)

        self.task_patient_combo = QComboBox()
        self.task_patient_combo.addItem("Hasta Yok")
        self.task_patient_combo.addItems(self.patients)
        form_layout.addWidget(QLabel("Hasta:"), 10, 0)
        form_layout.addWidget(self.task_patient_combo, 10, 1)

        self.task_files_list = QListWidget()
        self.add_file_button = QPushButton("Dosya Ekle")
        self.add_file_button.clicked.connect(self.add_file)
        self.remove_file_button = QPushButton("Dosya Sil")
        self.remove_file_button.clicked.connect(self.remove_file)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.task_files_list)
        file_buttons_layout = QVBoxLayout()
        file_buttons_layout.addWidget(self.add_file_button)
        file_buttons_layout.addWidget(self.remove_file_button)
        file_layout.addLayout(file_buttons_layout)
        form_layout.addWidget(QLabel("Ek Dosyalar:"), 11, 0)
        form_layout.addLayout(file_layout, 11, 1, 1, 2)

        form_group.setLayout(form_layout)
        left_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_task_button = QPushButton("➕ Yeni Görev Ekle")
        self.add_task_button.clicked.connect(self.add_task)
        self.preview_button = QPushButton("👁️ Görev Önizleme")
        self.preview_button.clicked.connect(self.preview_task)
        self.edit_task_button = QPushButton("✏️ Görevi Güncelle")
        self.edit_task_button.clicked.connect(self.edit_task)
        self.delete_task_button = QPushButton("🗑️ Görevi Sil")
        self.delete_task_button.clicked.connect(self.delete_task)
        self.clear_form_button = QPushButton("🧹 Formu Temizle")
        self.clear_form_button.clicked.connect(self.clear_form)
        self.save_template_button = QPushButton("💾 Şablon Olarak Kaydet")
        self.save_template_button.clicked.connect(self.save_as_template)
        button_layout.addWidget(self.add_task_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.edit_task_button)
        button_layout.addWidget(self.delete_task_button)
        button_layout.addWidget(self.clear_form_button)
        button_layout.addWidget(self.save_template_button)
        left_layout.addLayout(button_layout)
        task_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        filter_group = QGroupBox("Görev Filtreleme ve Sıralama")
        filter_layout = QHBoxLayout()
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.addItems(["Tümü"] + self.categories)
        self.filter_priority_combo = QComboBox()
        self.filter_priority_combo.addItems(["Tümü"] + self.priorities)
        self.filter_status_combo = QComboBox()
        self.filter_status_combo.addItems(["Tümü", "Bekliyor", "Gönderildi", "Gönderilemedi"])
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Varsayılan", "Saate Göre", "Kuruma Göre", "Hasta Adına Göre"])
        self.sort_combo.setCurrentText("Saate Göre")
        self.sort_combo.currentTextChanged.connect(self.sort_tasks)
        self.filter_button = QPushButton("🔍 Filtrele")
        self.filter_button.clicked.connect(self.filter_tasks)
        filter_layout.addWidget(QLabel("📋 Kategori:"))
        filter_layout.addWidget(self.filter_category_combo)
        filter_layout.addWidget(QLabel("🚨 Öncelik:"))
        filter_layout.addWidget(self.filter_priority_combo)
        filter_layout.addWidget(QLabel("✅ Durum:"))
        filter_layout.addWidget(self.filter_status_combo)
        filter_layout.addWidget(QLabel("🔄 Sırala:"))
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(self.filter_button)
        filter_group.setLayout(filter_layout)
        right_layout.addWidget(filter_group)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(13)
        self.task_table.setHorizontalHeaderLabels([
            "Hasta", "Görev\nAçıklaması", "Not", "Saatler", "Tekrar\nGünleri", "Görev\nSüresi", 
            "Bitiş\nTarihi", "Kurum\nAdı", "Durum", "Kategori", "Öncelik", "Başlangıç\nTarihi", 
            "Dosyalar"
        ])
        self.task_table.cellClicked.connect(self.load_task_for_edit)
        self.task_table.cellDoubleClicked.connect(self.show_task_details)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.task_table)
        scroll_area.setWidgetResizable(True)
        self.sort_tasks("Saate Göre")
        right_layout.addWidget(scroll_area)

        archive_button_layout = QHBoxLayout()
        self.archive_button = QPushButton("📜 Arşivlenen Görevler")
        self.archive_button.clicked.connect(self.show_archived_tasks)
        self.archive_selected_button = QPushButton("➡️ Arşive Ekle")
        self.archive_selected_button.clicked.connect(self.archive_selected_task)
        all_tasks_button = QPushButton("📋 Tüm Görevleri Görüntüle")
        all_tasks_button.clicked.connect(self.show_all_tasks_window)
        archive_button_layout.addWidget(self.archive_button)
        archive_button_layout.addWidget(self.archive_selected_button)
        archive_button_layout.addWidget(all_tasks_button)
        right_layout.addLayout(archive_button_layout)
        task_layout.addLayout(right_layout)
        self.task_tab.setLayout(task_layout)

        # Patients Tab
        patients_layout = QVBoxLayout()
        patients_title = QLabel("Hasta Listesi")
        patients_title.setFont(QFont("Arial", 14, QFont.Bold))
        patients_title.setAlignment(Qt.AlignCenter)
        patients_layout.addWidget(patients_title)

        self.patient_list = QListWidget()
        self.patient_list.addItems(self.patients)
        self.patient_list.itemClicked.connect(self.show_patient_tasks)
        patients_layout.addWidget(self.patient_list)

        add_patient_layout = QHBoxLayout()
        self.new_patient_input = QLineEdit()
        self.new_patient_input.setPlaceholderText("Yeni Hasta Adı")
        add_patient_button = QPushButton("➕ Hasta Ekle")
        add_patient_button.clicked.connect(lambda: self.add_patient(self.new_patient_input.text()))
        add_patient_layout.addWidget(self.new_patient_input)
        add_patient_layout.addWidget(add_patient_button)
        patients_layout.addLayout(add_patient_layout)

        delete_patient_button = QPushButton("🗑️ Seçili Hastayı Sil")
        delete_patient_button.clicked.connect(self.delete_patient)
        patients_layout.addWidget(delete_patient_button)

        # Patient Task Table
        patient_tasks_group = QGroupBox("Seçilen Hastanın Görevleri")
        patient_tasks_layout = QVBoxLayout()
        self.patient_task_table = QTableWidget()
        self.patient_task_table.setColumnCount(13)
        self.patient_task_table.setHorizontalHeaderLabels([
            "Hasta", "Görev\nAçıklaması", "Not", "Saatler", "Tekrar\nGünleri", "Görev\nSüresi", 
            "Bitiş\nTarihi", "Kurum\nAdı", "Durum", "Kategori", "Öncelik", "Başlangıç\nTarihi", 
            "Dosyalar"
        ])
        self.patient_task_table.cellDoubleClicked.connect(self.show_patient_task_details)
        patient_tasks_layout.addWidget(self.patient_task_table)
        patient_tasks_group.setLayout(patient_tasks_layout)
        patients_layout.addWidget(patient_tasks_group)

        patients_layout.addStretch()
        self.patients_tab.setLayout(patients_layout)

        # Calendar Tab
        calendar_layout = QVBoxLayout()
        calendar_title = QLabel("Görev Takvimi")
        calendar_title.setFont(QFont("Arial", 14, QFont.Bold))
        calendar_title.setAlignment(Qt.AlignCenter)
        calendar_layout.addWidget(calendar_title)

        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale(QLocale.Turkish))
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.show_tasks_for_date)
        self.calendar.setStyleSheet("""
            QCalendarWidget QToolButton { 
                height: 30px; 
                width: 100px; 
                font-size: 12pt; 
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #F0F4F8; 
            }
            QCalendarWidget QAbstractItemView { 
                font-size: 12pt; 
                selection-background-color: #4A90E2; 
                selection-color: white; 
            }
            QCalendarWidget QTableView { 
                border: 1px solid #BDC3C7; 
                padding: 2px; 
            }
            QCalendarWidget QTableView::item { 
                padding: 2px; 
                margin: 0px; 
            }
        """ if self.config["theme"] == "Açık Mod" else """
            QCalendarWidget QToolButton { 
                height: 30px; 
                width: 100px; 
                font-size: 12pt; 
                color: #CFD8DC; 
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #455A64; 
            }
            QCalendarWidget QAbstractItemView { 
                font-size: 12pt; 
                selection-background-color: #607D8B; 
                selection-color: #CFD8DC; 
            }
            QCalendarWidget QTableView { 
                border: 1px solid #607D8B; 
                padding: 2px; 
            }
            QCalendarWidget QTableView::item { 
                padding: 2px; 
                margin: 0px; 
            }
        """)
        calendar_layout.addWidget(self.calendar)

        calendar_tasks_group = QGroupBox("Seçilen Günün Görevleri")
        calendar_tasks_layout = QVBoxLayout()
        self.calendar_task_list = QListWidget()
        self.calendar_task_list.setStyleSheet("font-size: 12pt; padding: 5px;")
        calendar_tasks_layout.addWidget(self.calendar_task_list)
        calendar_tasks_group.setLayout(calendar_tasks_layout)
        calendar_layout.addWidget(calendar_tasks_group)

        self.daily_task_count = QLabel("Günlük Görev Sayısı: 0")
        self.daily_task_count.setFont(QFont("Arial", 10))
        calendar_layout.addWidget(self.daily_task_count)
        self.calendar_tab.setLayout(calendar_layout)

        # Stats Tab
        stats_layout = QVBoxLayout()
        self.sent_label = QLabel(f"Gönderilen Görevler: {len([t for t in self.tasks if t['status'] == 'Gönderildi'])}")
        self.failed_label = QLabel(f"Gönderilemeyen Görevler: {len([t for t in self.tasks if t['status'] == 'Gönderilemedi'])}")
        total_tasks = len(self.tasks)
        completion_rate = (len([t for t in self.tasks if t['status'] == 'Gönderildi']) / total_tasks * 100) if total_tasks > 0 else 0
        self.completion_rate_label = QLabel(f"Görev Tamamlanma Oranı: {completion_rate:.2f}%")

        category_counts = {cat: 0 for cat in self.categories}
        for task in self.tasks:
            category = task.get("category", "Diğer")
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts["Diğer"] += 1
        category_text = "\n".join([f"{cat}: {count}" for cat, count in category_counts.items()])
        self.category_label = QLabel(f"Kategorilere Göre Görevler:\n{category_text}")

        priority_counts = {pri: 0 for pri in self.priorities}
        for task in self.tasks:
            priority = task.get("priority", "Normal")
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts["Normal"] += 1
        priority_text = "\n".join([f"{pri}: {count}" for pri, count in priority_counts.items()])
        self.priority_label = QLabel(f"Önceliklere Göre Görevler:\n{priority_text}")

        stats_layout.addWidget(self.sent_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.completion_rate_label)
        stats_layout.addWidget(self.category_label)
        stats_layout.addWidget(self.priority_label)
        stats_layout.addStretch()
        self.stats_tab.setLayout(stats_layout)

        # Settings Tab
        settings_layout = QVBoxLayout()
        settings_tabs = QTabWidget()

        general_tab = QWidget()
        general_layout = QVBoxLayout()

        self.method_combo = QComboBox()
        self.method_combo.addItems(["Selenium", "WhatsApp API"])
        self.method_combo.setCurrentText(self.config["message_method"])
        general_layout.addWidget(QLabel("Mesaj Gönderme Yöntemi:"))
        general_layout.addWidget(self.method_combo)

        api_layout = QFormLayout()
        self.whatsapp_api_key = QLineEdit(self.config["whatsapp_api_key"])
        self.whatsapp_api_key.setMinimumWidth(300)
        api_layout.addRow("API Anahtarı:", self.whatsapp_api_key)

        self.whatsapp_api_phone = QLineEdit(self.config["whatsapp_api_phone"])
        self.whatsapp_api_phone.setMinimumWidth(300)
        api_layout.addRow("Telefon Numarası ID:", self.whatsapp_api_phone)

        self.api_group = QGroupBox("WhatsApp API Ayarları")
        self.api_group.setLayout(api_layout)
        general_layout.addWidget(self.api_group)

        smtp_layout = QFormLayout()
        self.smtp_server = QLineEdit(self.config["smtp_server"])
        smtp_layout.addRow("SMTP Sunucusu:", self.smtp_server)
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(self.config["smtp_port"])
        smtp_layout.addRow("SMTP Portu:", self.smtp_port)
        self.smtp_username = QLineEdit(self.config["smtp_username"])
        smtp_layout.addRow("SMTP Kullanıcı Adı:", self.smtp_username)
        self.smtp_password = QLineEdit(self.config["smtp_password"])
        self.smtp_password.setEchoMode(QLineEdit.Password)
        smtp_layout.addRow("SMTP Şifre:", self.smtp_password)
        self.notification_email = QLineEdit(self.config["notification_email"])
        smtp_layout.addRow("Bildirim E-postası:", self.notification_email)
        self.smtp_group = QGroupBox("E-posta Ayarları")
        self.smtp_group.setLayout(smtp_layout)
        general_layout.addWidget(self.smtp_group)

        general_layout.addWidget(QLabel("Mesaj Formatı:"))
        self.message_template = QTextEdit(self.config["default_message_template"])
        self.message_template.setMinimumHeight(150)
        general_layout.addWidget(self.message_template)

        self.pre_send_delay = QSpinBox()
        self.pre_send_delay.setRange(5, 60)
        self.pre_send_delay.setValue(self.config["pre_send_delay"])
        general_layout.addWidget(QLabel("Ön Gönderme Süresi (dakika):"))
        general_layout.addWidget(self.pre_send_delay)

        preview_button = QPushButton("Önizleme")
        preview_button.clicked.connect(self.preview_message_template)
        general_layout.addWidget(preview_button)

        test_group = QGroupBox("Test Mesajı Gönder")
        test_layout = QVBoxLayout()
        self.test_group_combo = QComboBox()
        self.test_group_combo.addItems(self.groups)
        test_layout.addWidget(QLabel("Hedef Kurum:"))
        test_layout.addWidget(self.test_group_combo)
        self.test_message = QLineEdit("Bu bir test mesajıdır.")
        self.test_message.setMinimumWidth(300)
        test_layout.addWidget(QLabel("Test Mesajı:"))
        test_layout.addWidget(self.test_message)
        send_test_button = QPushButton("Test Gönder")
        send_test_button.clicked.connect(self.send_test_message)
        test_layout.addWidget(send_test_button)
        test_group.setLayout(test_layout)
        general_layout.addWidget(test_group)

        general_layout.addStretch()
        general_tab.setLayout(general_layout)
        settings_tabs.addTab(general_tab, "Genel Ayarlar")

        selenium_tab = QWidget()
        selenium_layout = QVBoxLayout()

        selenium_form_layout = QFormLayout()
        selenium_form_layout.setLabelAlignment(Qt.AlignRight)

        self.search_box_xpath = QLineEdit(self.config["search_box_xpath"])
        self.search_box_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Search Box XPath:", self.search_box_xpath)

        self.message_box_xpath = QLineEdit(self.config["message_box_xpath"])
        self.message_box_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Message Box XPath:", self.message_box_xpath)

        self.browser_timeout = QSpinBox()
        self.browser_timeout.setRange(10, 60)
        self.browser_timeout.setValue(int(self.config["browser_timeout"]))
        self.browser_timeout.setMinimumWidth(150)
        selenium_form_layout.addRow("Tarayıcı Zaman Aşımı (sn):", self.browser_timeout)

        self.post_send_delay = QSpinBox()
        self.post_send_delay.setRange(5, 30)
        self.post_send_delay.setValue(int(self.config["post_send_delay"]))
        self.post_send_delay.setMinimumWidth(150)
        selenium_form_layout.addRow("Gönderme Sonrası Bekleme (sn):", self.post_send_delay)

        self.qr_scan_delay = QSpinBox()
        self.qr_scan_delay.setRange(10, 60)
        self.qr_scan_delay.setValue(int(self.config["qr_scan_delay"]))
        self.qr_scan_delay.setMinimumWidth(150)
        selenium_form_layout.addRow("QR Tarama Bekleme (sn):", self.qr_scan_delay)

        self.chrome_profile_dir = QLineEdit(self.config["chrome_profile_dir"])
        self.chrome_profile_dir.setMinimumWidth(300)
        selenium_form_layout.addRow("Chrome Profil Dizini:", self.chrome_profile_dir)

        self.headless_checkbox = QCheckBox("Headless Mode")
        self.headless_checkbox.setChecked(self.config["headless"])
        selenium_form_layout.addRow(self.headless_checkbox)

        self.window_width_spinbox = QSpinBox()
        self.window_width_spinbox.setRange(800, 1920)
        self.window_width_spinbox.setValue(self.config["window_width"])
        self.window_width_spinbox.setMinimumWidth(150)
        selenium_form_layout.addRow("Pencere Genişliği:", self.window_width_spinbox)

        self.window_height_spinbox = QSpinBox()
        self.window_height_spinbox.setRange(600, 1080)
        self.window_height_spinbox.setValue(self.config["window_height"])
        self.window_height_spinbox.setMinimumWidth(150)
        selenium_form_layout.addRow("Pencere Yüksekliği:", self.window_height_spinbox)

        self.user_agent_input = QLineEdit(self.config["user_agent"])
        self.user_agent_input.setMinimumWidth(300)
        selenium_form_layout.addRow("User Agent:", self.user_agent_input)

        self.proxy_input = QLineEdit(self.config["proxy"])
        self.proxy_input.setMinimumWidth(300)
        self.proxy_input.setPlaceholderText("ör. http://proxy.example.com:8080")
        selenium_form_layout.addRow("Proxy:", self.proxy_input)

        self.disable_notifications_checkbox = QCheckBox("Bildirimleri Devre Dışı Bırak")
        self.disable_notifications_checkbox.setChecked(self.config["disable_notifications"])
        selenium_form_layout.addRow(self.disable_notifications_checkbox)

        self.page_load_strategy_combo = QComboBox()
        self.page_load_strategy_combo.addItems(["normal", "eager", "none"])
        self.page_load_strategy_combo.setCurrentText(self.config["page_load_strategy"])
        self.page_load_strategy_combo.setMinimumWidth(150)
        selenium_form_layout.addRow("Sayfa Yükleme Stratejisi:", self.page_load_strategy_combo)

        self.element_wait_time_spinbox = QSpinBox()
        self.element_wait_time_spinbox.setRange(5, 30)
        self.element_wait_time_spinbox.setValue(self.config["element_wait_time"])
        self.element_wait_time_spinbox.setMinimumWidth(150)
        selenium_form_layout.addRow("Eleman Bekleme Süresi (sn):", self.element_wait_time_spinbox)

        self.retry_count_spinbox = QSpinBox()
        self.retry_count_spinbox.setRange(1, 5)
        self.retry_count_spinbox.setValue(self.config["retry_count"])
        self.retry_count_spinbox.setMinimumWidth(150)
        selenium_form_layout.addRow("Yeniden Deneme Sayısı:", self.retry_count_spinbox)

        self.caption_box_xpath = QLineEdit(self.config["caption_box_xpath"])
        self.caption_box_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Caption Box XPath:", self.caption_box_xpath)

        self.document_menu_xpath = QLineEdit(self.config["document_menu_xpath"])
        self.document_menu_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Document Menu XPath:", self.document_menu_xpath)

        self.media_menu_xpath = QLineEdit(self.config["media_menu_xpath"])
        self.media_menu_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Media Menu XPath:", self.media_menu_xpath)

        self.attachment_button_xpath = QLineEdit(self.config["attachment_button_xpath"])
        self.attachment_button_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("Attachment Button XPath:", self.attachment_button_xpath)

        self.file_input_xpath = QLineEdit(self.config["file_input_xpath"])
        self.file_input_xpath.setMinimumWidth(300)
        selenium_form_layout.addRow("File Input XPath:", self.file_input_xpath)

        self.selenium_group = QGroupBox("Selenium Ayarları")
        self.selenium_group.setLayout(selenium_form_layout)
        selenium_layout.addWidget(self.selenium_group)
        selenium_layout.addStretch()
        selenium_tab.setLayout(selenium_layout)
        settings_tabs.addTab(selenium_tab, "Selenium Ayarları")

        file_tab = QWidget()
        file_layout = QVBoxLayout()

        export_db_button = QPushButton("Veritabanını Dışa Aktar")
        export_db_button.clicked.connect(self.export_database)
        file_layout.addWidget(export_db_button)

        import_db_button = QPushButton("Veritabanını İçe Aktar")
        import_db_button.clicked.connect(self.import_database)
        file_layout.addWidget(import_db_button)

        backup_button = QPushButton("Yedek Oluştur")
        backup_button.clicked.connect(self.create_backup)
        file_layout.addWidget(backup_button)

        export_tasks_button = QPushButton("Görevleri Dışa Aktar")
        export_tasks_button.clicked.connect(self.export_tasks_to_csv)
        file_layout.addWidget(export_tasks_button)

        import_tasks_button = QPushButton("Görevleri İçe Aktar")
        import_tasks_button.clicked.connect(self.import_tasks_from_csv)
        file_layout.addWidget(import_tasks_button)

        file_layout.addStretch()
        file_tab.setLayout(file_layout)
        settings_tabs.addTab(file_tab, "Dosya İşlemleri")

        users_tab = QWidget()
        users_layout = QVBoxLayout()
        manage_users_button = QPushButton("Kullanıcıları Yönet")
        manage_users_button.clicked.connect(self.manage_users_dialog)
        users_layout.addWidget(manage_users_button)
        users_layout.addStretch()
        users_tab.setLayout(users_layout)
        settings_tabs.addTab(users_tab, "Kullanıcı Yönetimi")

        button_layout = QHBoxLayout()
        save_button = QPushButton("Kaydet")
        save_button.clicked.connect(self.save_settings)
        reset_button = QPushButton("Varsayılana Sıfırla")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)
        settings_layout.addWidget(settings_tabs)
        settings_layout.addLayout(button_layout)
        self.settings_tab.setLayout(settings_layout)

        # Instructions Tab
        instructions_layout = QVBoxLayout()
        instructions_title_label = QLabel(f"{self.config.get('app_name', 'LİMAN HUZUR ve HASTA BAKIM EVİ')}\nPersonel Görev Yöneticisi Kullanım Kılavuzu")
        instructions_title_label.setFont(QFont("Arial", 18, QFont.Bold))
        instructions_title_label.setAlignment(Qt.AlignCenter)
        instructions_title_label.setStyleSheet(
            "color: #2C3E50; background-color: #ECF0F1; padding: 10px; border-radius: 5px; margin-bottom: 20px;" 
            if self.config["theme"] == "Açık Mod" 
            else "color: #CFD8DC; background-color: #455A64; padding: 10px; border-radius: 5px; margin-bottom: 20px;"
        )
        instructions_layout.addWidget(instructions_title_label)

        instructions_text = """
        <style>
            h3 { color: #3498DB; font-size: 16px; margin-top: 15px; margin-bottom: 5px; }
            p { margin: 5px 0; line-height: 1.5; }
            ul { margin: 5px 0 10px 20px; }
            li { margin: 5px 0; }
            a { color: #3498DB; text-decoration: none; }
        </style>

        <p style='font-size: 14px;'><b>🎉 Hoş Geldiniz!</b><br>
        Bu uygulama, hasta bakım evi personellerinin görevlerini düzenlemek ve WhatsApp üzerinden bildirim göndermek için tasarlandı.</p>

        <h3>🆕 1. İlk Kurulum</h3>
        <ul>
            <li>Uygulama ilk kez açıldığında, geliştirici "atlantis" kullanıcı adı ve "maestro" şifresiyle giriş yapar.</li>
            <li>İlk kurulumda logo, uygulama adı ve diğer bilgileri girerek uygulamayı kişiselleştirin.</li>
            <li>Firma için bir yönetici kullanıcı adı ve şifre oluşturun.</li>
            <li>"Hesabı Oluştur ve Kaydet" butonuna tıklayın.</li>
        </ul>

        <h3>🔑 2. Uygulamaya Giriş</h3>
        <ul>
            <li>Yönetici veya diğer kullanıcı adı ve şifresiyle giriş yapın.</li>
            <li>Şifrenizi görmek için "Şifreyi Göster" kutusunu işaretleyin.</li>
            <li>"Giriş Yap"a tıklayın veya Enter’a basın.</li>
        </ul>

        <h3>🖥️ 3. Arayüzü Tanıyın</h3>
        <ul>
            <li><b>Üst Alan:</b> Logo, saat/tarih, tema ve kurum yönetimi araçları.</li>
            <li><b>Orta Alan:</b> Görev formu, filtreleme ve görev tablosu.</li>
            <li><b>Sekmeler:</b> Görevler, Hastalar, Takvim, İstatistik, Ayarlar, Kullanım Talimatları, Hakkında, Görev Geçmişi.</li>
        </ul>

        <h3>👤 4. Kullanıcı Yönetimi</h3>
        <ul>
            <li>"Ayarlar" > "Kullanıcı Yönetimi" sekmesinden yeni kullanıcı ekleyin veya silin.</li>
            <li>Sadece ilk yönetici veya geliştirici bu yetkilere sahiptir.</li>
            <li>Geliştirici kullanıcısı ilk kurulumdan sonra kaldırılır.</li>
        </ul>

        <h3>➕ 5. Görev Ekleme</h3>
        <ul>
            <li>"Görevler" sekmesinde görev detaylarını doldurun.</li>
            <li>"Hasta" alanında bir hasta seçebilir veya boş bırakabilirsiniz.</li>
            <li>"Yeni Görev Ekle"ye tıklayın.</li>
            <li>Şablonları kullanarak hızlı görev oluşturabilirsiniz.</li>
        </ul>

        <h3>🏢 6. Kurum Ekleme ve Silme</h3>
        <ul>
            <li><b>Ekleme:</b> "➕" butonuyla kurum adını girin.</li>
            <li><b>Silme:</b> "🗑️" ile silin, şifrenizi onaylayın.</li>
        </ul>

        <h3>👨‍⚕️ 7. Hasta Yönetimi</h3>
        <ul>
            <li>"Hastalar" sekmesinden hasta ekleyin veya silin.</li>
            <li>Hasta silme işlemi için onay gereklidir.</li>
            <li>Hastalar görevlerle ilişkilendirilebilir.</li>
        </ul>

        <h3>📧 8. E-posta Bildirimleri</h3>
        <ul>
            <li>Ayarlar sekmesinden SMTP bilgilerini ve bildirim e-posta adresini girin.</li>
        </ul>

        <h3>💡 9. İpuçları ve Notlar</h3>
        <ul>
            <li>Yönetici, ilk kurulumda oluşturulan kullanıcıdır ve tam yetkiye sahiptir.</li>
            <li>Görev geçmişi sekmesinden tüm işlemleri takip edebilirsiniz.</li>
        </ul>

        <h3>📞 10. Destek</h3>
        <ul>
            <li>E-posta: <a href='mailto:mstf.akbal@gmail.com'>mstf.akbal@gmail.com</a></li>
            <li>Telefon: +90 544 748 59 59</li>
            <li>Instagram: <a href='https://instagram.com/mstf.akbal'>@mstf.akbal</a></li>
        </ul>
        """

        instructions_label = QLabel(instructions_text)
        instructions_label.setFont(QFont("Arial", 12))
        instructions_label.setWordWrap(True)
        instructions_label.setTextFormat(Qt.RichText)
        instructions_label.setOpenExternalLinks(True)
        instructions_label.setStyleSheet(
            "background-color: #F9FAFB; border: 1px solid #BDC3C7; border-radius: 5px; padding: 15px;"
            if self.config["theme"] == "Açık Mod" 
            else "background-color: #37474F; border: 1px solid #607D8B; border-radius: 5px; padding: 15px;"
        )

        scroll_area = QScrollArea()
        scroll_area.setWidget(instructions_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #ECF0F1;
                width: 12px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4A90E2;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """ if self.config["theme"] == "Açık Mod" else """
            QScrollBar:vertical {
                border: none;
                background: #455A64;
                width: 12px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #78909C;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        instructions_layout.addWidget(scroll_area)
        instructions_layout.addStretch()
        self.instructions_tab.setLayout(instructions_layout)

        # About Tab
        about_layout = QVBoxLayout()
        about_logo_label = QLabel()
        about_logo_label.setPixmap(QIcon(self.icon_file).pixmap(100, 100))
        about_logo_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_logo_label)

        about_title_label = QLabel(f"{self.config.get('app_name', 'LİMAN HUZUR ve HASTA BAKIM EVİ')}\nPersonel Görev Yöneticisi")
        about_title_label.setFont(QFont("Arial", 14, QFont.Bold))
        about_title_label.setAlignment(Qt.AlignCenter)
        about_title_label.setStyleSheet("color: #2C3E50;" if self.config["theme"] == "Açık Mod" else "color: #CFD8DC;")
        about_layout.addWidget(about_title_label)

        about_version_label = QLabel("Sürüm: 1.0.0\nGeliştirme Tarihi: Şubat 2025")
        about_version_label.setFont(QFont("Arial", 10))
        about_version_label.setAlignment(Qt.AlignCenter)
        about_version_label.setStyleSheet("color: #2C3E50;" if self.config["theme"] == "Açık Mod" else "color: #CFD8DC;")
        about_layout.addWidget(about_version_label)

        about_description_label = QLabel(
            f"{self.config.get('other_info', 'Bu uygulama, hasta bakım evi personellerinin görevlerini planlamak ve WhatsApp üzerinden otomatik bildirimler göndermek için tasarlanmıştır.')}"
        )
        about_description_label.setFont(QFont("Arial", 11))
        about_description_label.setWordWrap(True)
        about_description_label.setAlignment(Qt.AlignCenter)
        about_description_label.setStyleSheet("color: #2C3E50; margin: 10px;" if self.config["theme"] == "Açık Mod" else "color: #CFD8DC; margin: 10px;")
        about_layout.addWidget(about_description_label)

        dev_group = QGroupBox("Geliştirici Bilgileri")
        dev_group.setFont(QFont("Arial", 12, QFont.Bold))
        dev_layout = QFormLayout()

        developer_label = QLabel("Mustafa AKBAL")
        developer_label.setFont(QFont("Arial", 11))
        dev_layout.addRow("Ad:", developer_label)

        email_label = QLabel('<a href="mailto:mstf.akbal@gmail.com" style="color: #3498DB; text-decoration: none;">mstf.akbal@gmail.com</a>')
        email_label.setFont(QFont("Arial", 11))
        email_label.setOpenExternalLinks(True)
        dev_layout.addRow("E-posta:", email_label)

        phone_label = QLabel("+90 544 748 59 59")
        phone_label.setFont(QFont("Arial", 11))
        dev_layout.addRow("Telefon:", phone_label)

        instagram_label = QLabel('<a href="https://instagram.com/mstf.akbal" style="color: #3498DB; text-decoration: none;">@mstf.akbal</a>')
        instagram_label.setFont(QFont("Arial", 11))
        instagram_label.setOpenExternalLinks(True)
        dev_layout.addRow("Instagram:", instagram_label)

        dev_group.setLayout(dev_layout)
        about_layout.addWidget(dev_group)

        copyright_label = QLabel("© 2025 Mustafa AKBAL. Tüm hakları saklıdır.")
        copyright_label.setFont(QFont("Arial", 9))
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #7F8C8D; margin-top: 10px;" if self.config["theme"] == "Açık Mod" else "color: #B0BEC5; margin-top: 10px;")
        about_layout.addWidget(copyright_label)

        about_layout.addStretch()
        self.about_tab.setLayout(about_layout)

        # History Tab
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Görev Açıklaması", "Eylem", "Zaman Damgası", "Kullanıcı"])
        self.update_history_table()
        history_layout.addWidget(self.history_table)
        self.history_tab.setLayout(history_layout)

        self.method_combo.currentTextChanged.connect(self.toggle_method_settings)
        self.toggle_method_settings(self.config["message_method"])

        self.highlight_task_days()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_clock()
        self.timer.start(1000)

    def toggle_method_settings(self, method):
        self.selenium_group.setVisible(method == "Selenium")
        self.api_group.setVisible(method == "WhatsApp API")

    def preview_message_template(self):
        template = self.message_template.toPlainText()
        sample_message = template.format(
            description="Örnek Görev",
            note="Bu bir test notudur",
            category="Hatırlatma",
            priority="Yüksek"
        )
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Mesaj Formatı Önizleme")
        layout = QVBoxLayout()
        preview_text = QTextEdit(sample_message)
        preview_text.setReadOnly(True)
        layout.addWidget(preview_text)
        preview_dialog.setLayout(layout)
        preview_dialog.exec_()

    def send_test_message(self):
        group_name = self.test_group_combo.currentText()
        message = self.test_message.text()
        if not group_name or not message:
            QMessageBox.warning(self, "Hata", "Lütfen bir grup ve test mesajı girin!")
            return
        try:
            if self.config["message_method"] == "Selenium":
                self.send_via_selenium("Test Mesajı", group_name, message, [])
            else:
                self.send_via_api("Test Mesajı", group_name, message, [])
            if self.smtp_server.text() and self.smtp_username.text() and self.notification_email.text():
                self.send_email("Test Mesajı", group_name, message)
            QMessageBox.information(self, "Başarılı", "Test mesajı gönderildi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Test mesajı gönderilemedi: {str(e)}")

    def export_database(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Veritabanını Dışa Aktar", "", "Veritabanı Dosyaları (*.db)")
        if file_path:
            try:
                shutil.copyfile(db_file, file_path)
                QMessageBox.information(self, "Başarılı", "Veritabanı dışa aktarıldı!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Veritabanı dışa aktarılamadı: {str(e)}")

    def import_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Veritabanını İçe Aktar", "", "Veritabanı Dosyaları (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Onay", "Mevcut veritabanı üzerine yazılacak. Devam etmek istiyor musunuz?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    shutil.copyfile(file_path, db_file)
                    self.tasks = self.load_tasks()
                    self.archived_tasks = self.load_archived_tasks()
                    self.groups = self.load_groups()
                    self.patients = self.load_patients()
                    self.task_history = self.load_task_history()
                    self.config, self.logo_data = self.load_config_and_logo()
                    if self.temp_logo_file and os.path.exists(self.temp_logo_file):
                        os.remove(self.temp_logo_file)
                    self.temp_logo_file = os.path.join(tempfile.gettempdir(), 'temp_logo.png')
                    with open(self.temp_logo_file, 'wb') as f:
                        f.write(self.logo_data)
                    self.icon_file = self.temp_logo_file
                    self.update_task_table()
                    self.update_statistics()
                    self.update_history_table()
                    self.update_patient_task_table(None)
                    self.setWindowIcon(QIcon(self.icon_file))
                    self.setWindowTitle(self.config.get("app_name", "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi"))
                    self.init_ui()
                    QMessageBox.information(self, "Başarılı", "Veritabanı içe aktarıldı!")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Veritabanı içe aktarılamadı: {str(e)}")

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(app_path, f"backup_{timestamp}.db")
        try:
            shutil.copyfile(db_file, backup_path)
            QMessageBox.information(self, "Başarılı", f"Yedek oluşturuldu: {backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yedek oluşturulamadı: {str(e)}")

    def export_tasks_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Görevleri Dışa Aktar", "", "CSV Dosyaları (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["patient", "description", "note", "time", "repeat", "duration_type", "duration_value", 
                                  "end_date", "group_name", "status", "category", "priority", "start_date", "files"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for task in self.tasks:
                        writer.writerow({
                            "patient": task.get("patient", "Hasta Yok"),
                            "description": task["description"],
                            "note": task.get("note", ""),
                            "time": ",".join(task["time"]),
                            "repeat": ",".join(task["repeat"]),
                            "duration_type": task.get("duration_type", "Sürekli"),
                            "duration_value": task.get("duration_value", 1),
                            "end_date": task.get("end_date", "Sürekli"),
                            "group_name": task.get("group_name", ""),
                            "status": task["status"],
                            "category": task.get("category", ""),
                            "priority": task.get("priority", "Normal"),
                            "start_date": task.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                            "files": ",".join(task.get("files", []))
                        })
                QMessageBox.information(self, "Başarılı", "Görevler CSV dosyasına dışa aktarıldı!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Görevler dışa aktarılamadı: {str(e)}")

    def import_tasks_from_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Görevleri İçe Aktar", "", "CSV Dosyaları (*.csv)")
        if file_path:
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    required_fields = {"description", "time", "repeat", "group_name"}
                    if not all(field in reader.fieldnames for field in required_fields):
                        QMessageBox.warning(self, "Hata", "CSV dosyasında gerekli alanlar eksik!")
                        return
                    
                    for row in reader:
                        times = row["time"].split(",")
                        repeat_days = row["repeat"].split(",")
                        files = row.get("files", "").split(",") if row.get("files") else []
                        patient = row.get("patient", None) if row.get("patient") and row["patient"] != "Hasta Yok" else None
                        task = {
                            "description": row["description"],
                            "note": row.get("note", ""),
                            "time": times,
                            "repeat": repeat_days,
                            "duration_type": row.get("duration_type", "Sürekli"),
                            "duration_value": int(row.get("duration_value", 1)),
                            "end_date": row.get("end_date", "Sürekli"),
                            "group_name": row["group_name"],
                            "status": "Bekliyor",
                            "category": row.get("category", "Diğer"),
                            "priority": row.get("priority", "Normal"),
                            "start_date": row.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                            "files": files,
                            "patient": patient
                        }
                        self.tasks.append(task)
                        self.save_task_history(task["description"], "CSV'den İçe Aktarıldı", self.current_user)
                self.save_tasks()
                self.sort_tasks("Saate Göre")
                self.schedule_tasks()
                self.update_statistics()
                self.update_history_table()
                self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)
                QMessageBox.information(self, "Başarılı", "Görevler CSV'den başarıyla içe aktarıldı!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"CSV içe aktarma hatası: {str(e)}")

    def save_settings(self):
        self.config["message_method"] = self.method_combo.currentText()
        self.config["search_box_xpath"] = self.search_box_xpath.text()
        self.config["message_box_xpath"] = self.message_box_xpath.text()
        self.config["browser_timeout"] = str(self.browser_timeout.value())
        self.config["post_send_delay"] = str(self.post_send_delay.value())
        self.config["qr_scan_delay"] = str(self.qr_scan_delay.value())
        self.config["chrome_profile_dir"] = self.chrome_profile_dir.text()
        self.config["whatsapp_api_key"] = self.whatsapp_api_key.text()
        self.config["whatsapp_api_phone"] = self.whatsapp_api_phone.text()
        self.config["default_message_template"] = self.message_template.toPlainText()
        self.config["headless"] = self.headless_checkbox.isChecked()
        self.config["window_width"] = self.window_width_spinbox.value()
        self.config["window_height"] = self.window_height_spinbox.value()
        self.config["user_agent"] = self.user_agent_input.text()
        self.config["proxy"] = self.proxy_input.text()
        self.config["disable_notifications"] = self.disable_notifications_checkbox.isChecked()
        self.config["page_load_strategy"] = self.page_load_strategy_combo.currentText()
        self.config["element_wait_time"] = self.element_wait_time_spinbox.value()
        self.config["retry_count"] = self.retry_count_spinbox.value()
        self.config["caption_box_xpath"] = self.caption_box_xpath.text()
        self.config["document_menu_xpath"] = self.document_menu_xpath.text()
        self.config["media_menu_xpath"] = self.media_menu_xpath.text()
        self.config["attachment_button_xpath"] = self.attachment_button_xpath.text()
        self.config["file_input_xpath"] = self.file_input_xpath.text()
        self.config["pre_send_delay"] = self.pre_send_delay.value()
        self.config["smtp_server"] = self.smtp_server.text()
        self.config["smtp_port"] = self.smtp_port.value()
        self.config["smtp_username"] = self.smtp_username.text()
        self.config["smtp_password"] = self.smtp_password.text()
        self.config["notification_email"] = self.notification_email.text()
        self.save_config_and_logo(self.config)
        QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!")
        self.toggle_method_settings(self.config["message_method"])
        self.schedule_tasks()

    def reset_to_defaults(self):
        defaults = self.get_default_config()
        self.method_combo.setCurrentText(defaults["message_method"])
        self.search_box_xpath.setText(defaults["search_box_xpath"])
        self.message_box_xpath.setText(defaults["message_box_xpath"])
        self.browser_timeout.setValue(int(defaults["browser_timeout"]))
        self.post_send_delay.setValue(int(defaults["post_send_delay"]))
        self.qr_scan_delay.setValue(int(defaults["qr_scan_delay"]))
        self.chrome_profile_dir.setText(defaults["chrome_profile_dir"])
        self.whatsapp_api_key.setText(defaults["whatsapp_api_key"])
        self.whatsapp_api_phone.setText(defaults["whatsapp_api_phone"])
        self.message_template.setText(defaults["default_message_template"])
        self.headless_checkbox.setChecked(defaults["headless"])
        self.window_width_spinbox.setValue(defaults["window_width"])
        self.window_height_spinbox.setValue(defaults["window_height"])
        self.user_agent_input.setText(defaults["user_agent"])
        self.proxy_input.setText(defaults["proxy"])
        self.disable_notifications_checkbox.setChecked(defaults["disable_notifications"])
        self.page_load_strategy_combo.setCurrentText(defaults["page_load_strategy"])
        self.element_wait_time_spinbox.setValue(defaults["element_wait_time"])
        self.retry_count_spinbox.setValue(defaults["retry_count"])
        self.caption_box_xpath.setText(defaults["caption_box_xpath"])
        self.document_menu_xpath.setText(defaults["document_menu_xpath"])
        self.media_menu_xpath.setText(defaults["media_menu_xpath"])
        self.attachment_button_xpath.setText(defaults["attachment_button_xpath"])
        self.file_input_xpath.setText(defaults["file_input_xpath"])
        self.pre_send_delay.setValue(defaults["pre_send_delay"])
        self.smtp_server.setText(defaults["smtp_server"])
        self.smtp_port.setValue(defaults["smtp_port"])
        self.smtp_username.setText(defaults["smtp_username"])
        self.smtp_password.setText(defaults["smtp_password"])
        self.notification_email.setText(defaults["notification_email"])
        self.config = defaults.copy()
        with open(default_icon_file, 'rb') as f:
            self.logo_data = f.read()
        self.save_config_and_logo(self.config, self.logo_data, "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi", "")
        if self.temp_logo_file and os.path.exists(self.temp_logo_file):
            os.remove(self.temp_logo_file)
        self.temp_logo_file = os.path.join(tempfile.gettempdir(), 'temp_logo.png')
        with open(self.temp_logo_file, 'wb') as f:
            f.write(self.logo_data)
        self.icon_file = self.temp_logo_file
        QMessageBox.information(self, "Başarılı", "Ayarlar varsayılana sıfırlandı!")
        self.toggle_method_settings(self.config["message_method"])
        self.setWindowIcon(QIcon(self.icon_file))
        self.setWindowTitle(self.config.get("app_name", "LİMAN HUZUR ve HASTA BAKIM EVİ Personel Görev Yöneticisi"))
        self.update_patient_task_table(None)
        self.init_ui()

    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Dosya Seç", "", "Dosyalar (*.png *.jpg *.pdf *.txt)")
        for file_path in file_paths:
            if file_path not in [self.task_files_list.item(i).text() for i in range(self.task_files_list.count())]:
                self.task_files_list.addItem(file_path)

    def remove_file(self):
        selected_items = self.task_files_list.selectedItems()
        for item in selected_items:
            self.task_files_list.takeItem(self.task_files_list.row(item))

    def add_emoji(self, emoji):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QTextEdit):
            cursor = focused_widget.textCursor()
            cursor.insertText(emoji)
            focused_widget.setTextCursor(cursor)
        else:
            cursor = self.task_description_input.textCursor()
            cursor.insertText(emoji)
            self.task_description_input.setTextCursor(cursor)

    def show_tasks_for_date(self, date):
        self.calendar_task_list.clear()
        selected_date = date.toString("yyyy-MM-dd")
        daily_tasks = []
        for task in self.tasks:
            if task["start_date"] <= selected_date and (task["end_date"] == "Sürekli" or task["end_date"] >= selected_date):
                today = datetime.strptime(selected_date, "%Y-%m-%d").weekday()
                days_map = {"Pazartesi": 0, "Salı": 1, "Çarşamba": 2, "Perşembe": 3, "Cuma": 4, "Cumartesi": 5, "Pazar": 6}
                if "Hergün" in task["repeat"] or any(days_map.get(day) == today for day in task["repeat"]):
                    patient_info = f" - Hasta: {task['patient']}" if task.get("patient") else ""
                    task_info = (
                        f"📋 {task['description']}{patient_info} - Saat: {', '.join(task['time'])} "
                        f"- Kategori: {task['category']} - Öncelik: {task['priority']}"
                    )
                    daily_tasks.append(task_info)
        
        if daily_tasks:
            for task_info in daily_tasks:
                self.calendar_task_list.addItem(task_info)
        else:
            self.calendar_task_list.addItem("Bu tarihte görev bulunmamaktadır.")
        
        self.daily_task_count.setText(f"Günlük Görev Sayısı: {len(daily_tasks)}")

    def highlight_task_days(self):
        format = QTextCharFormat()
        format.setBackground(QColor("#FFFF99"))
        for task in self.tasks:
            start_date = QDate.fromString(task["start_date"], "yyyy-MM-dd")
            end_date = QDate.fromString(task["end_date"], "yyyy-MM-dd") if task["end_date"] != "Sürekli" else QDate.currentDate().addYears(1)
            current_date = start_date
            while current_date <= end_date:
                self.calendar.setDateTextFormat(current_date, format)
                current_date = current_date.addDays(1)

    def add_time(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Saat Seç")
        layout = QVBoxLayout()
        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        layout.addWidget(time_edit)
        ok_button = QPushButton("Tamam")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            time_str = time_edit.time().toString("HH:mm")
            if time_str not in [self.task_time_list.item(i).text() for i in range(self.task_time_list.count())]:
                self.task_time_list.addItem(time_str)

    def remove_time(self):
        selected_items = self.task_time_list.selectedItems()
        for item in selected_items:
            self.task_time_list.takeItem(self.task_time_list.row(item))

    def filter_tasks(self):
        selected_category = self.filter_category_combo.currentText()
        selected_priority = self.filter_priority_combo.currentText()
        selected_status = self.filter_status_combo.currentText()
        filtered_tasks = [task for task in self.tasks if
                          (selected_category == "Tümü" or task.get("category", "") == selected_category) and
                          (selected_priority == "Tümü" or task.get("priority", "") == selected_priority) and
                          (selected_status == "Tümü" or task.get("status", "") == selected_status)]
        self.sort_tasks(self.sort_combo.currentText(), filtered_tasks)

    def sort_tasks(self, sort_criteria, tasks=None):
        if tasks is None:
            tasks = self.tasks.copy()
        if sort_criteria == "Saate Göre":
            tasks.sort(key=lambda x: min(x["time"]) if x["time"] else "00:00")
        elif sort_criteria == "Kuruma Göre":
            tasks.sort(key=lambda x: x.get("group_name", ""))
        elif sort_criteria == "Hasta Adına Göre":
            tasks.sort(key=lambda x: x.get("patient", "z") or "z")  # "z" ensures None values go to the end
        self.update_task_table(tasks)

    def change_theme(self, theme_name):
        self.setStyleSheet(self.themes[theme_name])
        self.config["theme"] = theme_name
        self.save_config_and_logo(self.config)
        self.init_ui()

    def delete_group(self):
        selected_group = self.group_combo.currentText()
        if not selected_group:
            return
        password, ok = QInputDialog.getText(self, "Şifre Doğrulama", "Şifrenizi girin:", QLineEdit.Password)
        if ok and any(self.users[user]["password"] == password for user in self.users):
            related_tasks = [task for task in self.tasks if task.get("group_name") == selected_group]
            if related_tasks:
                reply = QMessageBox.question(self, "Onay", "İlişkili görevler arşive taşınsın mı?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.archived_tasks.extend(related_tasks)
                    self.tasks = [task for task in self.tasks if task.get("group_name") != selected_group]
                    self.save_tasks()
                    self.save_archived_tasks()
            self.groups.remove(selected_group)
            self.group_combo.clear()
            self.group_combo.addItems(self.groups)
            self.save_groups()

    def clear_form(self):
        self.task_template_combo.setCurrentIndex(0)
        self.task_description_input.clear()
        self.task_note_input.clear()
        self.task_time_list.clear()
        self.task_files_list.clear()
        for checkbox in self.day_checkboxes.values():
            checkbox.setChecked(False)
        self.task_duration_input.setCurrentIndex(0)
        self.task_duration_spinbox.setValue(1)
        self.task_end_date_input.setDate(datetime.now().date())
        self.task_end_date_checkbox.setChecked(False)
        self.task_start_date_input.setDate(datetime.now().date())
        self.task_category_combo.setCurrentIndex(0)
        self.task_priority_combo.setCurrentIndex(0)
        self.task_patient_combo.setCurrentIndex(0)

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d.%m.%Y")
        self.clock_label.setText(current_time)
        self.date_label.setText(current_date)
        self.status_label.setText(f"Bugün Gönderilen: {len([t for t in self.tasks if t['status'] == 'Gönderildi'])}")
        self.update_statistics()

    def update_duration_spinbox(self):
        duration_type = self.task_duration_input.currentText()
        self.task_duration_spinbox.setEnabled(duration_type != "Sürekli")
        if duration_type == "Günlük":
            self.task_duration_spinbox.setMaximum(365)
        elif duration_type == "Haftalık":
            self.task_duration_spinbox.setMaximum(52)
        elif duration_type == "Aylık":
            self.task_duration_spinbox.setMaximum(12)

    def toggle_end_date_input(self):
        self.task_end_date_input.setEnabled(self.task_end_date_checkbox.isChecked())

    def add_group(self):
        group_name, ok = QInputDialog.getText(self, "Kurum Ekle", "Kurum Adı:")
        if ok and group_name and group_name not in self.groups:
            self.groups.append(group_name)
            self.group_combo.addItem(group_name)
            self.save_groups()

    def get_selected_days(self):
        return [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]

    def add_task(self):
        description = self.task_description_input.toPlainText()
        note = self.task_note_input.toPlainText()
        times = [self.task_time_list.item(i).text() for i in range(self.task_time_list.count())]
        repeat_days = self.get_selected_days()
        duration_type = self.task_duration_input.currentText()
        duration_value = self.task_duration_spinbox.value() if duration_type != "Sürekli" else 1
        end_date = self.task_end_date_input.date().toString("yyyy-MM-dd") if self.task_end_date_checkbox.isChecked() else "Sürekli"
        group_name = self.group_combo.currentText()
        category = self.task_category_combo.currentText()
        priority = self.task_priority_combo.currentText()
        start_date = self.task_start_date_input.date().toString("yyyy-MM-dd")
        files = [self.task_files_list.item(i).text() for i in range(self.task_files_list.count())]
        patient = self.task_patient_combo.currentText() if self.task_patient_combo.currentText() != "Hasta Yok" else None

        if not description or not times or not repeat_days or not group_name:
            QMessageBox.warning(self, "Hata", "Görev açıklaması, saatler, tekrar günleri ve grup adı boş olamaz!")
            return

        task = {
            "description": description,
            "note": note,
            "time": times,
            "repeat": repeat_days,
            "duration_type": duration_type,
            "duration_value": duration_value,
            "end_date": end_date,
            "group_name": group_name,
            "status": "Bekliyor",
            "category": category,
            "priority": priority,
            "start_date": start_date,
            "files": files,
            "patient": patient
        }
        self.tasks.append(task)
        self.save_tasks()
        self.save_task_history(description, "Görev Eklendi", self.current_user)
        self.sort_tasks("Saate Göre")
        self.clear_form()
        self.schedule_tasks()
        self.update_statistics()
        self.update_history_table()
        self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def update_task_table(self, tasks=None):
        if tasks is None:
            tasks = self.tasks
        self.task_table.setRowCount(len(tasks))
        self.task_table.setColumnCount(13)
        self.task_table.setHorizontalHeaderLabels([
            "Hasta", "Görev\nAçıklaması", "Not", "Saatler", "Tekrar\nGünleri", "Görev\nSüresi", 
            "Bitiş\nTarihi", "Kurum\nAdı", "Durum", "Kategori", "Öncelik", "Başlangıç\nTarihi", 
            "Dosyalar"
        ])
        
        for i, task in enumerate(tasks):
            items = [
                QTableWidgetItem(task.get("patient", "Hasta Yok")),
                QTableWidgetItem(task["description"]),
                QTableWidgetItem(task.get("note", "")),
                QTableWidgetItem(", ".join(task["time"])),
                QTableWidgetItem(", ".join(task["repeat"])),
                QTableWidgetItem(task.get("duration_type", "Sürekli")),
                QTableWidgetItem(task.get("end_date", "Sürekli")),
                QTableWidgetItem(task.get("group_name", "")),
                QTableWidgetItem(task["status"]),
                QTableWidgetItem(task.get("category", "")),
                QTableWidgetItem(task.get("priority", "Düşük")),
                QTableWidgetItem(task.get("start_date", datetime.now().strftime("%Y-%m-%d"))),
                QTableWidgetItem(", ".join(task.get("files", [])))
            ]

            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.task_table.setItem(i, j, item)

                priority = task.get("priority", "Düşük")
                priority_color = QColor(255, 99, 71) if priority == "Yüksek" else QColor(255, 193, 7) if priority == "Orta" else QColor(144, 238, 144)
                status = task["status"]
                status_color = QColor(0, 255, 0) if status == "Gönderildi" else QColor(255, 0, 0) if status == "Gönderilemedi" else QColor(255, 255, 255)
                item.setBackground(priority_color if j != 8 else status_color)
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.task_table.setWordWrap(True)
        self.task_table.resizeRowsToContents()
        for row in range(self.task_table.rowCount()):
            if self.task_table.rowHeight(row) > 50:
                self.task_table.setRowHeight(row, 50)
        header = self.task_table.horizontalHeader()
        for i in range(self.task_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setMaximumSectionSize(300)
        self.task_table.setMinimumWidth(1200)

    def load_task_for_edit(self, row, column):
        if column != 1:  # Only load when clicking "Görev Açıklaması" (column 1)
            return
        task = self.tasks[row]
        self.task_description_input.setPlainText(task["description"])
        self.task_note_input.setPlainText(task.get("note", ""))
        self.task_time_list.clear()
        for time_str in task["time"]:
            self.task_time_list.addItem(time_str)
        self.task_files_list.clear()
        for file_path in task.get("files", []):
            self.task_files_list.addItem(file_path)
        for day in task["repeat"]:
            if day in self.day_checkboxes:
                self.day_checkboxes[day].setChecked(True)
        self.task_duration_input.setCurrentText(task.get("duration_type", "Sürekli"))
        self.task_duration_spinbox.setValue(task.get("duration_value", 1))
        if task.get("end_date", "Sürekli") != "Sürekli":
            self.task_end_date_input.setDate(QDate.fromString(task["end_date"], "yyyy-MM-dd"))
            self.task_end_date_checkbox.setChecked(True)
        else:
            self.task_end_date_checkbox.setChecked(False)
        self.task_start_date_input.setDate(QDate.fromString(task.get("start_date", datetime.now().strftime("%Y-%m-%d")), "yyyy-MM-dd"))
        self.group_combo.setCurrentText(task.get("group_name", ""))
        self.task_category_combo.setCurrentText(task.get("category", ""))
        self.task_priority_combo.setCurrentText(task.get("priority", "Düşük"))
        self.task_patient_combo.setCurrentText(task.get("patient", "Hasta Yok"))

    def show_task_details(self, row, column):
        task = self.tasks[row]
        dialog = TaskEditDialog(task, self.patients, self)
        if dialog.exec_() == QDialog.Accepted:
            self.save_tasks()
            self.save_task_history(task["description"], "Görev Güncellendi", self.current_user)
            self.sort_tasks("Saate Göre")
            self.update_statistics()
            self.update_history_table()
            self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def edit_task(self):
        selected_row = self.task_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen düzenlemek için bir görev seçin!")
            return
        description = self.task_description_input.toPlainText()
        note = self.task_note_input.toPlainText()
        times = [self.task_time_list.item(i).text() for i in range(self.task_time_list.count())]
        repeat_days = self.get_selected_days()
        duration_type = self.task_duration_input.currentText()
        duration_value = self.task_duration_spinbox.value()
        end_date = self.task_end_date_input.date().toString("yyyy-MM-dd") if self.task_end_date_checkbox.isChecked() else "Sürekli"
        group_name = self.group_combo.currentText()
        category = self.task_category_combo.currentText()
        priority = self.task_priority_combo.currentText()
        start_date = self.task_start_date_input.date().toString("yyyy-MM-dd")
        files = [self.task_files_list.item(i).text() for i in range(self.task_files_list.count())]
        patient = self.task_patient_combo.currentText() if self.task_patient_combo.currentText() != "Hasta Yok" else None

        if not description or not times or not repeat_days or not group_name:
            QMessageBox.warning(self, "Hata", "Görev açıklaması, saatler, tekrar günleri ve grup adı boş olamaz!")
            return

        task = {
            "description": description,
            "note": note,
            "time": times,
            "repeat": repeat_days,
            "duration_type": duration_type,
            "duration_value": duration_value,
            "end_date": end_date,
            "group_name": group_name,
            "status": "Bekliyor",
            "category": category,
            "priority": priority,
            "start_date": start_date,
            "files": files,
            "patient": patient
        }
        self.tasks[selected_row] = task
        self.save_tasks()
        self.save_task_history(description, "Görev Güncellendi", self.current_user)
        self.sort_tasks("Saate Göre")
        self.clear_form()
        self.schedule_tasks()
        self.update_statistics()
        self.update_history_table()
        self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def preview_task(self):
        description = self.task_description_input.toPlainText()
        note = self.task_note_input.toPlainText()
        category = self.task_category_combo.currentText()
        priority = self.task_priority_combo.currentText()
        patient = self.task_patient_combo.currentText() if self.task_patient_combo.currentText() != "Hasta Yok" else None
        files = [self.task_files_list.item(i).text() for i in range(self.task_files_list.count())]
        message = self.config["default_message_template"].format(description=description, note=note, category=category, priority=priority)
        if patient:
            message += f"\n\n👤 Hasta: {patient}"
        if files:
            message += "\n\n📎 Ek Dosyalar: " + ", ".join(files)
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Görev Önizleme")
        layout = QVBoxLayout()
        preview_text = QTextEdit(message)
        preview_text.setReadOnly(True)
        layout.addWidget(preview_text)
        preview_dialog.setLayout(layout)
        preview_dialog.exec_()

    def delete_task(self):
        selected_row = self.task_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silmek için bir görev seçin!")
            return
        reply = QMessageBox.question(self, "Onay", "Bu görevi silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            description = self.tasks[selected_row]["description"]
            self.tasks.pop(selected_row)
            self.save_tasks()
            self.save_task_history(description, "Görev Silindi", self.current_user)
            self.sort_tasks("Saate Göre")
            self.clear_form()
            self.update_statistics()
            self.update_history_table()
            self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def show_all_tasks_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tüm Görevler")
        dialog.setMinimumSize(1000, 600)
        dialog.setStyleSheet(self.themes[self.config["theme"]])
        layout = QVBoxLayout()

        tasks_table = QTableWidget()
        tasks_table.setColumnCount(13)
        tasks_table.setHorizontalHeaderLabels([
            "Hasta", "Görev Açıklaması", "Not", "Saatler", "Tekrar Günleri", "Görev Süresi", 
            "Bitiş Tarihi", "Kurum Adı", "Durum", "Kategori", "Öncelik", "Başlangıç Tarihi", 
            "Dosyalar"
        ])
        tasks_table.setRowCount(len(self.tasks))
        
        for i, task in enumerate(self.tasks):
            items = [
                QTableWidgetItem(task.get("patient", "Hasta Yok")),
                QTableWidgetItem(task["description"]),
                QTableWidgetItem(task.get("note", "")),
                QTableWidgetItem(", ".join(task["time"])),
                QTableWidgetItem(", ".join(task["repeat"])),
                QTableWidgetItem(task.get("duration_type", "Sürekli")),
                QTableWidgetItem(task.get("end_date", "Sürekli")),
                QTableWidgetItem(task.get("group_name", "")),
                QTableWidgetItem(task["status"]),
                QTableWidgetItem(task.get("category", "")),
                QTableWidgetItem(task.get("priority", "Düşük")),
                QTableWidgetItem(task.get("start_date", datetime.now().strftime("%Y-%m-%d"))),
                QTableWidgetItem(", ".join(task.get("files", [])))
            ]
            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tasks_table.setItem(i, j, item)

        tasks_table.setWordWrap(True)
        tasks_table.resizeRowsToContents()
        for row in range(tasks_table.rowCount()):
            if tasks_table.rowHeight(row) > 50:
                tasks_table.setRowHeight(row, 50)
        tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for i in range(tasks_table.columnCount()):
            tasks_table.horizontalHeader().setMaximumSectionSize(300)
        
        tasks_table.cellDoubleClicked.connect(self.show_task_details)

        layout.addWidget(tasks_table)
        dialog.setLayout(layout)
        dialog.exec_()

    def schedule_tasks(self):
        schedule.clear()
        for task in self.tasks:
            if task["status"] == "Bekliyor" and task["start_date"] <= datetime.now().strftime("%Y-%m-%d"):
                for time_str in task["time"]:
                    task_time = datetime.strptime(time_str, "%H:%M")
                    now = datetime.now()
                    scheduled_time = now.replace(hour=task_time.hour, minute=task_time.minute, second=0, microsecond=0)
                    if scheduled_time < now:
                        scheduled_time += timedelta(days=1)
                    time_diff = (scheduled_time - now).total_seconds() / 60
                    pre_send_delay = self.config["pre_send_delay"]
                    if time_diff > pre_send_delay:
                        send_time = (scheduled_time - timedelta(minutes=pre_send_delay)).strftime("%H:%M")
                        schedule.every().day.at(send_time).do(self.send_whatsapp_message, task["description"], task["group_name"])
                    else:
                        schedule.every().day.at(time_str).do(self.send_whatsapp_message, task["description"], task["group_name"])

    def send_whatsapp_message(self, description, group_name):
        task = next((task for task in self.tasks if task["description"] == description), None)
        if task and task["status"] == "Bekliyor":
            message = self.config["default_message_template"].format(
                description=description, 
                note=task.get("note", ""),
                category=task.get("category", ""),
                priority=task.get("priority", "")
            )
            if task.get("patient"):
                message += f"\n\n👤 Hasta: {task['patient']}"
            try:
                if self.config["message_method"] == "Selenium":
                    self.send_via_selenium(description, group_name, message, task["files"])
                else:
                    self.send_via_api(description, group_name, message, task["files"])
                if self.smtp_server.text() and self.smtp_username.text() and self.notification_email.text():
                    self.send_email(description, group_name, message)
                self.update_task_status(description, "Gönderildi")
                self.save_task_history(description, "Mesaj Gönderildi", self.current_user)
            except Exception as e:
                self.update_task_status(description, "Gönderilemedi")
                self.save_task_history(description, f"Mesaj Gönderilemedi: {str(e)}", self.current_user)
            self.update_history_table()
            self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def send_via_selenium(self, description, group_name, message, files):
        if self.driver is None or not self.driver.window_handles:
            self.driver = self.init_browser()
        
        try:
            self.driver.get("https://web.whatsapp.com")
            wait = WebDriverWait(self.driver, int(self.config["element_wait_time"]))
            retry_count = self.config["retry_count"]
            for attempt in range(retry_count):
                try:
                    search_box = wait.until(EC.presence_of_element_located((By.XPATH, self.config["search_box_xpath"])))
                    search_box.clear()
                    search_box.send_keys(group_name)
                    time.sleep(2)
                    search_box.send_keys(Keys.ENTER)

                    if files:
                        for file_path in files:
                            file_extension = os.path.splitext(file_path)[1].lower()
                            attachment_button = wait.until(EC.element_to_be_clickable((By.XPATH, self.config["attachment_button_xpath"])))
                            attachment_button.click()
                            time.sleep(1)
                            
                            if file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mov", ".avi", ".mkv"]:
                                menu_option = wait.until(EC.element_to_be_clickable((By.XPATH, self.config["media_menu_xpath"])))
                            elif file_extension in [".pdf", ".doc", ".docx", ".txt"]:
                                menu_option = wait.until(EC.element_to_be_clickable((By.XPATH, self.config["document_menu_xpath"])))
                            else:
                                logging.warning(f"Bilinmeyen dosya türü: {file_extension}")
                                menu_option = wait.until(EC.element_to_be_clickable((By.XPATH, self.config["document_menu_xpath"])))
                            
                            menu_option.click()
                            time.sleep(1)
                            
                            file_input = wait.until(EC.presence_of_element_located((By.XPATH, self.config["file_input_xpath"])))
                            file_input.send_keys(file_path)
                            time.sleep(2)
                            
                            caption_box = wait.until(EC.presence_of_element_located((By.XPATH, self.config["caption_box_xpath"])))
                            pyperclip.copy(message)
                            caption_box.send_keys(Keys.COMMAND + "v" if platform.system() == "Darwin" else Keys.CONTROL + "v")
                            time.sleep(1)
                            
                            caption_box.send_keys(Keys.ENTER)
                            time.sleep(int(self.config["post_send_delay"]))
                            
                            time.sleep(5)
                            pyautogui.press("esc")
                            time.sleep(1)
                    else:
                        message_box = wait.until(EC.presence_of_element_located((By.XPATH, self.config["message_box_xpath"])))
                        pyperclip.copy(message)
                        message_box.send_keys(Keys.COMMAND + "v" if platform.system() == "Darwin" else Keys.CONTROL + "v")
                        message_box.send_keys(Keys.ENTER)
                        time.sleep(int(self.config["post_send_delay"]))
                    
                    break
                except Exception as e:
                    logging.error(f"Mesaj gönderme hatası (Deneme {attempt + 1}/{retry_count}): {str(e)}")
                    if attempt == retry_count - 1:
                        raise Exception("Mesaj gönderilemedi")
                    time.sleep(5)
        except NoSuchWindowException:
            logging.error("Tarayıcı penceresi kapandı, yeniden başlatılıyor...")
            self.driver = self.init_browser()
            self.send_via_selenium(description, group_name, message, files)

    def send_via_api(self, description, group_name, message, files):
        api_key = self.config["whatsapp_api_key"]
        phone_id = self.config["whatsapp_api_phone"]
        url = f"https://graph.facebook.com/v13.0/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": group_name,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            for file_path in files:
                file_extension = os.path.splitext(file_path)[1].lower()
                file_type = "image" if file_extension in [".jpg", ".jpeg", ".png"] else "document"
                with open(file_path, "rb") as f:
                    files_payload = {"file": (os.path.basename(file_path), f, file_type)}
                    files_response = requests.post(f"https://graph.facebook.com/v13.0/{phone_id}/media", headers={"Authorization": f"Bearer {api_key}"}, files=files_payload)
                    if files_response.status_code == 200:
                        media_id = files_response.json()["id"]
                        media_payload = {
                            "messaging_product": "whatsapp",
                            "to": group_name,
                            "type": file_type,
                            file_type: {"id": media_id}
                        }
                        requests.post(url, headers=headers, json=media_payload)
        else:
            raise Exception(f"API hatası: {response.text}")

    def send_email(self, description, group_name, message):
        try:
            recipient = self.config["notification_email"]
            if not recipient:
                logging.warning("Bildirim e-posta adresi bulunamadı.")
                return

            msg = MIMEText(message)
            msg["Subject"] = f"Görev: {description}"
            msg["From"] = self.config["smtp_username"]
            msg["To"] = recipient

            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["smtp_username"], self.config["smtp_password"])
                server.send_message(msg)
            logging.info(f"{recipient} adresine e-posta gönderildi.")
        except Exception as e:
            logging.error(f"E-posta gönderilemedi: {str(e)}")

    def init_browser(self):
        if self.driver is not None:
            self.driver.quit()
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={self.config['chrome_profile_dir']}")
        if self.config["headless"]:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--window-size={self.config['window_width']},{self.config['window_height']}")
        chrome_options.add_argument(f"--user-agent={self.config['user_agent']}")
        if self.config["proxy"]:
            chrome_options.add_argument(f"--proxy-server={self.config['proxy']}")
        if self.config["disable_notifications"]:
            chrome_options.add_argument("--disable-notifications")
        chrome_options.page_load_strategy = self.config["page_load_strategy"]
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.get("https://web.whatsapp.com")
        time.sleep(int(self.config["qr_scan_delay"]))
        return self.driver

    def update_task_status(self, description, status):
        for task in self.tasks:
            if task["description"] == description:
                task["status"] = status
                break
        self.save_tasks()
        self.sort_tasks("Saate Göre")
        self.update_statistics()
        self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def update_statistics(self):
        sent_count = len([t for t in self.tasks if t['status'] == 'Gönderildi'])
        failed_count = len([t for t in self.tasks if t['status'] == 'Gönderilemedi'])
        total_tasks = len(self.tasks)
        completion_rate = (sent_count / total_tasks * 100) if total_tasks > 0 else 0

        self.sent_label.setText(f"Gönderilen Görevler: {sent_count}")
        self.failed_label.setText(f"Gönderilemeyen Görevler: {failed_count}")
        self.completion_rate_label.setText(f"Görev Tamamlanma Oranı: {completion_rate:.2f}%")

        category_counts = {cat: 0 for cat in self.categories}
        for task in self.tasks:
            category = task.get("category", "Diğer")
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts["Diğer"] += 1
        category_text = "\n".join([f"{cat}: {count}" for cat, count in category_counts.items()])
        self.category_label.setText(f"Kategorilere Göre Görevler:\n{category_text}")

        priority_counts = {pri: 0 for pri in self.priorities}
        for task in self.tasks:
            priority = task.get("priority", "Normal")
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts["Normal"] += 1
        priority_text = "\n".join([f"{pri}: {count}" for pri, count in priority_counts.items()])
        self.priority_label.setText(f"Önceliklere Göre Görevler:\n{priority_text}")

    def update_history_table(self):
        self.history_table.setRowCount(len(self.task_history))
        for i, entry in enumerate(self.task_history):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry["description"]))
            self.history_table.setItem(i, 1, QTableWidgetItem(entry["action"]))
            self.history_table.setItem(i, 2, QTableWidgetItem(entry["timestamp"]))
            self.history_table.setItem(i, 3, QTableWidgetItem(entry["user"]))
            for j in range(4):
                item = self.history_table.item(i, j)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.history_table.resizeRowsToContents()
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def reset_colors_daily(self):
        def reset():
            for task in self.tasks:
                if task["status"] != "Gönderildi":
                    task["status"] = "Bekliyor"
            self.save_tasks()
            self.sort_tasks("Saate Göre")
            self.update_statistics()
            self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)
        schedule.every().day.at("00:00").do(reset)

    def start_scheduler(self):
        self.scheduler_thread = SchedulerThread(self)
        self.scheduler_thread.start()

    def show_archived_tasks(self):
        archived_dialog = QDialog(self)
        archived_dialog.setWindowTitle("Arşivlenen Görevler")
        layout = QVBoxLayout()
        archived_table = QTableWidget()
        archived_table.setColumnCount(13)
        archived_table.setHorizontalHeaderLabels([
            "Hasta", "Görev Açıklaması", "Not", "Saatler", "Tekrar Günleri", "Görev Süresi", 
            "Bitiş Tarihi", "Kurum Adı", "Durum", "Kategori", "Öncelik", "Başlangıç Tarihi", 
            "Dosyalar"
        ])
        archived_table.setRowCount(len(self.archived_tasks))
        for i, task in enumerate(self.archived_tasks):
            items = [
                QTableWidgetItem(task.get("patient", "Hasta Yok")),
                QTableWidgetItem(task["description"]),
                QTableWidgetItem(task.get("note", "")),
                QTableWidgetItem(", ".join(task["time"])),
                QTableWidgetItem(", ".join(task["repeat"])),
                QTableWidgetItem(task.get("duration_type", "Sürekli")),
                QTableWidgetItem(task.get("end_date", "Sürekli")),
                QTableWidgetItem(task.get("group_name", "")),
                QTableWidgetItem(task["status"]),
                QTableWidgetItem(task.get("category", "")),
                QTableWidgetItem(task.get("priority", "Düşük")),
                QTableWidgetItem(task.get("start_date", datetime.now().strftime("%Y-%m-%d"))),
                QTableWidgetItem(", ".join(task.get("files", [])))
            ]
            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                archived_table.setItem(i, j, item)

        layout.addWidget(archived_table)
        archived_dialog.setLayout(layout)
        archived_dialog.exec_()

    def archive_selected_task(self):
        selected_row = self.task_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen arşive taşımak için bir görev seçin!")
            return
        task = self.tasks.pop(selected_row)
        self.archived_tasks.append(task)
        self.save_tasks()
        self.save_archived_tasks()
        self.save_task_history(task["description"], "Görev Arşivlendi", self.current_user)
        self.update_task_table()
        self.update_statistics()
        self.update_history_table()
        self.update_patient_task_table(self.patient_list.currentItem().text() if self.patient_list.currentItem() else None)

    def save_as_template(self):
        name, ok = QInputDialog.getText(self, "Şablon Kaydet", "Şablon Adı:")
        if ok and name:
            description = self.task_description_input.toPlainText()
            note = self.task_note_input.toPlainText()
            times = [self.task_time_list.item(i).text() for i in range(self.task_time_list.count())]
            repeat_days = self.get_selected_days()
            duration_type = self.task_duration_input.currentText()
            duration_value = self.task_duration_spinbox.value()
            category = self.task_category_combo.currentText()
            priority = self.task_priority_combo.currentText()
            files = [self.task_files_list.item(i).text() for i in range(self.task_files_list.count())]
            patient = self.task_patient_combo.currentText() if self.task_patient_combo.currentText() != "Hasta Yok" else None

            if not description or not times or not repeat_days:
                QMessageBox.warning(self, "Hata", "Görev açıklaması, saatler ve tekrar günleri boş olamaz!")
                return

            template = {
                "name": name,
                "description": description,
                "note": note,
                "time": times,
                "repeat": repeat_days,
                "duration_type": duration_type,
                "duration_value": duration_value,
                "category": category,
                "priority": priority,
                "files": files,
                "patient": patient
            }
            templates = self.load_task_templates()
            templates.append(template)
            self.save_task_templates(templates)
            self.task_template_combo.addItem(name)
            QMessageBox.information(self, "Başarılı", f"'{name}' şablonu kaydedildi!")

    def load_template(self, template_name):
        if template_name == "Şablon Seçiniz":
            self.clear_form()
            return
        templates = self.load_task_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        if template:
            self.task_description_input.setPlainText(template["description"])
            self.task_note_input.setPlainText(template.get("note", ""))
            self.task_time_list.clear()
            for time_str in template["time"]:
                self.task_time_list.addItem(time_str)
            self.task_files_list.clear()
            for file_path in template.get("files", []):
                self.task_files_list.addItem(file_path)
            for day in template["repeat"]:
                if day in self.day_checkboxes:
                    self.day_checkboxes[day].setChecked(True)
            self.task_duration_input.setCurrentText(template.get("duration_type", "Sürekli"))
            self.task_duration_spinbox.setValue(template.get("duration_value", 1))
            self.task_category_combo.setCurrentText(template.get("category", ""))
            self.task_priority_combo.setCurrentText(template.get("priority", "Düşük"))
            self.task_patient_combo.setCurrentText(template.get("patient", "Hasta Yok"))

    def show_patient_tasks(self, item):
        if item:
            patient_name = item.text()
            self.update_patient_task_table(patient_name)
        else:
            self.update_patient_task_table(None)

    def update_patient_task_table(self, patient_name):
        self.patient_task_table.setRowCount(0)
        if not patient_name:
            return
        
        patient_tasks = [task for task in self.tasks if task.get("patient") == patient_name]
        self.patient_task_table.setRowCount(len(patient_tasks))
        
        for i, task in enumerate(patient_tasks):
            items = [
                QTableWidgetItem(task.get("patient", "Hasta Yok")),
                QTableWidgetItem(task["description"]),
                QTableWidgetItem(task.get("note", "")),
                QTableWidgetItem(", ".join(task["time"])),
                QTableWidgetItem(", ".join(task["repeat"])),
                QTableWidgetItem(task.get("duration_type", "Sürekli")),
                QTableWidgetItem(task.get("end_date", "Sürekli")),
                QTableWidgetItem(task.get("group_name", "")),
                QTableWidgetItem(task["status"]),
                QTableWidgetItem(task.get("category", "")),
                QTableWidgetItem(task.get("priority", "Düşük")),
                QTableWidgetItem(task.get("start_date", datetime.now().strftime("%Y-%m-%d"))),
                QTableWidgetItem(", ".join(task.get("files", [])))
            ]

            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.patient_task_table.setItem(i, j, item)

                priority = task.get("priority", "Düşük")
                priority_color = QColor(255, 99, 71) if priority == "Yüksek" else QColor(255, 193, 7) if priority == "Orta" else QColor(144, 238, 144)
                status = task["status"]
                status_color = QColor(0, 255, 0) if status == "Gönderildi" else QColor(255, 0, 0) if status == "Gönderilemedi" else QColor(255, 255, 255)
                item.setBackground(priority_color if j != 8 else status_color)
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.patient_task_table.setWordWrap(True)
        self.patient_task_table.resizeRowsToContents()
        for row in range(self.patient_task_table.rowCount()):
            if self.patient_task_table.rowHeight(row) > 50:
                self.patient_task_table.setRowHeight(row, 50)
        header = self.patient_task_table.horizontalHeader()
        for i in range(self.patient_task_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setMaximumSectionSize(300)
        self.patient_task_table.setMinimumWidth(1200)

    def show_patient_task_details(self, row, column):
        patient_tasks = [task for task in self.tasks if task.get("patient") == self.patient_list.currentItem().text()]
        if row < len(patient_tasks):
            task = patient_tasks[row]
            dialog = TaskEditDialog(task, self.patients, self)
            if dialog.exec_() == QDialog.Accepted:
                self.save_tasks()
                self.save_task_history(task["description"], "Görev Güncellendi", self.current_user)
                self.sort_tasks("Saate Göre")
                self.update_statistics()
                self.update_history_table()
                self.update_patient_task_table(self.patient_list.currentItem().text())

    def closeEvent(self, event):
        self.save_tasks()
        self.save_archived_tasks()
        if self.driver:
            self.driver.quit()
        if hasattr(self, 'scheduler_thread') and self.scheduler_thread.isRunning():
            self.scheduler_thread.stop()
            self.scheduler_thread.wait()
        if self.temp_logo_file and os.path.exists(self.temp_logo_file):
            os.remove(self.temp_logo_file)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppSchedulerApp()
    window.show()
    sys.exit(app.exec_())