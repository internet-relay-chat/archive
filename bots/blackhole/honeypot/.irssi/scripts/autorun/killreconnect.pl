use strict;
use Irssi;

Irssi::signal_add('event error', sub { Irssi::signal_stop(); });

Irssi::signal_add('event kill', sub {
    my ($server, $args, $nick, $address) = @_;
    my $reason = $args;
    $reason =~ s/^.*://g;
    Irssi::print("You were killed by $nick ($reason)."); 
    Irssi::signal_stop(); 
});