# VHS tape — generates the README demo GIF automatically.
#
#   1. Install VHS:  https://github.com/charmbracelet/vhs
#      (brew install vhs   |   go install github.com/charmbracelet/vhs@latest)
#   2. From the repo root run:  vhs demo/demo.tape
#   3. Output lands at demo/demo.gif — embed it at the top of README.md

Output demo/demo.gif

Set FontSize 15
Set Width 860
Set Height 560
Set Padding 12
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful
Set TypingSpeed 0

Hide
Type "bash demo/demo.sh"
Enter
Show

# demo.sh paces itself (~25s); just wait for it to finish.
Sleep 30s
