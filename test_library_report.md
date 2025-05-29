# Library Structure Report

Generated: 2025-05-28 21:09:00

## Library Information
- **Name**: Test
- **Description**: Example library for testing
- **Maintainer**: Dr. Test <email@example.com>
- **License**: MIT
- **Website**: https://example.com/library
- **Repository**: https://github.com/example/library


## Directory Structure
### Symbols
Path: `symbols`

Subdirectories:
- `actives`
- `passives`

### Footprints
Path: `footprints`

Subdirectories:
- `passives`
- `smd`
- `tht`

### Models_3D
Path: `3dmodels`

Subdirectories:
- `passives`

### Documentation
Path: `docs`

Subdirectories:
- `passives`


## Symbols
### Symbol Files
-  `symbols\passives\capacitors\capacitors.kicad_sym`
-  `symbols\passives\resistors\resistors.kicad_sym`

### Symbol Validation Results

#### passives

##### capacitors
- **C1**
    - ✅ Symbol name 'C1' matches pattern: ^C[0-9]+$
    - ✅ Property Reference value 'C1' matches pattern: ^C[0-9]+$
    - ✅ Property Description value '100nF Capacitor' matches pattern: ^[0-9.]+[pnu]F Capacitor$
    - ✅ Property Validated value 'true' matches pattern: None
    - ⚠️ Unknown property: Value
    - ⚠️ Unknown property: Footprint
    - ⚠️ Unknown property: Datasheet
    - ⚠️ Unknown property: Voltage
    - ❌ Symbol has 0 pins, but minimum required is 2
- **C2**
    - ✅ Symbol name 'C2' matches pattern: ^C[0-9]+$
    - ✅ Property Reference value 'C2' matches pattern: ^C[0-9]+$
    - ✅ Property Description value '10uF Capacitor' matches pattern: ^[0-9.]+[pnu]F Capacitor$
    - ✅ Property Validated value 'true' matches pattern: None
    - ⚠️ Unknown property: Value
    - ⚠️ Unknown property: Footprint
    - ⚠️ Unknown property: Datasheet
    - ⚠️ Unknown property: Voltage
    - ❌ Symbol has 0 pins, but minimum required is 2

##### resistors
- **R1**
    - ✅ Symbol name 'R1' matches pattern: ^R[0-9]+$
    - ✅ Property Reference value 'R1' matches pattern: ^R[0-9]+$
    - ✅ Property Description value '10k Resistor' matches pattern: ^[0-9.]+[kM]?[Î©]? Resistor$
    - ✅ Property Validated value 'true' matches pattern: None
    - ✅ Property Value value '10k' matches pattern: ^[0-9.]+[kM]?[Î©]?$
    - ⚠️ Unknown property: Footprint
    - ⚠️ Unknown property: Datasheet
    - ⚠️ Unknown property: Tolerance
    - ⚠️ Unknown property: Power
    - ❌ Symbol has 0 pins, but minimum required is 2
- **R2**
    - ✅ Symbol name 'R2' matches pattern: ^R[0-9]+$
    - ✅ Property Reference value 'R2' matches pattern: ^R[0-9]+$
    - ✅ Property Description value '1M Resistor' matches pattern: ^[0-9.]+[kM]?[Î©]? Resistor$
    - ✅ Property Validated value 'true' matches pattern: None
    - ✅ Property Value value '1M' matches pattern: ^[0-9.]+[kM]?[Î©]?$
    - ⚠️ Unknown property: Footprint
    - ⚠️ Unknown property: Datasheet
    - ⚠️ Unknown property: Tolerance
    - ⚠️ Unknown property: Power
    - ❌ Symbol has 0 pins, but minimum required is 2


## Footprints
### Footprint Files
-  `footprints\smd\capacitors\Test_cap.kicad_mod`

### Footprint Validation Results

#### smd

##### capacitors
- **C_0603_1608Metric**
    - ✅ Footprint name 'C_0603_1608Metric' matches pattern: ^C_[0-9]+_[0-9]+Metric$
    - ✅ Property Reference value 'C1' matches pattern: ^C[0-9]+$
    - ✅ Property Description value '100nF SMD Capacitor' matches pattern: ^[0-9.]+[pnu]F SMD Capacitor$
    - ✅ Property Validated value 'true' matches pattern: None
    - ✅ Footprint contains all required layers: F.Cu
    - ⚠️ Unknown property: Value
    - ⚠️ Unknown property: Datasheet
    - ❌ Footprint has 0 pads, but minimum required is 2


## 3D Models
### 3D Model Files
-  `3dmodels\passives\capacitors\GRM0115C1C120JE01L.STEP`

### 3D Model Validation Results

#### capacitors

##### capacitors
- **GRM0115C1C120JE01L**
    - ✅ Model name 'GRM0115C1C120JE01L' matches pattern: ^[A-Z0-9-]+$
    - ⚠️ Model does not match any defined category
    - ❌ Missing required property: Description
    - ❌ Missing required property: Validated


## Documentation
### Documentation Files
-  `docs\passives\capacitors\GRM033R61A474ME05-01A.pdf`

### Documentation Validation Results

#### capacitors

##### capacitors
- **GRM033R61A474ME05-01A**
    - ⚠️ Category/subcategory 'capacitors/capacitors' not found in structure for document 'GRM033R61A474ME05-01A'
    - ⚠️ Could not determine documentation category for document 'GRM033R61A474ME05-01A'
