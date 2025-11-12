from setuptools import setup, find_packages


setup(
    name="personal_assistant",
    version="0.1",
    packages=["personal_assistant"],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'personal_assistant = personal_assistant.main:main',
        ]
    }
)