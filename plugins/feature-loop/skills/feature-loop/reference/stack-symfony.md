# Pack spécialiste — Symfony (6.4 LTS / 7.x, PHP 8.2+)

Chargé par la mère à l'Étape 2bis quand `specialist_stack` contient Symfony (détection : `composer.json` avec `symfony/framework-bundle`, arbo `config/ src/ templates/`). La mère **injecte les sections par rôle** dans les briefs des agents (impl → §1, tests → §2, review → §3) et exécute §4 au gate. §5 nourrit tous les rôles (pièges spécifiques aux LLM). Sources : best practices officielles symfony.com + pièges constatés sur des runs réels (chaque piège marqué *vécu* a coûté une itération ou un échec CI quelque part).

## 0. Discipline de version (avant tout)

- **Lire `composer.lock`** (pas composer.json) pour les versions réelles : Symfony, Doctrine ORM, PHPUnit. Les API divergent fortement entre majeures — c'est la 1re source d'hallucination.
- En cas de doute sur une signature → vérifier dans `vendor/` (le code installé EST la doc exacte) avant le web.
- Attributs PHP partout (`#[Route]`, `#[AsCommand]`, `#[ORM\Column]`, `#[IsGranted]`) — les annotations `@` sont mortes ; en générer est un marqueur de training data périmé.

## 1. Invariants IMPL (agent A)

**Architecture (best practices officielles)**
- Contrôleurs minces étendant `AbstractController` ; la logique vit dans des services autowirés (constructor injection, `private readonly`). Pas de bundle applicatif, des namespaces.
- Config : env vars pour l'infrastructure, **paramètres `app.*`** pour le comportement applicatif, secrets Symfony pour le sensible. Pattern fallback : `'%env(default:app_x_default:X)%'`.
- Formulaires = classes dédiées ; contraintes de validation **sur l'objet métier**, pas sur les champs ; boutons dans les templates ; une seule action affiche ET traite (`handleRequest` → `isSubmitted() && isValid()`).
- Honeypot : champ `mapped: false` + `tabindex=-1` caché — et le **template doit le rendre** (`form_widget(form.website)`) si le rendu est champ-par-champ (pas de `form_rest` → champ silencieusement absent → honeypot mort). *vécu*
- Sécurité : password hasher `auto`, voters pour l'authz complexe, rate limiter Symfony (`fixed_window` par IP, fallback `getClientIp() ?? 'unknown'`). Réponses **neutres** sur les chemins de rejet (anti-énumération) : même flash, même redirect que le nominal — et formulation **conditionnelle** (« si votre demande est valide, vous recevrez… ») pour rester vrai sans révéler le rejet. Injecter les **interfaces** (`RateLimiterFactoryInterface`), pas les classes concrètes.

**Doctrine — les pièges qui coûtent une itération**
- `Doctrine\ORM\Query::execute()` pour les DELETE/UPDATE DQL — **`executeStatement()` n'existe que côté DBAL** ; confusion = crash CI. *vécu*
- Les bulk DQL **bypassent les lifecycle events et l'identity map** — jamais pour des entités avec cascades applicatives.
- **Cécité de l'identity map sur l'unicité en batch** : un check d'existence SQL (`SELECT COUNT…`) ne voit PAS les entités persistées non flushées → deux entités d'un même batch peuvent recevoir la même valeur « unique » → violation d'index au flush, parfois avalée par un `catch` de lot (perte silencieuse). Tout générateur de valeur unique appelé en batch doit tenir un **registre en mémoire** des valeurs assignées non flushées. *vécu — 2 bloquants sur un run*
- `em->clear()` détache TOUT (ORM 3 : pas d'argument) — ne plus référencer aucune entité du lot après ; les caches d'entités locaux (`$personCache`…) deviennent stale.
- Migrations : **additives** par défaut ; colonne unique nullable OK sur PostgreSQL (NULL multiples tolérés) ; toute modif d'entité ⇒ sa migration dans le MÊME diff. Éditer une migration **déjà appliquée** ne la rejoue pas sur la DB runtime (cf. smoke live).
- `publishedAt` & co : vérifier `DateTime` vs `DateTimeImmutable` dans l'entité réelle — ne pas deviner.

**Twig**
- Auto-échappement actif sur `.html.twig` — jamais de `|raw` sur une donnée utilisateur ; les emails HTML utilisent des **styles inline** (le CSS du site ne s'y applique pas).
- **`app.flashes` consomme le bag au premier appel** — une seconde boucle plus bas dans le même template est toujours vide (utiliser `app.flashes('label')` par type, ou un seul bloc global). *vécu*
- `{% block javascripts %}` HORS de `{% block body %}` ; `block('x')` exige que le bloc existe si `strict_variables`.

## 2. Invariants TESTS (agent B)

- `WebTestCase` : `createClient()` AVANT tout `getContainer()` ; soumissions via crawler (`selectButton(...)->form()` + champs `formName[champ]`).
- **`assertEmailCount()` est PAR-REQUÊTE, même avec `$client->disableReboot()`** — le services resetter vide le MessageLogger entre les requêtes. Scénario multi-soumissions : asserter l'état **en base** (rows) + `assertEmailCount(0|1)` sur la **dernière** requête seulement. *vécu — échec CI*
- Rate limiter : vider `cache.rate_limiter` en `setUp()` (sinon bleeding inter-tests). Tester le N+1ᵉ refus par l'état DB, pas par le message (neutre par design).
- Commandes console : `KernelTestCase` + `CommandTester` ; antidater un `createdAt` sans setter via `ReflectionProperty` (en assumant l'invariant métier protégé).
- PHPUnit : `docker exec -e APP_ENV=test …` si le projet le demande — lire le README/CLAUDE.md du repo, l'env de test Symfony est souvent piégeux.
- **Jamais d'affectation `$password = '…'` dans un test** — les scanners de secrets CI (GitGuardian) flaggent le *pattern d'affectation* ; le même littéral inline dans le tableau du form passe. *vécu — échec CI*
- Pas d'assertion sur le texte exact d'un flash neutre (il peut changer) : asserter le comportement (rows, emails, redirect).

## 3. Checklist REVIEW (agent C / devil's advocate)

- **Neutralité des rejets** : honeypot/rate-limit répondent-ils EXACTEMENT comme le nominal (flash, redirect) ? Un message différencié = canal d'énumération. Inversement : le message commun ment-il à un humain (faux positif password-manager) ? → formulation conditionnelle.
- **Open redirect** : tout `redirect($x)` où `$x` dérive d'un header (`Referer`) ou d'un paramètre non validé. *vécu*
- **Double opt-in / machines à états sur entités** : vérifier les transitions INVERSES (désinscrit→réinscrit, rejeté→re-soumis) — c'est là que les champs d'état (`confirmedAt`…) sont oubliés. *vécu — bypass du double opt-in*
- Emails : envoi APRÈS persist/validation (jamais sur un chemin de rejet) ; `TransportExceptionInterface` en best-effort si c'est le pattern du projet ; pas de PII dans les logs.
- DQL/SQL : paramètres bindés partout ; `LOWER(COALESCE(col,''))` si colonne nullable dans un LIKE ; échappement wildcards (`addcslashes('%_\\')`) cohérent avec l'existant.
- Batch + unicité : cf. §1 (le finding le plus rentable de la stack).
- Fixtures/imports au boot : une édition « directe en BDD » survivra-t-elle au prochain `docker compose up` ? (source de vérité = les fixtures, pattern fréquent des projets Symfony dockerisés).

## 4. Gate objectif Symfony (commandes)

Dans l'ordre coût croissant, selon ce qui est dispo (vendor/ requis pour bin/console) :
```bash
php -l <fichiers modifiés>                                  # toujours possible, même sans vendor
php bin/console lint:twig templates/                        # templates touchés
php bin/console lint:yaml config/
php bin/console lint:container                              # câblage services
php bin/console doctrine:schema:validate --skip-sync        # mapping ↔ migrations
vendor/bin/phpstan analyse (si présent) ; php bin/phpunit
```
Sans vendor/ local (clone de review) : `php -l` + **la CI du projet est le gate** — pousser tôt, lire les logs d'échec (`gh run view --log-failed`), itérer. Smoke live : attention au serveur dev stale et à la DB runtime non migrée (≠ DB de test).

## 5. Anti-hallucination spécifique LLM × Symfony

Les erreurs LLM les plus fréquentes sur cette stack (à s'auto-vérifier avant de livrer) :
1. **API d'une autre majeure** : méthodes Doctrine DBAL sur des objets ORM (cf. `executeStatement`), signatures Symfony 5 sur du 7, annotations au lieu d'attributs. Parade : composer.lock + vendor/ comme oracle.
2. **Clés de config inventées** (yaml framework/doctrine) : une clé inconnue casse au boot → `lint:container`/boot dans la CI la détecte ; ne pas inventer, copier une entrée existante du projet.
3. **Sémantique des helpers de test supposée au lieu de vérifiée** (cf. `assertEmailCount`) : quand un test multi-requêtes dépend d'un comportement d'accumulation, vérifier la sémantique sur UN run avant d'en dépendre.
4. **Oubli du couple entité⇄migration** : champ ajouté sans migration (ou l'inverse) — `doctrine:schema:validate` au gate.
5. **Tests qui épousent l'implémentation** (texte de flash, ordre HTML) au lieu du contrat observable (DB, emails, codes HTTP).
