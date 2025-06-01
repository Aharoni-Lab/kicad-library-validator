# Library Structure Report

Generated: 2025-05-31 23:50:50

## Library Information
- **Name**: .Lab
- **Description**: Validated KiCad library for lab-wide hardware
- **Maintainer**: Daniel Aharoni <daharoni@mednet.ucla.edu>
- **License**: MIT
- **Website**: https://github.com/Aharoni-Lab/kicad-lab-library
- **Repository**: https://github.com/Aharoni-Lab/kicad-lab-library.git


## Directory Structure
### Symbols
Path: `symbols`

Subdirectories:
- `active`
- `connector`
- `logic`
- `mcu`
- `memory`
- `passive`
- `power`
- `sensor`

### Footprints
Path: `footprints`

Subdirectories:
- `ic`
- `passive`

### Models_3D
Path: `3dmodels`

Subdirectories:
- `ic`
- `passive`

### Documentation
Path: `docs`

Subdirectories:
- `active`
- `mcu`
- `memory`
- `passive`
- `power`

### Tables
Path: `tables`


## Symbols
### Symbol Files
-  `symbols\active\comparator\comparator.kicad_sym`
-  `symbols\active\opamp\opamp.kicad_sym`
-  `symbols\active\transistor\transistor.kicad_sym`
-  `symbols\connector\header\header.kicad_sym`
-  `symbols\connector\jst\jst.kicad_sym`
-  `symbols\connector\molex\molex.kicad_sym`
-  `symbols\connector\usb\usb.kicad_sym`
-  `symbols\logic\flipflop\flipflop.kicad_sym`
-  `symbols\logic\gate\gate.kicad_sym`
-  `symbols\logic\level_shifter\level_shifter.kicad_sym`
-  `symbols\logic\multiplexer\multiplexer.kicad_sym`
-  `symbols\mcu\espressif\espressif.kicad_sym`
-  `symbols\mcu\microchip\microchip.kicad_sym`
-  `symbols\mcu\st\st.kicad_sym`
-  `symbols\memory\eeprom\eeprom.kicad_sym`
-  `symbols\memory\flash\flash.kicad_sym`
-  `symbols\memory\ram\ram.kicad_sym`
-  `symbols\passive\capacitor\capacitor.kicad_sym`
-  `symbols\passive\diode\diode.kicad_sym`
-  `symbols\passive\ferrite_bead\ferrite_bead.kicad_sym`
-  `symbols\passive\inductor\inductor.kicad_sym`
-  `symbols\passive\resistor\resistor.kicad_sym`
-  `symbols\power\power_monitor\power_monitor.kicad_sym`
-  `symbols\power\regulator\regulator.kicad_sym`
-  `symbols\power\supervisor\supervisor.kicad_sym`
-  `symbols\sensor\accelerometer\accelerometer.kicad_sym`
-  `symbols\sensor\gyro\gyro.kicad_sym`
-  `symbols\sensor\pressure\pressure.kicad_sym`
-  `symbols\sensor\temperature\temperature.kicad_sym`

### Symbol Validation Results
### passive
##### capacitor
- **C**
  - ✅ **Passing Validations:**
    - Symbol: Property 'Validated' value 'Yes' matches pattern: ^(Yes|No)$
    - Symbol: Reference 'C' has correct prefix: C
    - Symbol: Pin count matches expected: 2
- **C_45deg**
  - ✅ **Passing Validations:**
    - Symbol: Property 'Validated' value 'Yes' matches pattern: ^(Yes|No)$
    - Symbol: Reference 'C' has correct prefix: C
    - Symbol: Pin count matches expected: 2
- **C_Small**
  - ✅ **Passing Validations:**
    - Symbol: Property 'Validated' value 'Yes' matches pattern: ^(Yes|No)$
    - Symbol: Reference 'C' has correct prefix: C
    - Symbol: Pin count matches expected: 2


## Footprints
### Footprint Files
-  `footprints\passive\capacitor_smd.pretty\C_0201_0603Metric.kicad_mod`

### Footprint Validation Results
### passive
##### capacitor_smd
- **C_0201_0603Metric**
  - ✅ **Passing Validations:**
    - Footprint: Property 'Validated' value 'Yes' matches pattern: ^(Yes|No)$


## 3D Models
### 3D Model Files
-  `3dmodels\passive\capacitor_smd.3dshapes\C_0201_0603Metric.step`

### 3D Model Validation Results
### passive
##### capacitor_smd
- **C_0201_0603Metric**
  - ✅ **Passing Validations:**
    - 3D Model: Model format .step is valid
    - 3D Model: Model name 'C_0201_0603Metric' matches pattern: ^C_[0-9]{4}_[0-9]{4}Metric$


## Documentation
No documentation files found.
