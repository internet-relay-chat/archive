use strict;
use warnings;
use Irssi;
use Irssi::Irc;

sub cmd_unfuck {
    my @windows = Irssi::windows();
    foreach my $window (@windows) {
        next if $window->{immortal};
        $window->{active}->{topic_by} ? next : $window->destroy;
    }
}

Irssi::command_bind('unfuck',  'cmd_unfuck');