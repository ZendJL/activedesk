import sys
import json
import random
from datetime import datetime
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QStackedWidget, QGridLayout, QFrame)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QCursor

class ActiveDeskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ActiveDesk - Pausas Activas")
        self.resize(750, 550)
        
        # Variables de estado
        self.tiempo_restante = 30 * 60
        self.en_pausa = False
        self.historial_hoy = []
        self.archivo_historial = "historial.json"
        self.ejercicio_actual = None
        
        self.cargar_datos()
        self.cargar_historial()
        
        # Temporizadores
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_mensaje = QTimer(self)
        self.timer_mensaje.setSingleShot(True)
        self.timer_mensaje.timeout.connect(self.limpiar_mensaje)
        
        self.init_ui()
        self.timer_reloj.start(1000)

    def cargar_datos(self):
        try:
            with open('exercises.json', 'r', encoding='utf-8') as f:
                self.datos_ejercicios = json.load(f)
        except FileNotFoundError:
            self.datos_ejercicios = {"ejercicios": []}
            self.mostrar_mensaje("Error: No se encontró exercises.json")

    def cargar_historial(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.archivo_historial):
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if datos.get("fecha") == hoy:
                    self.historial_hoy = datos.get("sesiones", [])
                else:
                    self.historial_hoy = [] # Nuevo día, reset
        else:
            self.historial_hoy = []

    def guardar_historial(self):
        datos = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "sesiones": self.historial_hoy
        }
        with open(self.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
        
        self.lbl_progreso.setText(f"Progreso del día: {len(self.historial_hoy)} sesiones completadas.")

    def mostrar_mensaje(self, texto):
        self.lbl_notificacion.setText(texto)
        self.timer_mensaje.start(4000) # El mensaje desaparece a los 4 segundos

    def limpiar_mensaje(self):
        self.lbl_notificacion.setText("")

    def init_ui(self):
        # Widget Central y Gestor de Pantallas
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_base = QVBoxLayout(widget_central)
        layout_base.setContentsMargins(20, 20, 20, 10)
        
        self.stack = QStackedWidget()
        
        # Crear las tres vistas
        self.vista_reloj = self.crear_vista_reloj()
        self.vista_seleccion = self.crear_vista_seleccion()
        self.vista_activa = self.crear_vista_activa()
        
        self.stack.addWidget(self.vista_reloj)      # Index 0
        self.stack.addWidget(self.vista_seleccion)  # Index 1
        self.stack.addWidget(self.vista_activa)     # Index 2
        
        layout_base.addWidget(self.stack)
        
        # Barra de notificaciones inferior (siempre visible)
        self.lbl_notificacion = QLabel("")
        self.lbl_notificacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_notificacion.setStyleSheet("color: #4caf50; font-weight: bold;")
        layout_base.addWidget(self.lbl_notificacion)
        
        # Inicializar UI
        self.lbl_progreso.setText(f"Progreso del día: {len(self.historial_hoy)} sesiones completadas.")

    # --- PANTALLA 1: RELOJ PRINCIPAL ---
    def crear_vista_reloj(self):
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_reloj = QLabel("30:00")
        self.lbl_reloj.setObjectName("relojPrincipal")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_controles = QHBoxLayout()
        layout_controles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_intervalo = QLabel("Avisarme cada:")
        self.combo_intervalo = QComboBox()
        self.combo_intervalo.addItems(["15 min", "30 min", "45 min", "60 min"])
        self.combo_intervalo.setCurrentIndex(1)
        self.combo_intervalo.currentIndexChanged.connect(self.cambiar_intervalo)
        
        layout_controles.addWidget(lbl_intervalo)
        layout_controles.addWidget(self.combo_intervalo)
        
        # Botones de Pausa
        layout_pausas = QHBoxLayout()
        self.btn_pausa_comida = QPushButton("🍽️ Comida")
        self.btn_pausa_entrenamiento = QPushButton("🏋️ Entrenamiento")
        self.btn_pausa_libre = QPushButton("⏸️ Pausa Libre")
        self.btn_reanudar = QPushButton("▶️ Reanudar")
        
        for btn in [self.btn_pausa_comida, self.btn_pausa_entrenamiento, self.btn_pausa_libre, self.btn_reanudar]:
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
        self.btn_pausa_libre.clicked.connect(self.alternar_pausa)
        self.btn_reanudar.clicked.connect(self.alternar_pausa)
        self.btn_reanudar.hide()
        
        layout_pausas.addWidget(self.btn_pausa_comida)
        layout_pausas.addWidget(self.btn_pausa_entrenamiento)
        layout_pausas.addWidget(self.btn_pausa_libre)
        layout_pausas.addWidget(self.btn_reanudar)
        
        self.btn_test = QPushButton("Saltar al Panel (Test)")
        self.btn_test.setObjectName("btnTest")
        self.btn_test.clicked.connect(self.abrir_panel_seleccion)
        
        self.lbl_progreso = QLabel("Progreso del día: 0 sesiones")
        self.lbl_progreso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_progreso.setStyleSheet("color: #aaa; margin-top: 20px;")
        
        layout.addWidget(self.lbl_reloj)
        layout.addLayout(layout_controles)
        layout.addSpacing(20)
        layout.addLayout(layout_pausas)
        layout.addSpacing(20)
        layout.addWidget(self.btn_test)
        layout.addWidget(self.lbl_progreso)
        
        return vista

    # --- PANTALLA 2: SELECCIÓN DE EJERCICIO ---
    def crear_vista_seleccion(self):
        vista = QWidget()
        self.layout_grid_contenedor = QVBoxLayout(vista)
        self.layout_grid_contenedor.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl_titulo = QLabel("¡Es hora de tu pausa activa!")
        lbl_titulo.setFont(QFont("Ubuntu", 20, QFont.Weight.Bold))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_grid_contenedor.addWidget(lbl_titulo)
        self.layout_grid_contenedor.addSpacing(10)
        
        self.contenedor_botones = QWidget()
        self.grid = QGridLayout(self.contenedor_botones)
        self.layout_grid_contenedor.addWidget(self.contenedor_botones)
        
        self.layout_grid_contenedor.addStretch()
        btn_omitir = QPushButton("Omitir sesión")
        btn_omitir.setObjectName("btnOmitir")
        btn_omitir.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_omitir.clicked.connect(self.omitir_sesion)
        self.layout_grid_contenedor.addWidget(btn_omitir)
        
        return vista

    # --- PANTALLA 3: EJERCICIO ACTIVO ---
    def crear_vista_activa(self):
        vista = QWidget()
        layout = QVBoxLayout(vista)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_titulo_activo = QLabel("Haciendo Ejercicio")
        self.lbl_titulo_activo.setFont(QFont("Ubuntu", 24, QFont.Weight.Bold))
        self.lbl_titulo_activo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_reps_activo = QLabel("0 reps")
        self.lbl_reps_activo.setFont(QFont("Ubuntu", 16))
        self.lbl_reps_activo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reps_activo.setStyleSheet("color: #4caf50;")
        
        # Aquí iría el QMovie para el GIF animado (Placeholder por ahora)
        self.lbl_gif_placeholder = QLabel("[ GIF ANIMADO AQUI ]")
        self.lbl_gif_placeholder.setFixedSize(300, 200)
        self.lbl_gif_placeholder.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")
        self.lbl_gif_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_terminar = QPushButton("¡Sesión Completada!")
        btn_terminar.setObjectName("btnTerminar")
        btn_terminar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_terminar.clicked.connect(self.completar_sesion)
        
        layout.addWidget(self.lbl_titulo_activo)
        layout.addWidget(self.lbl_reps_activo)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_gif_placeholder)
        layout.addSpacing(30)
        layout.addWidget(btn_terminar)
        
        return vista

    # --- LÓGICA DE TIEMPO Y NAVEGACIÓN ---
    def actualizar_reloj(self):
        if not self.en_pausa and self.stack.currentIndex() == 0:
            self.tiempo_restante -= 1
            mins, secs = divmod(self.tiempo_restante, 60)
            self.lbl_reloj.setText(f"{mins:02d}:{secs:02d}")
            
            if self.tiempo_restante <= 0:
                self.abrir_panel_seleccion()

    def cambiar_intervalo(self):
        mins = int(self.combo_intervalo.currentText().split()[0])
        self.tiempo_restante = mins * 60
        mins, secs = divmod(self.tiempo_restante, 60)
        self.lbl_reloj.setText(f"{mins:02d}:{secs:02d}")
        self.mostrar_mensaje(f"Intervalo ajustado a {mins} minutos.")

    def alternar_pausa(self):
        self.en_pausa = not self.en_pausa
        if self.en_pausa:
            self.lbl_reloj.setStyleSheet("color: #555;")
            self.btn_pausa_libre.hide()
            self.btn_reanudar.show()
            self.mostrar_mensaje("App pausada. ¡Tómate tu tiempo!")
        else:
            self.lbl_reloj.setStyleSheet("color: white;")
            self.btn_reanudar.hide()
            self.btn_pausa_libre.show()
            self.mostrar_mensaje("¡De vuelta al código!")

    def abrir_panel_seleccion(self):
        self.timer_reloj.stop()
        
        # Limpiar botones anteriores
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
            
        ejercicios = self.datos_ejercicios.get("ejercicios", [])
        if not ejercicios:
            self.mostrar_mensaje("No hay ejercicios cargados.")
            return

        # Simular recomendación básica
        recomendado = random.choice(ejercicios)
        
        fila, col = 0, 0
        for ej in ejercicios:
            btn = QPushButton()
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            if ej == recomendado:
                btn.setObjectName("btnRecomendado")
                msg = ej["mensajes_contexto"].get("post_sedentarismo", "")
                btn.setText(f"🌟 RECOMENDADO\n{ej['nombre']}\n\n{ej['repeticiones_sugeridas']}\n\n{msg}")
                self.grid.addWidget(btn, 0, 0, 1, 2)
                fila = 1
            else:
                btn.setObjectName("btnNormal")
                btn.setText(f"{ej['nombre']}\n{ej['repeticiones_sugeridas']}")
                self.grid.addWidget(btn, fila, col)
                col += 1
                if col > 1:
                    col = 0
                    fila += 1
                    
            btn.clicked.connect(lambda ch, e=ej: self.iniciar_ejercicio(e))

        self.stack.setCurrentIndex(1) # Cambiar a la vista de selección

    def iniciar_ejercicio(self, ejercicio):
        self.ejercicio_actual = ejercicio
        self.lbl_titulo_activo.setText(ejercicio["nombre"])
        self.lbl_reps_activo.setText(ejercicio["repeticiones_sugeridas"])
        self.stack.setCurrentIndex(2) # Cambiar a la vista de ejercicio

    def completar_sesion(self):
        self.historial_hoy.append({
            "id": self.ejercicio_actual["id"],
            "tipo": self.ejercicio_actual["tipo"],
            "hora": datetime.now().strftime("%H:%M")
        })
        self.guardar_historial()
        self.mostrar_mensaje(f"¡Excelente! Sesión de {self.ejercicio_actual['nombre']} registrada.")
        self.reiniciar_ciclo()

    def omitir_sesion(self):
        self.mostrar_mensaje("Sesión omitida. Seguimos programando.")
        self.reiniciar_ciclo()

    def reiniciar_ciclo(self):
        self.cambiar_intervalo()
        self.stack.setCurrentIndex(0) # Volver al reloj
        self.timer_reloj.start(1000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Estilos CSS/QSS rediseñados
    estilos = """
        QMainWindow {
            background-color: #1e1e2e; /* Fondo principal oscuro estilo Catppuccin */
        }
        QLabel {
            color: #cdd6f4;
        }
        #relojPrincipal {
            font-size: 80px;
            font-weight: bold;
            color: #89b4fa; /* Acento azul */
        }
        QComboBox {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45475a;
            border: 1px solid #89b4fa;
        }
        #btnTest {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            padding: 12px;
        }
        #btnTest:hover {
            background-color: #b4befe;
        }
        #btnRecomendado {
            background-color: #a6e3a1; /* Verde destacado */
            color: #1e1e2e;
            border: none;
            text-align: left;
            padding: 20px;
            font-size: 16px;
        }
        #btnRecomendado:hover {
            background-color: #94e2d5;
        }
        #btnNormal {
            padding: 20px;
            font-size: 15px;
        }
        #btnOmitir {
            background-color: #f38ba8; /* Rojo suave */
            color: #1e1e2e;
            border: none;
            margin-top: 20px;
        }
        #btnOmitir:hover {
            background-color: #eba0ac;
        }
        #btnTerminar {
            background-color: #a6e3a1;
            color: #1e1e2e;
            font-size: 18px;
            padding: 15px;
        }
    """
    app.setStyleSheet(estilos)
    
    ventana = ActiveDeskApp()
    ventana.show()
    sys.exit(app.exec())