// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.

// 256 rows of 512-pixels (32 * 16-bit words)
// @SCREEN (0x4000)
// 1=black, 0=white

// @KBD
// 0 = no key, otherwise keypress

(MAIN)

    // R3 = main
    @MAIN
    D = A
    @3
    M = D
    
    @KBD
    D = M

    // if (pressed) {
    @ISNOTPRESSED
    D ; JEQ

    (ISPRESSED)
    // R2=black
    @0
    D = A
    @2
    M = D - 1

    // Will return to main
    @SETCOLOUR
    0; JMP

    (ISNOTPRESSED)

    // R2=white
    @0
    D = A
    @2
    M = D

    // Will return to main
    @SETCOLOUR
    0; JMP

// Just in case!
(HALT)
    @HALT
    0; JMP

(SETCOLOUR)

    // R0=256 * 32
    // R1=@SCREEN
    // (caller) R2=colour
    // (caller) R3=return
    // while (R0 > 0) {
    //   *R1 = R2
    //   R1++
    //   R0--
    // }

    // R0=256*32
    @8192
    D = A
    @0
    M = D

    // R1=@SCREEN
    @SCREEN
    D = A
    @1
    M = D

    (SETCOLOURLOOP)

    // while (R0 > 0) {
    @0
    D = M
    @SETCOLOUREND
    D ; JLE 

    // *R1 = R3
    @2
    D = M
    @1
    A = M
    M = D

    // R1++
    @1
    D = M + 1
    M = D

    // R0--
    @0
    D = M - 1
    M = D

    // end block
    @SETCOLOURLOOP
    0; JMP

    (SETCOLOUREND)

    @3
    A = M
    0; JMP
