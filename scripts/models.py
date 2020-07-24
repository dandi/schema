from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl, EmailStr, create_model
from typing import List, Union, Optional
from datetime import date
import yaml
from copy import deepcopy

def create_enum(path):
    with open(path)as fp:
        data = yaml.safe_load(fp)
    items = {}
    klass = None
    for idx, item in enumerate(data["@graph"]):
        if item["@type"] == "rdfs:Class":
            klass = item["@id"].replace("dandi:", "")
            klass_doc = item["rdfs:comment"]
        else:
            value = item["@id"].replace("dandi:", "")
            items[f"var{idx:02d}"] = value
    if klass is None or len(items) == 0:
        raise ValueError(f"YAML {path} did not generate a klass or items")
    newklass = Enum(klass, items)
    newklass.__doc__ = klass_doc
    return newklass


AccessType = create_enum("terms/AccessType.yaml")
RoleType = create_enum("terms/RoleType.yaml")
Relation = create_enum("terms/RelationType.yaml")
License = create_enum("terms/LicenseType.yaml")
IdentifierType = create_enum("terms/IdentifierType.yaml")


class PropertyValue(BaseModel):
    maxValue: float = None
    minValue: float = None
    unitCode: Union[str, AnyUrl] = None
    unitText: str = None
    value: Union[bool, float, str, int, List[Union[bool, float, str, int]]] = None
    valueReference: PropertyValue = None   # Note: recursive (circular or not)
    propertyID: Union[IdentifierType, AnyUrl, str] = None


PropertyValue.update_forward_refs()
Identifier = Union[str, AnyUrl, PropertyValue]


class Contributor(BaseModel):
    identifier: Identifier = None
    email: EmailStr = None
    url: AnyUrl = None
    roleName: List[RoleType]
    includeInCitation: bool = True
    awardNumber: str = None


class Person(Contributor):
    name: str = Field(description="Use the format: lastname, firstname ...", title="Name")
    affiliation: List[str]


class Organization(Contributor):
    name: str = Field(title="Name")
    contactPoint: str = None


class EthicsApproval(BaseModel):
    identifier: Identifier = None
    name: str
    url: str


class Resource(BaseModel):
    identifier: Identifier = None
    name: str = None
    url: str
    repository: Union[str, AnyUrl] = None
    relation: Relation


class About(BaseModel):
    identifier: Identifier = None
    name: str = None


class AccessRequirements(BaseModel):
    status: AccessType
    email: EmailStr = None
    contactPoint: str = None
    description: str = None
    embargoedUntil: date = None


class AssetsSummary(BaseModel):
    """Summary over assets contained in a dandiset (published or not)"""

    # stats which are not stats
    numberOfBytes: int = Field(readonly=True, sameas="schema:contentSize")
    numberOfFiles: int = Field(readonly=True)  # universe
    numberOfSubjects: int = Field(readonly=True)  # NWB + BIDS
    numberOfSamples: int = Field(None, readonly=True)  # more of NWB
    numberOfCells: int = Field(None, readonly=True)

    dataStandard: List[str] = Field(readonly=True)  # TODO: types of things NWB, BIDS
    # Web UI: icons per each modality?
    modality: List[str] = Field(readonly=True)  # TODO: types of things, BIDS etc...
    # Web UI: could be an icon with number, which if hovered on  show a list?
    measurementTechnique: List[str] = Field(readonly=True)
    variableMeasured: List[PropertyValue] = Field(None, readonly=True)


class Digest(BaseModel):
    value: str
    cryptoType: AnyUrl


class BioSample(BaseModel):
    assayType: AnyUrl # from OBI
    anatomy: AnyUrl  # from UBERON
    strain: str = None
    identifier: Identifier = None
    vendor: Organization = None
    age: str = None
    sex: str = None
    species: str = None


class Dandiset(BaseModel):
    """A body of structured information describing a DANDI dataset."""
    schemaVersion: str = Field(default="0.0.0", readonly=True)
    identifier: Identifier = Field(readonly=True)
    name: str = Field(title="Title", description="Name of this dataset")
    description: str = Field(title="",
                             description="A")

    contributor: List[Union[Person, Organization]] = \
        Field(title="Contributors",
              description="The people or organizations who have"
                          "contributed to creating this dataset")

    license: List[License] = Field(title="License",
                             description="A license document that applies to this "
                                         "content, typically indicated by URL.",
                             prefix="schema")
    keywords: List[str] = Field(title="Keywords",
                                description="Keywords or tags used to describe "
                                            "this content. Multiple entries in a "
                                            "keywords list are typically delimited "
                                            "by commas.")
    about: List[About] = None
    studyTarget: List[Union[str, AnyUrl]] = None
    protocol: List[str] = None
    ethicsApproval: List[EthicsApproval] = None
    acknowledgement: str = None

    access: List[AccessRequirements]
    relatedResource: List[Resource] = None

    # Linking to this dandiset or the larger thing
    url: AnyUrl = Field(readonly=True, description="permalink to the dandiset")
    repository: AnyUrl = Field(readonly=True, description="location of the ")

    # From assets
    assetsSummary: AssetsSummary = Field(readonly=True)

    # From server (requested by users even for drafts)
    manifestLocation: List[AnyUrl] = Field(readonly=True)

    @classmethod
    def unvalidated(__pydantic_cls__: "Type[Model]", **data: Any) -> "Model":
        for name, field in __pydantic_cls__.__fields__.items():
            try:
                data[name]
            except KeyError:
                if field.required:
                    value = None
                if field.default is None:
                    # deepcopy is quite slow on None
                    value = None
                else:
                    value = deepcopy(field.default)
                data[name] = value
        self = __pydantic_cls__.__new__(__pydantic_cls__)
        object.__setattr__(self, "__dict__", data)
        object.__setattr__(self, "__fields_set__", set(data.keys()))
        return self


class PublishedDandiset(Dandiset):
    # On publish
    version: str = Field(readonly=True)
    datePublished: date = Field(readonly=True)
    publishedBy: AnyUrl = Field(None, readonly=True)  # TODO: formalize "publish" activity to at least the Actor
    doi: Optional[Union[str, AnyUrl]] = Field(None, readonly=True)


class Asset(BaseModel):
    """Metadata used to describe an asset.

    Derived from C2M2 (Level 0 and 1) and schema.org
    """
    schemaVersion: str = Field(default="0.0.0", readonly=True)
    identifier: Identifier = Field(readonly=True)  # yoh: might be UUID
    contentSize: str
    encodingFormat: Union[str, AnyUrl]
    digest: Digest
    name: str

    path: str = None
    isPartOf: Identifier

    # this is from C2M2 level 1 - using EDAM vocabularies - in our case we would
    # need to come up with things for neurophys
    dataType: AnyUrl

    sameAs: AnyUrl = None
    access: List[AccessRequirements] = None
    relatedResource: List[Resource] = None

    modality: List[str] = Field(readonly=True)
    measurementTechnique: List[str] = Field(readonly=True)
    variableMeasured: List[PropertyValue] = Field(readonly=True)

    generatedBy: Optional[AnyUrl] = Field(None, readonly=True)
    wasDerivedFrom: BioSample = None

    # on publish or set by server
    contentUrl: List[AnyUrl]
    datePublished: date


# this is equivalent to json.dumps(MainModel.schema(), indent=2):
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        print({'dandiset': PublishedDandiset, 'asset': Asset}[sys.argv[1]].schema_json(indent=2))
