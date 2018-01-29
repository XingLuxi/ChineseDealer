#!/usr/bin/perl

# xml2moses.pl [OPTIONS] INPUT  OUTPUT
# ------------------------------------
# INPUT is an unzipped XML file from 
# http://www.linguatools.org/tools/corpora/wikipedia-parallel-titles-corpora/.
# which name must match the following pattern:
#     wikititles-2014_<L1><L2>.xml
# where L1 and L2 are one of the following language designators: 
#     {ar,bg,cs,da,de,el,en,es,fa,fi,fr,hu,it,ja,ko,nl,pl,pt,ro,ru,sv,tr,zh}.
#
# OUTPUT is the base name of the two output files in Moses format. The two output
# files have the names: OUTPUT.<L1> and OUTPUT.<L2>.

# OPTIONS are:
# -include-redirects              Generate all bilingual permutations of titles and redirects (and
#                                 textlinks if option -include-textlinks is given, too). 
# -include-textlinks              Generate all bilingual permutations of titles and textlinks (and
#                                 redirects if option -include-redirects is given, too). 
# -exclude-categories-l1 FILE     If the L1 part of a translation entry has one of 
#                                 the categories listed in FILE, the whole entry is
#                                 ignored. FILE must have one category per line.
# -exclude-categories-l2 FILE     Same as above, but for the L2 part.
# -only-categories-l1 FILE        Only translations are output that have one of the
#                                 categories listed in FILE in their L1 part. 
# -only-categories-l2 FILE        Same as above, but for the L2 part.
# -no-equal                       translations that are equal on both sides are 
#                                 ignored
# -no-colon                       translations that contain a colon on either side are
#                                 ignored
# -no-numbers                     translations that contain a number on either side are
#                                 ignored
# -check-unicode-range            This option is useful only for certain pairs of L1
#                                 and L2. It checks if all characters on each side
#                                 of a translation belong to the unicode range of their
#                                 respective language script. There are the following
#                                 scripts: - Arabic (ar,fa)
#                                          - Cyrillic (bg,ru)
#                                          - Greek (el)
#                                          - CJK (ja,ko,zh)
#                                          - Latin (cs,da,de,en,es,fi,fr,hu,it,nl,pl,pt,ro,sv,tr)
#                                 For instance the following translation would be ignored
#                                 if L1=ar and L2=en:
#                                    Subway <> Subway
#                                 whereas the next one will be output:
#                                    سب واي <> Subway
#
# Output will be two files in Moses format (one entry per line, both output
# files have the same number of lines). If name of input file is
#    wikititles-2014_<L1><L2>.xml
# then the two output files
#    wikititles-2014_<L1><L2>.<L1>
#    wikititles-2014_<L1><L2>.<L2>
# are generated.
#
# (C) 2014 peter.kolb@linguatools.org
##############################################################################
use strict;
use utf8;
use Encode;
use open ':encoding(UTF-8)'; # protect against Malformed UTF-8 character (fatal)
binmode STDOUT => ':utf8';
binmode STDIN => ':utf8';
binmode STDERR => ':utf8';

# script groups
# =============
# --- ar, fa ---
# Arabic, U+0600 bis U+06FF
# Arabic Supplement, 0750 bis 077F
# Arabisch, erweitert-A (engl. Arabic Extended-A, U+08A0 bis U+08FF)
# Arabic Presentation Forms-A, U+FB50 bis U+FDFF
# Arabic Presentation Forms-B, U+FE70 bis U+FEFF
# Arabic Mathematical Alphabetic Symbols, U+1EE00 bis U+1EEFF
# Syriac, 0700 bis 074F
my $arabic = "[\x{0600}-\x{06FF}\x{0750}-\x{077F}\x{08A0}-\x{08FF}\x{FB50}-\x{FDFF}\x{FE70}-\x{FEFF}\x{1EE00}-\x{1EEFF}\x{0700}-\x{074F}]";

# --- bg, ru ---
# Cyrillic: U+0400–U+04FF
# Cyrillic Supplement: U+0500–U+052F
# Cyrillic Extended-A: U+2DE0–U+2DFF
# Cyrillic Extended-B: U+A640–U+A69F
# Phonetic Extensions: U+1D2B, U+1D78, 2 Cyrillic characters
my $cyrillic = "[\x{0400}-\x{04FF}\x{0500}-\x{052F}\x{2DE0}-\x{2DFF}\x{A640}-\x{A69F}\x{1D2B}\x{1D78}]";

# --- el ---
# U+0370–U+03FF Greek & Coptic
# U+1F00–U+1FFF Greek Extended
my $greek = "[\x{0370}-\x{03FF}\x{1F00}-\x{1FFF}]";
 
# --- ja, ko, zh ---
# 4e00-9fbf, 3040-309f and 30a0-30ff
my $cjk = "[\x{4e00}-\x{9fbf}\x{3040}-\x{309f}\x{30a0}-\x{30ff}]";

# --- all others ---
# Basic Latin, 0000–007F
# Latin-1 Supplement, 0080–00FF
# Latin Extended-A, 0100–017F
# Latin Extended-B, 0180–024F
# Phonetic Extensions, 1D00–1D7F
# Phonetic Extensions Supplement, 1D80–1DBF
# Latin Extended Additional, 1E00–1EFF
# Superscripts and Subscripts, 2070-209F
# Letterlike Symbols, 2100–214F
# Number Forms, 2150–218F
# Latin Extended-C, 2C60–2C7F
# Latin Extended-D, A720–A7FF
# Latin Extended-E, AB30–AB6F
# Alphabetic Presentation Forms (Latin ligatures) FB00–FB4F
# Halfwidth and Fullwidth Forms (fullwidth Latin letters) FF00–FFEF
my $latin = "[\x{0000}-\x{007f}\x{0080}-\x{00FF}\x{0100}-\x{017F}\x{0180}-\x{024F}\x{1d00}-\x{1d7f}\x{1d80}-\x{1dbf}\x{1e00}-\x{1eff}\x{2070}-\x{209f}\x{2100}-\x{214f}\x{2150}-\x{218f}\x{2c60}-\x{2c7f}\x{a720}-\x{a7ff}\x{ab30}-\x{ab6f}\x{fb00}-\x{fb4f}\x{ff00}-\x{ffef}]";

my $include_redirects = 0;
my $include_textlinks = 0;
my $no_equal = 0;
my $no_colon = 0;
my $no_numbers = 0;
my $check_unicode = 0;
my $exclude_cats_l1 = 0;
my $exclude_cats_l2 = 0;
my $only_cats_l1 = 0;
my $only_cats_l2 = 0;
my $cats_l1_file;
my $cats_l2_file;
my $input_file;
my $output_base;

for(my $i = 0; $i <= $#ARGV; $i++){
    if( $ARGV[$i] eq "-include-redirects" ){ $include_redirects = 1; }
    elsif( $ARGV[$i] eq "-include-textlinks" ){ $include_textlinks = 1; }
    elsif( $ARGV[$i] eq "-exclude-categories-l1" ){ 
	$exclude_cats_l1 = 1; 
	$cats_l1_file = $ARGV[$i + 1];					    
	$i++;
    }
    elsif( $ARGV[$i] eq "-exclude-categories-l2" ){ 
	$exclude_cats_l2 = 1; 
	$cats_l2_file = $ARGV[$i + 1];
	$i++;					    
    }
    elsif( $ARGV[$i] eq "-only-categories-l1" ){ 
	$only_cats_l1 = 1; 
	$cats_l1_file = $ARGV[$i + 1];
	$i++;					    
    }
    elsif( $ARGV[$i] eq "-only-categories-l2" ){ 
	$only_cats_l2 = 1; 
	$cats_l2_file = $ARGV[$i + 1];
	$i++;					    
    }
    elsif( $ARGV[$i] eq "-no-equal" ){ $no_equal = 1; }
    elsif( $ARGV[$i] eq "-no-colon" ){ $no_colon = 1; }
    elsif( $ARGV[$i] eq "-no-numbers" ){ $no_numbers = 1; }
    elsif( $ARGV[$i] eq "-check-unicode-range" ){ $check_unicode = 1; }
    elsif( $ARGV[$i] =~ /^-/ ){
	print "WARNING: unrecognized option $ARGV[$i]\n";
    }
    else{
	if( $input_file eq "" ){
	    $input_file = $ARGV[$i];
	}elsif( $output_base eq "" ){
	    $output_base = $ARGV[$i];
	}else{
	    print "ERROR: too many INPUT/OUTPUT files:\n";
	    print "       INPUT is $input_file\n";
	    print "       OUTPUT is $output_base\n";
	    print "       What is \"$ARGV[$i]\"?\n";
	    usage();
	    exit;
	}
    }
}

# input file
my $l1; my $l2;
if( $input_file eq "" ){
    print "ERROR: no input file!\n";
    usage();
    exit;
}
if( $output_base eq "" ){
    print "ERROR: no output name!\n";
    usage();
    exit;
}
if( $input_file =~ /wikititles-2014_(..)(..)\.xml$/ ){
    $l1 = $1;
    $l2 = $2;
}else{
    print "ERROR: input file does not match the pattern wikititles-2014_<L1><L2>.xml\n";
    print "       where <L1> and <L2> one of {ar,bg,cs,da,de,el,en,es,fa,fi,fr,hu,it,ja,ko,nl,pl,pt,ro,ru,tr,zh}.\n";
    exit;    
}

# open output files
my $output_l1 = $output_base . "." . $l1;
my $output_l2 = $output_base . "." . $l2;
open(OUT1, ">$output_l1") or die "Could not write $output_l1\n";
open(OUT2, ">$output_l2") or die "Could not write $output_l2\n";

my %CATS_L1;
if( $cats_l1_file ne "" ){
    read_categories($cats_l1_file, \%CATS_L1);
}
my %CATS_L2;
if( $cats_l2_file ne "" ){
    read_categories($cats_l2_file, \%CATS_L2);
}

open(XML, "<$input_file") or die "Could not read $input_file\n";
my $id; my $t_in = 0; my $t_out = 0;
my $filt_equal = 0; my $filt_colon = 0; my $filt_number = 0; my $filt_code = 0;
my $excl1 = 0; my $excl2 = 0;
while(<XML>){
    chomp;
    if( /<translation id="([0-9]+)">/ ){
	# -----------------------------------
	# read <translation>...</translation>
	# -----------------------------------
	$id = $1;
	$t_in++;
	my $translation = "";
	do{
	    $_ = <XML>;
	    chomp;
	    $translation = $translation . $_;
	}while( $_ !~ /<\/translation>/ );
	# L1 entries
	my %ENTRIES_L1;
	# title L1
	if( $translation =~ /<entry lang="$l1">(.+?)<\/entry>/ ){
	    $ENTRIES_L1{$1} = 1;
	}else{
	    print "WARNING: id=$id: no entry for $l1 found!\n";
	}
	# redirects L1
	my @redirects_l1;
	if( $translation =~ /<redirects lang="$l1">(.+?)<\/redirects>/ ){
	    my $r = $1;
	    @redirects_l1 = $r =~ /<redirect>(.+?)<\/redirect>/g;
	}
	# textlinks L1
	my @textlinks_l1;
	if( $translation =~ /<textlinks lang="$l1">(.+?)<\/textlinks>/ ){
	    my $t = $1;
	    @textlinks_l1 = $t =~ /<textlink>(.+?)<\/textlink>/g;
	}
	# categories L1
	my @cats_l1;
	if( $translation =~ /<categories lang="$l1">(.+?)<\/categories>/ ){
	    my $cats = $1;
	    @cats_l1 = $cats =~ /<category>(.+?)<\/category>/g;
	}
	# L2 entries
	my %ENTRIES_L2;
	# title L2
	if( $translation =~ /<entry lang="$l2">(.+?)<\/entry>/ ){
	    $ENTRIES_L2{$1} = 1;
	}else{
	    print "WARNING: id=$id: no entry for $l2 found!\n";
	}
	# redirects L2
	my @redirects_l2;
	if( $translation =~ /<redirects lang="$l2">(.+?)<\/redirects>/ ){
	    my $r = $1;
	    @redirects_l2 = $r =~ /<redirect>(.+?)<\/redirect>/g;
	}
	# textlinks L2
	my @textlinks_l2;
	if( $translation =~ /<textlinks lang="$l2">(.+?)<\/textlinks>/ ){
	    my $t = $1;
	    @textlinks_l2 = $t =~ /<textlink>(.+?)<\/textlink>/g;
	}
	# categories L2
	my @cats_l2;
	if( $translation =~ /<categories lang="$l2">(.+?)<\/categories>/ ){
	    my $cats = $1;
	    @cats_l2 = $cats =~ /<category>(.+?)<\/category>/g;
	}
	# ------
	# FILTER
	# ------
	# exclude categories
	if( $exclude_cats_l1 == 1 ){
	    my $ignore = 0;
	    foreach my $c ( @cats_l1 ){
		if( exists($CATS_L1{$c}) ){
		    $ignore = 1;
		    $excl1++;
		    last;
		}
	    }
	    next if( $ignore == 1 );
	}
	if( $exclude_cats_l2 == 1 ){
	    my $ignore = 0;
	    foreach my $c ( @cats_l2 ){
		if( exists($CATS_L2{$c}) ){
		    $ignore = 1;
		    $excl2++;
		    last;
		}
	    }
	    next if( $ignore == 1 );
	}
	# only categories
	if( $only_cats_l1 == 1 ){
	    my $ignore = 1;
	    foreach my $c ( @cats_l1 ){
		if( exists($CATS_L1{$c}) ){
		    $ignore = 0;
		    last;
		}
	    }
	    next if( $ignore == 1 );
	}
	if( $only_cats_l2 == 1 ){
	    my $ignore = 1;
	    foreach my $c ( @cats_l2 ){
		if( exists($CATS_L2{$c}) ){
		    $ignore = 0;
		    last;
		}
	    }
	    next if( $ignore == 1 );
	}
	# include redirects
	if( $include_redirects == 1 ){
	    foreach my $r ( @redirects_l1 ){
		$ENTRIES_L1{$r} = 1;
	    }
	    foreach my $r ( @redirects_l2 ){
		$ENTRIES_L2{$r} = 1;
	    }
	}
	# include textlinks
	if( $include_textlinks == 1 ){
	    foreach my $t ( @textlinks_l1 ){
		next if( $t =~ /^\s*$/ );
		$ENTRIES_L1{$t} = 1;
	    }
	    foreach my $t ( @textlinks_l2 ){
		next if( $t =~ /^\s*$/ );
		$ENTRIES_L2{$t} = 1;
	    }
	}
	# ------
	# OUTPUT
	# ------
	foreach my $e1 ( keys %ENTRIES_L1 ){
	    foreach my $e2 ( keys %ENTRIES_L2 ){
		my $output = 1;
		if( $no_equal == 1 && $e1 eq $e2 ){
		    $output = 0;
		    $filt_equal++;
		}
		if( $no_colon == 1 && ($e1 =~ /\:/ || $e2 =~ /\:/ ) ){
		    $output = 0;
		    $filt_colon++;
		}
		if( $no_numbers == 1 && ($e1 =~ /[0-9]/ || $e2 =~ /[0-9]/ ) ){
		    $output = 0;
		    $filt_number++;
		}
		if( $check_unicode == 1 ){
		    if( check_unicode($e1, $e2) == 0 ){
			$output = 0;
			$filt_code++;
		    }
		}
		if( $output == 1 ){
		    print OUT1 "$e1\n";
		    print OUT2 "$e2\n";
		    $t_out++;
		}
	    }
	}
    }
}

print "wrote $t_out translations.\n";
if( $exclude_cats_l1 == 1 ){ print "Filtered $excl1 entries with exclude categories\n"; }
if( $exclude_cats_l2 == 1 ){ print "Filtered $excl2 entries with exclude categories\n"; }
if( $no_equal == 1 ){ print "Filtered $filt_equal equal translations\n"; }
if( $no_colon == 1 ){ print "Filtered $filt_colon translations with a colon\n"; }
if( $no_numbers == 1 ){ print "Filtered $filt_number translations with a number\n"; }
if( $check_unicode == 1 ){ print "Filtered $filt_code translations because of unicode range\n"; }
if( $id != $t_in ){
    print "WARNING: last translation.id is $id, but $t_in translations were read from XML.\n";
}

################################ 
# read category list from file #
################################ 
sub read_categories {
    my $file = shift;
    my $h_ref = shift;

    open(EIN, "<$file") or die "ERROR: Could not open file $file\n";
    while(<EIN>){
	chomp;
	next if( /^\s*$/ );
	$h_ref->{$_} = 1;
    }
    close(EIN);
    my $c = keys %CATS_L1;
    print "read $c categories from $cats_l1_file\n";
}

######################
sub get_script {
    my $lang = shift;

    if( $lang eq "ar" || $lang eq "fa" ){
	return $arabic;
    }
    if( $lang eq "bg" || $lang eq "ru" ){
	return $cyrillic;
    }
    if( $lang eq "el" ){
	return $greek;
    }
    if( $lang eq "ja" || $lang eq "ko" || $lang eq "zh" ){
	return $cjk;
    }
    return $latin;
}

###################
sub check_unicode {
    my $e1 = shift;
    my $e2 = shift;

    my $script1 = get_script($l1);
    my $script2 = get_script($l2);
    if( $script1 eq $script2 ){
	return 1;
    }

    if( $e1 =~ /$script2/ ){
	return 0;
    }
    if( $e2 =~ /$script1/ ){
	return 0;
    }

    return 1;
}

############
sub usage(){

print STDERR <<END;

xml2moses.pl [OPTIONS] INPUT  OUTPUT
OPTIONS:
  -include-redirects
  -include-textlinks
  -exclude-categories-l1 FILE
  -exclude-categories-l2 FILE
  -only-categories-l1 FILE
  -only-categories-l2 FILE
  -no-equal
  -no-colon
  -no-numbers
  -check-unicode-range 
END
}
