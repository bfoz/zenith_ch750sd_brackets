# Zenith CH750 Super Duty Brackets

Custom brackets that can be used to improve wire and hose routing.

## Fabrication

The various online cut shops have different ordering processes so you'll need to consult their documentation. 

If you're familiar with FreeCAD's Sheet Metal Workbench you can try using the "Unfold" feature to generate the flattened drawing files to send to the shop. 
However, exporting to a STEP file seems to produce more consistent results.

NOTE: As of June 2025, the unfolded files don't work well with [Send Cut Send](https://sendcutsend.com); use the STEP files instead.


## Wing Trailing Edge Bracket

The stock kit doesn't use the space inside of the wing trailing edge skins for very much.
If your build uses that space for a fuel return hose, or for the pitot and AoA hoses, you can use these brackets to help keep everything organized.

The file `TrailingEdgeBracket.FCStd` is a FreeCAD file containing several different bracket designs meant for different configurations of wiring and hoses in the left wing. 

To make the brackets for the right wing, simply flip the bend angle in FreeCAD (make sure you have the Sheet Metal Workbench installed). 
Alternatively, most cut shops that do online ordering will give you the option of duplicating the part with a reversed bend angle at order time.
You'll have two extra holes in the resulting right wing bracket because only the left wing has the pitot and AoA tubes. Feel free to use those holes for something else, or simply leave them unpopulated.

If you're using the braided fuel hoses from [Aircraft Specialty](https://www.aircraftspecialty.com) the part named `BushingsGrommets` should work well for you.

### Bushings and Grommets

Each bracket is meant to be used with snap bushings and grommets for holding the hoses and wires. 

These parts have been used successfully with fuel hoses from [Aircraft Specialty](https://www.aircraftspecialty.com) and the [Dynon pneumatic installation kit](https://shop.dynon.com/products/pitot-static-aoa-pneumatic-installation-kit):

- [1/4" ID Snap Bushings](https://www.amazon.com/dp/B00OP6070I) for 1/4" OD pitot and AoA hoses
- [1/2" ID AN931 Elastic Grommet](https://www.aircraftspruce.com/catalog/appages/an931.php) for the fuel return hose
- [1/4" ID AN931 Elastic Grommet](https://www.aircraftspruce.com/catalog/appages/an931.php) for the wingtip and landing light wires

### Installation

1. Slide the brackets and grommets onto the fuel return hose first. You won't be able to that later.
2. The fuel return hoses grommets are a tight fit. Use a small flat screwdriver to force the grommets into the bracket around the hose. Be careful to not damage the grommets.
3. Push the 1/4" ID wire grommets into their respective holes
4. Snap the snap bushings into their holes
5. Cleco the brackets to the rear spar
6. Feed the pitot and AoA tubes through the snap bushings
7. Feed the wires through the wire grommets
8. Rivet the brackets once you're happy with everything

## Fuel Return Hose Bracket

## Wingtip wires bracket
