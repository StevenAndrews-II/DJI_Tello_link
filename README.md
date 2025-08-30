# 🚁 TelloLink – Alternative DJI Tello Communication Layer  

A Python communications library by **Steven Andrews II** providing a flexible **UDP-based communication layer** for the DJI Tello drone.  
This project was built as an **alternative to the official SDK client**, offering threading support, telemetry parsing, and connection management.  

---

## ✨ Features  

- 📡 Uplink / downlink handlers with socket-based threading  
- 🔄 Connection state machine with ping/timeout detection  
- 🛰️ Telemetry buffer + parser (structured telemetry access)  
- ⚡ Low-level UDP socket management (custom ports, safe reconnects)  
- 🛠️ Utility layer for simple `connect()`, `disconnect()`, `uplink()`, and telemetry queries  
- 🔌 Multi-threaded design – keeps downlink, telemetry, and control separated  

---

## 🚀 Installation  

This library depends on Python’s standard library modules:  

- `socket`  
- `threading`  

No external dependencies required.  

Clone this repo:  

```bash
git clone https://github.com/StevenAndrews-II/DJI_Tello_link
.git
cd DJI_Tello_link
```

---

## 📖 Usage Example  

```python
from tello_link import TelloLink
import time

# Initialize link
tello = TelloLink()

# Send a simple command
tello.uplink("command")  # put drone in SDK mode
time.sleep(1)

tello.uplink("takeoff")
time.sleep(5)

tello.uplink("land")

# Get telemetry
battery = tello.get_telem("bat")
print("Battery level:", battery)
```

---

## 📚 API Reference  

### Backend  
- `downlink_com(port)` → Thread: receives responses from drone commands  
- `downlink_telemetry(port)` → Thread: receives telemetry packets  
- `uplink(DATA, hold_ping: bool)` → send data uplink to drone  
- `connection_()` → connection state machine (handles pings, reconnects)  
- `telem_buffer()` → parses telemetry into structured dict  

### Utility (Frontend)  
- `uplink(DATA, hold_ping: bool)` → sends commands/data uplink  
- `disconnect()` → disconnect from drone  
- `connect()` → reconnect to drone  
- `get_telem(search_id)` → get telemetry value by key  

---

## ⚙️ Telemetry Keys  

The following telemetry values are supported via `get_telem()`:  

```
mid, x, y, z, pitch, roll, yaw, 
vgx, vgy, vgz, templ, temph, 
tof, h, bat, time, baro, 
agx, agy, agz
```

---

## 🛠️ Project Info  

- Author: **Steven Andrews II**  
- Project Type: Experimental / Alternative SDK  
- License: MIT (consider adding LICENSE file)  
