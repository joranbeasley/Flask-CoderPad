![Demo Of Coderpad](docs/demo1.gif)

INSTALL
-------
`pip install git+git://github.com/joranbeasley/CoderPad#egg=CoderPad -U`

**Supports at least** Python2.7 and Python3.6 and i assume all versions between, it does not support 2.6!

**additionally requires** eventlet or some other backend supported by [Flask-Socketio](https://flask-socketio.readthedocs.io/en/latest/#requirements)

RUN THE SERVER
--------------
`serve-coderpad` note that this should be in the scripts folder of your python install

you can use the 

`setup-coderpad` command to configure your server (This should run automagically the first time you run the server)

WISHLIST
--------

* add support for languages other than python
* XSS injection in chat panel needs to be identified and fixed
* can we use angular for the editor page?
