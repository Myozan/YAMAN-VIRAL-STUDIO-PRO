# Enterprise Edition — Source Boundary

This directory is a boundary marker and contains no proprietary implementation.

## Important

The public YAMAN VIRAL STUDIO PRO repository remains MIT-licensed for its existing Community source. Do not place confidential Enterprise source code, signing keys, customer data, license files containing customer information, or paid distribution artifacts in this public repository.

## Recommended repository layout

Keep the commercial implementation in a separate **private** repository controlled by the rights holder:

```text
YAMAN-VIRAL-STUDIO-PRO/                 # Public — MIT Community
  app/
  web/
  docs/
  LICENSE
  LICENSING.md

YAMAN-VIRAL-STUDIO-ENTERPRISE/          # Private — commercial modules
  enterprise/
    sso/
    rbac/
    audit/
    tenant-management/
  packaging/
  contracts/                            # Access-controlled; no customer secrets in Git
  LICENSE-COMMERCIAL.md
```

The directory names above are an architectural proposal, not a claim that these modules already exist.

## Integration rules

1. Enterprise extensions should integrate through documented interfaces or a separately maintained adapter layer.
2. The Community build must run without private Enterprise code or credentials.
3. Enterprise packaging must explicitly include only modules authorized by the applicable customer agreement.
4. Keep a software bill of materials (SBOM) and third-party license inventory for every release.
5. Do not copy MIT Community files into the private repository and then claim their existing MIT grants have been revoked. Preserve their notices and MIT terms.
6. Do not distribute commercial modules until the commercial agreement, module inventory, version, usage limits, and support terms have been approved and signed.

## Commercial source header

Use the following header only for newly authored proprietary Enterprise source files, after legal review and approval of the final commercial license:

```text
SPDX-License-Identifier: LicenseRef-Yaman-Commercial
Copyright (c) [YEAR] [LEGAL RIGHTS HOLDER]
Commercial use, redistribution, and modification are governed only by the
separate written agreement applicable to the licensed Enterprise module.
```

This header is an identification marker; it is not itself a complete license agreement.
