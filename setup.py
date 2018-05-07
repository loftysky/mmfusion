from setuptools import setup, find_packages

setup(
    name='mmfusion',
    version='0.1.dev0',
    description="Lofty Sky\'s Fusion tools",
    url='http://github.com/loftysky/mmfusion',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    include_package_data=True,
    
    author='Mike Boers',
    author_email='mmfusion@mikeboers.com',
    license='BSD-3',
    
    entry_points={
        'console_scripts': '''
        
            mmfusion-submit-render = mmfusion.render:submit_main
            mmfusion-fix-pathmap = mmfusion.pathmap:fix_main

            fusion = mmfusion.launcher:main
            
        ''',
    },
    
)
