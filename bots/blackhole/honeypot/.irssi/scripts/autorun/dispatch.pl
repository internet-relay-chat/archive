use strict;
use warnings;
use Irssi;
use Irssi::Irc;

sub event_default_command {
    my ($command, $server) = @_;
    return if (Irssi::settings_get_bool("dispatch_unknown_commands") == 0 || !$server);
    $server->send_raw($command);
    Irssi::signal_stop();
}

Irssi::settings_add_bool("misc", "dispatch_unknown_commands", 1);
Irssi::signal_add_first("default command", "event_default_command");
