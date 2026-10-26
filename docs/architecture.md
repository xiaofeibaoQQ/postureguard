# Architecture

```
 Wearable (nRF52840)                 Companion app / desktop client
 ┌──────────────────┐   BLE GATT    ┌──────────────────────────────┐
 │ ToF  (distance)  │ ───────────▶  │ BLE client                   │
 │ IMU  (head pitch)│               │ Pose engine (MediaPipe)      │
 │ Haptic motor     │ ◀───────────  │ Fusion + rules engine        │
 │ LiPo + charger   │  haptic cmds  │ SQLite log, dashboard        │
 └──────────────────┘               └──────────────────────────────┘
```

## Fusion rules (starting values, to be tuned in pilot)

| Signal | Source | Trigger |
|---|---|---|
| Viewing distance | ToF | < 30 cm (phone/tablet) or < 45 cm (laptop/desktop) for 5 s |
| Head pitch | IMU | > 30° below horizontal for 60 s |
| Forward-head score | Pose AI | z-score above baseline + threshold for 30 s |
| Break reminder | Timer | 20 min of screen use, then look 6 m away for 20 s |

Safeguards: debounce, hysteresis (e.g. 5 cm / 5°), 2-minute cooldown, and context gating (only while a linked screen is on and in use).

## Privacy

Camera is opt-in with a visible indicator. Frames stay in memory and are never stored or uploaded.
