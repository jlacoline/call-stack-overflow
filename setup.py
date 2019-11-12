from setuptools import setup

setup(
    name='call-stackoverflow',
    version='0.1.0',
    description='Just let stackoverflow.com do your job',
    url='https://github.com/jlacoline/call-stack-overflow',
    author='https://github.com/jlacoline',
    author_email='jean.lacoline@gmail.com',
    license='WTFPL',
    keywords='stackoverflow',
    packages=["callstackoverflow"],
    install_requires=['requests', 'google', 'beautifulsoup4']
)
