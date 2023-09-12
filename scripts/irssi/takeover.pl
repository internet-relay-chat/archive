# Takeover (IRSSI Channel Takeover Script)
# Developed by acidvegas in Perl
# http://github.com/acidvegas/irssi
# takeover.pl

# Todo:
# Detect max network modes.
# Kickban comma separated nicks.

use strict;
use Irssi;
use Irssi::Irc;

sub takeover {
    my ($data, $server, $channel) = @_;
    Irssi::printformat(MSGLEVEL_CLIENTCRAP, "takeover_crap", "Not connected to server."),        return if (!$server or !$server->{connected});
    Irssi::printformat(MSGLEVEL_CLIENTCRAP, "takeover_crap", "No active channel in window."),    return if (!$channel or ($channel->{type} ne "CHANNEL"));
    my $own_prefixes = $channel->{ownnick}{prefixes};
    Irssi::printformat(MSGLEVEL_CLIENTCRAP, "takeover_crap", "You are not a channel operator."), return if ($own_prefixes =~ /~|&|@|%/);
    my ($qops, $aops, $hops, $qcount, $acount, $hcount, $modes);
    my $hostname      = $channel->{ownnick}{host};
    my $nicklist      = $channel->nicks();
    foreach my $nick ($channel->nicks()) {
        next if ($nick eq $server->{nick});
        if ($nick->{prefixes} =~ /~/) {
            $qops .= "$nick->{nick} ";
            $qcount++;
        }
        if ($nick->{prefixes} =~ /&/) {
            $aops .= "$nick->{nick} ";
            $acount++;
        }
        if ($nick->{halfop}) {
            $hops .= "$nick->{nick} ";
            $hcount++;
        }
    }
    if ($qops) {
        $modes = "q" x $qcount;
        $channel->command("mode -$modes $qops");
    }
    if ($aops) {
        $modes = "a" x $qcount;
        $channel->command("mode -$modes $aops");
    }
    if ($hops) {
        $modes = "h" x $qcount;
        $channel->command("mode -$modes $hops");
    }
    $channel->command("deop -YES *");
    $channel->command("devoice -YES *");
    foreach ($channel->nicks()) {
        next if ($_->{'nick'} eq $server->{nick});
        $channel->command("kickban $_->{'nick'}");
    }
    $channel->command("ban *!*@*");
    $channel->command("mode +im");
    $channel->command("mode +e *!$hostname");
    $channel->command("mode +I *!$hostname");
}

Irssi::theme_register(['takeover_crap', '{line_start}{hilight takeover:} $0',]);
Irssi::command_bind('takeover', 'takeover');
