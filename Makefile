PYTHON_OK := $(shell python --version 2>&1)
PYINSTALLER_OK := $(shell pyinstaller --version)
ifeq ('$(PYTHON_OK)','')
    $(error package 'python' not found)
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

test:
	@echo "Test Jutsu Build"
	@find ./tests -type f -name '*.ju' -exec jutsu {} \; 
	
