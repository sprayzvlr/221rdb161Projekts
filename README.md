# SCADA AI Project

## Apraksts
Šis ir SCADA AI prototips Pythonā ar:
- Sensoru datu apstrādi un anomāliju detekciju (RandomForest)
- Tkinter GUI: galvenais logs, statistikas logs, procesi un PLC simulācija
- (Opcija) TCP/UDP vai OPC UA komunikācija

## Uzstādīšana
```bash
git clone <repo>
cd scada_ai_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt