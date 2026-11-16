// Box.asm
// Roll No: 2501730077   K = 77
// Box: starts at row 77, 20 rows tall (rows 77..96),
//      width = 16 * ((77 mod 4) + 1) = 16 * 2 = 32 pixels = 2 words, from left edge.
// First word address = SCREEN + 32*77 = 16384 + 2464 = 18848.
// Key pressed  -> box black.  No key -> box white (disappears).

(MAIN)
    @KBD
    D=M
    @PRESSED
    D;JNE          // any key pressed?

    @color         // no key: colour = 0 (white)
    M=0
    @DRAW
    0;JMP

(PRESSED)
    @color         // key: colour = -1 (all 16 bits black)
    M=-1

(DRAW)
    @SCREEN
    D=A
    @2464          // 32 * 77
    D=D+A
    @addr          // addr = start of row 77
    M=D
    @20
    D=A
    @rows          // rows left = 20
    M=D

(LOOP)
    @color
    D=M
    @addr
    A=M
    M=D            // word 0 of this row (pixels 0-15)
    A=A+1
    M=D            // word 1 of this row (pixels 16-31)

    @32
    D=A
    @addr
    M=D+M          // move down one row (+32 words)

    @rows
    M=M-1
    D=M
    @LOOP
    D;JGT          // repeat until 20 rows done

    @MAIN
    0;JMP          // forever