# blackhole
A bot mitigation system for the Internet Relay Chat (IRC) protocol.

###### Information
The entire blackhole system works on IRSSI connections across different boxes.

The honeypot connections will message the blackhole connection the nick of anyone who does a CTCP, DCC, INVITE, or Private Message.

The blackhole bot will kill anyone who triggers the honeypots, it will also kick anyone who masshilights or hilights a honeypot.

Honeypot nicks and hosts need to be added to the 'triggers' file and reloaded on the blackhole connection.

Make sure you do `chmod -w triggers` on the honypot's `triggers` file to prevent accidental removal of triggers.

You can change the `/timer add limit 300 /alimit` line in the blackhole startup file to `/timer add limit 300 /acslimit` to use ChanServs mode lock feature.