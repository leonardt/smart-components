import setuptools

setuptools.setup(
    name="onyx_sram_subsystem",
    version="0.0.1",
    author="Lenny Truong",
    author_email="lenny@cs.stanford.edu",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "magma-lang",
        "fault"
    ]
)
