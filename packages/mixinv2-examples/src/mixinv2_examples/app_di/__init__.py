"""app_di: package-based DI example mirroring the README @scope examples.

Modules mirror the README step-by-step walkthrough:
- SqliteDatabase    → SQLiteDatabase scope  (Step 1)
- Pragmas/          → @patch / @merge examples (Step 2)
- UserRepository/   → UserRepository scope  (Step 4)
- app_services/     → AppServices scope     (Step 4)

Composite scopes declared via @extend:
- Step1App          → SqliteDatabase + UserRepository (Step 1)
- Step4RequestApp   → SqliteDatabase + UserRepository + HttpHandlers (Step 4, no server)
- Step4App          → all four modules (Step 4, full stack)
"""

from mixinv2 import LexicalReference
from mixinv2 import extend, public, scope


# [docs:module-extend]
@extend(
    LexicalReference(path=("SqliteDatabase",)),
    LexicalReference(path=("UserRepository",)),
)
@public
@scope
class Step1App:
    pass
# [/docs:module-extend]


@extend(
    LexicalReference(path=("SqliteDatabase",)),
    LexicalReference(path=("UserRepository",)),
    LexicalReference(path=("HttpHandlers",)),
)
@public
@scope
class Step4RequestApp:
    pass


@extend(
    LexicalReference(path=("SqliteDatabase",)),
    LexicalReference(path=("UserRepository",)),
    LexicalReference(path=("HttpHandlers",)),
    LexicalReference(path=("NetworkServer",)),
)
@public
@scope
class Step4App:
    pass
