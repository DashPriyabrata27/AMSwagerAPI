from typing import Any

from app.schemas.author import (
    AuthorResponse,
    AuthorIdentityDetails,
    AffiliationYearDetails,
    LastInstitutionDetails,
    CountryDetails,
    TopicDetails,
    TopicItem,
    TopicShareDetails,
    XConceptDetails,
    SummaryStatistics,
    WorkCitationHistory,
)

from app.utils.data_utils import (
    as_list,
    normalize_text,
    normalize_year,
    normalize_count,
    normalize_country_code,
    normalize_float,
    unique_preserve_order,
    year_key,
)


# 1. Extract Author Identity Details

def _extract_author_identity(raw_author: dict[str, Any]) -> AuthorIdentityDetails:

    # Extract external identifiers
    ids = raw_author.get("ids")

    if not isinstance(ids, dict):
        ids = {}

    # Extract display name
    display_name = normalize_text(raw_author.get("display_name"))

    # Extract author name
    author_name = (
        normalize_text(raw_author.get("full_name"))
        or display_name
    )

    # Extract primary ORCID
    orcid = (
        normalize_text(raw_author.get("orcid"))
        or normalize_text(ids.get("orcid"))
    )

    # Extract observed ORCIDs
    observed_orcid_values = raw_author.get("observed_orcids")

    if observed_orcid_values is None:
        observed_orcid_values = ids.get("observed_orcids")

    observed_orcids = []

    for item in as_list(observed_orcid_values):
        value = normalize_text(item)

        if value:
            observed_orcids.append(value)

    observed_orcids = unique_preserve_order(observed_orcids)

    # Extract raw author names
    raw_author_names = []

    for item in as_list(raw_author.get("raw_author_names")):
        value = normalize_text(item)

        if value:
            raw_author_names.append(value)

    raw_author_names = unique_preserve_order(raw_author_names)

    # Build author identity response
    return AuthorIdentityDetails(
        author_id=normalize_text(raw_author.get("id")),
        author_name=author_name,
        display_name=display_name,
        raw_author_names=raw_author_names,
        orcid=orcid,
        observed_orcids=observed_orcids,
    )


# 2.Extract Affiliations and Affiliation-Year Mapping

def _extract_affiliations(
    raw_affiliations: Any,
) -> list[AffiliationYearDetails]:

    grouped_affiliations = {}

    for affiliation in as_list(raw_affiliations):

        if not isinstance(affiliation, dict):
            continue

        institution = affiliation.get("institution") or {}

        if not isinstance(institution, dict):
            institution = {}

        institution_id = normalize_text(
            institution.get("id")
        )

        ror = normalize_text(
            institution.get("ror")
        )

        display_name = normalize_text(
            institution.get("display_name")
        )

        institution_type = normalize_text(
            institution.get("type")
        )

        for year in as_list(affiliation.get("years")):

            year_label = year_key(year)
            normalized_year = normalize_year(year)

            year_value = (
                normalized_year
                if normalized_year is not None
                else year_label
            )

            group = grouped_affiliations.setdefault(
                year_label,
                {
                    "year": year_value,
                    "institution_ids": [],
                    "ror": [],
                    "display_names": [],
                    "type": [],
                    "seen_ids": set(),
                },
            )

            # Avoid duplicate identifiable institutions.
            if institution_id:

                if institution_id in group["seen_ids"]:
                    continue

                group["seen_ids"].add(institution_id)

            # Keep all institution attributes aligned.
            group["institution_ids"].append(institution_id)
            group["ror"].append(ror)
            group["display_names"].append(display_name)
            group["type"].append(institution_type)

    # Build final affiliation response.
    affiliation_details = []

    for group in grouped_affiliations.values():

        affiliation_details.append(
            AffiliationYearDetails(
                year=group["year"],
                institution_ids=group["institution_ids"],
                ror=group["ror"],
                display_names=group["display_names"],
                type=group["type"],
                institution_count=len(group["seen_ids"]),
            )
        )

    return affiliation_details


# 3. Extract Last Known Institutions

def _extract_last_institution(
    raw_author: dict[str, Any],
    raw_affiliations: Any,
) -> list[LastInstitutionDetails]:

    last_known = as_list(
        raw_author.get("last_known_institutions")
    )

    grouped_institutions = {}

    if not last_known:
        return []

    # Find the latest observed year for each institution.
    institution_latest_year = {}

    for affiliation in as_list(raw_affiliations):

        if not isinstance(affiliation, dict):
            continue

        institution = affiliation.get("institution") or {}

        if not isinstance(institution, dict):
            continue

        institution_id = normalize_text(
            institution.get("id")
        )

        if not institution_id:
            continue

        for year in as_list(affiliation.get("years")):

            normalized_year = normalize_year(year)

            if normalized_year is None:
                continue

            current_year = institution_latest_year.get(
                institution_id
            )

            if current_year is None or normalized_year > current_year:
                institution_latest_year[institution_id] = (
                    normalized_year
                )

    # Group last-known institutions by latest year.
    for institution in last_known:

        if not isinstance(institution, dict):
            continue

        institution_id = normalize_text(
            institution.get("id")
        )

        ror = normalize_text(institution.get("ror"))

        display_name = normalize_text(
            institution.get("display_name")
        )

        institution_type = normalize_text(
            institution.get("type")
        )

        latest_year = institution_latest_year.get(
            institution_id
        )

        group = grouped_institutions.setdefault(
            latest_year,
            {
                "latest_year": latest_year,
                "institution_id": [],
                "ror": [],
                "display_name": [],
                "type": [],
                "seen_ids": set(),
            },
        )

        # Avoid duplicate identifiable institutions.
        if institution_id:

            if institution_id in group["seen_ids"]:
                continue

            group["seen_ids"].add(institution_id)

        group["institution_id"].append(institution_id)
        group["ror"].append(ror)
        group["display_name"].append(display_name)
        group["type"].append(institution_type)

    # Build final response objects.
    last_institutions = []

    for group in grouped_institutions.values():

        last_institutions.append(
            LastInstitutionDetails(
                latest_year=group["latest_year"],
                institution_id=group["institution_id"],
                ror=group["ror"],
                display_name=group["display_name"],
                type=group["type"],
                institution_count=len(group["seen_ids"]),
            )
        )

    return last_institutions


# 4. Extract Country-Year Mapping

def _extract_country_year(
    raw_affiliations: Any,
) -> dict[str, list[str]]:

    country_year = {}

    for affiliation in as_list(raw_affiliations):

        if not isinstance(affiliation, dict):
            continue

        institution = affiliation.get("institution") or {}

        if not isinstance(institution, dict):
            continue

        country_code = normalize_country_code(
            institution.get("country_code")
        )

        if not country_code:
            continue

        for year in as_list(affiliation.get("years")):

            year_label = year_key(year)

            country_year.setdefault(year_label, [])
            country_year[year_label].append(country_code)

    return {
        year: unique_preserve_order(country_codes)
        for year, country_codes in country_year.items()
    }


# 5. Extract Topic Details

def _extract_topics(
    raw_topics: Any,
) -> tuple[list[TopicItem], dict[str, TopicItem]]:

    topic_items = []
    topics_by_id = {}

    for topic in as_list(raw_topics):

        if not isinstance(topic, dict):
            continue

        domain = topic.get("domain") or {}
        field = topic.get("field") or {}
        subfield = topic.get("subfield") or {}

        if not isinstance(domain, dict):
            domain = {}

        if not isinstance(field, dict):
            field = {}

        if not isinstance(subfield, dict):
            subfield = {}

        # Extract individual topic information
        topic_id = normalize_text(topic.get("id"))

        topic_name = normalize_text(
            topic.get("display_name")
        )

        subfield_id = normalize_text(subfield.get("id"))

        subfield_name = normalize_text(
            subfield.get("display_name")
        )

        field_id = normalize_text(field.get("id"))

        field_name = normalize_text(
            field.get("display_name")
        )

        domain_id = normalize_text(domain.get("id"))

        domain_name = normalize_text(
            domain.get("display_name")
        )

        topic_count = normalize_count(
            topic.get("count")
        )

        # Build individual topic record
        details = TopicItem(
            topic_id=topic_id,
            topic_name=topic_name,
            subfield_id=subfield_id,
            subfield_name=subfield_name,
            field_id=field_id,
            field_name=field_name,
            domain_id=domain_id,
            domain_name=domain_name,
            topic_count=(
                topic_count if topic_count is not None else 0
            ),
        )

        topic_items.append(details)

        # Maintain topic lookup for topic-share extraction
        if topic_id:
            topics_by_id[topic_id] = details

    return topic_items, topics_by_id


def _build_topic_summary(
    topics: list[TopicItem],
) -> TopicDetails:

    domain_ids = {
        topic.domain_id
        for topic in topics
        if topic.domain_id
    }

    field_ids = {
        topic.field_id
        for topic in topics
        if topic.field_id
    }

    subfield_ids = {
        topic.subfield_id
        for topic in topics
        if topic.subfield_id
    }

    return TopicDetails(
        topic_count=len(topics),
        domain_count=len(domain_ids),
        field_count=len(field_ids),
        subfield_count=len(subfield_ids),
        topics=topics,
    )


# 6. Extract Topic-Share Details

def _extract_topic_share(
    raw_topic_share: Any,
    topics_by_id: dict[str, TopicItem],
) -> list[TopicShareDetails]:

    topic_share_details = []

    for item in as_list(raw_topic_share):

        if not isinstance(item, dict):
            continue

        topic_id = (
            normalize_text(item.get("id"))
            or normalize_text(item.get("topic_id"))
        )

        # Retrieve the corresponding topic hierarchy.
        topic = topics_by_id.get(topic_id)

        topic_name = (
            topic.topic_name if topic else None
        )

        subfield_id = (
            topic.subfield_id if topic else None
        )

        subfield_name = (
            topic.subfield_name if topic else None
        )

        field_id = (
            topic.field_id if topic else None
        )

        field_name = (
            topic.field_name if topic else None
        )

        domain_id = (
            topic.domain_id if topic else None
        )

        domain_name = (
            topic.domain_name if topic else None
        )

        # Build topic-share record.
        topic_share_details.append(
            TopicShareDetails(
                topic_id=topic_id,
                topic_name=topic_name,

                subfield_id=subfield_id,
                subfield_name=subfield_name,

                field_id=field_id,
                field_name=field_name,

                domain_id=domain_id,
                domain_name=domain_name,

                value=normalize_float(item.get("value")),
            )
        )

    return topic_share_details

# 7. Extract X-Concepts

def _extract_x_concepts(
    raw_concepts: Any,
) -> list[XConceptDetails]:

    concepts = []

    for concept in as_list(raw_concepts):

        if not isinstance(concept, dict):
            continue

        concepts.append(
            XConceptDetails(
                concept_id=normalize_text(
                    concept.get("id")
                ),

                wikidata_id=normalize_text(
                    concept.get("wikidata")
                    or concept.get("wikidata_id")
                ),

                display_name=normalize_text(
                    concept.get("display_name")
                ),

                score=normalize_float(
                    concept.get("score")
                ),
            )
        )

    return concepts


# 8. Extract Summary Statistics

def _extract_summary_statistics(
    raw_author: dict[str, Any],
) -> SummaryStatistics:

    summary_stats = raw_author.get("summary_stats") or {}

    if not isinstance(summary_stats, dict):
        summary_stats = {}

    return SummaryStatistics(
        total_work_count=normalize_count(
            raw_author.get("works_count")
        ),

        total_cited_by_count=normalize_count(
            raw_author.get("cited_by_count")
        ),

        two_year_mean_citedness=normalize_float(
            summary_stats.get("2yr_mean_citedness")
        ),

        h_index=normalize_count(
            summary_stats.get("h_index")
        ),

        i10_index=normalize_count(
            summary_stats.get("i10_index")
        ),
    )

# 9. Extract Work and Citation History

def _extract_work_citation_history(
    raw_counts_by_year: Any,
) -> WorkCitationHistory:

    work_count_year = {}
    cited_count_year = {}

    for item in as_list(raw_counts_by_year):

        if not isinstance(item, dict):
            continue

        year = year_key(item.get("year"))

        work_count_year[year] = normalize_count(
            item.get("works_count")
        )

        cited_count_year[year] = normalize_count(
            item.get("cited_by_count")
        )

    return WorkCitationHistory(
        work_count_year=work_count_year,
        cited_count_year=cited_count_year,
    )

# Main Extraction Function
def extract_author_data(
    raw_author: dict[str, Any],
) -> AuthorResponse:
    """
    Extract and normalize author information from raw OpenAlex JSON.

    Returns:
        AuthorResponse containing exactly nine sections
        for the GET author endpoint.

    This function performs extraction and normalization only.
    It does not evaluate suspiciousness or calculate scores.
    """

    # Validate the OpenAlex response
    if not isinstance(raw_author, dict):
        raise ValueError(
            "Invalid OpenAlex author data. Expected a dictionary."
        )

    if not raw_author.get("id"):
        raise ValueError(
            "OpenAlex author response does not contain an ID."
        )

    # 1. Author Identity
    author_identity = _extract_author_identity(raw_author)

    # 2. Affiliations
    raw_affiliations = raw_author.get("affiliations") or []

    affiliations_details = _extract_affiliations(
        raw_affiliations
    )

    # 3. Last Known Institution
    last_institution = _extract_last_institution(
        raw_author,
        raw_affiliations,
    )

    # 4. Country Details
    country_year = _extract_country_year(raw_affiliations)

    country_details = CountryDetails(
        country_year=country_year
    )

    # 5. Topics
    topics, topics_by_id = _extract_topics(
        raw_author.get("topics")
    )

    topic_details = _build_topic_summary(topics)

    # 6. Topic-Share Details
    topic_share_details = _extract_topic_share(
        raw_author.get("topic_share"),
        topics_by_id,
    )

    # 7. X-Concepts
    x_concepts = _extract_x_concepts(
        raw_author.get("x_concepts")
    )

    # 8. Summary Statistics
    summary_statistics = _extract_summary_statistics(
        raw_author
    )

    # 9. Work and Citation History
    work_citation_history = _extract_work_citation_history(
        raw_author.get("counts_by_year")
    )

    # Build GET response containing exactly nine fields
    response = AuthorResponse(
        author_identity=author_identity,
        affiliations_details=affiliations_details,
        last_institution=last_institution,
        country_details=country_details,
        topic_details=topic_details,
        topic_share_details=topic_share_details,
        x_concepts=x_concepts,
        summary_statistics=summary_statistics,
        work_citation_history=work_citation_history,
    )

    return response
