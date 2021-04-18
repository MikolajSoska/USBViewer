import setuptools

requirements = []
with open('requirements.txt', 'r') as requirements_file:
    for line in requirements_file:
        line = line.strip()
        if line:
            requirements.append(line)

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='usb_viewer',
    version='1.0',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    python_requires='>=3.7',
    url='https://github.com/MikolajSoska/usb-viewer',
    author='Mikołaj Soska',
    author_email='mikolaj.soska1@gmail.com',
    description='Forensic tool for viewing USB devices history and details.',
    long_description=long_description
)
