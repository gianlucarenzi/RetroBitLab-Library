# RetroBitLab-Library
Collection stuff for Kicad projects

This repository is needed when cloning other repos from my github space.
All project are usually relative to my home computer path, but this Library is needed at the same level of the other projects.

E-Mail me for any question you may have:

Gianluca Renzi icjtqr@gmail.com

Happy coding and hacking! ;-)

## Third-party parts

### Apple II expansion bus (CC BY-SA 4.0)

Converted to KiCad 5 from [markadev/KiCad-AppleII](https://github.com/markadev/KiCad-AppleII)
(commit `9c33c63`), licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/);
these files stay under that license:

- symbols `Bus_Apple_II_Card_Side`, `Bus_Apple_II_Computer_Side` (`RetroBitLab.lib`): the Apple II
  bus symbol by Nikolay Nikolov ([kicad-symbols MR 3693](https://gitlab.com/kicad/libraries/kicad-symbols/-/merge_requests/3693)),
  as modified by markadev; here `Φ0`/`Φ1` are named `PHI0`/`PHI1`;
- footprint `APPLE2-PERIPHERAL-BUS-EDGE` (from `Peripheral_Bus_Edge`): card edge fingers. KiCad 5
  footprints cannot hold keepout zones: the original's three rule areas (bevel, no vias/pads in the
  finger area, no copper pour) are drawn on `Cmts.User` and must be added on the board;
- footprint `EDAC_395-050-520-201_APPLE2-SLOT` (from `EDAC_395-050-520-201_CounterClockwise`): the
  motherboard-side slot socket, rows 200 mil apart;
- 3D model `RetroBitLab.3dshapes/EDAC_395-050-520-201.step`: from EDAC (through DigiKey).
