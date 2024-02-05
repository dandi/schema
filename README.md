# Schemas associated with the DANDI archive

Core repository for just the schema associated with dandisets and assets. All files are released under a [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).

Each release contains the following files:

- `dandiset.json`: A draft dandiset schema
- `dandiset-published.json`: A published dandiset schema
- `asset.json`: A draft asset schema
- `asset-published.json`: A published asset schema
- `context.json`: A JSON-LD context for dandisets and assets

This is largely a Read-Only repository. Pydantic data models are in 
https://github.com/dandi/dandischema/ and they are used to produce 
changes to `./releases`.

## Viewing the schemas

This [online schema viewing application](https://json-schema.app/) can be used to view the JSON schemas.

#### Examples: 

1. [Dandiset version 0.6.6](https://json-schema.app/view/%23?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdandi%2Fschema%2Fmaster%2Freleases%2F0.6.6%2Fdandiset.json)
1. [Asset version 0.6.6](https://json-schema.app/view/%23?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdandi%2Fschema%2Fmaster%2Freleases%2F0.6.6%2Fasset.json)

Simply replacing the version number should provide access to a specific schema version. For example:

- `0.5.2`: https://json-schema.app/view/%23?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdandi%2Fschema%2Fmaster%2Freleases%2F0.5.2%2Fdandiset.json
- `0.6.0`: https://json-schema.app/view/%23?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdandi%2Fschema%2Fmaster%2Freleases%2F0.6.0%2Fdandiset.json
