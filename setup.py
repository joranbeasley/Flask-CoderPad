from setuptools import setup
from CoderPad import  __version__
setup(
    name='CoderPad',
    version=__version__,
    packages=['CoderPad', 'CoderPad.views', 'CoderPad.coderpad_socket_server'],
    url='',
    license='',
    include_package_data=True, # looks in MANIFEST.in
    entry_points = {
        'console_scripts': [
            'serve-coderpad=CoderPad.serve_coderpad:main',
            'setup-coderpad=CoderPad.configure:DoSetupCoderpadSite',
            'configure-coderpad=CoderPad.configure:DoSetupCoderpadSite'
        ],
    },
    install_requires=['flask','Flask-SQLAlchemy','Flask-Socketio','Flask-Login'],
    author='Joran Beasley',
    author_email='joranbeasley@gmail.com',
    description='Interactive Shared Coding Environment For Interviews'
)
