CC = gcc
CLFAGS = -shared -m64 -IC:\Users\maste\Documents\TerminalHome\Projects\Ecoacoustic-Calculator\eco_calc\ffmpeg-7.1-full_build-shared\include

eco_calc.dll: eco_calc.c
	$(CC) $(CLFAGS) -o $@ $^

clean:
	rm -f eco_calc.dll