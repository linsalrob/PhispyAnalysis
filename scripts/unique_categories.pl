use strict;

my $count; my %gbf;
while (<>) {
	chomp;
	my @a=split /\t/;
	next unless ($a[2]);
	$gbf{$a[0]}=$a[1];
	if ($a[2]) {
		$count->{$a[0]}->{$a[2]}++;
	}
}

foreach my $ass (keys %gbf) {
	my @most = sort {$count->{$ass}->{$b} <=> $count->{$ass}->{$a}} keys %{$count->{$ass}};
	print join("\t", $ass, $gbf{$ass}, $most[0]), "\n";
}
