# BLE GATT specification (draft)

Custom 128-bit service UUID: `[generate with uuidgen]`

| Characteristic | Properties | Payload | Rate |
|---|---|---|---|
| Distance | Notify | `uint16` mm, `uint8` status (0 valid, 1 out of range, 2 low signal) | 5 Hz (adaptive 1–10) |
| Head pitch | Notify | `int8` pitch °, `int8` roll ° | 2 Hz |
| Screen state | Write | `uint8` flags: bit0 screen on, bit1 in use, bit2 quiet mode | On change |
| Haptic | Write without response | `uint8` pattern id, `uint8` intensity | On event |
| Config | Read / Write | thresholds, sampling rate, firmware version | On change |
| Battery (standard 0x180F) | Read / Notify | `uint8` percent | Every 60 s |

Suggested connection interval 50–100 ms. Default 23-byte ATT MTU is sufficient.
