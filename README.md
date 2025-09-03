# Zenith CH750 Super Duty Brackets

Custom brackets that can be used to improve wire, cable, and hose routing.

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

`FuelReturnHoseBracket.FCStd`

If you're using a fuel return hose and routing it through the wing bay just outboard of the fuel tank, 
this bracket can be used to keep the hose from bouncing around inside of the wing.

The part in the file is for the left wing. Flip the bend angle to make the part for the right wing.

### Bushings and Grommets

- [1/2" ID AN931 Elastic Grommet](https://www.aircraftspruce.com/catalog/appages/an931.php) 

### Installation

- Use 2 A4 rivets to attach the bracket to the rear stiffener in the wing bay just outboard of the fuel tank. You will need to match drill holes in the stiffener.
- Position the bracket roughly in the middle of the stiffener, or wherever seems to be right for your fuel hose.
- The stiffening flange of the bracket should be outboard of the fuel hose to prevent the hose from rubbing on the flange. 


## Wingtip wire brackets

`WingtipWireBracket.FCStd`

If you run the wingtip wires through the outboard-most bay in the wing, this bracket will keep the wires from flopping around inside that bay.

**NOTE**: This bracket is currently sized for the 3-conductor wire that comes with the kit. I haven't yet tested it with the 4-conductor wire that most builders use.

### Bushings and Grommets

- [1/8" ID AN931 Elastic Grommet](https://www.aircraftspruce.com/catalog/appages/an931.php) 

### Installation

1. Align the bracket with the stiffener in the outobard-most bay of the wing
2. Match-drill the two rivet holes using a #30 drill bit
3. Rivet to the stiffener with 2 A4 rivets
4. Push the grommet into the hole
5. Feed the wires through the grommet


## Elevator Pulley Bracket

`ElevatorPulleyBracket.FCStd`

The stock kit uses nylon blocks as "pulleys" for the elevator control cables. Presumably, steel cables rubbing on plastic will eventually wear out the plastic, 
necessitating periodic replacement. If you'd like to avoid that problem, or at least delay it, you can install pulleys just forward of the jump seat rear channel 
that will keep the control cables from rubbing on the nylon.

### Fabrication

The CAD file includes two parts, `Bracket` and `Base`, that need to be fabricated. The other parts are only for reference. 

- Export the `Bracket` and `Base` parts as STEP files and send them to your favorite cut shop
- Use 1mm thick (0.040") Aluminum for both parts
- The CAD file uses the bend radius and K-factor for [Send Cut Send](https://sendcutsend.com). Adjust as needed for your shop.

### Parts

| Part Number | Quantity | Description |
|-------------|----------|-------------|
| [MC20220-1](https://www.aircraftspruce.com/catalog/pnpages/MS20220-1.php)     | 2 | 1.75" Phenolic Pulley                                 |
| [AN5-13A](https://www.aircraftspruce.com/catalog/hapages/an5.php)             | 2 | Bolt                                                  |
| [AN365-524A](https://www.aircraftspruce.com/pages/ha/nut_an365/an365_2.php)   | 2 | Elastic Stop Nut                                      |
| [AN960-516](https://www.aircraftspruce.com/catalog/hapages/flatwashers.php)   | 4 | Washer                                                |
|                                                                               |   | Tape (blue tape, electrical tape, whatever is handy)  |

### Installation

**NOTE**: The base plates can be installed on either the inside, or the outside, of the airplane. The cables will line up either way. The difference is purely aesthetic.

1. Run the control cables through the holes in the rear jump seat channel, tie weights to the ends, and adjust to approximate the final position of the cables
2. Set the base plate and pulley brackets on the cabin floor with the cables running through the brackets
3. Install the pulleys in the brackets (using the bolts, nuts, and washers) with the cables under the pulleys
4. Align the pulleys and brackets with the cables and make sure everything looks "right"
5. With the base plates under the brackets, and all of the rivet holes aligned, tape the base plates to the cabin floor skin
6. Remove the pulleys and brackets while leaving the base plate in place
7. Match drill the holes in the base plates through the cabin floor skin using a #20 drill bit
8. Debur the holes
9. Cleco the base plates and brackets in place. **NOTE**: The base plates can be installed on the inside or the outside of the airplane. The choice is purely aesthetic.
10. Rivet with A5 rivets **from the outisde** of the airplane
11. Re-install the pulleys with the control cables under the pulleys


