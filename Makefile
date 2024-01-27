PYTHON_OK := $(shell python --version 2>&1)
PYTHON3_OK := $(shell python3 --version 2>&1)
PYINSTALLER_OK := $(shell pyinstaller --version)
ifeq ('$(PYTHON_OK)','')
	ifeq ('$(PYTHON3_OK)','')
    	$(error package 'python' or 'python3' not found)
	endif
endif
ifeq ('$(PYINSTALLER_OK)','')
    $(error package 'pyinstaller' not found)
endif

install:
	@echo "Beginning Jutsu installation"
	rm -rf installer
	mkdir installer && cd installer && \
	pyinstaller --onefile ../code/driver.py -n jutsu
	sudo mv installer/dist/jutsu /usr/local/bin/
	rm -rf installer
	@echo "Jutsu installed in /usr/local/bin"
	@echo "Installation Completed"

test-build:
	@echo "Test Jutsu Build"
	@find ./tests -type f -name '*.ju' -exec jutsu {} \; 


ifeq ('$(PYTHON3_OK)','')
test:
	@echo "Execute Full Jutsu Test Suite"
	@find ./tests/unit -type f -name '*.ju' -exec python code/driver.py {} \; 
test-unit:
	@echo "Execute Jutsu Unit Tests"
	@find ./tests/unit -type f -name '*.ju' -exec python code/driver.py {} \; 
test-error:
	@echo "Execute Jutsu Error Handling Tests"
	@find ./tests/error_handling -type f -name '*.ju' -exec python code/driver.py {} \; 
	
else
test:
	@echo "Execute Full Jutsu Test Suite"
	@find ./tests/unit -type f -name '*.ju' -exec python3 code/driver.py {} \; 
test-unit:
	@echo "Execute Jutsu Unit Tests"
	@find ./tests/unit -type f -name '*.ju' -exec python3 code/driver.py {} \; 
test-error:
	@echo "Execute Jutsu Error Handling Tests"
	@find ./tests/error_handling -type f -name '*.ju' -exec python3 code/driver.py {} \; 
endif
