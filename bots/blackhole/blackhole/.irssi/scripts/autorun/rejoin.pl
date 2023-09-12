use Irssi;
use Irssi::Irc;
use strict;

my $delay  = 1;
my $acttag = 0;
my @tags;

sub rejoin {
    my ( $data ) = @_;
    my ( $tag, $servtag, $channel, $pass ) = split( / +/, $data );
    my $server = Irssi::server_find_tag( $servtag );
    $server->send_raw( "JOIN $channel $pass" ) if ( $server );
    Irssi::timeout_remove( $tags[$tag] );
}

sub event_rejoin_kick {
    my ( $server, $data ) = @_;
    my ( $channel, $nick ) = split( / +/, $data );
    return if ( $server->{ nick } ne $nick );
    my $chanrec = $server->channel_find( $channel );
    my $password = $chanrec->{ key } if ( $chanrec );
    my $rejoinchan = $chanrec->{ name } if ( $chanrec );
    my $servtag = $server->{ tag };
    Irssi::print "Rejoining $rejoinchan in $delay seconds.";
    $tags[$acttag] = Irssi::timeout_add( $delay * 1000, "rejoin", "$acttag $servtag $rejoinchan $password" );
    $acttag++;
    $acttag = 0 if ( $acttag > 60 );
}

Irssi::signal_add('event kick', 'event_rejoin_kick');