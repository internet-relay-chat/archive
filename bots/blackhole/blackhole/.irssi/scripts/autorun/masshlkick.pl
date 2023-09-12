use strict;
use Irssi;
use Irssi::Irc;

our $VERSION = '1.0';
our %IRSSI = (
    authors     => 'acidvegas',
    contact     => 'acidvegas@supernets.org',
    name        => 'MassHLKick',
    description => 'A script to kick people who mass hilight on a channel.',
    license     => 'ISC',
    url         => 'http://github.com/acidvegas/irssi',
);

sub sig_public {
  my ($server, $msg, $nick, $address, $target) = @_;
  my $count;
  my $channel = $server->channel_find($target);
  my $max_num_nicks=Irssi::settings_get_int('mass_hilight_threshold');
  while ($msg =~ /([\]\[\\`_{|}\w^-][\]\[\\`_{|}\w\d^-]*)/g) {
      if ($channel->nick_find($1)) {
          $count++;
      }
  }
  if ($count > $max_num_nicks) {
      $channel->command("kick $target $nick ENTER THE VOID");
  }
}

Irssi::signal_add_first('message public', 'sig_public');
Irssi::settings_add_int('misc','mass_hilight_threshold', 5);
