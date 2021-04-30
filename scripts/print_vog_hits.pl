use strict;

my $f = shift || die "Genbank file";

# silently exit if the file doesn't exist, because who cares!
if (! -e $f) {exit(0)}

# phispy/GCA_00000/GCA_000006665/VOGS/GCA_000006665.1_ASM666v1_VOGS_phage.gbk.gz
my $out = $f;
$out =~ s/_VOGS_phage.gbk.gz/_VOG_hits.txt.gz/;
if (-e $out) {die "$out already exists"}

if (index($f, ".gz") > 0) {
	open(IN, "gunzip -c $f |") || die "$! $f";
}
else {
	open(IN, $f) || die "$! $f";
}
my $pp;
open(OUT, "| gunzip -c - > $out") || die "$! $out";
while (<IN>) {
	if (index($_, "LOCUS") == 0) {
		my @a=split /\s+/;
		$pp=$a[1];
	}
	if (index($_, "/phmm=") > 0) {
		s/^.*phmm=//;
		s/:/\t/;
		s/"//g;
		print join("\t", $f, $pp, $_);
		print OUT join("\t", $f, $pp, $_);
	}
}
close IN;
close OUT;
