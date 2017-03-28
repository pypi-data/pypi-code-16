# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path

setup_requires = [ ]

# 패키지에 필요한 사전 설치 패키지 입니다.
install_requires = [
    'boto3'
]

# readme.rst불러오기
here = path.abspath( path.dirname( __file__ ) )
with open( path.join( here, 'README.rst' ), 'r' ) as f :
    readme = f.read()

dependency_links = [
]

setup(
        # 패키지 이름
        name='lambdAWS',
        # 패키지 버전 - 버전이 바뀌어야 pypi에 업로드 됩니다. 버전이 바뀌지 않으면 바뀐사항이 업로드 되지 않습니다.
        version='0.0.17',
        # 패키지 관련 홈페이지 주소
        url='https://bitbucket.org/indjdev/lambdaws',
        # 패키지의 라이센스
        license='MIT License',
        # 패키지에 대한 간략한 설명
        description='lambda에서 각종 AWS서비스를 사용하기 위한 래핑모듈',
        # 패키지에 대한 상세 설명을
        long_description=readme,
        # 패키지 제작자 정보
        author='wesky93',
        author_email='wesky93@gmail.com',
        # 업로드에 포함할 패키지들
        packages=[ "lambdAWS" ],
        include_package_data=True,
        # 위에 작성한 사전 설치 패키지
        install_requires=install_requires,

        setup_requires=setup_requires,
        dependency_links=dependency_links,
        # 자신의 패키지에 달 키워드 - 본인이 원하는 키워드로 자유롭게 달면 됩니다.
        keywords=[ 'aws', 'lambda', 's3', 'sns', 'dynamodb' ],
        # 패키지 분류 - 이건 pypi에 있는 분류에 맞춰 작성해야합니다. 아무것이나 넣었다간 빌드실패합니다.
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: MIT License',
        ]

)