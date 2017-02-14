import re


# logic required for building URLs and such
class UrlBuilder:
    qualified_regex = re.compile(r'^https?://[^\s]+$')
    domain_relative_regex = re.compile(r'^/[^\s]+$')
    domain_regex = re.compile(r'^(?P<domain>https?://[^/\s]+)/?')

    # given current url and url shard, build fully qualified url
    @staticmethod
    def build_qualified(original, shard):

        # check already fully qualified url
        if UrlBuilder.qualified_regex.match(shard):
            return shard

        # get domain
        domain = UrlBuilder.domain_regex.match(original).group('domain')

        # build domain relative url
        if UrlBuilder.domain_relative_regex.match(shard):
            return domain + shard

        # build context relative url
        return original + shard
