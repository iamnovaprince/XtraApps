# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example generates keyword ideas from a list of seed keywords."""


import argparse
import sys
from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException

# Location IDs are listed here: https://developers.google.com/adwords/api/docs/appendix/geotargeting
# and they can also be retrieved using the GeoTargetConstantService as shown
# here: https://developers.google.com/google-ads/api/docs/targeting/location-targeting
_DEFAULT_LOCATION_IDS = ["1023191"]  # location ID for New York, NY
# A language criterion ID. For example, specify 1000 for English. For more
# information on determining this value, see the below link:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#languages.
_DEFAULT_LANGUAGE_ID = "1000"  # language ID for English


# [START generate_keyword_ideas]
def main(
    client, customer_id, location_ids, language_id, keyword_texts, page_url
):
    keyword_plan_idea_service = client.get_service(
        "KeywordPlanIdeaService", version="v6"
    )
    keyword_competition_level_enum = client.get_type(
        "KeywordPlanCompetitionLevelEnum", version="v6"
    ).KeywordPlanCompetitionLevel
    keyword_plan_network = client.get_type(
        "KeywordPlanNetworkEnum", version="v6"
    ).GOOGLE_SEARCH_AND_PARTNERS

    gtc_service = client.get_service("GeoTargetConstantService", version="v6")
    locations = [
        gtc_service.geo_target_constant_path(location_id)
        for location_id in location_ids
    ]
    language = client.get_service(
        "LanguageConstantService", version="v6"
    ).language_constant_path(language_id)

    # Only one of these values will be passed to the KeywordPlanIdeaService
    # depending on whether keywords, a page_url or both were given.
    url_seed = None
    keyword_seed = None
    keyword_url_seed = None

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not keyword_texts and page_url:
        url_seed = client.get_type("UrlSeed", version="v6")
        url_seed.url = page_url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of strings.
    if keyword_texts and not page_url:
        keyword_seed = client.get_type("KeywordSeed", version="v6")
        keyword_seed.keywords.extend(keyword_texts)

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if keyword_texts and page_url:
        keyword_url_seed = client.get_type("KeywordAndUrlSeed", version="v6")
        keyword_url_seed.url = page_url
        keyword_url_seed.keywords.extend(keyword_texts)

    try:
        keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
            customer_id=customer_id,
            geo_target_constants=locations,
            include_adult_keywords=False,
            keyword_plan_network=keyword_plan_network,
            language=language,
            url_seed=url_seed,
            keyword_seed=keyword_seed,
            keyword_and_url_seed=keyword_url_seed,
        )

        for idea in keyword_ideas:
            competition_value = keyword_competition_level_enum.Name(
                idea.keyword_idea_metrics.competition
            )
            print(
                f'Keyword idea text "{idea.text}" has '
                f'"{idea.keyword_idea_metrics.avg_monthly_searches}" '
                f'average monthly searches and "{competition_value}" '
                "competition.\n"
            )
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
        # [END generate_keyword_ideas]


if __name__ == "__main__":
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = GoogleAdsClient.load_from_storage()

    parser = argparse.ArgumentParser(
        description="Generates keyword ideas from a list of seed keywords."
    )

    # The following argument(s) should be provided to run the example.
    parser.add_argument(
        "-c",
        "--customer_id",
        type=str,
        required=True,
        help="The Google Ads customer ID.",
    )
    parser.add_argument(
        "-k",
        "--keyword_texts",
        nargs="+",
        type=str,
        required=False,
        default=[],
        help="Space-delimited list of starter keywords",
    )
    # To determine the appropriate location IDs, see:
    # https://developers.google.com/adwords/api/docs/appendix/geotargeting.
    parser.add_argument(
        "-l",
        "--location_ids",
        nargs="+",
        type=str,
        required=False,
        default=_DEFAULT_LOCATION_IDS,
        help="Space-delimited list of location criteria IDs",
    )
    # To determine the appropriate language ID, see:
    # https://developers.google.com/adwords/api/docs/appendix/codes-formats#languages.
    parser.add_argument(
        "-i",
        "--language_id",
        type=str,
        required=False,
        default=_DEFAULT_LANGUAGE_ID,
        help="The language criterion ID.",
    )
    # Optional: Specify a URL string related to your business to generate ideas.
    parser.add_argument(
        "-p",
        "--page_url",
        type=str,
        required=False,
        help="A URL string related to your business",
    )

    args = parser.parse_args()

    main(
        google_ads_client,
        "WBasaFk8x5fksvQdkTXR4Q",
        "in"
        "eng",
        "modi",
        "",
    )