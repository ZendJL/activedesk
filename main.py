import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QFrame)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

class ActiveDeskApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Configuraciones de ventana para Linux
        self.setWindowTitle("ActiveDesk")
        self.resize(600, 450)
        
        # Variables de estado
        self.tiempo_restante = 30 * 60  # 30 minutos por defecto (en segundos)
        self.en_pausa = False
        
        # Cargar base de datos de ejercicios
        self.cargar_datos()
        
        # Temporizador principal
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        
        # Interfaz
        self.init_ui()
        
    def cargar_datos(self):
        try:
            with open('exercises.json', 'r', encoding='utf-8') as f:
                self.datos_ejercicios = json.load(f)
        except FileNotFoundError:
            self.datos_ejercicios = {"ejercicios": []}
            print("Advertencia: No se encontró exercises.json")

    def init_ui(self):
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(20)
        
        # --- SECCIÓN SUPERIOR: Reloj y Controles de Tiempo ---
        layout_controles = QHBoxLayout()
        
        self.lbl_reloj = QLabel("30:00")
        self.lbl_reloj.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.combo_intervalo = QComboBox()
        self.combo_intervalo.addItems(["15 min", "30 min", "45 min", "60 min"])
        self.combo_intervalo.setCurrentIndex(1) # Por defecto 30 min
        self.combo_intervalo.currentIndexChanged.connect(self.cambiar_intervalo)
        
        layout_controles.addWidget(self.lbl_reloj)
        layout_controles.addWidget(self.combo_intervalo)
        
        # --- SECCIÓN MEDIA: Presets de Pausa ---
        layout_pausas = QHBoxLayout()
        
        self.btn_pausa_comida = QPushButton("🍽️ Pausa Comida")
        self.btn_pausa_entrenamiento = QPushButton("🏋️ Modo Entrenamiento")
        self.btn_pausa_libre = QPushButton("⏸️ Pausa Libre")
        self.btn_reanudar = QPushButton("▶️ Reanudar")
        self.btn_reanudar.setEnabled(False)
        
        # Conectar botones de pausa (lógica a implementar)
        self.btn_pausa_libre.clicked.connect(self.alternar_pausa)
        self.btn_reanudar.clicked.connect(self.alternar_pausa)
        
        layout_pausas.addWidget(self.btn_pausa_comida)
        layout_pausas.addWidget(self.btn_pausa_entrenamiento)
        layout_pausas.addWidget(self.btn_pausa_libre)
        layout_pausas.addWidget(self.btn_reanudar)
        
        # --- SECCIÓN INFERIOR: Botón de Prueba y Progreso ---
        self.btn_test_alerta = QPushButton("Forzar Alerta (Test)")
        self.btn_test_alerta.clicked.connect(self.mostrar_dashboard_ejercicios)
        
        self.lbl_progreso = QLabel("Progreso del día: 0 sesiones completadas.")
        self.lbl_progreso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ensamblar todo
        layout_principal.addLayout(layout_controles)
        layout_principal.addLayout(layout_pausas)
        layout_principal.addWidget(self.btn_test_alerta)
        layout_principal.addWidget(self.lbl_progreso)
        
        self.setLayout(layout_principal)
        
        # Iniciar el reloj
        self.timer.start(1000) # Se ejecuta cada 1000 ms (1 segundo)

    def actualizar_reloj(self):
        if not self.en_pausa:
            self.tiempo_restante -= 1
            
            minutos = self.tiempo_restante // 60
            segundos = self.tiempo_restante % 60
            self.lbl_reloj.setText(f"{minutos:02d}:{segundos:02d}")
            
            if self.tiempo_restante <= 0:
                self.timer.stop()
                self.mostrar_dashboard_ejercicios()

    def cambiar_intervalo(self):
        # Obtener los minutos del texto seleccionado (ej. "30 min" -> 30)
        texto = self.combo_intervalo.currentText()
        minutos = int(texto.split()[0])
        self.tiempo_restante = minutos * 60
        self.actualizar_reloj()

    def alternar_pausa(self):
        self.en_pausa = not self.en_pausa
        if self.en_pausa:
            self.lbl_reloj.setStyleSheet("color: gray;")
            self.btn_reanudar.setEnabled(True)
            self.btn_pausa_libre.setEnabled(False)
            self.btn_pausa_comida.setEnabled(False)
            self.btn_pausa_entrenamiento.setEnabled(False)
        else:
            self.lbl_reloj.setStyleSheet("color: black;")
            self.btn_reanudar.setEnabled(False)
            self.btn_pausa_libre.setEnabled(True)
            self.btn_pausa_comida.setEnabled(True)
            self.btn_pausa_entrenamiento.setEnabled(True)

    def mostrar_dashboard_ejercicios(self):
        # Aquí programaremos la ventana del Dashboard con la sugerencia inteligente
        print("¡Hora de moverse! Abriendo panel de recomendaciones...")
        # Lógica temporal para reiniciar el reloj tras el "test"
        self.cambiar_intervalo()
        if not self.timer.isActive():
            self.timer.start(1000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Aplicar un estilo oscuro básico (QSS)
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', Ubuntu, sans-serif;
        }
        QPushButton {
            background-color: #3d3d3d;
            border: 1px solid #555;
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        QPushButton:disabled {
            background-color: #1a1a1a;
            color: #555;
        }
        QComboBox {
            background-color: #3d3d3d;
            border: 1px solid #555;
            padding: 5px;
        }
    """)
    
    ventana = ActiveDeskApp()
    ventana.show()
    sys.exit(app.exec())