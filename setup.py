from setuptools import setup, find_packages

setup(
    name="storage-api-proxy",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "snowflake-connector-python",
        "aiosqlite",
        "httpx",
    ],
) 