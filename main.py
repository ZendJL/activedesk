import sys
import json
import random
from datetime import datetime
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QGridLayout, QSpinBox,
                             QFrame, QScrollArea, QSizePolicy, QSlider, QLineEdit, QMessageBox, QStyle, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import QTimer, Qt, QRectF, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor, QPainter, QColor, QPen, QLinearGradient, QBrush, QPixmap, QMovie, QAction, QIcon


# ==========================================
# WIDGET: Temporizador Circular
# ==========================================
class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self.progreso = 1.0
        self.texto = "30:00"

    def actualizar(self, progreso, texto):
        self.progreso = max(0.0, min(1.0, progreso))
        self.texto = texto
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(15, 23, 42, 160)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(5, 5, self.width() - 10, self.height() - 10)

        rect = QRectF(15, 15, self.width() - 30, self.height() - 30)

        pen_fondo = QPen(QColor("#1e293b"), 14)
        pen_fondo.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fondo)
        painter.drawArc(rect, 0, 360 * 16)

        pen_progreso = QPen(QColor("#00d2ff"), 14)
        pen_progreso.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_progreso)
        angulo_inicio = 90 * 16
        angulo_span = int(-self.progreso * 360 * 16)
        painter.drawArc(rect, angulo_inicio, angulo_span)

        painter.setPen(QColor("#ffffff"))
        font_grande = QFont("Ubuntu", 36, QFont.Weight.Bold)
        painter.setFont(font_grande)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.texto)

        font_pequena = QFont("Ubuntu", 11)
        painter.setFont(font_pequena)
        painter.setPen(QColor("#64748b"))
        rect_sub = QRectF(10, self.height() / 2 + 32, self.width() - 20, 30)
        painter.drawText(rect_sub, Qt.AlignmentFlag.AlignCenter, "Tiempo Restante")
        painter.end()


# ==========================================
# WIDGET: Tarjeta de Ejercicio (clickeable)
# ==========================================
class TarjetaEjercicio(QFrame):
    ejercicio_seleccionado = pyqtSignal(dict)

    def __init__(self, ejercicio, destacado=False, parent=None):
        super().__init__(parent)
        self.ejercicio = ejercicio
        self.setObjectName("cardDestacado" if destacado else "cardEjercicio")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(320 if destacado else 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        if destacado:
            lbl_badge = QLabel("⭐ RECOMENDADO PARA TI")
            lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_badge.setStyleSheet(
                "color:#0f172a; background-color:#facc15; border-radius:10px;"
                "padding:3px 8px; font-size:10px; font-weight:bold; letter-spacing:1px;"
            )
            layout.addWidget(lbl_badge, alignment=Qt.AlignmentFlag.AlignCenter)

        emoji_map = {
            "cardio": "🏃", "tren_inferior": "🦵", "tren_superior": "💪",
            "movilidad": "🧘", "pesos": "🏋️"
        }
        emoji = emoji_map.get(ejercicio.get("tipo", ""), "✨")

        self.lbl_img = QLabel()
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setFixedHeight(130 if destacado else 115)
        self.lbl_img.setStyleSheet(
            "background-color: rgba(15,23,42,0.55);"
            "border-radius: 8px;"
            "padding: 6px;"
        )
        self.movie = None

        ruta_media = ejercicio.get("gif", "")
        if ruta_media and os.path.exists(ruta_media):
            if ruta_media.lower().endswith(".gif"):
                self.movie = QMovie(ruta_media)
                if self.movie.isValid():
                    original_size = self.movie.frameRect().size()
                    if original_size.isEmpty():
                        original_size = QSize(320, 180)

                    max_size = QSize(220 if destacado else 180, 118 if destacado else 96)
                    scaled_size = original_size.scaled(
                        max_size,
                        Qt.AspectRatioMode.KeepAspectRatio
                    )

                    self.movie.setScaledSize(scaled_size)
                    self.lbl_img.setMovie(self.movie)
                    self.movie.start()
                else:
                    self.lbl_img.setText(emoji)
                    self.lbl_img.setStyleSheet(
                        "background-color: rgba(15,23,42,0.55);"
                        "border-radius: 8px;"
                        "font-size: 30px;"
                    )
            else:
                pix = QPixmap(ruta_media)
                if not pix.isNull():
                    max_size = QSize(220 if destacado else 180, 118 if destacado else 96)
                    scaled = pix.scaled(
                        max_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.lbl_img.setPixmap(scaled)
                else:
                    self.lbl_img.setText(emoji)
                    self.lbl_img.setStyleSheet(
                        "background-color: rgba(15,23,42,0.55);"
                        "border-radius: 8px;"
                        "font-size: 30px;"
                    )
        else:
            self.lbl_img.setText(emoji)
            self.lbl_img.setStyleSheet(
                "background-color: rgba(15,23,42,0.55);"
                "border-radius: 8px;"
                "font-size: 30px;"
            )

        lbl_nom = QLabel(ejercicio.get("nombre", "Ejercicio"))
        lbl_nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nom.setWordWrap(True)
        lbl_nom.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #f8fafc;"
        )
        lbl_nom.setMaximumHeight(42)

        reps_txt = ejercicio.get("repeticiones_sugeridas", "")
        lbl_reps = QLabel(f"🔁 {reps_txt}" if reps_txt else "▶ 1 serie")
        lbl_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_reps.setStyleSheet(
            "color: #00d2ff; font-size: 12px; font-weight: bold;"
        )

        btn_emp = QPushButton("Empezar ▸")
        btn_emp.setObjectName("btnAcento")
        btn_emp.setFixedHeight(34)
        btn_emp.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout.addWidget(self.lbl_img)
        layout.addWidget(lbl_nom)
        layout.addWidget(lbl_reps)

        if destacado:
            msg = ejercicio.get("mensajes_contexto", {}).get("post_sedentarismo", "")
            if msg:
                lbl_msg = QLabel(f"💡 {msg}")
                lbl_msg.setWordWrap(True)
                lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_msg.setStyleSheet(
                    "color:#94a3b8; font-size:11px; font-style: italic;"
                )
                lbl_msg.setMaximumHeight(54)
                layout.addWidget(lbl_msg)

        layout.addStretch()
        layout.addWidget(btn_emp)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.ejercicio_seleccionado.emit(self.ejercicio)
        super().mouseReleaseEvent(event)


# ==========================================
# WIDGET: Barra de progreso por ejercicio (dashboard)
# ==========================================
class BarraEjercicio(QWidget):
    def __init__(self, nombre, emoji, cantidad, maximo, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        fila_top = QHBoxLayout()
        lbl_nom = QLabel(f"{emoji} {nombre}")
        lbl_nom.setStyleSheet("font-size: 12px; color: #e2e8f0; font-weight: bold;")
        lbl_cant = QLabel(f"{cantidad}x")
        lbl_cant.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: bold;")
        fila_top.addWidget(lbl_nom)
        fila_top.addStretch()
        fila_top.addWidget(lbl_cant)

        self.barra_fondo = QFrame()
        self.barra_fondo.setFixedHeight(10)
        self.barra_fondo.setStyleSheet("background-color: #1e293b; border-radius: 5px;")
        layout_barra = QHBoxLayout(self.barra_fondo)
        layout_barra.setContentsMargins(0, 0, 0, 0)

        pct = min(1.0, cantidad / maximo) if maximo > 0 else 0
        self.relleno = QFrame()
        self.relleno.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        layout_barra.addWidget(self.relleno, int(pct * 100) if pct > 0 else 0)
        if pct < 1.0:
            espacio = QFrame()
            espacio.setStyleSheet("background: transparent;")
            layout_barra.addWidget(espacio, int((1 - pct) * 100) + 1)

        layout.addLayout(fila_top)
        layout.addWidget(self.barra_fondo)


# ==========================================
# CONTENEDOR CON FONDO SEMI-TRANSPARENTE
# ==========================================
class PanelSolido(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor(15, 23, 42, 235))
        grad.setColorAt(1, QColor(10, 15, 30, 235))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()


# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
class ActiveDeskApp(QMainWindow):
    COLORES_TIPO = {
        "cardio": "#00d2ff",
        "tren_inferior": "#facc15",
        "tren_superior": "#f472b6",
        "movilidad": "#4ade80",
        "pesos": "#a78bfa",
    }
    EMOJI_TIPO = {
        "cardio": "🏃", "tren_inferior": "🦵", "tren_superior": "💪",
        "movilidad": "🧘", "pesos": "🏋️"
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Active Flow — Bienestar en el Trabajo")
        self.resize(1040, 680)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.97)

        self.minutos_configurados = 30
        self.tiempo_restante = self.minutos_configurados * 60
        self.en_pausa = False
        self.historial_hoy = []
        self.archivo_historial = "historial.json"

        self.cargar_datos()
        self.cargar_historial()

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)

        self.notificaciones_activas = True
        self.init_tray()
        self.init_ui()
        self.timer_reloj.start(1000)

    def init_tray(self):
        self.tray_icon = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Active Flow")

        menu = QMenu()
        action_mostrar = QAction("Mostrar Active Flow", self)
        action_mostrar.triggered.connect(self.restaurar_ventana)
        action_saltar = QAction("Elegir ejercicio ahora", self)
        action_saltar.triggered.connect(self.abrir_panel_seleccion)
        action_salir = QAction("Salir", self)
        action_salir.triggered.connect(QApplication.instance().quit)

        menu.addAction(action_mostrar)
        menu.addAction(action_saltar)
        menu.addSeparator()
        menu.addAction(action_salir)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.restaurar_ventana()

    def restaurar_ventana(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def alertar_snack(self):
        mensaje = "Es hora de levantarte y hacer tu snack de movimiento."
        if self.tray_icon is not None:
            self.tray_icon.showMessage(
                "Active Flow",
                mensaje,
                QSystemTrayIcon.MessageIcon.Information,
                12000
            )

        if self.isMinimized() or not self.isActiveWindow():
            self.restaurar_ventana()

        self.msg_recordatorio = QMessageBox(self)
        self.msg_recordatorio.setWindowTitle("⏰ Hora de moverte")
        self.msg_recordatorio.setIcon(QMessageBox.Icon.Information)
        self.msg_recordatorio.setText("Tu cuerpo te está pidiendo una pausa activa.")
        self.msg_recordatorio.setInformativeText("Elige un ejercicio ahora o ciérrame y vuelve a la app cuando quieras.")
        self.msg_recordatorio.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.msg_recordatorio.show()

    # --- DATOS E HISTORIAL ---
    def cargar_datos(self):
        try:
            with open('exercises.json', 'r', encoding='utf-8') as f:
                self.datos_ejercicios = json.load(f)
        except FileNotFoundError:
            self.datos_ejercicios = {"ejercicios": []}

    def cargar_historial(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.archivo_historial):
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.historial_hoy = datos.get("sesiones", []) if datos.get("fecha") == hoy else []
        else:
            self.historial_hoy = []

    def guardar_historial(self):
        datos = {"fecha": datetime.now().strftime("%Y-%m-%d"), "sesiones": self.historial_hoy}
        with open(self.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
        self.actualizar_ui_progreso()
        self.actualizar_dashboard()
        self.actualizar_display_timer()

    # --- RECOMENDACIÓN INTELIGENTE ---
    def elegir_ejercicio_recomendado(self):
        ejercicios = self.datos_ejercicios.get("ejercicios", [])
        if not ejercicios:
            return None
        conteos = {}
        for ej in ejercicios:
            conteos[ej["id"]] = sum(1 for s in self.historial_hoy if s.get("id") == ej["id"])
        minimo = min(conteos.values())
        candidatos = [ej for ej in ejercicios if conteos[ej["id"]] == minimo]
        return random.choice(candidatos)

    # --- INTERFAZ GRÁFICA ---
    def init_ui(self):
        widget_central = PanelSolido()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(14)

        header = QHBoxLayout()
        lbl_titulo_app = QLabel("⚡ Active Flow")
        lbl_titulo_app.setStyleSheet("font-size: 22px; font-weight: bold; color: #f8fafc;")
        lbl_sub_app = QLabel("Bienestar en el trabajo")
        lbl_sub_app.setStyleSheet("font-size: 12px; color: #64748b;")
        col_tit = QVBoxLayout()
        col_tit.setSpacing(0)
        col_tit.addWidget(lbl_titulo_app)
        col_tit.addWidget(lbl_sub_app)
        header.addLayout(col_tit)
        header.addStretch()
        layout_principal.addLayout(header)

        layout_columnas = QHBoxLayout()
        layout_columnas.setSpacing(20)

        # --- COLUMNA IZQUIERDA / ÚNICA EN MODO SELECCIÓN ---
        self.columna_izq = QStackedWidget()

        vista_reloj_contenedor = QWidget()
        vista_reloj_contenedor.setStyleSheet("background-color: transparent;")
        layout_vista_reloj = QVBoxLayout(vista_reloj_contenedor)
        layout_vista_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reloj_circular = CircularTimer()
        layout_vista_reloj.addWidget(self.reloj_circular)
        self.lbl_estado_izq = QLabel("Esperando para el próximo snack de movimiento…")
        self.lbl_estado_izq.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado_izq.setStyleSheet("color: #64748b; font-size: 13px; margin-top: 8px;")
        layout_vista_reloj.addWidget(self.lbl_estado_izq)

        vista_grid_contenedor = QWidget()
        vista_grid_contenedor.setStyleSheet("background-color: transparent;")
        layout_grid = QVBoxLayout(vista_grid_contenedor)
        lbl_titulo_grid = QLabel("🎯 Elige tu Snack de Movimiento")
        lbl_titulo_grid.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 6px; color: #f8fafc;")
        layout_grid.addWidget(lbl_titulo_grid)

        self.lbl_hint_grid = QLabel(
            "🧠 Elige el ejercicio que más te llame. "
            "La tarjeta con ⭐ es la recomendación más balanceada para este momento."
        )
        self.lbl_hint_grid.setWordWrap(True)
        self.lbl_hint_grid.setStyleSheet(
            "color: #94a3b8; font-size: 13px; "
            "background-color: rgba(30,41,59,0.45); "
            "border: 1px solid rgba(51,65,85,0.45); "
            "border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;"
        )
        layout_grid.addWidget(self.lbl_hint_grid)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(18)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        scroll.setWidget(grid_widget)
        layout_grid.addWidget(scroll)

        self.columna_izq.addWidget(vista_reloj_contenedor)
        self.columna_izq.addWidget(vista_grid_contenedor)
        self.columna_izq.currentChanged.connect(self.on_vista_cambiada)

        # --- COLUMNA DERECHA (solo vista reloj) ---
        self.columna_der = QWidget()
        self.columna_der.setFixedWidth(340)
        self.columna_der.setStyleSheet("background-color: transparent;")
        layout_der = QVBoxLayout(self.columna_der)
        layout_der.setContentsMargins(0, 0, 0, 0)
        layout_der.setSpacing(14)

        self.panel_intervalo = QFrame()
        self.panel_intervalo.setObjectName("panelCard")
        layout_int = QVBoxLayout(self.panel_intervalo)
        layout_int.setSpacing(10)

        lbl_int = QLabel("⏰  INTERVALO ENTRE SNACKS")
        lbl_int.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")

        self.lbl_timer_actual = QLabel(f"{self.minutos_configurados} min")
        self.lbl_timer_actual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_timer_actual.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #f8fafc; "
            "background-color: rgba(15,23,42,0.55); border: 1px solid rgba(51,65,85,0.8); "
            "border-radius: 12px; padding: 12px;"
        )

        lbl_slider = QLabel("Desliza para ajustar rápido")
        lbl_slider.setStyleSheet("color: #64748b; font-size: 12px;")

        self.slider_minutos = QSlider(Qt.Orientation.Horizontal)
        self.slider_minutos.setRange(1, 120)
        self.slider_minutos.setValue(self.minutos_configurados)
        self.slider_minutos.valueChanged.connect(self.on_slider_cambiado)

        fila_custom = QHBoxLayout()
        self.input_minutos = QLineEdit(str(self.minutos_configurados))
        self.input_minutos.setPlaceholderText("Minutos")
        self.input_minutos.setFixedHeight(38)
        self.input_minutos.setStyleSheet(
            "padding: 6px 10px; font-size: 15px; border-radius: 8px; "
            "background: rgba(15,23,42,0.7); color: #f1f5f9; border: 1px solid #334155;"
        )

        btn_aplicar_tiempo = QPushButton("Aplicar")
        btn_aplicar_tiempo.setObjectName("btnSecundario")
        btn_aplicar_tiempo.setFixedHeight(38)
        btn_aplicar_tiempo.clicked.connect(self.aplicar_tiempo_manual)

        fila_custom.addWidget(self.input_minutos)
        fila_custom.addWidget(btn_aplicar_tiempo)

        btn_forzar = QPushButton("⚡ Saltar Ahora")
        btn_forzar.setObjectName("btnAcento")
        btn_forzar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_forzar.setFixedHeight(40)
        btn_forzar.clicked.connect(self.abrir_panel_seleccion)

        layout_int.addWidget(lbl_int)
        layout_int.addWidget(self.lbl_timer_actual)
        layout_int.addWidget(lbl_slider)
        layout_int.addWidget(self.slider_minutos)
        layout_int.addLayout(fila_custom)
        layout_int.addWidget(btn_forzar)

        self.panel_prog = QFrame()
        self.panel_prog.setObjectName("panelCard")
        self.layout_prog = QVBoxLayout(self.panel_prog)
        self.layout_prog.setSpacing(8)
        lbl_prog_tit = QLabel("📊  DASHBOARD DE HOY")
        lbl_prog_tit.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        self.lbl_progreso_stats = QLabel("0 Snacks Completados")
        self.lbl_progreso_stats.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        self.lbl_neat = QLabel("NEAT Extra: ~0 kcal 🔥")
        self.lbl_neat.setStyleSheet("color: #00d2ff; font-size: 12px;")

        self.contenedor_barras = QVBoxLayout()
        self.contenedor_barras.setSpacing(10)

        lbl_banner = QLabel("🏴‍☠️  ¡El Rey del Movimiento!\nNo te rindas, ¡Nakama!")
        lbl_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_banner.setStyleSheet(
            "background-color: rgba(30,41,59,0.6); border-left: 4px solid #facc15; "
            "padding: 10px; margin-top: 6px; font-style: italic; color: #fef9c3; border-radius: 4px;"
        )

        self.layout_prog.addWidget(lbl_prog_tit)
        self.layout_prog.addWidget(self.lbl_progreso_stats)
        self.layout_prog.addWidget(self.lbl_neat)
        self.layout_prog.addLayout(self.contenedor_barras)
        self.layout_prog.addWidget(lbl_banner)

        layout_der.addWidget(self.panel_intervalo)
        layout_der.addWidget(self.panel_prog)
        layout_der.addStretch()

        layout_columnas.addWidget(self.columna_izq, 1)
        layout_columnas.addWidget(self.columna_der, 0)

        self.btn_pausa = QPushButton("⏸  Pausar avisos")
        self.btn_reanudar = QPushButton("▶  Reanudar avisos")
        self.btn_omitir_abajo = QPushButton("✗  Omitir ejercicio por ahora")
        self.btn_reanudar.setObjectName("btnAcento")
        self.btn_reanudar.hide()

        layout_pausas = QHBoxLayout()
        layout_pausas.setSpacing(10)

        for btn in [self.btn_pausa, self.btn_reanudar, self.btn_omitir_abajo]:
            btn.setFixedHeight(44)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if btn == self.btn_reanudar:
                btn.setObjectName("btnAcento")
            elif btn == self.btn_omitir_abajo:
                btn.setObjectName("btnPeligro")
                btn.hide()
            else:
                btn.setObjectName("btnSecundario")

        self.btn_pausa.clicked.connect(lambda: self.activar_pausa("Pausa"))
        self.btn_reanudar.clicked.connect(self.desactivar_pausa)
        self.btn_omitir_abajo.clicked.connect(self.reiniciar_ciclo)

        layout_pausas.addWidget(self.btn_pausa)
        layout_pausas.addWidget(self.btn_reanudar)
        layout_pausas.addWidget(self.btn_omitir_abajo)

        layout_principal.addLayout(layout_columnas)
        layout_principal.addLayout(layout_pausas)

        self.actualizar_ui_progreso()
        self.actualizar_dashboard()
        self.actualizar_display_timer()

    # --- CAMBIO DE VISTA: ocultar/mostrar paneles laterales ---
    def on_vista_cambiada(self, index):
        modo_seleccion = (index == 1)
        self.columna_der.setVisible(not modo_seleccion)
        self.btn_pausa.setVisible(not modo_seleccion and not self.en_pausa)
        self.btn_reanudar.setVisible(not modo_seleccion and self.en_pausa)
        self.btn_omitir_abajo.setVisible(modo_seleccion)

    # --- GRID DE EJERCICIOS CON RECOMENDADO DESTACADO ---
    def dibujar_grid_ejercicios(self):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        ejercicios = self.datos_ejercicios.get("ejercicios", [])
        recomendado = self.elegir_ejercicio_recomendado()

        fila, col = 0, 0
        columnas = 2

        for ej in ejercicios:
            es_destacado = recomendado is not None and ej["id"] == recomendado["id"]
            card = TarjetaEjercicio(ej, destacado=es_destacado)
            card.ejercicio_seleccionado.connect(self.completar_sesion)
            self.grid_layout.addWidget(card, fila, col)
            col += 1
            if col >= columnas:
                col = 0
                fila += 1


    # --- DASHBOARD GRÁFICO DE EJERCICIOS DEL DÍA ---
    def actualizar_dashboard(self):
        for i in reversed(range(self.contenedor_barras.count())):
            item = self.contenedor_barras.itemAt(i)
            w = item.widget()
            if w:
                w.setParent(None)

        ejercicios = self.datos_ejercicios.get("ejercicios", [])
        conteos = {}
        for ej in ejercicios:
            conteos[ej["id"]] = {
                "nombre": ej["nombre"],
                "tipo": ej.get("tipo", ""),
                "cantidad": sum(1 for s in self.historial_hoy if s.get("id") == ej["id"])
            }

        extra = sum(1 for s in self.historial_hoy if s.get("id") == "entrenamiento_fuerza")
        if extra:
            conteos["entrenamiento_fuerza"] = {"nombre": "Entrenamiento", "tipo": "pesos", "cantidad": extra}

        if not any(c["cantidad"] for c in conteos.values()):
            lbl_vacio = QLabel("Aún no registras movimiento hoy.\n¡Tu primer snack te espera! 💪")
            lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vacio.setWordWrap(True)
            lbl_vacio.setStyleSheet("color:#475569; font-size:12px; padding:10px;")
            self.contenedor_barras.addWidget(lbl_vacio)
            return

        maximo = max(c["cantidad"] for c in conteos.values()) or 1
        for datos in sorted(conteos.values(), key=lambda c: -c["cantidad"]):
            emoji = self.EMOJI_TIPO.get(datos["tipo"], "✨")
            color = self.COLORES_TIPO.get(datos["tipo"], "#00d2ff")
            barra = BarraEjercicio(datos["nombre"], emoji, datos["cantidad"], maximo, color)
            self.contenedor_barras.addWidget(barra)

        grupos_con_actividad = {k: v for k, v in conteos.items() if v["cantidad"] > 0}
        if grupos_con_actividad:
            minimo_tipo = min(grupos_con_actividad.values(), key=lambda v: v["cantidad"])
            lbl_balance = QLabel(f"💡 Considera hacer más: {minimo_tipo['nombre']}")
            lbl_balance.setWordWrap(True)
            lbl_balance.setStyleSheet("color:#facc15; font-size:11px; margin-top:4px;")
            self.contenedor_barras.addWidget(lbl_balance)

    def actualizar_recomendacion(self):
        self.dibujar_grid_ejercicios()

    def actualizar_ui_progreso(self):
        completados = len(self.historial_hoy)
        kcal_estimadas = completados * 15
        self.lbl_progreso_stats.setText(f"{completados} Snacks Completados Hoy")
        self.lbl_neat.setText(f"NEAT Extra: ~{kcal_estimadas} kcal 🔥")

    def actualizar_display_timer(self):
        self.lbl_timer_actual.setText(f"{self.minutos_configurados} min")
        self.input_minutos.setText(str(self.minutos_configurados))

    def on_slider_cambiado(self, valor):
        self.minutos_configurados = valor
        self.actualizar_display_timer()
        if not self.en_pausa and self.columna_izq.currentIndex() == 0:
            self.tiempo_restante = self.minutos_configurados * 60
            self.actualizar_reloj_visual()

    def aplicar_tiempo_manual(self):
        try:
            valor = int(self.input_minutos.text().strip())
        except ValueError:
            self.input_minutos.setText(str(self.minutos_configurados))
            return

        valor = max(1, min(120, valor))
        self.minutos_configurados = valor
        self.slider_minutos.blockSignals(True)
        self.slider_minutos.setValue(valor)
        self.slider_minutos.blockSignals(False)
        self.actualizar_display_timer()

        if not self.en_pausa and self.columna_izq.currentIndex() == 0:
            self.tiempo_restante = self.minutos_configurados * 60
            self.actualizar_reloj_visual()

    # --- LÓGICA DE TIEMPO ---
    def cambiar_minutos_configurados(self):
        self.minutos_configurados = self.slider_minutos.value()
        self.actualizar_display_timer()
        if not self.en_pausa and self.columna_izq.currentIndex() == 0:
            self.tiempo_restante = self.minutos_configurados * 60
            self.actualizar_reloj_visual()

    def actualizar_reloj(self):
        if not self.en_pausa and self.columna_izq.currentIndex() == 0:
            self.tiempo_restante -= 1
            self.actualizar_reloj_visual()
            if self.tiempo_restante <= 0:
                self.alertar_snack()
                self.abrir_panel_seleccion()

    def actualizar_reloj_visual(self):
        mins, secs = divmod(self.tiempo_restante, 60)
        texto = f"{mins:02d}:{secs:02d}"
        total_segs = self.minutos_configurados * 60
        progreso = self.tiempo_restante / total_segs if total_segs > 0 else 0
        self.reloj_circular.actualizar(progreso, texto)

    # --- NAVEGACIÓN Y PAUSAS ---
    def abrir_panel_seleccion(self):
        self.timer_reloj.stop()
        self.dibujar_grid_ejercicios()
        self.columna_izq.setCurrentIndex(1)

    def completar_sesion(self, ejercicio):
        self.historial_hoy.append({
            "id": ejercicio["id"],
            "tipo": ejercicio["tipo"],
            "hora": datetime.now().strftime("%H:%M")
        })
        self.guardar_historial()
        self.reiniciar_ciclo()

    def reiniciar_ciclo(self):
        self.tiempo_restante = self.minutos_configurados * 60
        self.actualizar_reloj_visual()
        self.columna_izq.setCurrentIndex(0)
        self.timer_reloj.start(1000)

    def activar_pausa(self, tipo):
        self.en_pausa = True
        self.timer_reloj.stop()
        self.btn_pausa.hide()
        self.btn_reanudar.show()
        self.lbl_estado_izq.setText(f"⏸️ Avisos pausados ({tipo}).")
        self.reloj_circular.actualizar(0, "PAUSA")

    def desactivar_pausa(self):
        self.en_pausa = False
        self.btn_reanudar.hide()
        self.btn_pausa.show()
        self.lbl_estado_izq.setText("Esperando para el próximo snack de movimiento…")
        self.reiniciar_ciclo()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    estilos = """
        QMainWindow {
            background-color: transparent;
        }
        QWidget {
            font-family: 'Segoe UI', Ubuntu, sans-serif;
        }
        QLabel {
            color: #f8fafc;
        }
        #panelCard {
            background-color: rgba(30, 41, 59, 0.72);
            border-radius: 14px;
            border: 1px solid rgba(51, 65, 85, 0.6);
            padding: 4px;
        }
        #cardEjercicio {
            background-color: rgba(30, 51, 82, 0.78);
            border-radius: 12px;
            border: 1px solid rgba(51, 65, 85, 0.7);
        }
        #cardEjercicio:hover {
            border: 1px solid #00d2ff;
            background-color: rgba(30, 58, 95, 0.85);
        }
        #cardDestacado {
            background-color: rgba(30, 64, 95, 0.9);
            border-radius: 12px;
            border: 2px solid #facc15;
        }
        #cardDestacado:hover {
            border: 2px solid #fde047;
            background-color: rgba(40, 74, 105, 0.92);
        }
        #btnAcento {
            background-color: #00d2ff;
            color: #0f172a;
            border: none;
            border-radius: 6px;
            padding: 8px 15px;
            font-weight: bold;
        }
        #btnAcento:hover { background-color: #38bdf8; }
        #btnSecundario {
            background-color: rgba(30, 41, 59, 0.75);
            color: #94a3b8;
            border: 1px solid rgba(51, 65, 85, 0.8);
            border-radius: 8px;
            font-weight: bold;
        }
        #btnSecundario:hover {
            background-color: rgba(51, 65, 85, 0.9);
            color: #f8fafc;
        }
        #btnPeligro {
            background-color: rgba(127, 29, 29, 0.85);
            color: #fca5a5;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-weight: bold;
        }
        #btnPeligro:hover { background-color: rgba(153, 27, 27, 0.95); }
        QSpinBox { color: #f1f5f9; }
        QLineEdit { color: #f1f5f9; selection-background-color: #00d2ff; }
        QSlider::groove:horizontal {
            height: 8px;
            background: rgba(15,23,42,0.75);
            border-radius: 4px;
        }
        QSlider::sub-page:horizontal {
            background: #00d2ff;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #f8fafc;
            border: 2px solid #00d2ff;
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
        QScrollBar:vertical {
            border: none; background: transparent;
            width: 7px; border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #334155; min-height: 20px; border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """
    app.setStyleSheet(estilos)

    ventana = ActiveDeskApp()
    ventana.show()
    sys.exit(app.exec())