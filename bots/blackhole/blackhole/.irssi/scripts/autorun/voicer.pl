use strict;
use warnings;
use Irssi;
use Irssi::Irc;

our $VERSION = '1.0';
our %IRSSI = (
    authors     => 'acidvegas (help from www)',
    contact     => 'acidvegas@supernets.org',
    name        => 'Voicer',
    description => 'A script to auto voice anyone who joins the channel after voicer_delay seconds..',
    license     => 'ISC',
    url         => 'http://github.coM/acidvegas/irssi',
);

sub send_voice {
    my ($server, $channel, $nick) = @{$_[0]};
    $server->command("/mode $channel +v $nick");
}

sub event_join {
    my ($server, $channel, $nick) = @_;
    my $delay = Irssi::settings_get_int('voicer_delay');
    Irssi::timeout_add_once( $delay * 1000, \&send_voice, [$server, $channel, $nick]);
}

Irssi::settings_add_int('misc', 'voicer_delay', 10);
Irssi::signal_add_last('message join', 'event_join');
