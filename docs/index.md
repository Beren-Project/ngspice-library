# Documentation

Use the documentation by task:

- Using the library: [Library usage](library-usage.md)
- Finding a device: [Device catalog](device-catalog.md)
- Understanding device behavior: [Device family pages](device-catalog.md#inventory)
- Adding or changing a model: [Model authoring guide](model-authoring-guide.md)
- Running and interpreting tests: [Validation guide](validation-guide.md)
- Understanding project boundaries: [Architecture](architecture.md)
- Maintaining the repository: [Development](development.md)
- Resolving common failures: [Troubleshooting](troubleshooting.md)
- Reviewing durable decisions: [Architecture decisions](architecture.md#durable-decisions)

Technical claims follow this precedence:

1. `lib/ngfuncs.lib` for public interfaces
2. `ifspec.ifs` for custom XSPICE interfaces
3. `cfunc.mod` for custom behavior
4. tests and examples for validation status
5. documentation

The vendored `src/ngspice/` tree is upstream build infrastructure and reference
material. Its stock devices and examples are not part of this project's public
device catalog.
