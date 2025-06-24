from setuptools import setup, find_packages

setup(
    name="glass-explorer",
    version="1.1.0",
    author="Rodopqsi",
    description="Explorador de archivos moderno en consola con controles multimedia, wifi y extras.",
    packages=find_packages(),
    install_requires=[
        "textual>=0.38.0",
        "screen-brightness-control>=0.14.1",
        "pywifi>=1.1.11",
        "Pillow>=10.0.0"
    ],
    entry_points={
        "console_scripts": [
            "glass-explorer = glass_explorer.main:main"
        ]
    },
    include_package_data=True,
    python_requires='>=3.10',
)