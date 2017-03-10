# -*- coding: utf-8

from __future__ import unicode_literals

from .base import BaseDandelionRequest, BaseDandelionParamsRequest


class EntityExtraction(BaseDandelionParamsRequest):
    """
    This is a named entity extraction & linking API that performs very well even on short texts, on which many other
    similar services do not. It currently works on English, French, German, Italian, Portuguese and Spanish texts.
    With this API you will be able to automatically tag your texts, extracting Wikipedia entities and enriching your
    data.

    https://dandelion.eu/docs/api/datatxt/nex/v1/
    """

    def __init__(self, **params):
        """
        :param params:
            text|url|html|html_fragment = These parameters define how you send text to the Entity Extraction API.
                Only one of them can be used in each request, following these guidelines:
                - use "text" when you have plain text that doesn't need any pre-processing;
                - use "url" when you have an URL and you want the Entity Extraction API to work on its main content;
                  it will fetch the URL for you, and use an AI algorithm to extract the relevant part of the document
                  to work on; in this case, the main content will also be returned by the API to allow you to properly
                  use the annotation offsets;
                - use "html" when you have an HTML document and you want the Entity Extraction API to work on its main
                  content, similarly to what the "url" parameter does.
                - use "html_fragment" when you have an HTML snippet and you want the Entity Extraction API to work on
                  its content. It will remove all HTML tags before analyzing it.
                | required
                | Type: string
            lang = The language of the text to be annotated; currently English, French, German, Italian, Portuguese and
                Spanish are supported.
                | optional
                | Type: string
                | Default value: auto
                | Accepted values: de | en | es | fr | it | pt | auto
            min_confidence = The threshold for the confidence value; entities with a confidence value below this
                threshold will be discarded. Confidence is a numeric estimation of the quality of the annotation, which
                ranges between 0 and 1. A higher threshold means you will get less but more precise annotations.
                A lower value means you will get more annotations but also more erroneous ones.
                | optional
                | Type: float
                | Default value: 0.6
                | Accepted values: 0.0 .. 1.0
            min_length = With this parameter you can remove those entities having a spot shorter than a minimum length.
                | optional
                | Type: integer
                | Default value: 2
                | Accepted values: 2 .. +inf
            social.hashtag = With this parameter you enable special hashtag parsing to correctly analyze tweets and
                facebook posts.
                | optional
                | Type: boolean
                | Default value: False
                | Accepted values: True | False
            social.mention = With this parameter you enable special mention parsing to correctly analyze tweets and
                facebook posts.
                | optional
                | Type: boolean
                | Default value: False
                | Accepted values: True | False
            include = Returns more information on annotated entities:
                - "types" adds type information from DBpedia or dandelion. DBpedia types are extracted based on the
                  lang parameter (e.g. if lang=en, types are extracted from DBpedia english). Please notice that
                  different DBpedia instances may contain different types for the same resource;
                - "categories" adds category information from DBpedia/Wikipedia;
                - "abstract" adds the text of the Wikipedia abstract;
                - "image" adds a link to an image depicting the tagged entity, as well as a link to the image
                  thumbnail, served by Wikipedia. Please check the licensing terms of each image on Wikipedia before
                  using it in your app;
                - "lod" adds links to equivalent (sameAs) entities in Linked Open Data repositories or other websites.
                  It currently only supports DBpedia and Wikipedia;
                - "alternate_labels" adds some other names used when referring to the entity.
                | optional
                | Type: comma-separated list
                | Default value: <empty string>
                | Accepted values: types, categories, abstract, image, lod, alternate_labels
                | Example: include=types,lod
            extra_types = Returns more information on annotated entities:
                - "phone" enables matching of phone numbers;
                - "vat" enables matching of VAT IDs (Italian only).
                Note that these parameters require the country parameter to be set, and VAT IDs will work only for
                Italy.
                | optional
                | Type	comma-separated list
                | Default value: <empty string>
                | Accepted values: phone, vat
                | Example: extra_types=phone,vat
            country = This parameter specifies the country which we assume VAT and telephone numbers to be coming from.
                This is important to get correct results, as different countries may adopt different formats.
                | optional
                | Type: string
                | Default value: <empty string>
                | Accepted values: AD, AE, AM, AO, AQ, AR, AU, BB, BR, BS, BY, CA, CH, CL, CN, CX, DE, FR, GB, HU, IT,
                                   JP, KR, MX, NZ, PG, PL, RE, SE, SG, US, YT, ZW
            custom_spots = Enable specific user-defined spots to be used when annotating the text.
                You can define your own spots or use someone else's ones if they shared the spots-ID with you.
                | optional
                | Type	string
                | Default value: <empty string>
                | Accepted values: any valid spots-ID

        """

        keys_allowed = [
            'text', 'url', 'html', 'html_fragment',
            'lang',
            'min_confidence',
            'min_length',
            'social.hashtag',
            'social.mention',
            'include',
            'extra_types',
            'country',
            'custom_spots',
        ]
        keys_unique = [
            ['text', 'url', 'html', 'html_fragment'],
        ]

        super(EntityExtraction, self).__init__(keys_allowed=keys_allowed, keys_unique=keys_unique, **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datatxt', 'nex', 'v1'),
            method='post'
        )


class TextSimilarity(BaseDandelionParamsRequest):
    """
    This API is a semantic sentence similarity API optimized on short sentences.
    With this API you will be able to compare two sentences and get a score of their semantic similarity.
    It works even if the two sentences don't have any word in common.

    https://dandelion.eu/docs/api/datatxt/sim/v1/
    """

    def __init__(self, **params):
        """
        :param params:
            text1|url1|html1|html_fragment1 = These parameters define how you send to the Text Similarity API the first
                text you want to compare. Only one of them can be used in each request, following these guidelines:
                - use "text" when you have plain text that doesn't need any pre-processing;
                - use "url" when you have an URL and you want the Text Similarity API to work on its main content;
                  it will fetch the URL for you, and use an AI algorithm to extract the relevant part of the document
                  to work on; in this case, the main content will also be returned by the API to allow you to properly
                  use the annotation offsets;
                - use "html" when you have an HTML document and you want the Text Similarity API to work on its main
                  content, similarly to what the "url" parameter does.
                - use "html_fragment" when you have an HTML snippet and you want the Text Similarity API to work on its
                  content. It will remove all HTML tags before analyzing it.
                | required
                | Type: string
            text2|url2|html2|html_fragment2 = These parameters define how you send to the Text Similarity API the
                second text you want to compare, in the same way as the text1|url1|html1|html_fragment1 parameters.
                | required
                | Type: string
            lang = The language of the texts to be compared; currently English, French, German, Italian, Portuguese and
                Spanish are supported. Leave this parameter out to let the Text Similarity API automatically detect the
                language for you.
                | optional
                | Type: string
                | Default value: auto
                | Accepted values: de | en | es | fr | it | pt | auto
            bow = The Text Similarity API normally uses a semantic algorithm for computing similarity of texts.
                It is possible, however, to use a more classical syntactic algorithm where the semantic one fails.
                This can be done with this parameter.
                - "never" uses always the semantic algorithm;
                - "both_empty" uses the syntactic algorithm if both the two texts have no semantic information;
                - "one_empty" uses the syntactic algorithm if at least one of the two inputs have no semantic
                  information;
                - "always" uses always the syntactic algorithm.
                | optional
                | Type: string
                | Default value: never
                | Accepted values: always | one_empty | both_empty | never
            nex.min_confidence = The threshold for the confidence value; entities with a confidence value below this
                threshold will be discarded. Confidence is a numeric estimation of the quality of the annotation, which
                ranges between 0 and 1. A higher threshold means you will get less but more precise annotations.
                A lower value means you will get more annotations but also more erroneous ones.
                | optional
                | Type: float
                | Default value: 0.6
                | Accepted values: 0.0 .. 1.0
            nex.min_length = With this parameter you can remove those entities having a spot shorter than a minimum
                length.
                | optional
                | Type: integer
                | Default value: 2
                | Accepted values: 2 .. +inf
            nex.social.hashtag = With this parameter you enable special hashtag parsing to correctly analyze tweets and
                facebook posts.
                | optional
                | Type: boolean
                | Default value: False
                | Accepted values: True | False
            nex.social.mention = With this parameter you enable special mention parsing to correctly analyze tweets and
                facebook posts.
                | optional
                | Type: boolean
                | Default value: False
                | Accepted values: True | False
            nex.include = Returns more information on annotated entities:
                - "types" adds type information from DBpedia or dandelion. DBpedia types are extracted based on the
                  lang parameter (e.g. if lang=en, types are extracted from DBpedia english). Please notice that
                  different DBpedia instances may contain different types for the same resource;
                - "categories" adds category information from DBpedia/Wikipedia;
                - "abstract" adds the text of the Wikipedia abstract;
                - "image" adds a link to an image depicting the tagged entity, as well as a link to the image
                  thumbnail, served by Wikipedia. Please check the licensing terms of each image on Wikipedia before
                  using it in your app;
                - "lod" adds links to equivalent (sameAs) entities in Linked Open Data repositories or other websites.
                  It currently only supports DBpedia and Wikipedia;
                - "alternate_labels" adds some other names used when referring to the entity.
                | optional
                | Type: comma-separated list
                | Default value: <empty string>
                | Accepted values: types, categories, abstract, image, lod, alternate_labels
                | Example: include=types,lod
            nex.extra_types = Returns more information on annotated entities:
                - "phone" enables matching of phone numbers;
                - "vat" enables matching of VAT IDs (Italian only).
                Note that these parameters require the country parameter to be set, and VAT IDs will work only for
                Italy.
                | optional
                | Type	comma-separated list
                | Default value: <empty string>
                | Accepted values: phone, vat
                | Example: extra_types=phone,vat
            nex.country = This parameter specifies the country which we assume VAT and telephone numbers to be coming
                from.
                This is important to get correct results, as different countries may adopt different formats.
                | optional
                | Type: string
                | Default value: <empty string>
                | Accepted values: AD, AE, AM, AO, AQ, AR, AU, BB, BR, BS, BY, CA, CH, CL, CN, CX, DE, FR, GB, HU, IT,
                                   JP, KR, MX, NZ, PG, PL, RE, SE, SG, US, YT, ZW
            nex.custom_spots = Enable specific user-defined spots to be used when annotating the text.
                You can define your own spots or use someone else's ones if they shared the spots-ID with you.
                | optional
                | Type	string
                | Default value: <empty string>
                | Accepted values: any valid spots-ID
        """

        keys_allowed = [
            'text1', 'url1', 'html1', 'html_fragment1',
            'text2', 'url2', 'html2', 'html_fragment2',
            'lang',
            'bow',
            'nex.min_confidence',
            'nex.min_length',
            'nex.social.hashtag',
            'nex.social.mention',
            'nex.include',
            'nex.extra_types',
            'nex.country',
            'nex.custom_spots',
        ]
        keys_unique = [
            ['text1', 'url1', 'html1', 'html_fragment1'],
            ['text2', 'url2', 'html2', 'html_fragment2'],
        ]

        super(TextSimilarity, self).__init__(keys_allowed=keys_allowed, keys_unique=keys_unique, **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datatxt', 'sim', 'v1'),
            method='post'
        )


class TextClassification(BaseDandelionParamsRequest):
    """
    This API classifies short documents into a set of user-defined classes. It's a very powerful and customizable tool
    for text classification, and defining your own models will take you just a couple of minutes.
    Curious? Read below how to call the Text Classification API, or discover how to define custom models.

    https://dandelion.eu/docs/api/datatxt/cl/v1/
    """

    def __init__(self, **params):
        """
        :param params:
            text|url|html|html_fragment = These parameters define how you send to the Text Classification API the text
                you want to classify. Only one of them can be used in each request, following these guidelines:
                - use "text" when you have plain text that doesn't need any pre-processing;
                - use "url" when you have an URL and you want the Text Classification API to work on its main content;
                  il will fetch the URL for you, and use an AI algorithm to extract the relevant part of the document
                  to work on; in this case, the main content will also be returned by the API to allow you to properly
                  use the annotation offsets;
                - use "html" when you have an HTML document and you want Text Classification API to work on its main
                  content, similarly to what the "url" parameter does.
                - use "html_fragment" when you have an HTML snippet and you want the Text Classification API to work on
                  its content. It will remove all HTML tags before analyzing it.
                | required
                | Type: string
            model = The unique ID of the model you want to use. If you want to learn how to manage your custom models,
                please refer to User-defined classifiers.
                | required
            min_score = return those categories that get a score above this threshold. There is not a gold-value for
                such parameter that works for every model, moreover it really depends on your use-case.
                Start experimenting with 0.25 and increase / decrease it depending on the results.
                | optional
                | Type: float
                | Default value: 0.0
                | Accepted values: 0.0 .. 1.0
            max_annotations = The Text Classification API uses the Entity Extraction API under the hood.
                With this parameter you can limit the number of annotations to be used for classifying the text, using
                only the top-most entities by their confidence.
                | optional
                | Type: integer
                | Default value: +inf
                | Accepted values: 1 .. +inf
            include = Returns more information about the classification process:
                - "score_details": we added this parameter for debug purposes: it will output, for each entity in the
                  model categories, a weight value that represents how much they have influenced the overall score of
                  their category. For each category, the weights sum up to 1.
                  Pay attention: This parameter can be used only by the model owner. You can share your models with
                  other users simply sending them the model ID, but they won't be able to use include=score_details.
                | optional
                | Type: string
                | Default value: <empty string>
                | Accepted values: score_details
                | Example: include=score_details
        """

        keys_allowed = [
            'text', 'url', 'html', 'html_fragment',
            'model',
            'min_score',
            'max_annotations',
            'include',
        ]
        keys_unique = [
            ['text', 'url', 'html', 'html_fragment'],
        ]

        super(TextClassification, self).__init__(keys_allowed=keys_allowed, keys_unique=keys_unique, **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datatxt', 'cl', 'v1'),
            method='post'
        )

    class UserDefinedClassifiers(BaseDandelionRequest):
        def create(self, data):
            return self._do_request(
                extra_url=('datatxt', 'cl', 'models', 'v1'),
                method='post',
                extra_dict={'data': data}
            )

        def read(self, id):
            return self._do_request(
                extra_url=('datatxt', 'cl', 'models', 'v1'),
                method='get',
                extra_dict={'id': id}
            )

        def update(self, id, data):
            return self._do_request(
                extra_url=('datatxt', 'cl', 'models', 'v1'),
                method='put',
                extra_dict={'id': id, 'data': data}
            )

        def delete(self, id):
            return self._do_request(
                extra_url=('datatxt', 'cl', 'models', 'v1'),
                method='delete',
                extra_dict={'id': id}
            )

        def list(self):
            return self._do_request(
                extra_url=('datatxt', 'cl', 'models', 'v1'),
                method='get'
            )


class LanguageDetection(BaseDandelionParamsRequest):
    """
    Language Detection API is a simple language identification API; it is a tool that may be useful when dealing with
    texts, so we decided to open it to all our users. It currently supports 96 languages.

    https://dandelion.eu/docs/api/datatxt/li/v1/
    """

    def __init__(self, **params):
        """
        :param params:
            text|url|html|html_fragment = These parameters define how you send to the Language Detection API the
                text for which you want the language to be recognized. Only one of them can be used in each request,
                following these guidelines:
                - use "text" when you have plain text that doesn't need any pre-processing;
                - use "url" when you have an URL and you want the Language Detection API to work on its main content;
                  it will fetch the URL for you, and use an AI algorithm to extract the relevant part of the document
                  to work on; in this case, the main content will also be returned by the API to allow you to properly
                  use the annotation offsets;
                - use "html" when you have an HTML document and you want the Language Detection API to work on its main
                  content, similarly to what the "url" parameter does.
                - use "html_fragment" when you have an HTML snippet and you want the Language Detection API to work on
                  its content. It will remove all HTML tags before analyzing it.
                | required
                | Type: string
            clean = Set this parameter to true if you want the text to be cleaned from urls, email addresses, hashtags,
                and more, before being processed.
                | optional
                | Type: boolean
                | Default value: False
                | Accepted values: True | False

        """

        keys_allowed = [
            'text', 'url', 'html', 'html_fragment',
            'clean',
        ]
        keys_unique = [
            ['text', 'url', 'html', 'html_fragment'],
        ]

        super(LanguageDetection, self).__init__(keys_allowed=keys_allowed, keys_unique=keys_unique, **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datatxt', 'li', 'v1'),
            method='post'
        )


class SentimentAnalysis(BaseDandelionParamsRequest):
    """
    This API analyses a text and tells whether the expressed opinion is positive, negative, or neutral.
    Given a short sentence, it returns a label representing the identified sentiment, along with a numeric score
    ranging from strongly positive (1.0) to extremely negative (-1.0).

    https://dandelion.eu/docs/api/datatxt/sent/v1/
    """

    def __init__(self, **params):
        """
        :param params:
            text|url|html|html_fragment = These parameters define how you send to the Sentiment Analysis API the text
                you want to analyze. Only one of them can be used in each request, following these guidelines:
                - use "text" when you have plain text that doesn't need any pre-processing;
                - use "url" when you have an URL and you want the Sentiment Analysis API to work on its main content;
                  it will fetch the URL for you, and use an AI algorithm to extract the relevant part of the document
                  to work on;
                - use "html" when you have an HTML document and you want the Sentiment Analysis API to work on its main
                  content, similarly to what the "url" parameter does.
                - use "html_fragment" when you have an HTML snippet and you want the Sentiment Analysis API to work on
                  its content. It will remove all HTML tags before analyzing it.
                | required
                | Type: string
            lang = The language of the text to be annotated; currently only English and Italian are supported.
                Leave this parameter out to let the Sentiment Analysis API automatically detect the language for you.
                | optional
                | Type: string
                | Default value: auto
                | Accepted values: en | it | auto
        """

        keys_allowed = [
            'text', 'url', 'html', 'html_fragment',
            'lang',
        ]
        keys_unique = [
            ['text', 'url', 'html', 'html_fragment'],
        ]

        super(SentimentAnalysis, self).__init__(keys_allowed=keys_allowed, keys_unique=keys_unique, **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datatxt', 'sent', 'v1'),
            method='post'
        )
