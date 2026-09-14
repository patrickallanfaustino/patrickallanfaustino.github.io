source cena.vmd

set TAC "/home/patrickfaustino/software/tachyon/compile/linux-64-thr/tachyon"

set OPTS "-fullshade -aasamples 24 -skylight_samples 144 -raydepth 12 \
          -trans_vmd -shadow_filter_on -clamp \
          -res 3840 2160 -numthreads 32 -format PNG"

display projection Orthographic
display depthcue off
display shadows on
display ambientocclusion on
display aoambient 0.80
display aodirect 0.30
display antialias on
axes location Off

file mkdir frames

set mol [molinfo top]
set nf  [molinfo $mol get numframes]

for {set i 0} {$i < $nf} {incr i} {
    set base [format "frames/f%05d" $i]
    if {[file exists "$base.png"]} { continue }
    animate goto $i
    mol ssrecalc $mol
    display update
    render Tachyon $base "$TAC $OPTS %s -o %s.png"
    puts "frame $i / $nf"
}

exit
