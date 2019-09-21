# friedrich-hass
This is a simple HomeAssistant integration for Friedrich Chill series
air conditioners (and maybe others that use the same IR protocol).
Includes Arduino code for a Teensy LC and a custom component for HomeAssistant
to send commands to the Teensy to control the AC.

## How it works
The commands sent by Friedrich's remote are idempotent - that is, they include
all the information about the state of the air conditioner. Rather then sending
a "temperature up" command, the remote sends a "set the temperature to 75
degrees." The OEM remote is stateful, and keeps track of the total state of the
air conditioner. Because of this, it's actually quite easy for us to control
the AC some other way - we don't need to ask the AC what it's state is, because
our commands will set the state to exactly what we want it to.

## Setup / Installation
You'll need:
* A Teensy microcontroller (I used a Teensy LC)
* An Infrared LED and appropritate current limiting resistor
* A machine running HomeAssistant (mine is running in Docker on a Raspberry Pi)
* A USB cable

### Hardware
Solder the LED and resistor to the appropriate transmit pin on the Teensy. The
[Teensy documentation](https://www.pjrc.com/teensy/td_libs_IRremote.html) has
a table that indicates the correct pin to use. Put the Teensy somewhere that
the infrared LED is pointed at the AC unit, and plug it with a micro USB cable.

Flash the Teensy with the Arduino sketch in the `arduino` folder, and test that
it works by sending a remote command with the serial console.

### HomeAssistant
Copy the `friedrich_ir` directory into the `custom_components` directory in
your HomeAssistant config directory (you may have to create `custom components`).

Plug the Teensy into the computer running HomeAssistant, and find out which TTY
device it comes up as (mine is `ttyACM0` on my Raspbian system).

Add these lines to your HomeAssisant `configuration.yaml`:

```yaml
climate:
  - platform: friedrich_ir
    device: /dev/ttyACM0
```

Restart the HomeAssistant server, and you should now have climate controls!

## Thanks
This was really easy for me to build, because Bryce Kahle did all the hard work
of reverse engineering the IR protocol that Friedrich uses:

https://brycekahle.com/2014/11/15/infrared-air-conditioner-control-with-a-spark-core/
