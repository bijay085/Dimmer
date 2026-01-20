import sys
import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional

# Global hotkey support
try:
    import keyboard
    GLOBAL_HOTKEYS_AVAILABLE = True
except ImportError:
    GLOBAL_HOTKEYS_AVAILABLE = False

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QPushButton, QSystemTrayIcon, 
                             QMenu, QAction, QGroupBox, QCheckBox, QMessageBox,
                             QTabWidget, QTimeEdit, QSpinBox, QDialog, QShortcut, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QTime, QMetaObject, Qt, QDateTime, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QColor, QIcon, QPixmap, QKeySequence, QPainter, QPen

# ============= Configuration Constants =============
class Config:
    """Simple configuration"""
    APP_NAME = "Screen Dimmer"
    APP_VERSION = "1.1"  # Updated version
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 1200
    
    # Spacing
    WIDGET_SPACING = 15
    MAIN_MARGIN = 20
    
    # Dimming settings - Very low default for maximum intensity
    DEFAULT_DIM = 25
    
    PROFILES_FILE = 'dimmer_profiles.json'
    STATE_FILE = 'dimmer_stats.json'  # Save current dimmer state
    
    # Colors - Much darker and more intense theme
    PRIMARY_COLOR = "#1a1a1a"      # Deep charcoal instead of blue-gray
    SUCCESS_COLOR = "#00ff41"       # Bright electric green
    WARNING_COLOR = "#ff0040"       # Bright electric red
    INFO_COLOR = "#0080ff"          # Bright electric blue
    BACKGROUND_COLOR = "#000000"    # Pure black background
    CARD_COLOR = "#0a0a0a"          # Very dark gray cards
    BORDER_COLOR = "#1a1a1a"        # Dark borders
    TEXT_COLOR = "#ffffff"          # Pure white text
    MUTED_COLOR = "#666666"         # Medium gray for muted text

# ============= Data Models =============
@dataclass
class Profile:
    """Profile data model"""
    dimming: int
    blue_light: bool
    blue_intensity: int
    
# ============= Simple Icon Creator =============
class IconCreator:
    """Creates simple icons for the application"""
    
    @staticmethod
    def create_tray_icon() -> QIcon:
        """Create a simple tray icon"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(Config.PRIMARY_COLOR))
        return QIcon(pixmap)

# ============= Style Manager =============
class StyleManager:
    """Enhanced style management with better spacing"""
    
    # Cache frequently used styles
    _app_stylesheet = None
    _button_styles = {}
    
    @staticmethod
    def get_app_stylesheet() -> str:
        """Get main application stylesheet"""
        if StyleManager._app_stylesheet is None:
            StyleManager._app_stylesheet = f"""
            QWidget {{ 
                background-color: {Config.BACKGROUND_COLOR}; 
                color: {Config.TEXT_COLOR}; 
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTabWidget::pane {{
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.BORDER_COLOR};
                border-radius: 8px;
                padding: 15px;
            }}
            QTabBar::tab {{
                background-color: #000000;
                color: #666666;
                padding: 12px 35px;
                margin: 0 2px;
                border-radius: 6px 6px 0 0;
                font-size: 18px;
                font-weight: 500;
                min-width: 140px;
                border: 1px solid #333333;
            }}
            QTabBar::tab:selected {{
                background-color: #0a0a0a;
                color: #ffffff;
                border-bottom: 2px solid #00ff41;
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: #1a1a1a;
                color: #ffffff;
                border-color: #00ff41;
            }}
            QGroupBox {{ 
                background-color: {Config.CARD_COLOR}; 
                border: 2px solid {Config.BORDER_COLOR}; 
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: {Config.CARD_COLOR};
            }}
            QSlider::groove:horizontal {{ 
                height: 8px; 
                background: #1a1a1a; 
                border-radius: 4px;
                border: 1px solid #333333;
            }}
            QSlider::handle:horizontal {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ff41, stop:1 #00cc33);
                width: 20px; 
                height: 20px; 
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid #000000;
            }}
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ff80, stop:1 #00ff41);
                border: 2px solid #00ff41;
            }}
            QSlider::handle:horizontal:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00cc33, stop:1 #00ff41);
            }}
            QCheckBox {{ 
                spacing: 10px; 
                font-size: 18px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #333333;
                background-color: #000000;
            }}
            QCheckBox::indicator:checked {{
                background-color: #00ff41;
                border-color: #00ff41;
            }}
            QLabel {{
                font-size: 18px;
                padding: 2px;
            }}
            QTimeEdit, QSpinBox {{
                background-color: #000000;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 18px;
            }}
            QTimeEdit:hover, QSpinBox:hover {{
                border-color: #00ff41;
            }}
            QTimeEdit:focus, QSpinBox:focus {{
                border-color: #00ff41;
                outline: none;
            }}
        """
        return StyleManager._app_stylesheet
    
    @staticmethod
    def get_button_style(color: str, active: bool = False) -> str:
        """Generate button stylesheet with enhanced visual feedback"""
        cache_key = f"{color}_{active}"
        if cache_key not in StyleManager._button_styles:
            if active:
                # Active state - brighter with glow effect
                StyleManager._button_styles[cache_key] = f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 12px 24px; 
                    border: 2px solid {color};
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    border-color: {color};
                    opacity: 0.85;
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    border-color: {color};
                    opacity: 0.75;
                }}
            """
            else:
                # Inactive state - standard style
                StyleManager._button_styles[cache_key] = f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 12px 24px; 
                    border: 2px solid {color};
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    border-color: {color};
                    opacity: 0.9;
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    border-color: {color};
                    opacity: 0.8;
                }}
            """
        return StyleManager._button_styles[cache_key]
    
    @staticmethod
    def get_preset_button_style() -> str:
        """Style for preset buttons"""
        return """
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a1a, stop:1 #000000);
                color: #ffffff;
                padding: 6px 12px; 
                border: 1px solid #333333; 
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
                min-width: 50px;
                min-height: 35px;
                text-align: center;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-color: #00ff41;
                border-width: 2px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00ff41, stop:1 #00cc33);
                border-color: #00ff80;
                border-width: 2px;
            }
            QPushButton:disabled {
                background: #0a0a0a;
                color: #444444;
                border-color: #222222;
            }
        """

# ============= Animation Utilities =============
class AnimationHelper:
    """Helper class for smooth animations"""
    
    @staticmethod
    def animate_button_state(button: QPushButton, active: bool, active_color: str, inactive_color: str, duration: int = 300):
        """Animate button state change with smooth transition"""
        if not button:
            return
        
        target_color = active_color if active else inactive_color
        target_text = button.text()
        
        # Update button style with transition
        if active:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {active_color};
                    color: white;
                    padding: 12px 24px; 
                    border: 2px solid {active_color};
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {active_color};
                    opacity: 0.85;
                }}
                QPushButton:pressed {{
                    background-color: {active_color};
                    opacity: 0.75;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {inactive_color};
                    color: white;
                    padding: 12px 24px; 
                    border: 2px solid {inactive_color};
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {inactive_color};
                    opacity: 0.9;
                }}
                QPushButton:pressed {{
                    background-color: {inactive_color};
                    opacity: 0.8;
                }}
            """)
    
    @staticmethod
    def animate_label_update(label: QLabel, new_text: str, highlight_color: str = Config.SUCCESS_COLOR, duration: int = 200):
        """Animate label text update with highlight effect"""
        if not label:
            return
        
        # Store original style
        original_style = label.styleSheet()
        
        # Update text immediately
        label.setText(new_text)
        
        # Create color flash animation by temporarily changing color
        if highlight_color and duration > 0:
            # Extract color from original style or use highlight color
            temp_style = original_style
            if "color:" in temp_style:
                # Replace existing color
                import re
                temp_style = re.sub(r'color:\s*[^;]+;', f'color: {highlight_color};', temp_style)
            else:
                # Add color if not present
                temp_style = temp_style.replace('QLabel {', f'QLabel {{ color: {highlight_color};')
            
            label.setStyleSheet(temp_style)
            
            # Restore original style after duration
            QTimer.singleShot(duration, lambda: label.setStyleSheet(original_style))

# ============= Icon Creator =============
class IconCreator:
    """Simple icon creator for the application with memory-efficient caching"""
    
    # Cache icons to reduce memory usage
    _tray_icon_cache = None
    _app_icon_cache = None
    
    @staticmethod
    def create_tray_icon() -> QIcon:
        """Create a simple tray icon (cached for memory efficiency)"""
        if IconCreator._tray_icon_cache is None:
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 0, 0, 0))
            
            from PyQt5.QtGui import QPainter, QBrush, QPen
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.setPen(QPen(QColor(0, 255, 65), 2))
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(2, 2, 12, 12)
            
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setBrush(QBrush(QColor(0, 255, 65)))
            painter.drawPie(3, 3, 10, 10, 0, 180 * 16)
            
            painter.end()
            IconCreator._tray_icon_cache = QIcon(pixmap)
        return IconCreator._tray_icon_cache
    
    @staticmethod
    def create_app_icon() -> QIcon:
        """Create application icon (cached for memory efficiency)"""
        if IconCreator._app_icon_cache is None:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 0, 0, 0))
            
            from PyQt5.QtGui import QPainter, QBrush, QPen
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.setPen(QPen(QColor(0, 255, 65), 3))
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(4, 4, 24, 24)
            
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(QBrush(QColor(0, 255, 65)))
            painter.drawPie(6, 6, 20, 20, 0, 180 * 16)
            
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(8, 8, 2, 2)
            painter.drawEllipse(14, 6, 2, 2)
            painter.drawEllipse(20, 8, 2, 2)
            
            painter.end()
            IconCreator._app_icon_cache = QIcon(pixmap)
        return IconCreator._app_icon_cache

# ============= IMPROVED Dimmer Overlay =============
class DimmerOverlay(QWidget):
    """ENHANCED overlay for much more effective screen dimming"""
    
    def __init__(self, screen=None):
        super().__init__()
        self.screen = screen if screen else QApplication.primaryScreen()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput |
            Qt.WindowDoesNotAcceptFocus
        )
        # Restore proper transparency for mouse events
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_AcceptTouchEvents, False)  # Disable touch events to allow system gestures
        self.setGeometry(self.screen.geometry())
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0)
        
        # Animation for smooth dimming transitions
        self._opacity_animation = None
        self._current_opacity = 0.0
        
        # Windows-specific configuration for better gesture support while maintaining click-through
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_NOACTIVATE = 0x08000000
                
                # Get current style
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                # Set layered window with transparency for click-through but allow gestures
                new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                print("Windows overlay configured for click-through and gesture support")
            except Exception as e:
                print(f"Failed to configure Windows overlay: {e}")
    
    def set_dimming(self, opacity: int, color: Optional[QColor] = None):
        """Set overlay opacity with MUCH MORE AGGRESSIVE dimming calculation (stability improved)"""
        try:
            # Validate opacity range
            opacity = max(0, min(95, opacity))
            
            if color:
                # Validate color values
                r = max(0, min(255, color.red()))
                g = max(0, min(255, color.green()))
                b = max(0, min(255, color.blue()))
                self.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
                
                # Special handling for blue light filter - use lighter, linear opacity
                # Blue light filter uses very low opacity values (0-12%) and needs to be readable
                if opacity <= 12:
                    # For blue light: use linear, light opacity - no aggressive multiplication
                    # 0% → 0.0, 12% → 0.12 (very subtle and readable)
                    actual_opacity = opacity / 100.0
                else:
                    # Regular dimming with color (when combined with dimmer)
                    # Use aggressive calculation but less so than pure black dimming
                    if opacity <= 15:
                        actual_opacity = opacity * 2.0 / 100  # Lighter than black dimming
                    elif opacity <= 30:
                        normalized = (opacity - 15) / 15
                        actual_opacity = 0.30 + (normalized ** 1.0) * 0.20
                    elif opacity <= 50:
                        normalized = (opacity - 30) / 20
                        actual_opacity = 0.50 + (normalized ** 1.2) * 0.15
                    else:
                        normalized = (opacity - 50) / 45
                        actual_opacity = 0.65 + (normalized ** 1.4) * 0.25
            else:
                # Pure black for maximum dimming effect
                self.setStyleSheet("background-color: rgb(0, 0, 0);")
                
                # MAXIMUM INTENSITY dimming calculation - extremely aggressive
                # Convert 0-95 slider range to maximum darkness at all levels
                if opacity <= 5:
                    # Very light dimming: 0-5% → 0-20% opacity
                    actual_opacity = opacity * 4.0 / 100
                elif opacity <= 15:
                    # Light dimming: 5-15% → 20-40% opacity
                    normalized = (opacity - 5) / 10
                    actual_opacity = 0.20 + (normalized ** 1.0) * 0.20
                elif opacity <= 30:
                    # Medium dimming: 15-30% → 40-65% opacity
                    normalized = (opacity - 15) / 15
                    actual_opacity = 0.40 + (normalized ** 1.2) * 0.25
                elif opacity <= 50:
                    # Heavy dimming: 30-50% → 65-80% opacity
                    normalized = (opacity - 30) / 20
                    actual_opacity = 0.65 + (normalized ** 1.4) * 0.15
                elif opacity <= 75:
                    # Very heavy dimming: 50-75% → 80-92% opacity
                    normalized = (opacity - 50) / 25
                    actual_opacity = 0.80 + (normalized ** 1.6) * 0.12
                else:
                    # EXTREME dimming: 75-95% → 92-99% opacity (almost black)
                    normalized = (opacity - 75) / 20
                    actual_opacity = 0.92 + (normalized ** 2.5) * 0.07
            
            # Clamp to safe range but allow maximum opacity
            actual_opacity = max(0.0, min(0.99, actual_opacity))
            
            # Smooth transition animation (with error handling)
            if self._opacity_animation:
                try:
                    self._opacity_animation.stop()
                except:
                    pass
            
            self._opacity_animation = QPropertyAnimation(self, b"windowOpacity")
            self._opacity_animation.setDuration(400)  # 400ms smooth transition
            self._opacity_animation.setEasingCurve(QEasingCurve.InOutCubic)
            self._opacity_animation.setStartValue(self._current_opacity)
            self._opacity_animation.setEndValue(actual_opacity)
            self._opacity_animation.finished.connect(lambda: setattr(self, '_current_opacity', actual_opacity))
            self._opacity_animation.start()
            
            self._current_opacity = actual_opacity
        except Exception as e:
            print(f"Error in set_dimming: {e}")
            # Fallback: set opacity directly without animation
            try:
                if opacity <= 95:
                    fallback_opacity = min(0.99, opacity / 100.0)
                    self.setWindowOpacity(fallback_opacity)
            except:
                pass
    
    def temporarily_hide_for_gestures(self):
        """Temporarily hide overlay to allow system gestures"""
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                
                # Temporarily remove transparency to allow gestures
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                new_style = current_style & ~WS_EX_TRANSPARENT  # Remove transparency
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                
                # Restore transparency after a short delay
                QTimer.singleShot(1000, lambda: self._restore_transparency())
            except Exception as e:
                print(f"Failed to temporarily hide overlay: {e}")
    
    def _restore_transparency(self):
        """Restore transparency after gesture mode"""
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                
                # Restore transparency
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                new_style = current_style | WS_EX_TRANSPARENT
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            except Exception as e:
                print(f"Failed to restore transparency: {e}")

# ============= Rain Overlay =============
class RainOverlay(QWidget):
    """Rain effect overlay for blinker"""
    
    def __init__(self, screen=None):
        super().__init__()
        self.screen = screen if screen else QApplication.primaryScreen()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setGeometry(self.screen.geometry())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        self.setWindowOpacity(1.0)
        
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_NOACTIVATE = 0x08000000
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                # Use layered window with transparency for click-through
                new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                print("Windows API rain overlay configured for click-through")
            except Exception as e:
                print(f"Failed to apply Windows API transparency: {e}")
        
        self.rain_items = []
        self.rain_timer = QTimer()
        self.rain_timer.timeout.connect(self._update_rain)
        self.rain_duration = 5000
        self.start_time = 0
        
    def start_rain(self, emoji_enabled: bool, text_enabled: bool):
        """Start rain effect"""
        self.emoji_enabled = emoji_enabled
        self.text_enabled = text_enabled
        self.rain_items = []
        self.start_time = QDateTime.currentMSecsSinceEpoch()
        
        self._create_rain_items()
        self.rain_timer.start(30)
        self.show()
        
    def _create_rain_items(self):
        """Create rain items (memory optimized)"""
        screen_rect = self.screen.geometry()
        # Limit items to prevent excessive memory usage
        max_items = getattr(self, 'max_rain_items', 50)
        emojis = ["👁️", "😊", "😉", "😴", "🥱", "😑", "😐", "🙄", "😏", "😌", "😋", "😍", "🤩", "😎", "🤓"]
        texts = ["Blink", "Blink", "Blink", "Are you blinking?", "Blink", "Blink", "Blink", "Are you blinking?"]
        
        # Memory optimization: limit items based on max_items setting
        item_count = min(25, max_items)
        spacing = screen_rect.width() // item_count if item_count > 0 else screen_rect.width() // 25
        for i in range(item_count):
            item = {}
            item['x'] = i * spacing + (spacing // 2)
            item['y'] = -50
            item['speed'] = 2 + (i % 5)
            
            if self.emoji_enabled and self.text_enabled:
                if i % 2 == 0:
                    item['content'] = emojis[i % len(emojis)]
                    item['type'] = 'emoji'
                else:
                    item['content'] = texts[i % len(texts)]
                    item['type'] = 'text'
            elif self.emoji_enabled:
                item['content'] = emojis[i % len(emojis)]
                item['type'] = 'emoji'
            else:
                item['content'] = texts[i % len(texts)]
                item['type'] = 'text'
                
            self.rain_items.append(item)
    
    def _update_rain(self):
        """Update rain animation (memory optimized)"""
        current_time = QDateTime.currentMSecsSinceEpoch()
        if current_time - self.start_time > self.rain_duration:
            # Stop rain and cleanup (memory optimization)
            self.rain_timer.stop()
            self.rain_items.clear()  # Clear items to free memory
            self.hide()
            return
            
        screen_rect = self.screen.geometry()
        # Memory optimization: remove items that are far off-screen
        self.rain_items = [item for item in self.rain_items if item['y'] < screen_rect.height() + 200]
        
        for item in self.rain_items:
            item['y'] += item['speed']
            if item['y'] > screen_rect.height():
                item['y'] = -50
                item['x'] = (item['x'] + 100) % screen_rect.width()
        
        self.update()
    
    def paintEvent(self, event):
        """Paint rain items"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = painter.font()
        font.setPointSize(20)
        painter.setFont(font)
        
        for item in self.rain_items:
            if item['type'] == 'emoji':
                painter.setPen(QPen(QColor(255, 255, 255, 255)))
                painter.drawText(item['x'], item['y'], item['content'])
            else:
                painter.setPen(QPen(QColor(0, 255, 65, 255)))
                painter.drawText(item['x'], item['y'], item['content'])

# ============= Profile Manager =============
class ProfileManager:
    """Manages profiles with caching"""
    
    def __init__(self):
        self._profiles: Dict[str, Profile] = {}
        self._cache_dirty = False
        self.load()
    
    def load(self):
        """Load profiles from disk"""
        try:
            with open(Config.PROFILES_FILE, 'r') as f:
                data = json.load(f)
                self._profiles = {k: Profile(**v) for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self._profiles = self._get_defaults()
            self.save()
    
    def save(self):
        """Save profiles to disk"""
        if not self._cache_dirty:
            return
            
        try:
            with open(Config.PROFILES_FILE, 'w') as f:
                data = {k: asdict(v) for k, v in self._profiles.items()}
                json.dump(data, f, indent=2)
            self._cache_dirty = False
        except IOError:
            pass
    
    def add(self, name: str, profile: Profile):
        """Add/update profile"""
        self._profiles[name] = profile
        self._cache_dirty = True
    
    def get(self, name: str) -> Optional[Profile]:
        """Get profile by name"""
        return self._profiles.get(name)
    
    def delete(self, name: str) -> bool:
        """Delete profile"""
        if name in self._profiles:
            del self._profiles[name]
            self._cache_dirty = True
            return True
        return False
    
    def list_names(self) -> list:
        """Get profile names"""
        return list(self._profiles.keys())
    
    def _get_defaults(self) -> Dict[str, Profile]:
        """Get default profiles - More intense values"""
        return {
            'Night Mode': Profile(85, True, 60),
            'Reading': Profile(60, False, 0),
            'Gaming': Profile(50, False, 0),
            'Movie': Profile(80, True, 30)
        }

# ============= State Manager =============
class StateManager:
    """Manages current dimmer state - saves and loads settings"""
    
    @staticmethod
    def save_state(dimmer_control):
        """Save current dimmer state to file"""
        try:
            state = {
                # Main dimmer settings
                'current_dim': dimmer_control.current_dim,
                'dimmer_active': dimmer_control.dimmer_active,
                'blue_light_active': dimmer_control.blue_light_active,
                'blue_intensity': dimmer_control.blue_intensity.value() if hasattr(dimmer_control, 'blue_intensity') and isinstance(getattr(dimmer_control, 'blue_intensity', None), QSlider) else (getattr(dimmer_control, 'blue_intensity', 50) if isinstance(getattr(dimmer_control, 'blue_intensity', None), int) else 50),
                
                # 2nd Display settings
                'second_display_enabled': dimmer_control.second_display_enabled,
                'second_display_dim': dimmer_control.second_display_dim,
                'second_display_blue_light': dimmer_control.second_display_blue_light,
                'second_display_blue_intensity': (
                    dimmer_control.second_display_blue_intensity 
                    if isinstance(dimmer_control.second_display_blue_intensity, int) 
                    else (
                        dimmer_control.second_display_blue_intensity_widget.value() 
                        if hasattr(dimmer_control, 'second_display_blue_intensity_widget') 
                           and dimmer_control.second_display_blue_intensity_widget
                        else getattr(dimmer_control, 'second_display_blue_intensity', 50)
                    )
                ),
                
                # Schedule settings
                'schedule_enabled': dimmer_control.schedule_enabled,
                'schedule_time_set': dimmer_control.schedule_time_set,
                'schedule_dim_value': dimmer_control.schedule_dim_value,
                'start_time': dimmer_control.start_time.toString('HH:mm') if dimmer_control.start_time else None,
                'end_time': dimmer_control.end_time.toString('HH:mm') if dimmer_control.end_time else None,
                
                # Blinker settings
                'blinker_active': dimmer_control.blinker_active,
                'emoji_blink_enabled': dimmer_control.emoji_blink_enabled,
                'text_blink_enabled': dimmer_control.text_blink_enabled,
                'rain_interval_minutes': dimmer_control.rain_interval_minutes,
                'rain_duration_seconds': dimmer_control.rain_duration_seconds,
            }
            
            with open(Config.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    @staticmethod
    def load_state():
        """Load dimmer state from file"""
        try:
            with open(Config.STATE_FILE, 'r') as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

# ============= Main Control Window =============
class DimmerControl(QWidget):
    """Main control window with enhanced UX"""
    
    def __init__(self):
        super().__init__()
        # Core components
        self.overlays: Dict[int, DimmerOverlay] = {}  # Store overlays by screen index
        self.profile_manager = ProfileManager()
        
        # State
        self.dimmer_active = False
        self.current_dim = Config.DEFAULT_DIM
        self.blue_light_active = False
        self.auto_dim_active = False
        self.hotkeys_active = False
        self.schedule_enabled = False
        self._toggle_in_progress = False  # Prevent multiple rapid toggles
        self._schedule_toggle_in_progress = False  # Prevent multiple rapid schedule toggles
        
        # Schedule variables
        self.start_time = None  # No default time - must be set by user
        self.end_time = None    # No default time - must be set by user
        self.schedule_dim_value = 70    # Default dim level
        self.schedule_time_set = False  # Track if user has set a schedule time
        
        # Timer variables
        self.timer_active = False
        self.timer_minutes = 0
        self.timer_end_time = None
        
        # Blinker variables
        self.blinker_active = False
        self.emoji_blink_enabled = False
        self.text_blink_enabled = True  # Always ticked
        self.rain_interval_minutes = 10
        self.rain_duration_seconds = 7
        self.rain_timer_active = False
        self.rain_overlays: Dict[int, RainOverlay] = {}  # Store rain overlays by screen index
        self.blinker_start_time = 0  # Track when blinker timer started
        
        # 2nd Display variables
        self.second_display_enabled = False
        self.second_display_dim = Config.DEFAULT_DIM
        self.second_display_blue_light = False
        self.second_display_blue_intensity = 50  # Value (will be overwritten with widget, then back to value)
        self.second_display_blue_intensity_widget = None  # Widget reference (set in _create_second_display_tab)
        self.second_display_preset_buttons = []  # Will be populated in tab creation
        
        # Initialize UI and features
        self._init_ui()
        self._load_saved_state()  # Load saved state after UI is created
        self._init_tray()
        self._init_timers()
        self._init_hotkeys()
        
    def _init_ui(self):
        """Initialize UI with dynamic sizing"""
        self.setWindowTitle(f'{Config.APP_NAME} v{Config.APP_VERSION}')
        self.setWindowIcon(IconCreator.create_app_icon())  # Set application icon
        self.setMinimumSize(600, 800)
        self.setMaximumSize(1200, 1500)  # Increased max size for better flexibility
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.setWindowFlags(Qt.Window)
        self.setStyleSheet(StyleManager.get_app_stylesheet())
        # Screen reader support
        self.setAccessibleName("Screen Dimmer Main Window")
        self.setAccessibleDescription("Main control window for screen dimming and blue light filtering application")
        
        # Main layout with proper margins
        layout = QVBoxLayout()
        layout.setSpacing(25)  # Increased spacing between major sections
        layout.setContentsMargins(Config.MAIN_MARGIN, Config.MAIN_MARGIN, Config.MAIN_MARGIN, Config.MAIN_MARGIN)
        
        # Header
        layout.addWidget(self._create_header())
        
        # Disclaimer
        layout.addWidget(self._create_disclaimer())
        
        # Add spacing between header and tabs
        layout.addSpacing(20)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(700)  # Make tabs container bigger
        self.tabs.setAccessibleName("Main Tabs")
        self.tabs.setAccessibleDescription("Tab navigation for Main, Schedule, Blinker, and Second Display controls")
        self.tabs.addTab(self._create_main_tab(), "⚡ Main")
        self.tabs.addTab(self._create_schedule_tab(), "🕐 Schedule")
        self.tabs.addTab(self._create_blinker_tab(), "✨ Blinker")
        self.tabs.addTab(self._create_second_display_tab(), "🖥️ 2nd Display")
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = self._create_status_bar()
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
    
    def _create_header(self) -> QWidget:
        """Create dynamic header"""
        header = QWidget()
        header.setSizePolicy(header.sizePolicy().Expanding, header.sizePolicy().Minimum)
        header.setStyleSheet(f"background-color: {Config.PRIMARY_COLOR}; border-radius: 8px;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)
        title = QLabel(f"🖥️ {Config.APP_NAME}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; padding: 5px;")
        title.setWordWrap(True)
        
        author = QLabel("👨‍💻 By: <a href='https://t.me/flamemodparadise' style='color: #e6f3ff; text-decoration: none;'>Bijay Koirala</a>")
        author.setAlignment(Qt.AlignCenter)
        author.setStyleSheet("color: #e6f3ff; font-size: 18px; padding: 2px;")
        author.setOpenExternalLinks(True)
        author.setWordWrap(True)
        
        contact_link = QLabel("Contact: <a href='https://bijaykoirala0.com.np' style='color: #e6f3ff; text-decoration: none;'>My Profile</a>")
        contact_link.setAlignment(Qt.AlignCenter)
        contact_link.setStyleSheet("color: #e6f3ff; font-size: 18px; padding: 2px;")
        contact_link.setOpenExternalLinks(True)
        contact_link.setWordWrap(True)
        
        tools_link = QLabel("Ok Bye")
        tools_link.setAlignment(Qt.AlignCenter)
        tools_link.setStyleSheet("color: #e6f3ff; font-size: 18px; padding: 2px;")
        tools_link.setOpenExternalLinks(True)
        tools_link.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(contact_link)
        layout.addWidget(tools_link)
        header.setLayout(layout)
        return header
    
    def _create_disclaimer(self) -> QWidget:
        """Create disclaimer widget"""
        disclaimer = QWidget()
        disclaimer.setSizePolicy(disclaimer.sizePolicy().Expanding, disclaimer.sizePolicy().Minimum)
        disclaimer.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.BORDER_COLOR};
            border-radius: 6px;
            padding: 10px;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        disclaimer_text = QLabel("⚠️ <b>Disclaimer:</b> This tool provides screen dimming and blue light filtering for eye comfort only. Not a medical device. Use responsibly and take regular breaks from screens.")
        disclaimer_text.setStyleSheet(f"""
            color: {Config.WARNING_COLOR};
            font-size: 16px;
            padding: 5px;
            background-color: transparent;
        """)
        disclaimer_text.setWordWrap(True)
        disclaimer_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(disclaimer_text)
        disclaimer.setLayout(layout)
        return disclaimer
    
    def _create_main_tab(self) -> QWidget:
        """Create main control tab with dynamic sizing"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget
        widget = QWidget()
        widget.setSizePolicy(widget.sizePolicy().Expanding, widget.sizePolicy().Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(22)  # Increased spacing in main tab
        layout.setContentsMargins(30, 30, 30, 30)  # Increased padding
        
        # Brightness control
        dim_group = QGroupBox("🔆 Brightness Control")
        dim_group.setSizePolicy(dim_group.sizePolicy().Expanding, dim_group.sizePolicy().Minimum)
        dim_layout = QVBoxLayout()
        dim_layout.setSpacing(22)  # Increased spacing in brightness control
        dim_layout.setContentsMargins(20, 28, 20, 20)
        
        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(15)
        
        self.dim_slider = QSlider(Qt.Horizontal)
        self.dim_slider.setRange(0, 95)
        self.dim_slider.setValue(25)
        self.dim_slider.valueChanged.connect(self._on_dim_changed)
        self.dim_slider.setMinimumHeight(30)
        self.dim_slider.setToolTip("Adjust screen brightness dimming level (0-95%). Higher values = darker screen.")
        self.dim_slider.setAccessibleName("Brightness Dimming Slider")
        self.dim_slider.setAccessibleDescription("Adjusts the screen brightness dimming level from 0 to 95 percent. Higher values create a darker screen.")
        slider_layout.addWidget(self.dim_slider)
        
        self.dim_label = QLabel("25%")
        self.dim_label.setAlignment(Qt.AlignCenter)
        self.dim_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff41; min-width: 60px; padding: 5px;")
        slider_layout.addWidget(self.dim_label)
        
        dim_layout.addLayout(slider_layout)
        
        # Presets - Maximum intensity values
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(12)
        for value in [15, 30, 50, 80]:
            btn = QPushButton(f"{value}%")
            btn.setStyleSheet(StyleManager.get_preset_button_style())
            btn.setMinimumHeight(15)
            btn.setMinimumWidth(22)
            btn.setToolTip(f"Quick preset: Set dimming to {value}%")
            btn.setAccessibleName(f"Preset Button {value} Percent")
            btn.setAccessibleDescription(f"Quick preset button to set dimming level to {value} percent")
            btn.clicked.connect(lambda _, v=value: self.dim_slider.setValue(v))
            preset_layout.addWidget(btn)
        
        dim_layout.addLayout(preset_layout)
        dim_group.setLayout(dim_layout)
        layout.addWidget(dim_group)
        
        # Toggle button
        self.toggle_btn = QPushButton("⚡ Enable Dimmer")
        self.toggle_btn.setStyleSheet(StyleManager.get_button_style(Config.SUCCESS_COLOR))
        self.toggle_btn.setMinimumHeight(50)
        self.toggle_btn.setMaximumHeight(60)
        self.toggle_btn.setToolTip("Enable or disable the screen dimmer. Shortcut: Alt+D")
        self.toggle_btn.setAccessibleName("Enable Dimmer Button")
        self.toggle_btn.setAccessibleDescription("Main toggle button to enable or disable screen dimming. Keyboard shortcut: Alt+D")
        self.toggle_btn.clicked.connect(self._toggle_dimmer)
        layout.addWidget(self.toggle_btn)
        
        # Blue light filter
        blue_group = QGroupBox("🔵 Blue Light Filter")
        blue_group.setSizePolicy(blue_group.sizePolicy().Expanding, blue_group.sizePolicy().Minimum)
        blue_layout = QVBoxLayout()
        blue_layout.setSpacing(22)  # Increased spacing in blue light control
        blue_layout.setContentsMargins(20, 28, 20, 20)
        
        self.blue_check = QCheckBox("Enable Blue Light Filter")
        self.blue_check.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        self.blue_check.setToolTip("Filter harmful blue light to reduce eye strain and improve sleep quality. Creates a warm, comfortable viewing experience.")
        self.blue_check.stateChanged.connect(self._on_blue_light_changed)
        blue_layout.addWidget(self.blue_check)
        
        intensity_layout = QHBoxLayout()
        intensity_layout.setSpacing(18)  # Increased spacing in intensity controls
        
        intensity_label = QLabel("Intensity:")
        intensity_label.setStyleSheet("font-size: 18px; font-weight: bold; min-width: 80px; padding: 5px;")
        intensity_layout.addWidget(intensity_label)
        
        self.blue_intensity = QSlider(Qt.Horizontal)
        self.blue_intensity.setRange(0, 100)
        self.blue_intensity.setValue(50)
        self.blue_intensity.valueChanged.connect(self._on_blue_intensity_changed)
        self.blue_intensity.setEnabled(False)
        self.blue_intensity.setMinimumHeight(30)
        self.blue_intensity.setToolTip("Adjust blue light filter intensity (0-100%). Higher values = warmer screen color.")
        self.blue_intensity.setAccessibleName("Blue Light Filter Intensity Slider")
        self.blue_intensity.setAccessibleDescription("Adjusts the blue light filter intensity from 0 to 100 percent. Higher values create a warmer screen color.")
        intensity_layout.addWidget(self.blue_intensity)
        
        self.warmth_label = QLabel("50%")
        self.warmth_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff8000; min-width: 50px; padding: 5px;")
        intensity_layout.addWidget(self.warmth_label)
        
        blue_layout.addLayout(intensity_layout)
        blue_group.setLayout(blue_layout)
        layout.addWidget(blue_group)
        
        # Add info about brightness control
        brightness_info = QLabel("🔆 <b>Screen Dimming:</b> Reduces screen brightness to protect your eyes and save battery. Perfect for dark environments or reducing eye strain.")
        brightness_info.setSizePolicy(brightness_info.sizePolicy().Expanding, brightness_info.sizePolicy().Minimum)
        brightness_info.setStyleSheet(f"""
            color: {Config.INFO_COLOR};
            font-size: 17px;
            font-family: "Segoe UI", "Arial", sans-serif;
            padding: 10px;
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.BORDER_COLOR};
            border-radius: 6px;
        """)
        brightness_info.setWordWrap(True)
        brightness_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(brightness_info)
        
        # Add info about blue light filter
        blue_light_info = QLabel("🔵 <b>Blue Light Filter:</b> Filters out harmful blue light that can cause eye strain and disrupt sleep. Creates a warm, comfortable viewing experience for evening and night use.")
        blue_light_info.setSizePolicy(blue_light_info.sizePolicy().Expanding, blue_light_info.sizePolicy().Minimum)
        blue_light_info.setStyleSheet(f"""
            color: {Config.INFO_COLOR};
            font-size: 17px;
            font-family: "Segoe UI", "Arial", sans-serif;
            padding: 10px;
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.BORDER_COLOR};
            border-radius: 6px;
        """)
        blue_light_info.setWordWrap(True)
        blue_light_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(blue_light_info)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Set widget to scroll area
        scroll.setWidget(widget)
        return scroll
    
    def _create_schedule_tab(self) -> QWidget:
        """Create simple schedule tab like main page"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget
        widget = QWidget()
        widget.setSizePolicy(widget.sizePolicy().Expanding, widget.sizePolicy().Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(18)  # Increased spacing in schedule tab
        layout.setContentsMargins(30, 30, 30, 30)  # Increased padding
        
        # Preset buttons
        preset_group = QGroupBox("⏰ Schedule Presets")
        preset_group.setSizePolicy(preset_group.sizePolicy().Expanding, preset_group.sizePolicy().Minimum)
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(18)  # Increased spacing in schedule presets
        preset_layout.setContentsMargins(18, 25, 18, 18)
        
        # Preset buttons
        preset_buttons_layout = QHBoxLayout()
        preset_buttons_layout.setSpacing(10)
        
        # 1. All Day (☀️)
        all_day_btn = QPushButton("☀️ All Day\n6 AM - 6 PM")
        all_day_btn.setStyleSheet(StyleManager.get_preset_button_style())
        all_day_btn.setMinimumHeight(50)
        all_day_btn.setMinimumWidth(120)
        all_day_btn.setToolTip("Set automatic dimming schedule from 6 AM to 6 PM (daytime)")
        all_day_btn.clicked.connect(lambda: self._apply_preset("all_day"))
        preset_buttons_layout.addWidget(all_day_btn)

        # 2. All Night (🌙)
        all_night_btn = QPushButton("🌙 All Night\n6 PM - 6 AM")
        all_night_btn.setStyleSheet(StyleManager.get_preset_button_style())
        all_night_btn.setMinimumHeight(50)
        all_night_btn.setMinimumWidth(120)
        all_night_btn.setToolTip("Set automatic dimming schedule from 6 PM to 6 AM (nighttime)")
        all_night_btn.clicked.connect(lambda: self._apply_preset("all_night"))
        preset_buttons_layout.addWidget(all_night_btn)

        # 3. Custom
        custom_btn = QPushButton("⚙️ Custom\nSet Your Own")
        custom_btn.setStyleSheet(StyleManager.get_preset_button_style())
        custom_btn.setMinimumHeight(50)
        custom_btn.setMinimumWidth(120)
        custom_btn.setToolTip("Set a custom schedule with your own start time, end time, and dimming level")
        custom_btn.clicked.connect(self._show_custom_time_dialog)
        preset_buttons_layout.addWidget(custom_btn)

        # 4. Timer (⏱️)
        timer_btn = QPushButton("⏱️ Timer\nQuick Start")
        timer_btn.setStyleSheet(StyleManager.get_preset_button_style())
        timer_btn.setMinimumHeight(50)
        timer_btn.setMinimumWidth(120)
        timer_btn.setToolTip("Start a quick timer that automatically disables dimming after a set duration")
        timer_btn.clicked.connect(self._show_timer_dialog)
        preset_buttons_layout.addWidget(timer_btn)
        
        preset_layout.addLayout(preset_buttons_layout)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Schedule display
        self.schedule_display = QLabel("No schedule set - Choose a preset first")
        self.schedule_display.setMinimumHeight(80)
        self.schedule_display.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.MUTED_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.MUTED_COLOR};
        """)
        self.schedule_display.setAlignment(Qt.AlignCenter)
        self.schedule_display.setWordWrap(True)
        layout.addWidget(self.schedule_display)
        
        # Control buttons
        self.schedule_control_btn = QPushButton("🚀 Enable Schedule")
        self.schedule_control_btn.setStyleSheet(StyleManager.get_button_style(Config.SUCCESS_COLOR))
        self.schedule_control_btn.setMinimumHeight(50)
        self.schedule_control_btn.setEnabled(False)
        self.schedule_control_btn.setToolTip("Enable or disable the automatic schedule. First select a preset above.")
        self.schedule_control_btn.setAccessibleName("Enable Schedule Button")
        self.schedule_control_btn.setAccessibleDescription("Button to enable or disable automatic dimming schedule. Select a preset first.")
        self.schedule_control_btn.clicked.connect(self._toggle_schedule_control)
        layout.addWidget(self.schedule_control_btn)
        
        # Time remaining display
        self.time_remaining_label = QLabel("No schedule set")
        self.time_remaining_label.setMinimumHeight(60)
        self.time_remaining_label.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.INFO_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.INFO_COLOR};
        """)
        self.time_remaining_label.setAlignment(Qt.AlignCenter)
        self.time_remaining_label.setWordWrap(True)
        layout.addWidget(self.time_remaining_label)
        
        # Status
        self.schedule_status = QLabel("Status: Disabled")
        self.schedule_status.setStyleSheet(f"""
            color: {Config.MUTED_COLOR};
            font-size: 18px;
            padding: 10px;
            text-align: center;
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.BORDER_COLOR};
            border-radius: 6px;
        """)
        self.schedule_status.setAlignment(Qt.AlignCenter)
        self.schedule_status.setWordWrap(True)
        layout.addWidget(self.schedule_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Set widget to scroll area
        scroll.setWidget(widget)
        return scroll
    
    
    def _create_status_bar(self) -> QWidget:
        """Create dynamic status bar"""
        status = QWidget()
        status.setSizePolicy(status.sizePolicy().Expanding, status.sizePolicy().Minimum)
        status.setStyleSheet(f"background-color: {Config.CARD_COLOR}; border-radius: 6px;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.status_label = QLabel("Dimmer Inactive")
        self.status_label.setStyleSheet("color: #666666; padding: 5px; font-size: 17px;")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Add shortcut info
        shortcut_label = QLabel("⌨️ Alt+D: Toggle | Alt+G: Gestures")
        shortcut_label.setStyleSheet("color: #00ff41; padding: 5px; font-size: 16px; font-weight: bold;")
        layout.addWidget(shortcut_label)
        
        status.setLayout(layout)
        return status
    
    def _create_blinker_tab(self) -> QWidget:
        """Create blinker tab with rain effects"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget
        widget = QWidget()
        widget.setSizePolicy(widget.sizePolicy().Expanding, widget.sizePolicy().Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)  # Increased padding
        
        # Blinker Control section
        blinker_control_group = QGroupBox("✨ Blinker Control")
        blinker_control_group.setSizePolicy(blinker_control_group.sizePolicy().Expanding, blinker_control_group.sizePolicy().Minimum)
        blinker_control_layout = QVBoxLayout()
        blinker_control_layout.setSpacing(18)
        blinker_control_layout.setContentsMargins(18, 25, 18, 18)
        
        # Emoji checkbox
        self.emoji_checkbox = QCheckBox("🎭 Blinking Emojis")
        self.emoji_checkbox.setStyleSheet("font-size: 18px; color: #c9d1d9;")
        self.emoji_checkbox.setToolTip("Enable emoji animations in the blink reminder rain effect")
        self.emoji_checkbox.setAccessibleName("Blinking Emojis Checkbox")
        self.emoji_checkbox.setAccessibleDescription("Checkbox to enable emoji animations in the blink reminder rain effect")
        self.emoji_checkbox.stateChanged.connect(self._on_emoji_blink_changed)
        blinker_control_layout.addWidget(self.emoji_checkbox)

        # Text checkbox (always ticked)
        self.text_checkbox = QCheckBox("📝 Blinking Text")
        self.text_checkbox.setStyleSheet("font-size: 18px; color: #c9d1d9;")
        self.text_checkbox.setChecked(True)  # Always ticked
        self.text_checkbox.setEnabled(False)  # Disabled so user can't untick
        self.text_checkbox.setToolTip("Text reminders are always enabled to help you remember to blink")
        self.text_checkbox.setAccessibleName("Blinking Text Checkbox")
        self.text_checkbox.setAccessibleDescription("Text reminders are always enabled to help you remember to blink")
        blinker_control_layout.addWidget(self.text_checkbox)
        
        blinker_control_group.setLayout(blinker_control_layout)
        layout.addWidget(blinker_control_group)
        
        # Rain Settings section
        rain_settings_group = QGroupBox("🌧️ Rain Settings")
        rain_settings_group.setSizePolicy(rain_settings_group.sizePolicy().Expanding, rain_settings_group.sizePolicy().Minimum)
        rain_settings_layout = QVBoxLayout()
        rain_settings_layout.setSpacing(18)
        rain_settings_layout.setContentsMargins(18, 25, 18, 18)
        
        # Rain interval input
        rain_interval_layout = QHBoxLayout()
        rain_interval_layout.setSpacing(10)
        
        rain_interval_label = QLabel("Rain Interval:")
        rain_interval_label.setStyleSheet("font-size: 18px; font-weight: bold; min-width: 120px; padding: 5px;")
        rain_interval_layout.addWidget(rain_interval_label)
        
        self.rain_interval_spinbox = QSpinBox()
        self.rain_interval_spinbox.setRange(1, 60)  # 1 to 60 minutes
        self.rain_interval_spinbox.setValue(10)  # Default 10 minutes
        self.rain_interval_spinbox.setSuffix(" min")
        self.rain_interval_spinbox.setStyleSheet("font-size: 18px;")
        self.rain_interval_spinbox.setToolTip("Time interval between blink reminders (1-60 minutes)")
        self.rain_interval_spinbox.setAccessibleName("Rain Interval Spinbox")
        self.rain_interval_spinbox.setAccessibleDescription("Set the time interval between blink reminders in minutes, from 1 to 60")
        self.rain_interval_spinbox.valueChanged.connect(self._on_rain_interval_changed)
        rain_interval_layout.addWidget(self.rain_interval_spinbox)
        
        rain_interval_layout.addStretch()
        rain_settings_layout.addLayout(rain_interval_layout)
        
        # Rain duration input
        rain_duration_layout = QHBoxLayout()
        rain_duration_layout.setSpacing(10)
        
        rain_duration_label = QLabel("Rain Time:")
        rain_duration_label.setStyleSheet("font-size: 18px; font-weight: bold; min-width: 120px; padding: 5px;")
        rain_duration_layout.addWidget(rain_duration_label)
        
        self.rain_duration_spinbox = QSpinBox()
        self.rain_duration_spinbox.setRange(1, 30)  # 1 to 30 seconds
        self.rain_duration_spinbox.setValue(7)  # Default 7 seconds
        self.rain_duration_spinbox.setSuffix(" sec")
        self.rain_duration_spinbox.setStyleSheet("font-size: 18px;")
        self.rain_duration_spinbox.setToolTip("Duration of the blink reminder rain effect (1-30 seconds)")
        self.rain_duration_spinbox.setAccessibleName("Rain Duration Spinbox")
        self.rain_duration_spinbox.setAccessibleDescription("Set the duration of the blink reminder rain effect in seconds, from 1 to 30")
        self.rain_duration_spinbox.valueChanged.connect(self._on_rain_duration_changed)
        rain_duration_layout.addWidget(self.rain_duration_spinbox)
        
        rain_duration_layout.addStretch()
        rain_settings_layout.addLayout(rain_duration_layout)
        
        
        
        rain_settings_group.setLayout(rain_settings_layout)
        layout.addWidget(rain_settings_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # Enable Blinker button
        self.blinker_control_btn = QPushButton("🚀 Enable Blinker")
        self.blinker_control_btn.setStyleSheet(StyleManager.get_button_style(Config.SUCCESS_COLOR))
        self.blinker_control_btn.setMinimumHeight(50)
        self.blinker_control_btn.setToolTip("Enable or disable the blink reminder feature. Shortcut: Alt+R")
        self.blinker_control_btn.clicked.connect(self._toggle_blinker)
        control_layout.addWidget(self.blinker_control_btn)

        # Test button
        test_btn = QPushButton("🌧️ Test Rain")
        test_btn.setStyleSheet(StyleManager.get_button_style(Config.INFO_COLOR))
        test_btn.setMinimumHeight(50)
        test_btn.setToolTip("Test the blink reminder rain effect immediately")
        test_btn.clicked.connect(self._trigger_immediate_rain)
        control_layout.addWidget(test_btn)
        
        layout.addLayout(control_layout)
        
        # Status display (shows Inactive/Active with remaining time)
        self.blinker_status = QLabel("Status: Inactive")
        self.blinker_status.setMinimumHeight(60)
        self.blinker_status.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.MUTED_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.MUTED_COLOR};
        """)
        self.blinker_status.setAlignment(Qt.AlignCenter)
        self.blinker_status.setWordWrap(True)
        layout.addWidget(self.blinker_status)
        
        # Shortcut info
        shortcut_info = QLabel("⌨️ Alt+R: Blinker | Alt+G: Gestures")
        shortcut_info.setStyleSheet("color: #00ff41; padding: 10px; font-size: 16px; font-weight: bold; text-align: center;")
        shortcut_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(shortcut_info)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Set widget to scroll area
        scroll.setWidget(widget)
        return scroll
    
    def _create_second_display_tab(self) -> QWidget:
        """Create 2nd display tab with independent controls"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget
        widget = QWidget()
        widget.setSizePolicy(widget.sizePolicy().Expanding, widget.sizePolicy().Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(22)
        layout.setContentsMargins(30, 30, 30, 30)  # Increased padding
        
        # Check if 2nd display is available
        screens = QApplication.screens()
        has_second_display = len(screens) > 1
        
        # Display status
        status_group = QGroupBox("📺 Display Status")
        status_group.setSizePolicy(status_group.sizePolicy().Expanding, status_group.sizePolicy().Minimum)
        status_layout = QVBoxLayout()
        status_layout.setSpacing(15)
        status_layout.setContentsMargins(20, 28, 20, 20)
        
        if has_second_display:
            status_text = f"✅ {len(screens)} display(s) detected"
            status_color = Config.SUCCESS_COLOR
            primary_info = QLabel(f"Primary: {screens[0].name()} ({screens[0].geometry().width()}x{screens[0].geometry().height()})")
            primary_info.setStyleSheet(f"font-size: 16px; color: {Config.TEXT_COLOR}; padding: 5px;")
            status_layout.addWidget(primary_info)
            
            if len(screens) > 1:
                second_info = QLabel(f"2nd Display: {screens[1].name()} ({screens[1].geometry().width()}x{screens[1].geometry().height()})")
                second_info.setStyleSheet(f"font-size: 16px; color: {Config.TEXT_COLOR}; padding: 5px;")
                status_layout.addWidget(second_info)
        else:
            status_text = "⚠️ Only 1 display detected - Connect a 2nd display via HDMI"
            status_color = Config.WARNING_COLOR
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {status_color}; padding: 10px;")
        status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Enable 2nd Display checkbox
        enable_group = QGroupBox("🖥️ 2nd Display Control")
        enable_group.setSizePolicy(enable_group.sizePolicy().Expanding, enable_group.sizePolicy().Minimum)
        enable_layout = QVBoxLayout()
        enable_layout.setSpacing(22)
        enable_layout.setContentsMargins(20, 28, 20, 20)
        
        self.second_display_check = QCheckBox("Enable 2nd Display Dimming")
        self.second_display_check.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        self.second_display_check.setEnabled(has_second_display)
        self.second_display_check.setToolTip("Enable independent dimming control for your second monitor")
        self.second_display_check.setAccessibleName("Enable Second Display Checkbox")
        self.second_display_check.setAccessibleDescription("Checkbox to enable independent dimming control for your second monitor")
        self.second_display_check.stateChanged.connect(self._on_second_display_changed)
        enable_layout.addWidget(self.second_display_check)
        
        enable_group.setLayout(enable_layout)
        layout.addWidget(enable_group)
        
        # Brightness control for 2nd display
        dim_group = QGroupBox("🔆 2nd Display Brightness")
        dim_group.setSizePolicy(dim_group.sizePolicy().Expanding, dim_group.sizePolicy().Minimum)
        dim_layout = QVBoxLayout()
        dim_layout.setSpacing(22)
        dim_layout.setContentsMargins(20, 28, 20, 20)
        
        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(15)
        
        self.second_display_slider = QSlider(Qt.Horizontal)
        self.second_display_slider.setRange(0, 95)
        self.second_display_slider.setValue(Config.DEFAULT_DIM)
        self.second_display_slider.valueChanged.connect(self._on_second_display_dim_changed)
        self.second_display_slider.setMinimumHeight(30)
        self.second_display_slider.setEnabled(False)
        self.second_display_slider.setToolTip("Adjust brightness dimming level for the second display (0-95%). Enable 2nd Display Dimming first.")
        self.second_display_slider.setAccessibleName("Second Display Brightness Slider")
        self.second_display_slider.setAccessibleDescription("Adjusts the brightness dimming level for the second display from 0 to 95 percent. Enable 2nd Display Dimming first.")
        slider_layout.addWidget(self.second_display_slider)
        
        self.second_display_label = QLabel(f"{Config.DEFAULT_DIM}%")
        self.second_display_label.setAlignment(Qt.AlignCenter)
        self.second_display_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff41; min-width: 60px; padding: 5px;")
        slider_layout.addWidget(self.second_display_label)
        
        dim_layout.addLayout(slider_layout)
        
        # Presets
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(12)
        self.second_display_preset_buttons = []
        for value in [15, 30, 50, 80]:
            btn = QPushButton(f"{value}%")
            btn.setStyleSheet(StyleManager.get_preset_button_style())
            btn.setMinimumHeight(15)
            btn.setMinimumWidth(22)
            btn.setEnabled(False)
            btn.setToolTip(f"Quick preset: Set 2nd display dimming to {value}%")
            btn.setAccessibleName(f"Second Display Preset Button {value} Percent")
            btn.setAccessibleDescription(f"Quick preset button to set second display dimming level to {value} percent")
            btn.clicked.connect(lambda _, v=value: self.second_display_slider.setValue(v))
            self.second_display_preset_buttons.append(btn)
            preset_layout.addWidget(btn)
        
        dim_layout.addLayout(preset_layout)
        dim_group.setLayout(dim_layout)
        layout.addWidget(dim_group)
        
        # Blue light filter for 2nd display
        blue_group = QGroupBox("🔵 2nd Display Blue Light Filter")
        blue_group.setSizePolicy(blue_group.sizePolicy().Expanding, blue_group.sizePolicy().Minimum)
        blue_layout = QVBoxLayout()
        blue_layout.setSpacing(22)
        blue_layout.setContentsMargins(20, 28, 20, 20)
        
        self.second_display_blue_check = QCheckBox("Enable Blue Light Filter")
        self.second_display_blue_check.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        self.second_display_blue_check.setEnabled(False)
        self.second_display_blue_check.setToolTip("Enable blue light filter for the second display. Enable 2nd Display Dimming first.")
        self.second_display_blue_check.setAccessibleName("Second Display Blue Light Filter Checkbox")
        self.second_display_blue_check.setAccessibleDescription("Checkbox to enable blue light filter for the second display. Enable 2nd Display Dimming first.")
        self.second_display_blue_check.stateChanged.connect(self._on_second_display_blue_light_changed)
        blue_layout.addWidget(self.second_display_blue_check)
        
        intensity_layout = QHBoxLayout()
        intensity_layout.setSpacing(18)
        
        intensity_label = QLabel("Intensity:")
        intensity_label.setStyleSheet("font-size: 18px; font-weight: bold; min-width: 80px; padding: 5px;")
        intensity_layout.addWidget(intensity_label)
        
        self.second_display_blue_intensity_widget = QSlider(Qt.Horizontal)
        self.second_display_blue_intensity_widget.setRange(0, 100)
        self.second_display_blue_intensity_widget.setValue(50)
        self.second_display_blue_intensity_widget.valueChanged.connect(self._on_second_display_blue_intensity_changed)
        self.second_display_blue_intensity_widget.setEnabled(False)
        self.second_display_blue_intensity_widget.setMinimumHeight(30)
        self.second_display_blue_intensity_widget.setToolTip("Adjust blue light filter intensity for the second display (0-100%). Enable Blue Light Filter first.")
        intensity_layout.addWidget(self.second_display_blue_intensity_widget)
        # Also keep reference in original name for compatibility
        self.second_display_blue_intensity = self.second_display_blue_intensity_widget
        
        self.second_display_warmth_label = QLabel("50%")
        self.second_display_warmth_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff8000; min-width: 50px; padding: 5px;")
        intensity_layout.addWidget(self.second_display_warmth_label)
        
        blue_layout.addLayout(intensity_layout)
        blue_group.setLayout(blue_layout)
        layout.addWidget(blue_group)
        
        # Info
        info_label = QLabel("💡 <b>2nd Display:</b> Control the second monitor independently. Enable this feature to dim your extended display separately from the primary screen.")
        info_label.setSizePolicy(info_label.sizePolicy().Expanding, info_label.sizePolicy().Minimum)
        info_label.setStyleSheet(f"""
            color: {Config.INFO_COLOR};
            font-size: 17px;
            font-family: "Segoe UI", "Arial", sans-serif;
            padding: 10px;
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.BORDER_COLOR};
            border-radius: 6px;
        """)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Set widget to scroll area
        scroll.setWidget(widget)
        return scroll
    
    def _init_tray(self):
        """Initialize system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(IconCreator.create_tray_icon())
        self._update_tray_tooltip()
        
        menu = QMenu()
        show_action = QAction('Show/Hide', self)
        show_action.setToolTip("Show or hide the main window")
        show_action.triggered.connect(self._toggle_window)
        menu.addAction(show_action)
        
        toggle_action = QAction('Toggle Dimmer', self)
        toggle_action.setToolTip("Enable or disable screen dimming")
        toggle_action.triggered.connect(self._toggle_dimmer)
        menu.addAction(toggle_action)
        
        menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setToolTip("Exit the application")
        exit_action.triggered.connect(self.quit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(lambda r: self._toggle_window() if r in [QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick] else None)
        self.tray_icon.show()
    
    def _init_timers(self):
        """Initialize timers with optimized intervals"""
        # Schedule timer - check every 30 seconds (optimized from 60s for better responsiveness)
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self._check_schedule)
        
        # Time remaining timer - update every 10 seconds (optimized from frequent updates)
        self.time_remaining_timer = QTimer()
        self.time_remaining_timer.timeout.connect(self._update_time_remaining)
        
        # Blinker countdown timer - update every 1 second (optimized for smooth countdown)
        self.blinker_countdown_timer = QTimer()
        self.blinker_countdown_timer.timeout.connect(self._update_blinker_countdown)
        
        # Timer for quick timer feature - check every 10 seconds (optimized)
        self.timer_timer = QTimer()
        self.timer_timer.timeout.connect(self._check_timer)
        
        # Timer for blinker rain effect
        self.blinker_timer = QTimer()
        self.blinker_timer.timeout.connect(self._blinker_rain_effect)
    
    def _update_tray_tooltip(self):
        """Update system tray tooltip with current dimming level"""
        # Check if tray_icon exists (may not be initialized yet during startup)
        if not hasattr(self, 'tray_icon') or self.tray_icon is None:
            return
        
        if self.dimmer_active:
            status_text = f"Active - {self.current_dim}%"
            if self.blue_light_active:
                # Check if blue_intensity widget exists and is a QSlider
                if hasattr(self, 'blue_intensity') and isinstance(self.blue_intensity, QSlider):
                    status_text += f" | Blue Light: {self.blue_intensity.value()}%"
                elif isinstance(getattr(self, 'blue_intensity', None), int):
                    status_text += f" | Blue Light: {self.blue_intensity}%"
            if self.second_display_enabled:
                status_text += f" | 2nd Display: {self.second_display_dim}%"
        else:
            status_text = "Inactive"
        
        tooltip = f"{Config.APP_NAME}\nStatus: {status_text}\nDim Level: {self.current_dim}%"
        self.tray_icon.setToolTip(tooltip)
    
    def _init_hotkeys(self):
        """Initialize hotkey system"""
        self.hotkeys_active = True
        
        if GLOBAL_HOTKEYS_AVAILABLE:
            # Global Alt+D shortcut that works from anywhere
            try:
                keyboard.add_hotkey('alt+d', self._hotkey_callback)
                keyboard.add_hotkey('alt+r', self._blinker_hotkey_callback)
                keyboard.add_hotkey('alt+g', self._gesture_hotkey_callback)
                print("Global hotkeys Alt+D, Alt+R, and Alt+G registered successfully")
            except Exception as e:
                print(f"Failed to register global hotkeys: {e}")
                # Fallback to local shortcuts
                self.dimmer_shortcut = QShortcut(QKeySequence("Alt+D"), self)
                self.dimmer_shortcut.activated.connect(self._toggle_dimmer)
                self.blinker_shortcut = QShortcut(QKeySequence("Alt+R"), self)
                self.blinker_shortcut.activated.connect(self._toggle_blinker)
        else:
            # Fallback to local shortcuts if keyboard module not available
            self.dimmer_shortcut = QShortcut(QKeySequence("Alt+D"), self)
            self.dimmer_shortcut.activated.connect(self._toggle_dimmer)
            self.blinker_shortcut = QShortcut(QKeySequence("Alt+R"), self)
            self.blinker_shortcut.activated.connect(self._toggle_blinker)
            print("Using local hotkeys (install 'keyboard' module for global hotkeys)")
    
    def _hotkey_callback(self):
        """Thread-safe callback for global hotkey"""
        # Use QTimer.singleShot to ensure we're on the main thread
        QTimer.singleShot(0, self._toggle_dimmer)
    
    def _blinker_hotkey_callback(self):
        """Thread-safe callback for blinker hotkey"""
        # Use QTimer.singleShot to ensure we're on the main thread
        QTimer.singleShot(0, self._toggle_blinker)
    
    def _gesture_hotkey_callback(self):
        """Thread-safe callback for gesture hotkey - temporarily hide overlay"""
        # Use QTimer.singleShot to ensure we're on the main thread
        QTimer.singleShot(0, self._temporarily_hide_overlay)
    
    # ============= State Management =============
    
    def _load_saved_state(self):
        """Load saved dimmer state from file"""
        state = StateManager.load_state()
        if not state:
            return
        
        try:
            # Block signals during loading to prevent callbacks before initialization
            # Make sure all widgets are created before loading state
            # Load main dimmer settings
            if 'current_dim' in state:
                self.current_dim = state['current_dim']
                if hasattr(self, 'dim_slider'):
                    self.dim_slider.blockSignals(True)  # Block signals during loading
                    self.dim_slider.setValue(self.current_dim)
                    self.dim_slider.blockSignals(False)  # Re-enable signals
                    self.dim_label.setText(f"{self.current_dim}%")
            
            if 'blue_light_active' in state:
                self.blue_light_active = state['blue_light_active']
                if hasattr(self, 'blue_check'):
                    self.blue_check.blockSignals(True)
                    self.blue_check.setChecked(self.blue_light_active)
                    self.blue_check.blockSignals(False)
            
            if 'blue_intensity' in state:
                blue_intensity = state['blue_intensity']
                if hasattr(self, 'blue_intensity') and isinstance(self.blue_intensity, QSlider):
                    self.blue_intensity.blockSignals(True)
                    self.blue_intensity.setValue(blue_intensity)
                    self.blue_intensity.blockSignals(False)
                    self.blue_intensity.setEnabled(self.blue_light_active)
            
            # Load 2nd display settings
            if 'second_display_enabled' in state:
                self.second_display_enabled = state['second_display_enabled']
                if hasattr(self, 'second_display_check'):
                    self.second_display_check.blockSignals(True)
                    self.second_display_check.setChecked(self.second_display_enabled)
                    self.second_display_check.blockSignals(False)
            
            if 'second_display_dim' in state:
                self.second_display_dim = state['second_display_dim']
                if hasattr(self, 'second_display_slider'):
                    self.second_display_slider.blockSignals(True)
                    self.second_display_slider.setValue(self.second_display_dim)
                    self.second_display_slider.blockSignals(False)
            
            if 'second_display_blue_light' in state:
                self.second_display_blue_light = state['second_display_blue_light']
                if hasattr(self, 'second_display_blue_check'):
                    self.second_display_blue_check.blockSignals(True)
                    self.second_display_blue_check.setChecked(self.second_display_blue_light)
                    self.second_display_blue_check.blockSignals(False)
            
            if 'second_display_blue_intensity' in state:
                blue_intensity_value = state['second_display_blue_intensity']
                
                # Store the integer value
                self.second_display_blue_intensity = blue_intensity_value
                
                # Update widget if it exists (using separate widget reference)
                if hasattr(self, 'second_display_blue_intensity_widget') and self.second_display_blue_intensity_widget:
                    self.second_display_blue_intensity_widget.blockSignals(True)
                    self.second_display_blue_intensity_widget.setValue(blue_intensity_value)
                    self.second_display_blue_intensity_widget.blockSignals(False)
            
            # Load schedule settings
            if 'schedule_enabled' in state:
                self.schedule_enabled = state['schedule_enabled']
            
            if 'schedule_time_set' in state:
                self.schedule_time_set = state['schedule_time_set']
            
            if 'schedule_dim_value' in state:
                self.schedule_dim_value = state['schedule_dim_value']
            
            if 'start_time' in state and state['start_time']:
                try:
                    time_parts = state['start_time'].split(':')
                    self.start_time = QTime(int(time_parts[0]), int(time_parts[1]))
                    if hasattr(self, 'start_time_edit'):
                        self.start_time_edit.setTime(self.start_time)
                except:
                    pass
            
            if 'end_time' in state and state['end_time']:
                try:
                    time_parts = state['end_time'].split(':')
                    self.end_time = QTime(int(time_parts[0]), int(time_parts[1]))
                    if hasattr(self, 'end_time_edit'):
                        self.end_time_edit.setTime(self.end_time)
                except:
                    pass
            
            # Load blinker settings
            if 'blinker_active' in state:
                self.blinker_active = state['blinker_active']
            
            if 'emoji_blink_enabled' in state:
                self.emoji_blink_enabled = state['emoji_blink_enabled']
                if hasattr(self, 'emoji_checkbox'):
                    self.emoji_checkbox.blockSignals(True)
                    self.emoji_checkbox.setChecked(self.emoji_blink_enabled)
                    self.emoji_checkbox.blockSignals(False)
            
            if 'text_blink_enabled' in state:
                self.text_blink_enabled = state['text_blink_enabled']
                if hasattr(self, 'text_checkbox'):
                    self.text_checkbox.blockSignals(True)
                    self.text_checkbox.setChecked(self.text_blink_enabled)
                    self.text_checkbox.blockSignals(False)
            
            if 'rain_interval_minutes' in state:
                self.rain_interval_minutes = state['rain_interval_minutes']
                if hasattr(self, 'rain_interval_spinbox') and isinstance(self.rain_interval_spinbox, QSpinBox):
                    self.rain_interval_spinbox.blockSignals(True)
                    self.rain_interval_spinbox.setValue(self.rain_interval_minutes)
                    self.rain_interval_spinbox.blockSignals(False)
            
            if 'rain_duration_seconds' in state:
                self.rain_duration_seconds = state['rain_duration_seconds']
                if hasattr(self, 'rain_duration_spinbox') and isinstance(self.rain_duration_spinbox, QSpinBox):
                    self.rain_duration_spinbox.blockSignals(True)
                    self.rain_duration_spinbox.setValue(self.rain_duration_seconds)
                    self.rain_duration_spinbox.blockSignals(False)
            
            # Apply dimmer state if it was active (delay to ensure UI is ready)
            if 'dimmer_active' in state and state['dimmer_active']:
                QTimer.singleShot(100, lambda: self._toggle_dimmer() if not self.dimmer_active else None)
            
            # Apply blue light if it was active
            if self.blue_light_active:
                QTimer.singleShot(200, self._update_blue_light)
            
            # Apply 2nd display if it was enabled
            if self.second_display_enabled:
                QTimer.singleShot(300, self._update_second_display)
            
            # Apply schedule if it was enabled
            if self.schedule_enabled and self.schedule_time_set:
                if hasattr(self, 'schedule_control_btn') and not self.schedule_enabled:
                    QTimer.singleShot(400, lambda: self.schedule_control_btn.click())
            
            # Apply blinker if it was active
            if self.blinker_active:
                if hasattr(self, 'blinker_control_btn') and not self.blinker_active:
                    QTimer.singleShot(500, lambda: self.blinker_control_btn.click())
            
        except Exception as e:
            import traceback
            print(f"Error loading saved state: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def _save_state(self):
        """Save current dimmer state to file"""
        StateManager.save_state(self)
    
    # ============= Helper Methods =============
    
    def _get_overlay_for_screen(self, screen_index: int) -> Optional[DimmerOverlay]:
        """Get or create overlay for a specific screen (stability improved)"""
        try:
            if screen_index not in self.overlays:
                screens = QApplication.screens()
                if screen_index < len(screens) and screens[screen_index]:
                    overlay = DimmerOverlay(screens[screen_index])
                    if overlay:
                        overlay.showFullScreen()
                        self.overlays[screen_index] = overlay
                else:
                    return None
            return self.overlays.get(screen_index)
        except Exception as e:
            print(f"Error getting overlay for screen {screen_index}: {e}")
            return None
    
    def _close_overlay_for_screen(self, screen_index: int):
        """Close overlay for a specific screen (stability improved)"""
        try:
            if screen_index in self.overlays:
                overlay = self.overlays[screen_index]
                if overlay:
                    overlay.close()
                    overlay.deleteLater()  # Ensure proper cleanup
                del self.overlays[screen_index]
        except Exception as e:
            print(f"Error closing overlay for screen {screen_index}: {e}")
            # Clean up even if there's an error
            if screen_index in self.overlays:
                del self.overlays[screen_index]
    
    def _get_enabled_screens(self):
        """Get list of enabled screen indices"""
        screens = QApplication.screens()
        enabled = [0]  # Primary screen is always enabled
        
        if self.second_display_enabled and len(screens) > 1:
            enabled.append(1)  # 2nd display
        
        return enabled
    
    def _apply_dimming_to_screen(self, screen_index: int, opacity: int, color: Optional[QColor] = None):
        """Apply dimming to a specific screen (stability improved)"""
        try:
            overlay = self._get_overlay_for_screen(screen_index)
            if overlay:
                overlay.set_dimming(opacity, color)
        except Exception as e:
            print(f"Error applying dimming to screen {screen_index}: {e}")
    
    # ============= Event Handlers =============
    
    @pyqtSlot(int)
    def _on_dim_changed(self, value: int):
        """Handle dimming change with smooth animation"""
        self.current_dim = value
        # Animate label update
        AnimationHelper.animate_label_update(self.dim_label, f"{value}%", Config.SUCCESS_COLOR, duration=150)
        
        # Update tray tooltip with new dimming level
        self._update_tray_tooltip()
        
        # Save state
        self._save_state()
        
        if self.dimmer_active:
            if self.blue_light_active:
                self._update_blue_light()
            else:
                # Apply to primary screen with smooth transition
                self._apply_dimming_to_screen(0, value)
    
    @pyqtSlot(int)
    def _on_second_display_changed(self, state: int):
        """Handle 2nd display enable/disable"""
        self.second_display_enabled = state == Qt.Checked
        # Update tray tooltip
        self._update_tray_tooltip()
        
        # Save state
        self._save_state()
        
        # Enable/disable controls
        self.second_display_slider.setEnabled(self.second_display_enabled)
        self.second_display_blue_check.setEnabled(self.second_display_enabled)
        # Update widget if it exists
        if hasattr(self, 'second_display_blue_intensity_widget') and self.second_display_blue_intensity_widget:
            self.second_display_blue_intensity_widget.setEnabled(
                self.second_display_enabled and self.second_display_blue_check.isChecked()
            )
        
        # Enable/disable preset buttons
        for btn in self.second_display_preset_buttons:
            btn.setEnabled(self.second_display_enabled)
        
        if self.second_display_enabled:
            # Apply current settings to 2nd display
            if self.dimmer_active or self.blue_light_active:
                self._update_second_display()
        else:
            # Close 2nd display overlay
            self._close_overlay_for_screen(1)
    
    @pyqtSlot(int)
    def _on_second_display_dim_changed(self, value: int):
        """Handle 2nd display dimming change"""
        self.second_display_dim = value
        # Update tray tooltip
        self._update_tray_tooltip()
        self.second_display_label.setText(f"{value}%")
        
        # Save state
        self._save_state()
        
        if self.second_display_enabled:
            if self.second_display_blue_light:
                self._update_second_display()
            else:
                self._apply_dimming_to_screen(1, value)
    
    @pyqtSlot(int)
    def _on_second_display_blue_light_changed(self, state: int):
        """Handle 2nd display blue light toggle"""
        self.second_display_blue_light = state == Qt.Checked
        # Update widget if it exists
        if hasattr(self, 'second_display_blue_intensity_widget') and self.second_display_blue_intensity_widget:
            self.second_display_blue_intensity_widget.setEnabled(self.second_display_blue_light)
        
        # Save state
        self._save_state()
        
        self._update_second_display()
    
    @pyqtSlot(int)
    def _on_second_display_blue_intensity_changed(self, value: int):
        """Handle 2nd display blue light intensity change"""
        self.second_display_blue_intensity = value
        self.second_display_warmth_label.setText(f"{value}%")
        
        # Save state
        self._save_state()
        
        if self.second_display_blue_light:
            self._update_second_display()
    
    def _update_second_display(self):
        """Update 2nd display with clean orange tint overlay"""
        if not self.second_display_enabled:
            return
        
        overlay = self._get_overlay_for_screen(1)
        if overlay:
            intensity = self.second_display_blue_intensity
            color = self._calculate_blue_light_color(intensity) if self.second_display_blue_light else None
            
            if self.second_display_blue_light:
                if self.dimmer_active:
                    # Combine dimming + clean orange tint
                    overlay.set_dimming(self.second_display_dim, color)
                else:
                    # Clean orange tint overlay only - very light and readable
                    if intensity == 0:
                        opacity = 0  # No overlay at 0%
                    else:
                        opacity = int(intensity * 0.12)  # 0% to 12% opacity - very light
                    overlay.set_dimming(opacity, color)
            else:
                overlay.set_dimming(self.second_display_dim)
    
    @pyqtSlot(int)
    def _on_blue_light_changed(self, state: int):
        """Handle blue light toggle"""
        self.blue_light_active = state == Qt.Checked
        self.blue_intensity.setEnabled(self.blue_light_active)
        
        # Save state
        self._save_state()
        
        # Blue light filter works independently
        self._update_blue_light()
    
    @pyqtSlot(int)
    def _on_blue_intensity_changed(self, value: int):
        """Handle blue light intensity change"""
        self.warmth_label.setText(f"{value}%")
        
        # Save state
        self._save_state()
        
        # Update tray tooltip
        self._update_tray_tooltip()
        
        if self.blue_light_active:
            self._update_blue_light()
    
    @pyqtSlot(int)
    def _on_emoji_blink_changed(self, state: int):
        """Handle emoji blink checkbox change"""
        self.emoji_blink_enabled = state == Qt.Checked
        self._save_state()
    
    @pyqtSlot(int)
    def _on_rain_interval_changed(self, value: int):
        """Handle rain interval change"""
        self.rain_interval_minutes = value
        # Restart timer if blinker is active
        if self.blinker_active:
            self.blinker_timer.stop()
            self.blinker_timer.start(self.rain_interval_minutes * 60 * 1000)
        
        # Save state
        self._save_state()
    
    @pyqtSlot(int)
    def _on_rain_duration_changed(self, value: int):
        """Handle rain duration change"""
        self.rain_duration_seconds = value
        # Update rain overlay duration if it exists
        for rain_overlay in self.rain_overlays.values():
            rain_overlay.rain_duration = value * 1000  # Convert to milliseconds
        
        # Save state
        self._save_state()
    
    
    
    def _trigger_immediate_rain(self):
        """Trigger immediate rain effect for testing"""
        self._blinker_rain_effect()
    
    
    def _calculate_blue_light_color(self, intensity: int) -> QColor:
        """Calculate clean orange tint for blue light filter - readable and smooth"""
        # Clean orange tint overlay - truly transparent at 0%
        # Intensity 0-100: maps to warm orange strength
        
        # At 0%: Completely white (no tint) - 255, 255, 255
        # At 100%: Warm orange tint (255, 200, 150) - readable warm orange
        
        if intensity == 0:
            # No tint at all - pure white
            return QColor(255, 255, 255)
        
        # Red: Keep at maximum for warmth
        red = 255
        
        # Green: Reduce gradually for orange tint (255 → 200 at 100%)
        green = int(255 - (intensity * 0.55))
        
        # Blue: Reduce for blue light filtering (255 → 150 at 100%)
        blue = int(255 - (intensity * 1.05))
        
        # Ensure readable values
        green = max(200, green)
        blue = max(150, blue)
        
        return QColor(red, green, blue)
    
    def _update_blue_light(self):
        """Update blue light filter with clean orange tint overlay"""
        if self.blue_light_active:
            # Apply to primary screen
            overlay = self._get_overlay_for_screen(0)
            if overlay:
                intensity = self.blue_intensity.value()
                color = self._calculate_blue_light_color(intensity)
                
                if self.dimmer_active:
                    # Combine dimming + clean orange tint
                    overlay.set_dimming(self.current_dim, color)
                else:
                    # Clean orange tint overlay only - very light and readable
                    # Range: 0% to 12% opacity - starts at 0, very subtle
                    if intensity == 0:
                        opacity = 0  # No overlay at 0%
                    else:
                        opacity = int(intensity * 0.12)  # 0% to 12% opacity - very light
                    overlay.set_dimming(opacity, color)
        else:
            # Blue light disabled
            if not self.dimmer_active:
                # Close primary overlay if dimmer is also not active
                self._close_overlay_for_screen(0)
            else:
                # Keep overlay but remove orange tint, keep dimming only
                self._apply_dimming_to_screen(0, self.current_dim)
    
    def _toggle_dimmer(self):
        """Toggle dimmer state"""
        # Prevent multiple rapid toggles
        if self._toggle_in_progress:
            return
        self._toggle_in_progress = True
        
        try:
            if not self.dimmer_active:
                # Apply to enabled screens
                enabled_screens = self._get_enabled_screens()
                
                for screen_idx in enabled_screens:
                    if screen_idx == 0:  # Primary screen
                        if self.blue_light_active:
                            self._update_blue_light()
                        else:
                            self._apply_dimming_to_screen(0, self.current_dim)
                    elif screen_idx == 1:  # 2nd display
                        if self.second_display_enabled:
                            self._update_second_display()
                
                self.dimmer_active = True
                self.toggle_btn.setText("⏸️ Disable Dimmer")
                # Use animation helper for smooth transition
                AnimationHelper.animate_button_state(
                    self.toggle_btn, True, Config.WARNING_COLOR, Config.SUCCESS_COLOR
                )
                # Animate label update
                AnimationHelper.animate_label_update(self.status_label, "🟢 Dimmer Active", Config.SUCCESS_COLOR)
                self.status_label.setStyleSheet(f"""
                    color: white;
                    font-size: 18px;
                    font-weight: 500;
                    padding: 6px 12px;
                    background-color: {Config.SUCCESS_COLOR};
                    border-radius: 6px;
                """)
                # Show notification
                self.tray_icon.showMessage(
                    'Dimmer Activated',
                    f'Screen dimming enabled at {self.current_dim}%',
                    QSystemTrayIcon.Information,
                    2000
                )
                # Update tray tooltip
                self._update_tray_tooltip()
                
                # Save state
                self._save_state()
            else:
                # Disable dimming on all screens
                enabled_screens = self._get_enabled_screens()
                
                for screen_idx in enabled_screens:
                    if screen_idx == 0:  # Primary screen
                        if not self.blue_light_active:
                            self._close_overlay_for_screen(0)
                        else:
                            # Keep overlay for clean orange tint but remove dimming
                            intensity = self.blue_intensity.value()
                            color = self._calculate_blue_light_color(intensity)
                            if intensity == 0:
                                opacity = 0  # No overlay at 0%
                            else:
                                opacity = int(intensity * 0.12)  # 0% to 12% opacity - very light
                            self._apply_dimming_to_screen(0, opacity, color)
                    elif screen_idx == 1:  # 2nd display
                        if not self.second_display_blue_light:
                            self._close_overlay_for_screen(1)
                        else:
                            # Keep overlay for clean orange tint but remove dimming
                            intensity = self.second_display_blue_intensity
                            color = self._calculate_blue_light_color(intensity)
                            if intensity == 0:
                                opacity = 0  # No overlay at 0%
                            else:
                                opacity = int(intensity * 0.12)  # 0% to 12% opacity - very light
                            self._apply_dimming_to_screen(1, opacity, color)
                
                self.dimmer_active = False
                self.toggle_btn.setText("⚡ Enable Dimmer")
                # Use animation helper for smooth transition
                AnimationHelper.animate_button_state(
                    self.toggle_btn, False, Config.WARNING_COLOR, Config.SUCCESS_COLOR
                )
                # Animate label update
                AnimationHelper.animate_label_update(self.status_label, "⭕ Dimmer Inactive", Config.MUTED_COLOR)
                self.status_label.setStyleSheet(f"""
                    color: {Config.MUTED_COLOR};
                    font-size: 18px;
                    font-weight: 500;
                    padding: 6px 12px;
                    background-color: {Config.BACKGROUND_COLOR};
                    border-radius: 6px;
                """)
                # Show notification
                self.tray_icon.showMessage(
                    'Dimmer Deactivated',
                    'Screen dimming disabled',
                    QSystemTrayIcon.Information,
                    2000
                )
                # Update tray tooltip
                self._update_tray_tooltip()
        finally:
            self._toggle_in_progress = False
    
    def _toggle_window(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def _temporarily_hide_overlay(self):
        """Temporarily hide overlay to allow system gestures"""
        if self.dimmer_active:
            # Hide overlays on all enabled screens
            for overlay in self.overlays.values():
                overlay.temporarily_hide_for_gestures()
            self.tray_icon.showMessage(
                'Gesture Mode',
                'Overlay temporarily hidden for system gestures',
                QSystemTrayIcon.Information,
                2000
            )
    
    def _update_time_remaining(self):
        """Update time remaining display"""
        if not self.schedule_time_set:
            self.time_remaining_label.setText("No schedule set")
            self.time_remaining_label.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.MUTED_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.MUTED_COLOR};
            """)
            # Stop timer when no schedule is set
            self.time_remaining_timer.stop()
            return
        
        current_time = QTime.currentTime()
        start_time = self.start_time
        end_time = self.end_time
        
        # Check if currently in schedule
        in_schedule = False
        if start_time <= end_time:
            in_schedule = start_time <= current_time <= end_time
        else:
            in_schedule = current_time >= start_time or current_time <= end_time
        
        if in_schedule:
            # Currently in schedule - show time until it ends
            if start_time <= end_time:
                # Same day schedule
                end_seconds = end_time.hour() * 3600 + end_time.minute() * 60
                current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                remaining_seconds = end_seconds - current_seconds
            else:
                # Overnight schedule
                if current_time >= start_time:
                    # After start time, before midnight
                    end_seconds = (end_time.hour() + 24) * 3600 + end_time.minute() * 60
                    current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                    remaining_seconds = end_seconds - current_seconds
                else:
                    # Before start time, after midnight
                    end_seconds = end_time.hour() * 3600 + end_time.minute() * 60
                    current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                    remaining_seconds = end_seconds - current_seconds
            
            if remaining_seconds > 0:
                hours = remaining_seconds // 3600
                minutes = (remaining_seconds % 3600) // 60
                if hours > 0:
                    time_text = f"⏰ Schedule ends in {hours}h {minutes}m"
                else:
                    time_text = f"⏰ Schedule ends in {minutes}m"
                
                self.time_remaining_label.setText(time_text)
                self.time_remaining_label.setStyleSheet(f"""
                    background-color: {Config.CARD_COLOR};
                    border: 2px solid {Config.SUCCESS_COLOR};
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    color: {Config.SUCCESS_COLOR};
                """)
            else:
                self.time_remaining_label.setText("⏰ Schedule ending now")
                self.time_remaining_label.setStyleSheet(f"""
                    background-color: {Config.CARD_COLOR};
                    border: 2px solid {Config.WARNING_COLOR};
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    color: {Config.WARNING_COLOR};
                """)
        else:
            # Not in schedule - show time until it starts
            if start_time <= end_time:
                # Same day schedule
                start_seconds = start_time.hour() * 3600 + start_time.minute() * 60
                current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                if current_seconds < start_seconds:
                    remaining_seconds = start_seconds - current_seconds
                else:
                    # Schedule already passed today, show until tomorrow
                    remaining_seconds = (24 * 3600) - current_seconds + start_seconds
            else:
                # Overnight schedule
                if current_time < end_time:
                    # Before end time (still in previous day's schedule)
                    start_seconds = start_time.hour() * 3600 + start_time.minute() * 60
                    current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                    remaining_seconds = start_seconds - current_seconds
                else:
                    # After end time, before start time
                    start_seconds = start_time.hour() * 3600 + start_time.minute() * 60
                    current_seconds = current_time.hour() * 3600 + current_time.minute() * 60
                    remaining_seconds = start_seconds - current_seconds
            
            if remaining_seconds > 0:
                hours = remaining_seconds // 3600
                minutes = (remaining_seconds % 3600) // 60
                if hours > 0:
                    time_text = f"⏳ Schedule starts in {hours}h {minutes}m"
                else:
                    time_text = f"⏳ Schedule starts in {minutes}m"
                
                self.time_remaining_label.setText(time_text)
                self.time_remaining_label.setStyleSheet(f"""
                    background-color: {Config.CARD_COLOR};
                    border: 2px solid {Config.INFO_COLOR};
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    color: {Config.INFO_COLOR};
                """)
            else:
                self.time_remaining_label.setText("⏰ Schedule starting now")
                self.time_remaining_label.setStyleSheet(f"""
                    background-color: {Config.CARD_COLOR};
                    border: 2px solid {Config.SUCCESS_COLOR};
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    color: {Config.SUCCESS_COLOR};
                """)
    
    def _update_blinker_countdown(self):
        """Update blinker countdown display"""
        if not self.blinker_active:
            self.blinker_status.setText("Status: Inactive")
            self.blinker_status.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.MUTED_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.MUTED_COLOR};
            """)
            self.blinker_countdown_timer.stop()
            return
        
        if self.blinker_start_time == 0:
            # Timer just started, set the start time
            self.blinker_start_time = QDateTime.currentMSecsSinceEpoch()
            return
        
        current_time = QDateTime.currentMSecsSinceEpoch()
        elapsed_time = current_time - self.blinker_start_time
        total_interval = self.rain_interval_minutes * 60 * 1000  # Convert to milliseconds
        remaining_time = total_interval - elapsed_time
        
        if remaining_time <= 0:
            # Time for next blink reminder
            self.blinker_status.setText("Status: Active - 👁️ Blink reminder starting now!")
            self.blinker_status.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.SUCCESS_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.SUCCESS_COLOR};
            """)
            # Reset start time for next cycle
            self.blinker_start_time = current_time
        else:
            # Calculate remaining time
            remaining_seconds = int(remaining_time / 1000)
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            if minutes > 0:
                time_text = f"Status: Active - Next reminder in {minutes}m {seconds}s"
            else:
                time_text = f"Status: Active - Next reminder in {seconds}s"
            
            self.blinker_status.setText(time_text)
            self.blinker_status.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.INFO_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.INFO_COLOR};
            """)
    
    def _toggle_schedule_control(self):
        """Toggle schedule enable/disable - merged functionality"""
        # Prevent multiple rapid toggles
        if self._schedule_toggle_in_progress:
            return
        self._schedule_toggle_in_progress = True
        
        try:
            # Check if schedule time has been set
            if not self.schedule_time_set:
                self.tray_icon.showMessage(
                    'No Schedule Time Set',
                    'Please choose a preset time first (Night, Evening, Late Night, or Custom)',
                    QSystemTrayIcon.Warning,
                    3000
                )
                return
            
            if not self.schedule_enabled:
                # Enable schedule
                self.schedule_enabled = True
                self.schedule_control_btn.setText("⏹️ Disable Schedule")
                self.schedule_control_btn.setStyleSheet(StyleManager.get_button_style(Config.WARNING_COLOR))
                self.schedule_status.setText("Status: Enabled")
                self.schedule_status.setStyleSheet(f"""
                    color: {Config.SUCCESS_COLOR};
                    font-size: 18px;
                    padding: 10px;
                    text-align: center;
                    background-color: {Config.CARD_COLOR};
                    border: 1px solid {Config.SUCCESS_COLOR};
                    border-radius: 6px;
                """)
                
                self.tray_icon.showMessage(
                    'Schedule Enabled',
                    'Automatic dimming is now active',
                    QSystemTrayIcon.Information,
                    2000
                )
                
                # Save state
                self._save_state()
            else:
                # Disable schedule and stop dimmer if active
                self.schedule_enabled = False
                if self.dimmer_active:
                    self._toggle_dimmer()
                
                self.schedule_control_btn.setText("🚀 Enable Schedule")
                self.schedule_control_btn.setStyleSheet(StyleManager.get_button_style(Config.SUCCESS_COLOR))
                self.schedule_status.setText("Status: Disabled")
                self.schedule_status.setStyleSheet(f"""
                    color: {Config.MUTED_COLOR};
                    font-size: 18px;
                    padding: 10px;
                    text-align: center;
                    background-color: {Config.CARD_COLOR};
                    border: 1px solid {Config.BORDER_COLOR};
                    border-radius: 6px;
                """)
        
                self.tray_icon.showMessage(
                    'Schedule Disabled',
                    'Automatic dimming stopped',
                    QSystemTrayIcon.Information,
                    2000
                )
        finally:
            self._schedule_toggle_in_progress = False
    
    def _apply_preset(self, preset_type: str):
        """Apply a schedule preset"""
        if preset_type == "all_day":
            self.start_time = QTime(6, 0)   # 6 AM
            self.end_time = QTime(18, 0)    # 6 PM
            self.schedule_dim_value = 75
            preset_name = "All Day"
        elif preset_type == "all_night":
            self.start_time = QTime(18, 0)  # 6 PM
            self.end_time = QTime(6, 0)     # 6 AM
            self.schedule_dim_value = 90
            preset_name = "All Night"
        elif preset_type == "night":
            self.start_time = QTime(20, 0)  # 8 PM
            self.end_time = QTime(7, 0)     # 7 AM
            self.schedule_dim_value = 85
            preset_name = "Night Mode"
        elif preset_type == "evening":
            self.start_time = QTime(18, 0)  # 6 PM
            self.end_time = QTime(23, 0)    # 11 PM
            self.schedule_dim_value = 75
            preset_name = "Evening"
        elif preset_type == "late_night":
            self.start_time = QTime(22, 0)  # 10 PM
            self.end_time = QTime(6, 0)     # 6 AM
            self.schedule_dim_value = 90
            preset_name = "Late Night"
        elif preset_type == "custom":
            self._show_custom_time_dialog()
            return # Exit after showing custom dialog
        
        self.schedule_time_set = True
        
        # Update display
        start_str = self.start_time.toString("h:mm AP")
        end_str = self.end_time.toString("h:mm AP")
        self.schedule_display.setText(f"{preset_name}: {start_str} - {end_str} ({self.schedule_dim_value}%)")
        self.schedule_display.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.PRIMARY_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.PRIMARY_COLOR};
        """)
        
        # Enable buttons now that time is set
        self.schedule_control_btn.setEnabled(True)
        
        # Start timers if they're not running
        if not self.schedule_timer.isActive():
            self.schedule_timer.start(30000)  # Optimized: check every 30 seconds
        if not self.time_remaining_timer.isActive():
            self.time_remaining_timer.start(10000)  # Optimized: update every 10 seconds
        
        # Check if this preset would be active now
        current_time = QTime.currentTime()
        in_schedule = False
        if self.start_time <= self.end_time:
            in_schedule = self.start_time <= current_time <= self.end_time
        else:
            in_schedule = current_time >= self.start_time or current_time <= self.end_time
        
        # Update status
        if in_schedule:
            self.schedule_status.setText("Status: Would be active now")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.SUCCESS_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.SUCCESS_COLOR};
                border-radius: 6px;
            """)
        else:
            self.schedule_status.setText("Status: Set for later")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.INFO_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.INFO_COLOR};
                border-radius: 6px;
            """)
        
        # Show notification
        status_text = "would be active now" if in_schedule else "set for later"
        self.tray_icon.showMessage(
            f'{preset_name} Preset Set',
            f'{start_str} - {end_str} at {self.schedule_dim_value}% ({status_text})',
            QSystemTrayIcon.Information,
            2000
        )
    
    def _show_custom_time_dialog(self):
        """Show dialog for custom time selection"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Custom Schedule Time")
        dialog.setModal(True)
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Config.CARD_COLOR};
                color: {Config.TEXT_COLOR};
            }}
            QLabel {{
                font-size: 18px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {Config.PRIMARY_COLOR};
                opacity: 0.9;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⚙️ Set Custom Schedule Time")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #58a6ff; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Start time
        start_layout = QHBoxLayout()
        start_label = QLabel("Start Time:")
        start_label.setMinimumWidth(100)
        start_layout.addWidget(start_label)
        
        self.custom_start_time = QTimeEdit()
        self.custom_start_time.setTime(QTime(22, 0))  # Default 10 PM
        self.custom_start_time.setDisplayFormat("h:mm AP")
        self.custom_start_time.setMinimumHeight(35)
        self.custom_start_time.setToolTip("Select the start time when automatic dimming should begin")
        start_layout.addWidget(self.custom_start_time)
        layout.addLayout(start_layout)
        
        # End time
        end_layout = QHBoxLayout()
        end_label = QLabel("End Time:")
        end_label.setMinimumWidth(100)
        end_layout.addWidget(end_label)
        
        self.custom_end_time = QTimeEdit()
        self.custom_end_time.setTime(QTime(6, 0))  # Default 6 AM
        self.custom_end_time.setDisplayFormat("h:mm AP")
        self.custom_end_time.setMinimumHeight(35)
        self.custom_end_time.setToolTip("Select the end time when automatic dimming should stop")
        end_layout.addWidget(self.custom_end_time)
        layout.addLayout(end_layout)
        
        # Dim level
        dim_layout = QHBoxLayout()
        dim_label = QLabel("Dim Level:")
        dim_label.setMinimumWidth(100)
        dim_layout.addWidget(dim_label)
        
        self.custom_dim_spinbox = QSpinBox()
        self.custom_dim_spinbox.setRange(10, 95)
        self.custom_dim_spinbox.setValue(85)
        self.custom_dim_spinbox.setSuffix("%")
        self.custom_dim_spinbox.setMinimumHeight(35)
        dim_layout.addWidget(self.custom_dim_spinbox)
        layout.addLayout(dim_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.MUTED_COLOR};
                color: white;
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply Custom Schedule")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.SUCCESS_COLOR};
                color: white;
            }}
        """)
        apply_btn.clicked.connect(lambda: self._apply_custom_schedule(dialog))
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def _apply_custom_schedule(self, dialog):
        """Apply custom schedule settings"""
        start_time = self.custom_start_time.time()
        end_time = self.custom_end_time.time()
        dim_value = self.custom_dim_spinbox.value()
        
        # Validate times
        if start_time == end_time:
            QMessageBox.warning(dialog, "Invalid Time", "Start time and end time cannot be the same!")
            return
        
        # Close dialog immediately after validation passes
        dialog.accept()
        
        # Set the custom schedule
        self.start_time = start_time
        self.end_time = end_time
        self.schedule_dim_value = dim_value
        self.schedule_time_set = True
        
        # Update display
        start_str = start_time.toString("h:mm AP")
        end_str = end_time.toString("h:mm AP")
        self.schedule_display.setText(f"Custom Schedule: {start_str} - {end_str} ({dim_value}%)")
        self.schedule_display.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.PRIMARY_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.PRIMARY_COLOR};
        """)
        
        # Enable buttons now that time is set
        self.schedule_control_btn.setEnabled(True)
        
        # Start timers if they're not running
        if not self.schedule_timer.isActive():
            self.schedule_timer.start(30000)  # Optimized: check every 30 seconds
        if not self.time_remaining_timer.isActive():
            self.time_remaining_timer.start(10000)  # Optimized: update every 10 seconds
        
        # Check if this custom schedule would be active now
        current_time = QTime.currentTime()
        in_schedule = False
        if start_time <= end_time:
            in_schedule = start_time <= current_time <= end_time
        else:
            in_schedule = current_time >= start_time or current_time <= end_time
        
        # Update status
        if in_schedule:
            self.schedule_status.setText("Status: Would be active now")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.SUCCESS_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.SUCCESS_COLOR};
                border-radius: 6px;
            """)
        else:
            self.schedule_status.setText("Status: Set for later")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.INFO_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.INFO_COLOR};
                border-radius: 6px;
            """)
        
        # Show notification
        status_text = "would be active now" if in_schedule else "set for later"
        self.tray_icon.showMessage(
            'Custom Schedule Set',
            f'{start_str} - {end_str} at {dim_value}% ({status_text})',
            QSystemTrayIcon.Information,
            2000
        )
    
    def _show_timer_dialog(self):
        """Show timer dialog for quick timer feature"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⏱️ Quick Timer")
        dialog.setModal(True)
        dialog.setFixedSize(350, 200)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Config.BACKGROUND_COLOR};
                color: {Config.TEXT_COLOR};
            }}
            QLabel {{
                color: {Config.TEXT_COLOR};
                font-size: 16px;
            }}
            QSpinBox {{
                background-color: {Config.CARD_COLOR};
                color: {Config.TEXT_COLOR};
                border: 1px solid {Config.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
            }}
            QPushButton {{
                background-color: {Config.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⏱️ Set Timer Duration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #58a6ff;")
        layout.addWidget(title)
        
        # Minutes input
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        minutes_label = QLabel("Minutes:")
        input_layout.addWidget(minutes_label)
        
        self.timer_minutes_spinbox = QSpinBox()
        self.timer_minutes_spinbox.setRange(1, 120)  # 1 minute to 2 hours
        self.timer_minutes_spinbox.setValue(10)  # Default 10 minutes
        self.timer_minutes_spinbox.setSuffix(" min")
        input_layout.addWidget(self.timer_minutes_spinbox)
        
        input_layout.addStretch()
        layout.addLayout(input_layout)
        
        # Info text
        info = QLabel("Dimmer will start immediately and turn off automatically after the timer ends.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet(f"color: {Config.MUTED_COLOR}; font-size: 14px;")
        layout.addWidget(info)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.WARNING_COLOR};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #f85149;
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        start_btn = QPushButton("🚀 Start Timer")
        start_btn.clicked.connect(lambda: self._start_timer(dialog))
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def _start_timer(self, dialog):
        """Start the timer feature"""
        minutes = self.timer_minutes_spinbox.value()
        
        # Close dialog
        dialog.accept()
        
        # Set timer variables
        self.timer_active = True
        self.timer_minutes = minutes
        
        # Calculate end time
        from datetime import datetime, timedelta
        self.timer_end_time = datetime.now() + timedelta(minutes=minutes)
        
        # Start dimmer immediately at current slider value
        if not self.dimmer_active:
            self._toggle_dimmer()
        
        # Start timer to check when to stop
        self.timer_timer.start(10000)  # Optimized: check every 10 seconds
        
        # Show notification
        self.tray_icon.showMessage(
            'Timer Started',
            f'Dimmer will turn off in {minutes} minutes',
            QSystemTrayIcon.Information,
            3000
        )
        
        # Update schedule display to show timer
        self.schedule_display.setText(f"⏱️ Timer: {minutes} minutes (Auto-stop)")
        self.schedule_display.setStyleSheet(f"""
            background-color: {Config.CARD_COLOR};
            border: 2px solid {Config.INFO_COLOR};
            border-radius: 8px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: {Config.INFO_COLOR};
        """)
        
        # Update status
        self.schedule_status.setText("Status: Timer Running")
        self.schedule_status.setStyleSheet(f"""
            color: {Config.INFO_COLOR};
            font-size: 18px;
            padding: 10px;
            text-align: center;
            background-color: {Config.CARD_COLOR};
            border: 1px solid {Config.INFO_COLOR};
            border-radius: 6px;
        """)
    
    def _check_timer(self):
        """Check if timer should end"""
        if not self.timer_active or not self.timer_end_time:
            self.timer_timer.stop()
            return
        
        # Check if timer has ended
        from datetime import datetime
        if datetime.now() >= self.timer_end_time:
            # Timer ended - stop dimmer
            if self.dimmer_active:
                self._toggle_dimmer()
            
            # Reset timer state
            self.timer_active = False
            self.timer_minutes = 0
            self.timer_end_time = None
            self.timer_timer.stop()
            
            # Show notification
            self.tray_icon.showMessage(
                'Timer Ended',
                'Dimmer turned off automatically',
                QSystemTrayIcon.Information,
                3000
            )
            
            # Reset display
            self.schedule_display.setText("No schedule set - Choose a preset first")
            self.schedule_display.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.MUTED_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.MUTED_COLOR};
            """)
            
            # Reset status
            self.schedule_status.setText("Status: Disabled")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.MUTED_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.BORDER_COLOR};
                border-radius: 6px;
            """)
    
    
    def _check_schedule(self):
        """Check if current time is within schedule"""
        if not self.schedule_enabled or not self.schedule_time_set:
            # Stop timers if no schedule is set to save resources
            if not self.schedule_time_set:
                self.schedule_timer.stop()
                self.time_remaining_timer.stop()
            return
        
        current_time = QTime.currentTime()
        start_time = self.start_time
        end_time = self.end_time
        
        # Check if current time is within schedule
        in_schedule = False
        if start_time <= end_time:
            # Same day schedule (e.g., 9:11 AM to 9:13 AM)
            in_schedule = start_time <= current_time <= end_time
        else:
            # Overnight schedule (e.g., 8 PM to 7 AM)
            in_schedule = current_time >= start_time or current_time <= end_time
        
        # Auto toggle dimmer based on schedule - FORCE enable when schedule time comes
        if in_schedule:
            # Schedule time is active - force enable dimmer regardless of current state
            if not self.dimmer_active:
                # Set dimmer to scheduled level and force enable
                self.dim_slider.setValue(self.schedule_dim_value)
                self._toggle_dimmer()
            
            # Show notification that schedule activated
            self.tray_icon.showMessage(
                    'Schedule Auto-Started',
                    f'Dimmer force-enabled at {self.schedule_dim_value}%',
                QSystemTrayIcon.Information,
                3000
            )
            # Update status when schedule is active
            self.schedule_status.setText("Status: Auto-Running")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.SUCCESS_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.SUCCESS_COLOR};
                border-radius: 6px;
            """)
        else:
            # Schedule time is not active
            if self.dimmer_active and not self.blue_light_active:
            # Only disable if blue light is not active
                self._toggle_dimmer()
            
            # Show notification that schedule ended
            self.tray_icon.showMessage(
                'Schedule Ended',
                'Dimmer disabled',
                QSystemTrayIcon.Information,
                3000
            )
            # Update status when schedule is not active
            self.schedule_status.setText("Status: Waiting")
            self.schedule_status.setStyleSheet(f"""
                color: {Config.INFO_COLOR};
                font-size: 18px;
                padding: 10px;
                text-align: center;
                background-color: {Config.CARD_COLOR};
                border: 1px solid {Config.INFO_COLOR};
                border-radius: 6px;
            """)
    
    # ============= Blinker Methods =============
    
    def _toggle_blinker(self):
        """Toggle blinker on/off"""
        if self.blinker_active:
            # Disable blinker
            self.blinker_active = False
            self.blinker_timer.stop()
            self.blinker_countdown_timer.stop()
            self.blinker_start_time = 0
            
            self.blinker_control_btn.setText("🚀 Enable Blinker")
            self.blinker_control_btn.setStyleSheet(StyleManager.get_button_style(Config.SUCCESS_COLOR))
            self.blinker_status.setText("Status: Inactive")
            self.blinker_status.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.MUTED_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.MUTED_COLOR};
            """)
            
            self.tray_icon.showMessage(
                'Blinker Disabled',
                'Rain effects stopped',
                QSystemTrayIcon.Information,
                2000
            )
            
            # Save state
            self._save_state()
        else:
            # Enable blinker
            self.blinker_active = True
            
            self.blinker_control_btn.setText("⏹️ Disable Blinker")
            self.blinker_control_btn.setStyleSheet(StyleManager.get_button_style(Config.WARNING_COLOR))
            self.blinker_status.setText("Status: Active")
            self.blinker_status.setStyleSheet(f"""
                background-color: {Config.CARD_COLOR};
                border: 2px solid {Config.SUCCESS_COLOR};
                border-radius: 8px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                color: {Config.SUCCESS_COLOR};
            """)
            
            # Start rain timer
            self.blinker_timer.start(self.rain_interval_minutes * 60 * 1000)  # Convert minutes to milliseconds
            
            # Start countdown timer and reset start time
            self.blinker_start_time = 0  # Will be set on first countdown update
            self.blinker_countdown_timer.start(1000)  # Keep at 1 second for smooth countdown display
            
            self.tray_icon.showMessage(
                'Blinker Enabled',
                f'Rain effects every {self.rain_interval_minutes} minutes',
                QSystemTrayIcon.Information,
                2000
            )
            
            # Save state
            self._save_state()
    
    def _blinker_rain_effect(self):
        """Create rain effect with emojis and text"""
        screens = QApplication.screens()
        
        # Create rain overlays for all enabled screens
        enabled_screens = self._get_enabled_screens()
        for screen_idx in enabled_screens:
            if screen_idx < len(screens):
                if screen_idx not in self.rain_overlays:
                    self.rain_overlays[screen_idx] = RainOverlay(screens[screen_idx])
                    self.rain_overlays[screen_idx].rain_duration = self.rain_duration_seconds * 1000
                self.rain_overlays[screen_idx].start_rain(self.emoji_blink_enabled, self.text_blink_enabled)
        
        # Show notification
        if self.emoji_blink_enabled and self.text_blink_enabled:
            title = "Blink Reminder: Eyes & Text"
        elif self.emoji_blink_enabled:
            title = "Blink Reminder: Eyes"
        else:
            title = "Blink Reminder: Text"
        
        self.tray_icon.showMessage(
            title,
            "Blink reminder started on screen!",
            QSystemTrayIcon.Information,
            2000
        )
        
        
        # Restart timer for next rain (only if blinker is active)
        if self.blinker_active:
            self.blinker_timer.stop()  # Stop current timer
            self.blinker_timer.start(self.rain_interval_minutes * 60 * 1000)  # Start new timer
            # Reset countdown timer for next cycle
            self.blinker_start_time = 0
    
    
    def closeEvent(self, event):
        """Handle close event - hide to tray instead of quitting"""
        # Hide window to system tray instead of closing
        self.hide()
        self.tray_icon.showMessage(
            'Screen Dimmer',
            'Application minimized to system tray',
            QSystemTrayIcon.Information,
            2000
        )
        event.ignore()  # Don't actually close the window
    
    def quit_app(self):
        """Clean shutdown"""
        # Stop all timers to prevent memory leaks
        self.schedule_timer.stop()
        self.time_remaining_timer.stop()
        self.timer_timer.stop()
        self.blinker_timer.stop()
        self.blinker_countdown_timer.stop()
        
        # Clean up global hotkeys
        if GLOBAL_HOTKEYS_AVAILABLE and self.hotkeys_active:
            try:
                keyboard.unhook_all()
                print("Global hotkeys cleaned up")
            except:
                pass
        
        # Clean up overlays (memory optimization)
        for overlay in list(self.overlays.values()):  # Use list() to avoid modification during iteration
            if overlay:
                overlay.close()
                overlay.deleteLater()  # Ensure proper cleanup
        self.overlays.clear()
        
        for rain_overlay in list(self.rain_overlays.values()):  # Use list() to avoid modification during iteration
            if rain_overlay:
                rain_overlay.close()
                rain_overlay.deleteLater()  # Ensure proper cleanup
        self.rain_overlays.clear()
        
        # Stop and cleanup timers (memory optimization)
        for timer_name in ['schedule_timer', 'time_remaining_timer', 'blinker_countdown_timer', 
                          'timer_timer', 'blinker_timer']:
            timer = getattr(self, timer_name, None)
            if timer:
                timer.stop()
                timer.deleteLater()
        
        # Save data
        self.profile_manager.save()
        
        # Clear caches (memory optimization)
        StyleManager._app_stylesheet = None
        StyleManager._button_styles.clear()
        IconCreator._tray_icon_cache = None
        IconCreator._app_icon_cache = None
        
        QApplication.quit()

# ============= Main Entry Point =============
def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Hide console on Windows
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, 0)
    
    # Check system tray
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Error", "System tray not available")
        sys.exit(1)
    
    # Set application icon
    app.setWindowIcon(IconCreator.create_app_icon())
    
    # Check for global hotkey support
    if not GLOBAL_HOTKEYS_AVAILABLE:
        print("For global hotkeys (Alt+D from anywhere), install: pip install keyboard")
    
    # Launch
    window = DimmerControl()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()