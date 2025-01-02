CLFAGS = -Wall -shared -m64

TARGET = eco_calc.dll
SRC = eco_calc.c

eco_calc.dll: eco_calc.c
	$(CC) $(CLFAGS) -o $(TARGET) $(SRC)

clean:
	rm -f eco_calc.dll