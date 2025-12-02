# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frontGUI.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 800)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(1000, 800))
        MainWindow.setMaximumSize(QSize(1000, 800))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tableWidget_drive = QTableWidget(self.centralwidget)
        self.tableWidget_drive.setObjectName(u"tableWidget_drive")
        self.tableWidget_drive.setGeometry(QRect(10, 304, 321, 191))
        self.tableWidget_drive.horizontalHeader().setStretchLastSection(True)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 111, 16))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(12)
        self.label.setFont(font)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 280, 141, 20))
        self.label_2.setFont(font)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 500, 141, 20))
        self.label_3.setFont(font)
        self.tableWidget_driver = QTableWidget(self.centralwidget)
        self.tableWidget_driver.setObjectName(u"tableWidget_driver")
        self.tableWidget_driver.setGeometry(QRect(10, 520, 321, 111))
        self.tableWidget_driver.horizontalHeader().setStretchLastSection(True)
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 680, 321, 91))
        font1 = QFont()
        font1.setPointSize(16)
        self.pushButton.setFont(font1)
        self.routeScrollArea = QScrollArea(self.centralwidget)
        self.routeScrollArea.setObjectName(u"routeScrollArea")
        self.routeScrollArea.setGeometry(QRect(340, 30, 651, 741))
        self.routeScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 649, 739))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.routeImageLabel = QLabel(self.scrollAreaWidgetContents)
        self.routeImageLabel.setObjectName(u"routeImageLabel")
        self.routeImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.routeImageLabel, 0, 0, 1, 1)

        self.routeScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.hyperlinkLabel = QLabel(self.centralwidget)
        self.hyperlinkLabel.setObjectName(u"hyperlinkLabel")
        self.hyperlinkLabel.setEnabled(False)
        self.hyperlinkLabel.setGeometry(QRect(20, 650, 311, 16))
        font2 = QFont()
        font2.setPointSize(10)
        self.hyperlinkLabel.setFont(font2)
        self.tableWidget_trip = QTableWidget(self.centralwidget)
        self.tableWidget_trip.setObjectName(u"tableWidget_trip")
        self.tableWidget_trip.setGeometry(QRect(10, 30, 321, 251))
        self.tableWidget_trip.horizontalHeader().setStretchLastSection(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DriveSafe", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Trip Information", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Driving Analysis", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Driver Information", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Load Trip", None))
        self.routeImageLabel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.hyperlinkLabel.setText(QCoreApplication.translate("MainWindow", u"Click here for live route map", None))
    # retranslateUi

