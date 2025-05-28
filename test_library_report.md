# Library Structure Report

Generated: 2025-05-28 14:48:47

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
- **C1**
    - ✅ Symbol name 'C1' matches pattern '^C[0-9]+$'
    - ✅ Property 'Reference' value 'C1' matches pattern '^C[0-9]+$'
    - ✅ Property 'Description' value '100nF Capacitor' matches pattern '^[0-9.]+[pnu]F Capacitor$'
    - ⚠️ Property 'Validated' type checking not implemented (expected boolean)
    - ⚠️ Property 'Validated' pattern is not a string or regex: None
    - ⚠️ Unknown property 'Value' in symbol 'C1'
    - ⚠️ Unknown property 'Footprint' in symbol 'C1'
    - ⚠️ Unknown property 'Datasheet' in symbol 'C1'
    - ⚠️ Unknown property 'Voltage' in symbol 'C1'
- **C2**
    - ✅ Symbol name 'C2' matches pattern '^C[0-9]+$'
    - ✅ Property 'Reference' value 'C2' matches pattern '^C[0-9]+$'
    - ✅ Property 'Description' value '10uF Capacitor' matches pattern '^[0-9.]+[pnu]F Capacitor$'
    - ⚠️ Property 'Validated' type checking not implemented (expected boolean)
    - ⚠️ Property 'Validated' pattern is not a string or regex: None
    - ⚠️ Unknown property 'Value' in symbol 'C2'
    - ⚠️ Unknown property 'Footprint' in symbol 'C2'
    - ⚠️ Unknown property 'Datasheet' in symbol 'C2'
    - ⚠️ Unknown property 'Voltage' in symbol 'C2'
- **R1**
    - ✅ Symbol name 'R1' matches pattern '^R[0-9]+$'
    - ✅ Property 'Reference' value 'R1' matches pattern '^R[0-9]+$'
    - ✅ Property 'Description' value '10k Resistor' matches pattern '^[0-9.]+[kM]?[Î©]? Resistor$'
    - ✅ Property 'Value' value '10k' matches pattern '^[0-9.]+[kM]?[Î©]?$'
    - ⚠️ Property 'Validated' type checking not implemented (expected boolean)
    - ⚠️ Property 'Validated' pattern is not a string or regex: None
    - ⚠️ Unknown property 'Footprint' in symbol 'R1'
    - ⚠️ Unknown property 'Datasheet' in symbol 'R1'
    - ⚠️ Unknown property 'Tolerance' in symbol 'R1'
    - ⚠️ Unknown property 'Power' in symbol 'R1'
- **R2**
    - ✅ Symbol name 'R2' matches pattern '^R[0-9]+$'
    - ✅ Property 'Reference' value 'R2' matches pattern '^R[0-9]+$'
    - ✅ Property 'Description' value '1M Resistor' matches pattern '^[0-9.]+[kM]?[Î©]? Resistor$'
    - ✅ Property 'Value' value '1M' matches pattern '^[0-9.]+[kM]?[Î©]?$'
    - ⚠️ Property 'Validated' type checking not implemented (expected boolean)
    - ⚠️ Property 'Validated' pattern is not a string or regex: None
    - ⚠️ Unknown property 'Footprint' in symbol 'R2'
    - ⚠️ Unknown property 'Datasheet' in symbol 'R2'
    - ⚠️ Unknown property 'Tolerance' in symbol 'R2'
    - ⚠️ Unknown property 'Power' in symbol 'R2'


## Footprints
### Footprint Files
-  `footprints\smd\capacitors\Test_cap.kicad_mod`

### Footprint Validation Results
- **C_0603_1608Metric**
    - ✅ Footprint name 'C_0603_1608Metric' matches pattern '^C_[0-9]+_[0-9]+Metric$'
    - ✅ Property 'Reference' value 'C1' matches pattern '^C[0-9]+$'
    - ✅ Property 'Description' value '100nF SMD Capacitor' matches pattern '^[0-9.]+[pnu]F SMD Capacitor$'
    - ✅ Footprint 'C_0603_1608Metric' contains all required layers
    - ⚠️ Unknown property 'Value' in footprint 'C_0603_1608Metric'
    - ⚠️ Unknown property 'Datasheet' in footprint 'C_0603_1608Metric'


## 3D Models
### 3D Model Files
-  `3dmodels\passives\capacitors\GRM0115C1C120JE01L.STEP`

### 3D Model Validation Results
- **GRM0115C1C120JE01L**
    - ⚠️ Category/subcategory 'capacitors/capacitors' not found in structure for model 'GRM0115C1C120JE01L'
    - ⚠️ Could not determine 3D model category for model 'GRM0115C1C120JE01L'


## Documentation
### Documentation Files
-  `docs\passives\capacitors\GRM033R61A474ME05-01A.pdf`

### Documentation Validation Results
- **GRM033R61A474ME05-01A**
    - ⚠️ Category/subcategory 'capacitors/capacitors' not found in structure for document 'GRM033R61A474ME05-01A'
    - ⚠️ Could not determine documentation category for document 'GRM033R61A474ME05-01A'
