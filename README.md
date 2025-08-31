# 🚁 TelloLink – Alternative DJI Tello Communication Layer  

A Python communications API by **Steven Andrews II** providing a flexible **UDP-based communication layer** for the DJI Tello drone.  
This project was built as an **alternative to the official SDK client**, offering threading support, telemetry parsing, and connection management for realtime control.  

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

This API depends on Python’s standard modules:  

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

- Example script: 
- auto stabilization - dead sticks 
- dynamic command buffer
- keys as sticks 
- button binds 

```python
from TelloLink import TelloLink
import time
import keyboard

TL                   = TelloLink()  # Initialize link

EXIT                 = False
FPS_LOCK             = 60
FPS_INTERVAL         = 1 / FPS_LOCK
delta_time           = 0
last_tick            = time.time()

# keyboard control
direction_buffer     = [0, 0, 0, 0]

# flight state tracking
dead_stick           = True
dead_stick_padding   = 2

# keys
w_down = s_down = a_down = d_down = False

# connection tracking
last_connection_state = False

def APP(): 
    global last_connection_state, w_down, s_down, a_down, d_down, dead_stick

    # display connection state
    if last_connection_state != TL.connection_data["connection_state"]:
        print(f"Drone connection state: {TL.connection_data['connection_state']}")
        last_connection_state = TL.connection_data["connection_state"]

    # single action commands
    if keyboard.is_pressed("t"):
        print("sending take off command")
        TL.uplink("takeoff")

    if keyboard.is_pressed("l"):
        print("sending land command")
        TL.uplink("land")

    # keyboard motion interface
    w_down = keyboard.is_pressed("w")
    s_down = keyboard.is_pressed("s")
    a_down = keyboard.is_pressed("a")
    d_down = keyboard.is_pressed("d")

    # reset buffer to 0 when no buttons are down
    if not w_down and not s_down:
        direction_buffer[0] = 0
    if not a_down and not d_down:
        direction_buffer[1] = 0

    # apply motion
    if w_down:
        direction_buffer[0] =  50
    if s_down:
        direction_buffer[0] = -50
    if a_down:
        direction_buffer[1] = -50
    if d_down:
        direction_buffer[1] =  50

    # Buffered uplink for motion control - dead stick handling 
    if direction_buffer != [0, 0, 0, 0]:
       TL.uplink(direction_buffer)
       dead_stick = False
    else:
        if not dead_stick:
            for _ in range(dead_stick_padding):
                TL.uplink(direction_buffer)
            dead_stick = True

# main loop, fps locked to 60
while not EXIT:
    tick         = time.time()
    delta        = tick - last_tick
    last_tick    = tick

    delta_time += delta

    if delta_time >= FPS_INTERVAL:
        TL.connection()
        APP()
        delta_time -= FPS_INTERVAL


```

---


## 📚 API Reference  

### Backend  
- `__downlink_com(port)` → Thread: receives responses from drone commands  
- `__downlink_telemetry(port)` → Thread: receives telemetry packets  
- `__telem_buffer()` → parses telemetry into structured dict  

### Utility (Frontend)  
- `uplink(DATA)` → sends commands/data uplink  
- `disconnect()` → disconnect from drone  
- `connect()` → reconnect to drone  
- `get_telem(search_id)` → get telemetry value by key

### Clock / state machine
- `connection()` → connection state machine (handles pings, reconnects)  

---

## ⚙️ Telemetry Keys  

The following telemetry values are supported via `get_telem()`:  
See DJI Protocol Documentation: 

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
- License: MIT 
