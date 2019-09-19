# Amir Accounting Software

Amir is an accounting software mostly focused on businesses based in Iran.

![Screenshot](http://www.freeamir.com/images/thumb/c/cd/Win1.png/727px-Win1.png)

## Requirements

* python3
* pip3 (python-pip3)
* setuptools
* python3-gi gettext python3-passlib python3-cairocffi python3-cairosvg python3-pdfrw

to install requirements simply run below commands:

```bash
git clone https://github.com/Jooyeshgar/amir.git
cd amir
sudo apt install python3-pip
pip3 install -r requirements.txt
sudo apt install python3-setuptools python3-gi gettext python3-passlib python3-cairocffi python3-cairosvg python3-pdfrw
```

## Installation

### From source

```bash
sudo python3 setup.py install
```

### Ubuntu

Deb package for the latest version is available in [Launchpad](https://launchpad.net/amir/0.1/0.1/+download/amir_0.2_all.deb) 

### Windows

Windows installer for the latest version is available [here](https://github.com/Jooyeshgar/amir/releases/download/v0.2.0/Amir-0.2.0-win32-setup.exe)

## Run

Run `amir` command in terminal.

```bash
amir
```

Default username is `root` and password should be empty.

## Development

To start development and contributing install with below commands:

```bash
git clone https://github.com/Jooyeshgar/amir.git
cd amir
sudo python3 setup.py develop
```

## Documentation

To generate documentations first install [doxygen](http://www.doxygen.org/)

```bash
git clone https://github.com/Jooyeshgar/amir.git
cd amir/doc
make all
```

## Author

Amir is developed by [Jooyeshgar](https://www.jooyeshgar.com)

## License

Amir is licensed under the GNU Genral Public License Version 3.0
