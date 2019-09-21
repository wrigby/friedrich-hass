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

## What works (and doesn't work)
Right now this supports setting the AC mode, temperature, and fan speed from
HomeAssistant. Turning the AC on and off isn't actually supported yet (I just
set the AC to Money Saver at 80 degrees when I leave my apartment).

Pull requests are are welcome!

## Setup / Installation
You'll need:
* A Teensy microcontroller (I used a Teensy LC)
* An Infrared LED and appropritate current limiting resistor
* A machine running HomeAssistant (mine is running in Docker on a Raspberry Pi)
* A USB A to Micro B cable

### Hardware
Solder the LED and resistor to the appropriate transmit pin on the Teensy. The
[Teensy documentation](https://www.pjrc.com/teensy/td_libs_IRremote.html) has
a table that indicates the correct pin to use. Put the Teensy somewhere that
the infrared LED is pointed at the AC unit, and plug it with a micro USB cable.

Flash the Teensy with the Arduino sketch in the `arduino` folder, and test that
it works by sending a remote command with the serial console.

### HomeAssistant
Copy the `friedrich_ir` directory into the `custom_components` directory in
your HomeAssistant config directory.

Plug the Teensy into the computer running HomeAssistant, and find out which TTY
device it comes up as (mine is `ttyACM0` on my Raspbian system). If you're
running HomeAssistant in Docker, you'll need to pass this device into the
container with the `--device /dev/ttyACM0` option to `docker run`.

Add these lines to your HomeAssisant `configuration.yaml`, setting `device` to
the correct TTY.

```yaml
climate:
  - platform: friedrich_ir
    device: /dev/ttyACM0
```

Restart the HomeAssistant server, and you should now have climate controls!

## Thanks
This was really easy for me to build, because Bryce Kahle [did all the hard work
of reverse engineering the IR protocol that Friedrich uses][1]


Also a big shoutout to [Fat Cat Fab Lab][2] in NYC. If you live in New York
and want to join an awesome community of makers, stop by and join us!

[1]: https://brycekahle.com/2014/11/15/infrared-air-conditioner-control-with-a-spark-core/
[2]: https://www.fatcatfablab.org/

