use strict;
use Irssi;

# The /v command will voice everyone in the channel that doesnt have voice or higher (halfop, op, etc).

sub cmd_massvoice {
    my ($data, $server, $channel) = @_;
    Irssi::printformat(MSGLEVEL_CRAP, "v: Not connected to server."),        return if (!$server or !$server->{connected});
    Irssi::printformat(MSGLEVEL_CRAP, "v: No active channel in window."),    return if (!$channel or ($channel->{type} ne "CHANNEL"));
    my @nicks             = $channel->nicks();
    my @normal_nicks      = grep { $_->{prefixes} !~ /[\~\&\@\%\+]/ } @nicks;
    my @normal_nick_names = map { $_->{nick} } @normal_nicks;
    my $spaced_nicks      = join(" ", @normal_nick_names);
    $channel->command("VOICE $spaced_nicks");
}

Irssi::command_bind('v', 'cmd_massvoice');
