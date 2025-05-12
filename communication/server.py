#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import json
import time
import random
import signal
import sys
import logging

# Konfigurējam logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProcessSimulator:
    """Klase procesa simulācijai"""

    def __init__(self):
        # Procesa mainīgie
        self.process_running = False
        self.temperature = 25.0  # Temperatūra (°C)
        self.setpoint_temperature = 25.0
        self.pressure = 0.0  # Spiediens (bar)
        self.setpoint_pressure = 0.0
        self.level = 0.0  # Līmenis tvertnē (%)

        # Simulācijas parametri
        self.simulation_thread = None
        self.running = False

        # Vēstures dati
        self.max_history_length = 100
        self.temperature_history = []
        self.pressure_history = []
        self.level_history = []

        # Laiki
        self.last_update = time.time()

    def start(self):
        """Sākt procesa simulāciju"""
        if not self.process_running:
            self.process_running = True
            self.running = True
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()
            logger.info("Process started")
            return True
        return False

    def stop(self):
        """Apturēt procesa simulāciju"""
        if self.process_running:
            self.process_running = False
            logger.info("Process stopped")
            return True
        return False

    def set_temperature(self, value):
        """Iestatīt temperatūras uzstādījumu"""
        try:
            value = float(value)
            if 0 <= value <= 100:
                self.setpoint_temperature = value
                logger.info(f"Temperature setpoint set to {value}°C")
                return True
            else:
                logger.warning(f"Temperature setpoint out of range: {value}")
                return False
        except (ValueError, TypeError):
            logger.error(f"Invalid temperature value: {value}")
            return False

    def set_pressure(self, value):
        """Iestatīt spiediena uzstādījumu"""
        try:
            value = float(value)
            if 0 <= value <= 100:
                self.setpoint_pressure = value
                logger.info(f"Pressure setpoint set to {value} bar")
                return True
            else:
                logger.warning(f"Pressure setpoint out of range: {value}")
                return False
        except (ValueError, TypeError):
            logger.error(f"Invalid pressure value: {value}")
            return False

    def run_simulation(self):
        """
        Galvenā simulācijas loģika, kas darbojas atsevišķā pavedienā.
        Simulē temperatūras un spiediena izmaiņas, balstoties uz iestatītajām vērtībām.
        """
        logger.info("Simulācija sākta")

        import time
        import random
        import numpy as np
        from datetime import datetime

        # Simulācijas parametri
        temp_noise_factor = 0.5  # Temperatūras trokšņa faktors
        pressure_noise_factor = 1.0  # Spiediena trokšņa faktors

        # Simulācijas konstantes
        temp_inertia = 0.98  # Temperatūras inerce (mazāka vērtība = ātrākas izmaiņas)
        pressure_inertia = 0.95  # Spiediena inerce

        # Iestatījumi kontrolei
        temp_control_factor = 0.1  # Cik stipri kontroles darbības ietekmē temperatūru
        pressure_control_factor = 0.2  # Cik stipri kontroles darbības ietekmē spiedienu

        # Simulācijas galvenais cikls
        try:
            while self.running:
                # Pārbauda, vai process darbojas
                if self.process_running:
                    # Aprēķina jauno temperatūru, ņemot vērā inerci un iestatīto vērtību
                    target_diff = self.setpoint_temperature - self.temperature
                    temp_change = target_diff * temp_control_factor

                    # Pievienojam nejaušu troksni
                    temp_noise = random.uniform(-1, 1) * temp_noise_factor

                    # Jaunā temperatūra
                    self.temperature += temp_change + temp_noise

                    # Aprēķina jauno spiedienu
                    target_pressure_diff = self.setpoint_pressure - self.pressure
                    pressure_change = target_pressure_diff * pressure_control_factor

                    # Pievieno nejaušu troksni spiedienam
                    pressure_noise = random.uniform(-1, 1) * pressure_noise_factor

                    # Jaunais spiediens
                    self.pressure += pressure_change + pressure_noise

                    # Simulē līmeņa maiņu atkarībā no temperatūras un spiediena
                    level_change = (self.temperature - 25) * 0.01 + (self.pressure - 50) * 0.005

                    # Nodrošina, ka līmenis paliek robežās 0-100
                    self.level = max(0, min(100, self.level + level_change))

                    # Pievieno jaunākās vērtības vēsturei
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.temperature_history.append((current_time, self.temperature))
                    self.pressure_history.append((current_time, self.pressure))
                    self.level_history.append((current_time, self.level))

                    # Ierobežo vēstures garumu
                    if len(self.temperature_history) > self.max_history_length:
                        self.temperature_history.pop(0)
                    if len(self.pressure_history) > self.max_history_length:
                        self.pressure_history.pop(0)
                    if len(self.level_history) > self.max_history_length:
                        self.level_history.pop(0)

                    # Atjaunina pēdējo datu atjaunināšanas laiku
                    self.last_update = datetime.now()

                    # Ieraksta statistiku žurnālā ik pēc 10 sekundēm (ja nepieciešams)
                    if random.random() < 0.1:  # ~10% iespēja katrā ciklā
                        logger.debug(f"Simulācijas stāvoklis: Temp={self.temperature:.2f}°C, "
                                     f"Spiediens={self.pressure:.2f} bar, "
                                     f"Līmenis={self.level:.2f}%")

                # Pauze starp simulācijas soļiem
                time.sleep(0.2)  # 5 atjauninājumi sekundē

        except Exception as e:
            logger.error(f"Simulācijas kļūda: {str(e)}")
        finally:
            logger.info("Simulācija apturēta")

    def get_status(self):
        """Atgriež pašreizējo procesa statusu"""
        return {
            "process_running": self.process_running,
            "temperature": round(self.temperature, 1),
            "pressure": round(self.pressure, 1),
            "level": round(self.level, 1),
            "setpoint_temperature": round(self.setpoint_temperature, 1),
            "setpoint_pressure": round(self.setpoint_pressure, 1),
            "timestamp": time.time()
        }

    def cleanup(self):
        """Iztīrīt un apturēt simulāciju"""
        self.running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(1.0)  # Gaidīt pavedienu beigt darbu
        logger.info("Simulation cleaned up")


class ProcessServer:
    """Servera klase, kas apkalpo pieprasījumus no HMI"""

    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.simulator = ProcessSimulator()

    def start(self):
        """Sākt servera darbību"""
        try:
            # Izveidojam TCP servera ligzdu
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Iestatām SO_REUSEADDR, lai izvairītos no adreses bloķēšanas pēc servera restarta
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)  # Ļaujam līdz 5 savienojumiem gaidīt rindā

            self.running = True
            logger.info(f"Server started on {self.host}:{self.port}")

            # Sākt simulācijas pavedienu
            self.simulator.running = True

            # Galvenais cikls, kas pieņem savienojumus
            while self.running:
                try:
                    # Gaidām jaunu savienojumu, ar timeout, lai varētu periodiski pārbaudīt self.running
                    self.server_socket.settimeout(1.0)
                    try:
                        client_socket, client_address = self.server_socket.accept()
                        logger.info(f"New connection from {client_address}")

                        # Sākam jaunu pavedienu katram klientam
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(client_socket, client_address),
                            daemon=True
                        )
                        client_thread.start()
                        self.clients.append((client_socket, client_thread))
                    except socket.timeout:
                        # Tas ir paredzēts, lai varētu periodiski pārbaudīt self.running
                        continue
                    except Exception as e:
                        if self.running:
                            logger.error(f"Error accepting connection: {e}")
                except KeyboardInterrupt:
                    logger.info("Server stopping due to keyboard interrupt")
                    self.running = False
                    break

        except Exception as e:
            logger.error(f"Error starting server: {e}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket, client_address):
        """Apstrādāt klienta savienojumu atsevišķā pavedienā"""
        logger.info(f"Handling client from {client_address}")

        try:
            # Iestatām īsāku timeout, lai varētu ātri reaģēt uz servera izslēgšanu
            client_socket.settimeout(1.0)

            buffer = ""
            while self.running:
                try:
                    # Lasām datus no klienta
                    data = client_socket.recv(1024)
                    if not data:
                        logger.info(f"Client {client_address} disconnected")
                        break

                    # Pievienojam saņemtos datus buferim
                    buffer += data.decode('utf-8')

                    # Apstrādājam katru rindu (JSON objektu), ko noslēdz newline
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line:
                            self.process_command(line, client_socket, client_address)

                except socket.timeout:
                    # Tas ir paredzēts, lai šis pavediens varētu reaģēt uz servera izslēgšanu
                    continue
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error from {client_address}: {e}")
                    # Mēģinām atjaunot buferi, tīrām to
                    buffer = ""
                except Exception as e:
                    logger.error(f"Error handling client {client_address}: {e}")
                    break

        except Exception as e:
            logger.error(f"Client handler error for {client_address}: {e}")
        finally:
            # Aizveram klienta savienojumu
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Client {client_address} handler finished")

    def process_command(self, command_str, client_socket, client_address):
        """Apstrādāt klienta komandu"""
        try:
            # Parsējam JSON komandu
            command_data = json.loads(command_str)
            command = command_data.get('command', '').lower()
            value = command_data.get('value', None)

            logger.info(f"Received command '{command}' from {client_address}")

            response = {"status": "error", "error": "Unknown command"}

            # Apstrādājam dažādas komandas
            if command == 'status':
                # Atgriežam pašreizējo statusu
                response = self.simulator.get_status()
                response["status"] = "ok"

            elif command == 'start':
                # Mēģinām sākt procesu
                if self.simulator.start():
                    response = {"status": "ok"}
                else:
                    response = {"status": "error", "error": "Process already running"}

            elif command == 'stop':
                # Mēģinām apturēt procesu
                if self.simulator.stop():
                    response = {"status": "ok"}
                else:
                    response = {"status": "error", "error": "Process already stopped"}

            elif command == 'set_temperature':
                # Iestatām temperatūru
                if self.simulator.set_temperature(value):
                    response = {"status": "ok"}
                else:
                    response = {"status": "error", "error": "Invalid temperature value"}

            elif command == 'set_pressure':
                # Iestatām spiedienu
                if self.simulator.set_pressure(value):
                    response = {"status": "ok"}
                else:
                    response = {"status": "error", "error": "Invalid pressure value"}

            # Atgriežam atbildi klientam
            client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {client_address}: {command_str}")
            response = {"status": "error", "error": "Invalid JSON"}
            client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
        except Exception as e:
            logger.error(f"Error processing command from {client_address}: {e}")
            response = {"status": "error", "error": str(e)}
            client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))

    def cleanup(self):
        """Iztīrīt resursus un apturēt serveri"""
        logger.info("Cleaning up server resources...")

        # Apturām simulāciju
        self.simulator.cleanup()

        # Aizveram savienojumus ar klientiem
        for client_socket, client_thread in self.clients:
            try:
                client_socket.close()
            except:
                pass

        # Aizveram servera ligzdu
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        logger.info("Server cleanup complete")


# Signālu apstrādes funkcija, lai varētu gracefully aizvērt serveri
def signal_handler(sig, frame):
    logger.info("Received shutdown signal, stopping server...")
    if server:
        server.running = False


if __name__ == "__main__":
    # Reģistrējam signālu apstrādi
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Inicializējam serveri
    host = 'localhost'  # Ja jums vajag savienojumu no citām ierīcēm, iestatiet '0.0.0.0'
    port = 5000

    # Komandu rindiņas argumentu apstrāde (ja nepieciešams)
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            logger.error(f"Invalid port: {sys.argv[2]}")
            sys.exit(1)

    logger.info(f"Starting server on {host}:{port}")
    server = ProcessServer(host, port)

    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopping due to keyboard interrupt")
    finally:
        server.running = False
        logger.info("Server stopped")
