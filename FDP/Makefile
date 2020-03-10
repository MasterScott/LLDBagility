.PHONY: all clean

all:
	mkdir -p build
	cd build/ && \
		cmake .. && \
		make
	cp build/lib/libFDP.dylib PyFDP/PyFDP/ 2>/dev/null || true
	cp build/lib/libFDP.so PyFDP/PyFDP/ 2>/dev/null || true

clean:
	rm -rf build/
	rm -rf PyFDP/PyFDP/libFDP.dylib
	rm -rf PyFDP/PyFDP/libFDP.so
