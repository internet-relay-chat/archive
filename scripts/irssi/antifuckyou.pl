# AntiFuckYou (SAJOIN Auto-Part Script)
# Developed by acidvegas in Perl
# http://github.com/acidvegas/irssi
# antifuckyou.pl

use strict;
use Irssi;

sub anti_fuckyou {
  my ($server, $msg, $nick, $address, $target) = @_;
  if ($msg =~ /You were forced to join.*/) {
    my $rand = &getRandom();
    my $server_addr = $server->{real_address};
    if ($nick eq $server_addr) {
      $msg =~ s/.*\W(\w)/$1/;
      $server->command("PART #$msg");
    }
  }
}

Irssi::signal_add('message irc notice', 'anti_fuckyou');
