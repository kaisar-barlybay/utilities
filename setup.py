import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
    name='utilities',
    version='0.1.12',
    author='Kaisar Barlybay',
    author_email='kaisar.barlybay.sse@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/kaisar-barlybay/utilities',
    project_urls={
        "Bug Tracker": "https://github.com/kaisar-barlybay/utilities/issues"
    },
    license='MIT',
    packages=['utilities', 'utilities.api'],
    install_requires=['Django>=4.0.3',
                      'mongoengine>=0.23.1',
                      'pymongo>=3.12.3',
                      'django-environ>=0.8.1',
                      'colorlog>=6.6.0',
                      'djangorestframework>=3.12.4',
                      'selenium>=4.1.3',
                      'sqlalchemy>=1.4.37',
                      'paramiko==2.11.0',
                      'spacy==3.3.0',
                      'nltk==3.7',
                      'pandas',
                      'langdetect>=1.0.9',
                      'translate-api>=4.9.5',
                      'translators>=5.4.2',
                      'deep-translator==1.9.1',
                      # 'ru-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.3.0/ru_core_news_sm-3.3.0-py3-none-any.whl',
                      # 'zh-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/zh_core_web_sm-3.3.0/zh_core_web_sm-3.3.0-py3-none-any.whl',
                      # 'en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.3.0/en_core_web_sm-3.3.0-py3-none-any.whl',
                      ],
)
