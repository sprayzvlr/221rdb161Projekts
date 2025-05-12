#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import socket
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QSlider, QTextEdit,
                             QTabWidget, QFormLayout, QLineEdit, QComboBox,
                             QStatusBar, QProgressBar, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer


class DataUpdateThread(QObject, threading.Thread):
    """Thread for data updates from the server"""
    data_updated = pyqtSignal(dict)
    connection_error = pyqtSignal(str)

    def __init__(self, host, port, protocol):
        QObject.__init__(self)
        threading.Thread.__init__(self, daemon=True)
        self.host = host
        self.port = port
        self.protocol = protocol
        self.running = False
        self.socket = None

    def connect(self):
        """Connect to the server"""
        try:
            if self.protocol == "TCP":
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(5)  # 5 second timeout
                self.running = True
                self.start()  # Start the thread
                return True
            else:
                self.connection_error.emit("Only TCP protocol is supported")
                return False
        except Exception as e:
            self.connection_error.emit(f"Connection error: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        # Wait for thread to complete
        if self.is_alive():
            self.join(1.0)  # Wait up to 1 second

    def send_command(self, command, value=None):
        """Send a command to the server"""
        if not self.socket:
            self.connection_error.emit("Not connected to server")
            return False

        try:
            # Prepare command
            cmd = {"command": command}
            if value is not None:
                cmd["value"] = value

            # Send command
            data = json.dumps(cmd).encode('utf-8')
            if self.protocol == "TCP":
                self.socket.sendall(data + b'\n')
                # Wait for response
                response = self.socket.recv(1024).decode('utf-8').strip()
                try:
                    return json.loads(response)
                except:
                    self.connection_error.emit(f"Invalid response: {response}")
                    return None
            else:
                self.connection_error.emit("Protocol not supported")
                return None
        except Exception as e:
            self.connection_error.emit(f"Command error: {str(e)}")
            self.running = False
            return None

    def run(self):
        """Thread main loop - poll for data updates"""
        while self.running:
            try:
                if self.protocol == "TCP":
                    # Send a status request
                    response = self.send_command("status")
                    if response and "status" in response:
                        # Emit the data update signal
                        self.data_updated.emit(response)
                    else:
                        time.sleep(1)  # Wait if no valid response
                else:
                    # Other protocols would be implemented here
                    time.sleep(1)
            except Exception as e:
                if self.running:  # Only emit if still running
                    self.connection_error.emit(f"Data update error: {str(e)}")
                    self.running = False
            time.sleep(0.5)  # Poll every 500ms


class ProcessControlHMI(QMainWindow):
    """Main HMI window for process control"""

    def __init__(self):
        super().__init__()

        # Initialize variables used by other methods
        self.host = "localhost"
        self.port = 5000
        self.protocol = "TCP"
        self.connected = False
        self.data_thread = None

        # Default values for process variables
        self.process_running = False
        self.temperature = 0
        self.pressure = 0
        self.level = 0

        # UI elements - will be initialized in methods
        self.central_widget = None
        self.main_layout = None
        self.tabs = None
        self.status_bar = None
        self.connect_button = None
        self.start_button = None
        self.stop_button = None
        self.temp_slider = None
        self.pressure_slider = None
        self.temp_value = None
        self.pressure_value = None
        self.process_status = None
        self.level_indicator = None
        self.log_text = None
        self.host_input = None
        self.port_input = None
        self.protocol_combo = None
        self.apply_button = None

        # Initialize UI
        self.setWindowTitle("Process Control HMI")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Create main window elements
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

        # Create tabs
        self.create_control_tab()
        self.create_monitoring_tab()
        self.create_settings_tab()

        # Create data update thread (but don't start it yet)
        self.data_thread = DataUpdateThread(self.host, self.port, self.protocol)
        self.data_thread.data_updated.connect(self.update_ui)
        self.data_thread.connection_error.connect(self.show_error)

    def create_control_tab(self):
        """Create the Control tab with process controls"""
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)

        # Connection section
        conn_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout(conn_group)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_button)

        layout.addWidget(conn_group)

        # Process control section
        process_group = QGroupBox("Process Control")
        process_layout = QVBoxLayout(process_group)

        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Process")
        self.start_button.clicked.connect(self.start_process)
        self.start_button.setEnabled(False)
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Process")
        self.stop_button.clicked.connect(self.stop_process)
        self.stop_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_button)

        process_layout.addLayout(buttons_layout)

        # Temperature control
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(0)
        self.temp_slider.setMaximum(100)
        self.temp_slider.setValue(0)
        self.temp_slider.valueChanged.connect(self.set_temperature)
        self.temp_slider.setEnabled(False)
        temp_layout.addWidget(self.temp_slider)

        self.temp_value = QLabel("0 °C")
        temp_layout.addWidget(self.temp_value)

        process_layout.addLayout(temp_layout)

        # Pressure control
        pressure_layout = QHBoxLayout()
        pressure_layout.addWidget(QLabel("Pressure:"))

        self.pressure_slider = QSlider(Qt.Horizontal)
        self.pressure_slider.setMinimum(0)
        self.pressure_slider.setMaximum(100)
        self.pressure_slider.setValue(0)
        self.pressure_slider.valueChanged.connect(self.set_pressure)
        self.pressure_slider.setEnabled(False)
        pressure_layout.addWidget(self.pressure_slider)

        self.pressure_value = QLabel("0 bar")
        pressure_layout.addWidget(self.pressure_value)

        process_layout.addLayout(pressure_layout)

        # Process status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Process Status:"))

        self.process_status = QLabel("Stopped")
        self.process_status.setStyleSheet("color: red;")
        status_layout.addWidget(self.process_status)

        process_layout.addLayout(status_layout)

        # Level indicator
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Tank Level:"))

        self.level_indicator = QProgressBar()
        self.level_indicator.setMinimum(0)
        self.level_indicator.setMaximum(100)
        self.level_indicator.setValue(0)
        level_layout.addWidget(self.level_indicator)

        process_layout.addLayout(level_layout)

        layout.addWidget(process_group)

        # Log section
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group)

        # Add the tab
        self.tabs.addTab(control_tab, "Control")

    def create_monitoring_tab(self):
        """Create the Monitoring tab with graphs and data visualization"""
        monitoring_tab = QWidget()
        layout = QVBoxLayout(monitoring_tab)

        # This is a placeholder - in a real implementation this would
        # contain graphs using matplotlib or similar
        layout.addWidget(QLabel("Monitoring tab - graphs would be displayed here"))

        # Temperature graph placeholder
        temp_group = QGroupBox("Temperature History")
        temp_layout = QVBoxLayout(temp_group)
        temp_layout.addWidget(QLabel("Temperature graph placeholder"))
        layout.addWidget(temp_group)

        # Pressure graph placeholder
        pressure_group = QGroupBox("Pressure History")
        pressure_layout = QVBoxLayout(pressure_group)
        pressure_layout.addWidget(QLabel("Pressure graph placeholder"))
        layout.addWidget(pressure_group)

        # Level graph placeholder
        level_group = QGroupBox("Level History")
        level_layout = QVBoxLayout(level_group)
        level_layout.addWidget(QLabel("Level graph placeholder"))
        layout.addWidget(level_group)

        # Add the tab
        self.tabs.addTab(monitoring_tab, "Monitoring")

    def create_settings_tab(self):
        """Create the Settings tab for connection settings"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)

        form_layout = QFormLayout()

        self.host_input = QLineEdit(self.host)
        form_layout.addRow("Host:", self.host_input)

        self.port_input = QLineEdit(str(self.port))
        form_layout.addRow("Port:", self.port_input)

        self.protocol_combo = QComboBox()
        self.protocol_combo.addItem("TCP")
        self.protocol_combo.addItem("UDP")
        self.protocol_combo.setCurrentText(self.protocol)
        form_layout.addRow("Protocol:", self.protocol_combo)

        layout.addLayout(form_layout)

        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        # Add the tab
        self.tabs.addTab(settings_tab, "Settings")

    def toggle_connection(self):
        """Connect or disconnect from the server"""
        if not self.connected:
            # Connect to the server
            if self.data_thread and self.data_thread.running:
                self.data_thread.disconnect()

            # Create a new thread with current settings
            self.data_thread = DataUpdateThread(self.host, self.port, self.protocol)
            self.data_thread.data_updated.connect(self.update_ui)
            self.data_thread.connection_error.connect(self.show_error)

            # Try to connect
            if self.data_thread.connect():
                self.connected = True
                self.connect_button.setText("Disconnect")
                self.status_bar.showMessage(f"Connected to {self.host}:{self.port}")
                self.log_text.append(f"Connected to server at {self.host}:{self.port}")

                # Enable process controls
                self.start_button.setEnabled(True)

                # Disable settings
                self.host_input.setEnabled(False)
                self.port_input.setEnabled(False)
                self.protocol_combo.setEnabled(False)
                self.apply_button.setEnabled(False)
            else:
                self.log_text.append("Failed to connect to server")
        else:
            # Disconnect from the server
            if self.data_thread:
                self.data_thread.disconnect()

            self.connected = False
            self.connect_button.setText("Connect")
            self.status_bar.showMessage("Disconnected")
            self.log_text.append("Disconnected from server")

            # Disable process controls
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.temp_slider.setEnabled(False)
            self.pressure_slider.setEnabled(False)

            # Reset status
            self.process_status.setText("Stopped")
            self.process_status.setStyleSheet("color: red;")
            self.process_running = False

            # Enable settings
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.protocol_combo.setEnabled(True)
            self.apply_button.setEnabled(True)

    def apply_settings(self):
        """Apply the connection settings"""
        try:
            # Validate and apply settings
            new_host = self.host_input.text().strip()
            new_port = int(self.port_input.text())
            new_protocol = self.protocol_combo.currentText()

            if new_port < 1 or new_port > 65535:
                raise ValueError("Port must be between 1 and 65535")

            # Apply settings
            self.host = new_host
            self.port = new_port
            self.protocol = new_protocol

            self.log_text.append(f"Settings updated: {self.host}:{self.port} ({self.protocol})")
        except ValueError as e:
            self.show_error(f"Invalid port number: {str(e)}")
        except Exception as e:
            self.show_error(f"Error applying settings: {str(e)}")

    def start_process(self):
        """Start the simulated process"""
        if not self.connected:
            self.show_error("Not connected to server")
            return

        response = self.data_thread.send_command("start")
        if response and response.get("status") == "ok":
            self.process_running = True
            self.process_status.setText("Running")
            self.process_status.setStyleSheet("color: green;")
            self.log_text.append("Process started")

            # Enable controls
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.temp_slider.setEnabled(True)
            self.pressure_slider.setEnabled(True)
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            self.log_text.append(f"Failed to start process: {error_msg}")

    def stop_process(self):
        """Stop the simulated process"""
        if not self.connected:
            self.show_error("Not connected to server")
            return

        response = self.data_thread.send_command("stop")
        if response and response.get("status") == "ok":
            self.process_running = False
            self.process_status.setText("Stopped")
            self.process_status.setStyleSheet("color: red;")
            self.log_text.append("Process stopped")

            # Disable controls
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.temp_slider.setEnabled(False)
            self.pressure_slider.setEnabled(False)
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            self.log_text.append(f"Failed to stop process: {error_msg}")

    def set_temperature(self, value):
        """Set the temperature setpoint"""
        if not self.connected or not self.process_running:
            return

        # Send temperature command to server
        response = self.data_thread.send_command("set_temperature", value)
        if response and response.get("status") == "ok":
            self.temperature = value
            self.temp_value.setText(f"{value} °C")
            self.log_text.append(f"Temperature set to {value} °C")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            self.log_text.append(f"Failed to set temperature: {error_msg}")

            # Reset slider to current value from server
            if response and "temperature" in response:
                current_temp = response["temperature"]
                self.temp_slider.setValue(current_temp)
                self.temp_value.setText(f"{current_temp} °C")

    def set_pressure(self, value):
        """Set the pressure setpoint"""
        if not self.connected or not self.process_running:
            return

        # Send pressure command to server
        response = self.data_thread.send_command("set_pressure", value)
        if response and response.get("status") == "ok":
            self.pressure = value
            self.pressure_value.setText(f"{value} bar")
            self.log_text.append(f"Pressure set to {value} bar")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            self.log_text.append(f"Failed to set pressure: {error_msg}")

            # Reset slider to current value from server
            if response and "pressure" in response:
                current_pressure = response["pressure"]
                self.pressure_slider.setValue(current_pressure)
                self.pressure_value.setText(f"{current_pressure} bar")

    def update_ui(self, data):
        """Update the UI with data from the server"""
        if "process_running" in data:
            self.process_running = data["process_running"]
            if self.process_running:
                self.process_status.setText("Running")
                self.process_status.setStyleSheet("color: green;")
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.temp_slider.setEnabled(True)
                self.pressure_slider.setEnabled(True)
            else:
                self.process_status.setText("Stopped")
                self.process_status.setStyleSheet("color: red;")
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.temp_slider.setEnabled(False)
                self.pressure_slider.setEnabled(False)

        if "temperature" in data:
            temp = data["temperature"]
            self.temperature = temp
            self.temp_value.setText(f"{temp} °C")
            # Only update slider if not being moved by user
            if not self.temp_slider.isSliderDown():
                self.temp_slider.setValue(int(temp))

        if "pressure" in data:
            pressure = data["pressure"]
            self.pressure = pressure
            self.pressure_value.setText(f"{pressure} bar")
            # Only update slider if not being moved by user
            if not self.pressure_slider.isSliderDown():
                self.pressure_slider.setValue(int(pressure))

        if "level" in data:
            level = data["level"]
            self.level = level
            self.level_indicator.setValue(int(level))

    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
        self.log_text.append(f"ERROR: {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessControlHMI()
    window.show()
    sys.exit(app.exec_())
