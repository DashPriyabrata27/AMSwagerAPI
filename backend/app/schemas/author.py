from pydantic import BaseModel, ConfigDict, Field


# Base Configuration
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

# 1. Author Identity Details
class AuthorIdentityDetails(BaseSchema):
    author_id: str | None = None
    author_name: str | None = None
    display_name: str | None = None

    raw_author_names: list[str] = Field(default_factory=list)

    orcid: str | None = None
    observed_orcids: list[str] = Field(default_factory=list)



# 2. AFFILIATIONS DETAILS
class AffiliationYearDetails(BaseSchema):
    year: int | str
    institution_ids: list[str | None] = Field(default_factory=list)
    ror: list[str | None] = Field(default_factory=list)
    display_names: list[str | None] = Field(default_factory=list)
    type: list[str | None] = Field(default_factory=list)
    institution_count: int = Field(ge=0)


# 3. LAST INSTITUTION DETAILS
class LastInstitutionDetails(BaseSchema):

    latest_year: int | None = None
    institution_id: list[str | None] = Field(default_factory=list)
    ror: list[str | None] = Field(default_factory=list)
    display_name: list[str | None] = Field(default_factory=list)
    type: list[str | None] = Field(default_factory=list)
    institution_count: int = Field(ge=0)


# 4. Country Details
class CountryDetails(BaseSchema):
    country_year: dict[str, list[str]] = Field(
        default_factory=dict
    )


# 5. Topic Details
class TopicItem(BaseSchema):
    topic_id: str | None = None
    topic_name: str | None = None

    subfield_id: str | None = None
    subfield_name: str | None = None

    field_id: str | None = None
    field_name: str | None = None

    domain_id: str | None = None
    domain_name: str | None = None

    topic_count: int = Field(default=0, ge=0)


class TopicDetails(BaseSchema):
    topic_count: int = Field(default=0, ge=0)
    domain_count: int = Field(default=0, ge=0)
    field_count: int = Field(default=0, ge=0)
    subfield_count: int = Field(default=0, ge=0)

    topics: list[TopicItem] = Field(default_factory=list)


# 6. Topic-Share Details
class TopicShareDetails(BaseSchema):
    topic_id: str | None = None
    topic_name: str | None = None

    subfield_id: str | None = None
    subfield_name: str | None = None

    field_id: str | None = None
    field_name: str | None = None

    domain_id: str | None = None
    domain_name: str | None = None

    value: float | None = None



# 7. X-Concepts Details
class XConceptDetails(BaseSchema):
    concept_id: str | None = None
    wikidata_id: str | None = None
    display_name: str | None = None
    score: float | None = None


# 8. Summary Statistics
class SummaryStatistics(BaseSchema):
    total_work_count: int | None = None
    total_cited_by_count: int | None = None

    two_year_mean_citedness: float | None = None

    h_index: int | None = None
    i10_index: int | None = None


# 9. Work and Citation History
class WorkCitationHistory(BaseSchema):
    work_count_year: dict[str, int | None] = Field(default_factory=dict)

    cited_count_year: dict[str, int | None] = Field(default_factory=dict)


# Complete Author Response — Exactly 9 Fields
class AuthorResponse(BaseSchema):

    # 1. Author Identity Details
    author_identity: AuthorIdentityDetails

    # 2. Affiliations Details
    affiliations_details: list[AffiliationYearDetails] = Field(default_factory=list)

    # 3. Last Institution Details
    last_institution: list[LastInstitutionDetails] | None = None

    # 4. Country Details
    country_details: CountryDetails = Field(default_factory=CountryDetails)

    # 5. Topic Details
    topic_details: TopicDetails = Field(default_factory=TopicDetails)

    # 6. Topic-Share Details
    topic_share_details: list[TopicShareDetails] = Field(default_factory=list)

    # 7. X-Concepts Details
    x_concepts: list[XConceptDetails] = Field(default_factory=list)

    # 8. Summary Statistics
    summary_statistics: SummaryStatistics

    # 9. Work and Citation History
    work_citation_history: WorkCitationHistory = Field(default_factory=WorkCitationHistory)