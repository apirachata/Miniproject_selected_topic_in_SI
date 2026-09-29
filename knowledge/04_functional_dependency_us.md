# Determining Functional Dependencies in Relational Databases

## 1. What a Functional Dependency Is

A **functional dependency** (FD) is a constraint between two sets of attributes in a relation. We write it as **X → Y**, read aloud as "X functionally determines Y," or equivalently "Y is functionally dependent on X." The formal meaning is this: for any two tuples (rows) t1 and t2 in any legal instance of the relation, if t1[X] = t2[X], then it must also be true that t1[Y] = t2[Y]. In plain language, once you know the value of X, the value of Y is fixed and unambiguous. The left-hand side X is called the **determinant**; the right-hand side Y is called the **dependent**. Both sides are *sets* of attributes, so `{ZipCode, HouseNumber} → {Street, City}` is perfectly ordinary; by convention we drop the braces and write `ZipCode, HouseNumber → Street, City`, and we abbreviate attribute names to single letters when the algebra gets dense (AB → CD means `{A,B} → {C,D}`).

Two clarifications matter from the outset. First, an FD is a statement about *every possible legal state of the database*, not about the rows that happen to be stored today. It encodes a rule of the enterprise being modeled, such as "each employee has exactly one Social Security number" or "each ISBN identifies exactly one book title." Second, X → Y does not imply Y → X. Functional dependency is directional. `SSN → EmployeeName` is true in essentially every organization; `EmployeeName → SSN` is false as soon as two employees share a name. Confusing these two directions is one of the most common errors students make.

## 2. Discovering FDs: Data Instances Versus Business Rules

There are exactly two sources of knowledge about functional dependencies: the **business rules** (interviews with users, policy documents, regulations, the data dictionary, the system catalog) and a **data instance** (a snapshot of actual rows). These two sources are not equally authoritative, and understanding why is essential.

A data instance can **disprove** an FD but can never definitively **prove** one. The logic is straightforward. To disprove X → Y you need a single counterexample: two rows agreeing on X but disagreeing on Y. That counterexample is conclusive, because the FD claims the situation is impossible and here it is. To prove X → Y, however, you would need to show that no counterexample can ever appear in any future state of the database — and no finite snapshot can establish that. An instance that satisfies X → Y merely shows that the FD is *not yet contradicted*.

Consider this small instance of a `Customer` table:

| CustID | CustName | ZipCode | City | State |
|--------|----------|---------|------|-------|
| C01 | Ana Ruiz | 60616 | Chicago | IL |
| C02 | Ben Cole | 02139 | Cambridge | MA |
| C03 | Cara Diaz | 60616 | Chicago | IL |
| C04 | Dan Frey | 78701 | Austin | TX |

From this instance you may safely conclude that `ZipCode → City` is *not disproved*, and it happens to match the real business rule (a US ZIP code lies within one city, ignoring a handful of edge cases). But the same instance equally fails to disprove `City → ZipCode`, since Chicago maps only to 60616 here. That FD is nevertheless **false in reality**: Chicago has more than fifty ZIP codes. The instance is simply too small. Likewise the instance does not disprove `CustName → CustID`, yet no analyst would accept it, because names are not unique. The methodological rule follows directly: **use the instance to eliminate candidate FDs, and use the business rules to assert the ones you keep.** A useful classroom drill is to hand students an instance, ask them to list every FD it satisfies, and then ask which of those survive contact with reality — typically fewer than half.

## 3. Trivial, Non-Trivial, and Completely Non-Trivial Dependencies

An FD X → Y is **trivial** when Y ⊆ X. For example `{A,B} → A` holds in every relation whatsoever, by definition of equality, and therefore carries no information. It is **non-trivial** when Y ⊄ X, that is, when at least one attribute on the right does not appear on the left: `{A,B} → {B,C}` is non-trivial because of C. It is **completely non-trivial** (some texts say *fully non-trivial*) when X ∩ Y = ∅, so the two sides share no attribute at all: `{A,B} → {C,D}`. Design work concerns itself almost entirely with non-trivial dependencies; trivial ones are included in the theory only because the inference rules need them to be closed and complete.

## 4. Armstrong's Axioms and the Derived Rules

Given a set F of FDs, other FDs follow logically. The set of all FDs implied by F is written **F⁺**, the *closure of F*. William W. Armstrong showed in 1974 that three rules are **sound** (they derive only true FDs) and **complete** (they derive every true FD):

1. **Reflexivity.** If Y ⊆ X, then X → Y. (This is what generates the trivial dependencies.)
2. **Augmentation.** If X → Y, then XZ → YZ for any attribute set Z. (Adding the same extra attributes to both sides preserves the dependency.)
3. **Transitivity.** If X → Y and Y → Z, then X → Z.

Three further rules are commonly used because they shorten derivations. Each is *derived* — provable from the axioms — rather than primitive.

**Union.** If X → Y and X → Z, then X → YZ. *Derivation:* from X → Y, augment with X to get XX → XY, i.e. X → XY. From X → Z, augment with Y to get XY → YZ. By transitivity on X → XY and XY → YZ, we obtain X → YZ.

**Decomposition (projection).** If X → YZ, then X → Y and X → Z. *Derivation:* by reflexivity YZ → Y; by transitivity with X → YZ we get X → Y. Symmetrically for Z. The union and decomposition rules together justify the standard convention of writing FDs with a single attribute on the right whenever convenient — the two forms are interchangeable.

**Pseudo-transitivity.** If X → Y and WY → Z, then WX → Z. *Derivation:* augment X → Y with W to get WX → WY; then apply transitivity with WY → Z to obtain WX → Z.

A worked derivation ties these together. Let R(A, B, C, D, E) with F = {A → B, BC → D, D → E}. Prove that AC → E. From A → B, augment with C: AC → BC. From BC → D and transitivity: AC → D. From D → E and transitivity: AC → E. Three steps, each citing a named rule — that is the level of rigor an exam answer should show.

Note carefully that certain plausible-looking rules are **not** valid. If X → Z then it does *not* follow that XY → Z is the only form, nor does XY → Z imply X → Z or Y → Z (this false rule is sometimes called "left decomposition" and it is a frequent source of wrong answers). Similarly, X → Y and Z → W do not give XZ → YW unless you apply augmentation twice and transitivity properly — the composition rule happens to be valid, but it must be derived, not assumed.

## 5. Attribute Closure X⁺

Rather than enumerate F⁺, which is exponentially large, we compute the **closure of an attribute set**: X⁺ is the set of all attributes functionally determined by X under F. The algorithm is short and mechanical:

```
result := X
repeat
    for each FD  V → W  in F
        if V ⊆ result then result := result ∪ W
until result stops changing
return result
```

**Worked example.** Let R(A, B, C, D, E) with F = {A → BC, CD → E, B → D, E → A}. Compute A⁺.

| Pass | FD applied | Reason | result |
|------|-----------|--------|--------|
| start | — | initialize | {A} |
| 1 | A → BC | A ⊆ {A} | {A, B, C} |
| 2 | B → D | B ⊆ {A,B,C} | {A, B, C, D} |
| 3 | CD → E | {C,D} ⊆ result | {A, B, C, D, E} |
| 4 | E → A | adds nothing new | {A, B, C, D, E} — stable |

So A⁺ = {A, B, C, D, E} = R. Computing the others the same way: E⁺ = {E, A, B, C, D} (E → A, then as above); (BC)⁺ = {B, C, D, E, A} (B → D, then CD → E, then E → A); (CD)⁺ = {C, D, E, A, B}. By contrast B⁺ = {B, D} and C⁺ = {C}, both far short of R.

### 5.1 Two Uses of Closure

**Testing whether F implies X → Y.** The FD X → Y is in F⁺ **if and only if** Y ⊆ X⁺. This single test replaces any amount of axiom-juggling. In the example above, is AB → E implied? (AB)⁺ ⊇ A⁺ = R, so yes. Is BC → A implied? (BC)⁺ = R ∋ A, so yes. Is D → C implied? D⁺ = {D}, which does not contain C, so no.

**Testing whether X is a superkey.** X is a **superkey** of R exactly when X⁺ = R (all attributes). X is a **candidate key** when in addition no proper subset of X is a superkey — that is, X is a *minimal* superkey.

## 6. Finding All Candidate Keys Systematically

Brute force over all 2ⁿ attribute subsets is impractical, so use the standard classification first. Partition the attributes of R into four groups by looking at where each attribute appears in F:

- **Group L** — appears only on left-hand sides. Must be in every candidate key.
- **Group R** — appears only on right-hand sides. Can be in no candidate key.
- **Group B** — appears on both sides. May or may not be in a key.
- **Group N** — appears in no FD at all. Must be in every candidate key.

Procedure: let *Core* = L ∪ N. Compute Core⁺. If Core⁺ = R, then Core is the unique candidate key and you are finished. Otherwise, add attributes from Group B to Core one at a time, then two at a time, and so on, testing the closure each time; keep every set whose closure is R and which contains no smaller successful set.

In our running example F = {A → BC, CD → E, B → D, E → A}, every attribute appears on both sides, so L = N = ∅ and Core = ∅, whose closure is ∅. We therefore test singletons: A⁺ = R ✔, E⁺ = R ✔, B⁺ = {B,D} ✘, C⁺ = {C} ✘, D⁺ = {D} ✘. Then pairs drawn from the failures, skipping any pair containing A or E (they would not be minimal): (BC)⁺ = R ✔, (BD)⁺ = {B,D} ✘, (CD)⁺ = R ✔. The candidate keys are therefore **{A}, {E}, {BC}, {CD}**.

An attribute that belongs to at least one candidate key is a **prime attribute**; one that belongs to none is **non-prime**. In this example every one of A, B, C, D, E is prime — a fact with immediate consequences for normalization, as Section 9 shows.

## 7. Canonical Cover (Minimal Cover)

A **canonical cover** F_c of F is an FD set that is equivalent to F but contains no redundancy. The three-step algorithm:

**Step 1 — Singleton right-hand sides.** Replace each X → {A1,…,An} by the n FDs X → A1, …, X → An (justified by decomposition). Discard duplicates.

**Step 2 — Remove extraneous left-hand attributes.** For each FD X → A where |X| > 1, and for each attribute B ∈ X, check whether A ∈ (X − B)⁺ computed *under the current FD set*. If so, B is extraneous and X → A is replaced by (X − B) → A. Re-check the shortened FD in case a second attribute is now extraneous.

**Step 3 — Remove redundant FDs.** For each remaining FD X → A, temporarily delete it, giving G = F − {X → A}, and compute X⁺ under G. If A ∈ X⁺, the FD was redundant; delete it permanently. Process FDs one at a time and never restore a deletion, because the result depends on the order — different orders can yield different but equally valid canonical covers.

**Complete worked example.** R(A, B, C, D) with F = {A → BC, B → C, A → B, AB → C, AC → D}.

*Step 1.* Split A → BC into A → B and A → C. The set becomes {A → B, A → C, B → C, AB → C, AC → D} (the duplicate A → B is dropped).

*Step 2.* Analyze AB → C. Is A extraneous? Compute B⁺ = {B, C}; it contains C, so yes — AB → C collapses to B → C, which already exists, so we drop it. Now analyze AC → D. Is C extraneous? A⁺ = {A, B, C, D}… careful: at this point we compute A⁺ using the current set, which gives {A, B, C} plus D via AC → D, so A⁺ ⊇ {C}; C is therefore extraneous and AC → D becomes A → D. Is A extraneous from AC → D? C⁺ = {C}, which lacks D, so A stays. Current set: {A → B, A → C, B → C, A → D}.

*Step 3.* Test A → C for redundancy. Remove it and compute A⁺ under {A → B, B → C, A → D}: {A} → {A,B} → {A,B,C} → {A,B,C,D}. Since C is recovered, A → C is redundant; delete it. Test A → B: without it, A⁺ = {A, D}, missing B, so keep it. Test B → C: without it, B⁺ = {B}, missing C, so keep it. Test A → D: without it, A⁺ = {A, B, C}, missing D, so keep it.

**F_c = {A → B, B → C, A → D}.** Three FDs replace the original five, with no loss of information.

## 8. Equivalence of Two FD Sets

Two sets F and G are **equivalent** (F ≡ G) when F⁺ = G⁺. Testing closures directly is infeasible, so use the covering test: **F covers G** if every FD X → Y in G satisfies Y ⊆ X⁺ computed under F. Then F ≡ G if and only if F covers G *and* G covers F. If only one direction holds, one set is strictly stronger. For instance, F = {A → B, B → C} and G = {A → B, A → C, B → C}: F covers G because under F, A⁺ = {A,B,C} ⊇ {C}; and G covers F trivially since F ⊆ G. So F ≡ G, and F is the more economical description. But F = {A → B} and G = {A → B, B → A} are not equivalent, because under F, B⁺ = {B} does not contain A.

## 9. Normal Forms Driven by Functional Dependencies

**First Normal Form (1NF)** requires that every attribute value be atomic — no repeating groups, no lists packed into a single cell, no nested relations. A row storing `Phones = "312-555-0101; 312-555-0177"` violates 1NF; the fix is a separate `CustomerPhone(CustID, Phone)` table.

**Second Normal Form (2NF)** requires 1NF plus the absence of any **partial dependency**: no non-prime attribute may depend on a *proper subset* of a candidate key. Failing example: `ORDERLINE(OrderID, ProductID, Qty, ProductName)` with key {OrderID, ProductID} and FD `ProductID → ProductName`. `ProductName` is non-prime and depends on half the key, so this is 2NF-violating. Decompose into `ORDERLINE(OrderID, ProductID, Qty)` and `PRODUCT(ProductID, ProductName)`. Note that a relation whose every candidate key is a single attribute is automatically in 2NF, because a single attribute has no proper non-empty subsets to depend on.

**Third Normal Form (3NF)** requires 2NF plus the absence of any **transitive dependency** of a non-prime attribute on a candidate key. Equivalently and more usefully: for every non-trivial FD X → A in F, either X is a superkey, **or** A is prime. Failing example: `EMPLOYEE(EmpID, DeptID, DeptName)` with key {EmpID}, `EmpID → DeptID` and `DeptID → DeptName`. `DeptName` reaches the key only through `DeptID`, which is not a superkey and `DeptName` is not prime. Decompose into `EMPLOYEE(EmpID, DeptID)` and `DEPARTMENT(DeptID, DeptName)`.

**Boyce–Codd Normal Form (BCNF)** tightens 3NF by deleting the "or A is prime" escape clause: for every non-trivial FD X → A, **X must be a superkey**. Failing example: `TEACHES(Student, Subject, Teacher)` where a student takes at most one teacher per subject, and each teacher teaches exactly one subject. The FDs are `{Student, Subject} → Teacher` and `Teacher → Subject`. Candidate keys are {Student, Subject} and {Student, Teacher}, so every attribute is prime and the relation *is* in 3NF; but `Teacher → Subject` has a non-superkey determinant, so it is not in BCNF. Decompose into `TS(Teacher, Subject)` and `ST(Student, Teacher)`.

## 10. Lossless Join and Dependency Preservation

A decomposition of R into R1 and R2 is **lossless** (more precisely, has the lossless-join property) if and only if the common attributes form a superkey of at least one fragment: **(R1 ∩ R2) → R1 or (R1 ∩ R2) → R2 must be in F⁺**. Applied to the TEACHES example, R1 ∩ R2 = {Teacher}, and `Teacher → Subject` makes {Teacher} a key of `TS(Teacher, Subject)`; the decomposition is therefore lossless. For decompositions into three or more fragments, use the **chase (tableau) algorithm**: build a matrix with one row per fragment and one column per attribute, write a distinguished symbol aⱼ where the fragment contains attribute j and a subscripted bᵢⱼ otherwise, then repeatedly apply each FD — whenever two rows agree on the determinant, equate their values on the dependent, preferring the a-symbol. The decomposition is lossless exactly when some row becomes all a's.

A decomposition is **dependency-preserving** if the union of the FDs projected onto each fragment is equivalent to the original F, meaning every constraint can be enforced by checking one table alone, without a join. TEACHES exposes the classic conflict: the BCNF decomposition {TS, ST} loses `{Student, Subject} → Teacher`, since Student and Subject never appear together in any fragment. Enforcing that rule now requires joining ST and TS on every insert. Staying in 3NF preserves all dependencies but tolerates the redundancy of storing each teacher's subject once per student. The general theorem is: a lossless, dependency-preserving decomposition into **3NF always exists** (Bernstein's synthesis algorithm constructs one from a canonical cover), whereas a lossless decomposition into **BCNF always exists but may not preserve dependencies**. This trade-off is the practical reason 3NF remains the working target in many production designs.

## 11. Multivalued Dependencies and 4NF — A Brief Extension

Some redundancy survives BCNF. A **multivalued dependency (MVD)** X ↠ Y holds when, for each X value, the set of associated Y values is independent of the remaining attributes. Consider `COURSE_INFO(Course, Instructor, Textbook)` where a course has a set of instructors and, independently, a set of textbooks. Then `Course ↠ Instructor` and `Course ↠ Textbook`. Storing 3 instructors and 4 textbooks forces 12 rows, and adding a textbook requires 3 new rows. There are no non-trivial FDs here, so the relation is in BCNF. **Fourth Normal Form (4NF)** requires that for every non-trivial MVD X ↠ Y, X be a superkey; the remedy is to split into `COURSE_INSTRUCTOR(Course, Instructor)` and `COURSE_TEXT(Course, Textbook)`, reducing 12 rows to 7. Every FD is also an MVD, so 4NF implies BCNF.

## 12. Case Study: University Course Enrollment

### 12.1 The Schema and a Sample Instance

A registrar's office maintains a single wide table `ENROLL` with twelve attributes: `SID` (student ID), `SName`, `Zip`, `City`, `State`, `CID` (course ID), `CTitle`, `Credits`, `Term`, `IID` (instructor ID), `IName`, `Grade`.

| SID | SName | Zip | City | State | CID | CTitle | Credits | Term | IID | IName | Grade |
|-----|-------|-----|------|-------|-----|--------|---------|------|-----|-------|-------|
| S101 | Ana Ruiz | 60616 | Chicago | IL | CS201 | Data Structures | 3 | 2026SP | T22 | Novak | A |
| S101 | Ana Ruiz | 60616 | Chicago | IL | CS310 | Database Systems | 4 | 2026SP | T14 | Iyer | B+ |
| S102 | Ben Cole | 02139 | Cambridge | MA | CS201 | Data Structures | 3 | 2026SP | T22 | Novak | B |
| S102 | Ben Cole | 02139 | Cambridge | MA | CS310 | Database Systems | 4 | 2026SP | T14 | Iyer | A |
| S103 | Cara Diaz | 60616 | Chicago | IL | CS201 | Data Structures | 3 | 2026SP | T22 | Novak | C+ |
| S103 | Cara Diaz | 60616 | Chicago | IL | MA150 | Discrete Math | 3 | 2026SP | T31 | Ortiz | B |
| S104 | Dan Frey | 78701 | Austin | TX | CS310 | Database Systems | 4 | 2026SP | T14 | Iyer | F |
| S104 | Dan Frey | 78701 | Austin | TX | MA150 | Discrete Math | 3 | 2026SP | T31 | Ortiz | A |
| S101 | Ana Ruiz | 60616 | Chicago | IL | MA150 | Discrete Math | 3 | 2026FA | T31 | Ortiz | B+ |
| S105 | Eve Grant | 02139 | Cambridge | MA | CS201 | Data Structures | 3 | 2026FA | T09 | Petrov | B+ |
| S105 | Eve Grant | 02139 | Cambridge | MA | CS310 | Database Systems | 4 | 2026FA | T14 | Iyer | A |
| S106 | Finn Hale | 60616 | Chicago | IL | CS201 | Data Structures | 3 | 2026FA | T09 | Petrov | B |

Business rules stated by the registrar give the FD set **F**: (1) `SID → SName, Zip`; (2) `Zip → City, State`; (3) `CID → CTitle, Credits`; (4) `CID, Term → IID` (each course runs one section per term); (5) `IID → IName`; (6) `SID, CID, Term → Grade`.

Observe how the instance behaves as *evidence*. Rows 1 and 10 show CS201 taught by Novak in 2026SP and by Petrov in 2026FA — this **disproves** `CID → IID` and confirms that Term genuinely belongs in the determinant of rule 4. Meanwhile the instance does not disprove `City → Zip` or `IName → IID`, yet both are rejected on business grounds, exactly as Section 2 warned.

### 12.2 Closure and Candidate Keys

Classify the attributes. `Term` appears only on left-hand sides; `SName, City, State, CTitle, Credits, IName, Grade` appear only on right-hand sides; `SID, Zip, CID, IID` appear on both. Core = {Term}, and Term⁺ = {Term}, so we extend. Test {SID, CID, Term}: start {SID, CID, Term}; rule 1 adds SName, Zip; rule 3 adds CTitle, Credits; rule 4 adds IID; rule 6 adds Grade; rule 2 adds City, State; rule 5 adds IName. Result = all twelve attributes, so it is a superkey. Minimality: {CID, Term}⁺ = {CID, Term, CTitle, Credits, IID, IName} ✘; {SID, Term}⁺ = {SID, Term, SName, Zip, City, State} ✘; {SID, CID}⁺ = {SID, CID, SName, Zip, City, State, CTitle, Credits} ✘. No proper subset works, and no other combination reaches all twelve, so **{SID, CID, Term} is the unique candidate key**. Prime attributes: SID, CID, Term. Non-prime: the other nine.

### 12.3 Canonical Cover

Splitting right-hand sides gives ten FDs: SID → SName, SID → Zip, Zip → City, Zip → State, CID → CTitle, CID → Credits, {CID,Term} → IID, IID → IName, {SID,CID,Term} → Grade. Checking left-hand sides: in {CID,Term} → IID, CID⁺ = {CID, CTitle, Credits} lacks IID and Term⁺ = {Term} lacks IID, so neither attribute is extraneous. In {SID,CID,Term} → Grade, dropping any one attribute leaves a closure (computed above) without Grade, so nothing is extraneous. No FD is redundant, because each right-hand attribute is derivable by exactly one route. **F is already its own canonical cover** — a tidy outcome that makes the subsequent synthesis straightforward.

### 12.4 Current Normal Form and the Anomalies

`ENROLL` is in 1NF but violates 2NF three times over: `SID → SName, Zip`, `CID → CTitle, Credits`, and `{CID,Term} → IID` are all partial dependencies on proper subsets of the key {SID, CID, Term}. It additionally harbors transitive dependencies (`SID → Zip → City, State` and `{CID,Term} → IID → IName`), so it fails 3NF as well.

The consequences are concrete. **Insertion anomaly:** the registrar cannot record that ZIP 90210 belongs to Beverly Hills, CA until some student living there enrolls in some course, because SID, CID, and Term are all key attributes and cannot be null. Nor can a newly approved course CS400 be cataloged before its first enrollee. **Update anomaly:** when Ana Ruiz moves from ZIP 60616 to 78701, rows 1, 2, and 9 must all change; updating only rows 1 and 2 leaves the database asserting that S101 lives in two different places — a violation of `SID → Zip` introduced purely by redundancy. **Deletion anomaly:** if Finn Hale withdraws and row 12 is deleted, and Eve Grant's row 10 has already been removed, the system loses the fact that CS201 was taught by Petrov (T09) in 2026FA, even though the section itself still exists.

### 12.5 Proposed Decomposition

Applying 3NF synthesis to the canonical cover — one relation per determinant, plus one containing a candidate key — yields six relations:

| Relation | Attributes | Key | FDs enforced |
|----------|-----------|-----|--------------|
| STUDENT | SID, SName, Zip | SID | SID → SName, Zip |
| ZIPCODE | Zip, City, State | Zip | Zip → City, State |
| COURSE | CID, CTitle, Credits | CID | CID → CTitle, Credits |
| SECTION | CID, Term, IID | CID, Term | CID, Term → IID |
| INSTRUCTOR | IID, IName | IID | IID → IName |
| ENROLLMENT | SID, CID, Term, Grade | SID, CID, Term | SID, CID, Term → Grade |

Every determinant is now the key of its own relation, so the design is in BCNF, not merely 3NF. The decomposition is **lossless**: joining ENROLLMENT with SECTION on {CID, Term} is safe because {CID, Term} is the key of SECTION; joining the result with STUDENT on SID is safe because SID keys STUDENT; and so on down the chain — at every binary step the shared attributes key one side. It is also **dependency-preserving**, since each of the six original FDs is checkable inside a single table with no join. All three anomalies disappear: a new ZIP code goes into ZIPCODE alone, Ana's move touches exactly one row of STUDENT, and deleting an enrollment cannot destroy section or catalog facts.

## 13. Summary of Normal Forms

| Normal form | Condition | Anomaly eliminated | Typical remedy |
|---|---|---|---|
| 1NF | All attribute values atomic; no repeating groups | Ambiguous, unqueryable multi-valued cells | Move the repeating group to its own relation |
| 2NF | 1NF, and no non-prime attribute partially depends on a candidate key | Redundancy tied to part of a composite key; insert/delete of the part-entity | Project each partial determinant into its own relation |
| 3NF | 2NF, and for every non-trivial X → A, X is a superkey **or** A is prime | Redundancy from transitive chains key → X → A | Split off the intermediate determinant |
| BCNF | For every non-trivial X → A, X is a superkey (no exceptions) | Remaining anomalies from non-key determinants that overlap candidate keys | Decompose on the offending determinant; may cost dependency preservation |
| 4NF | BCNF, and for every non-trivial MVD X ↠ Y, X is a superkey | Combinatorial row explosion from independent multivalued facts | Separate each independent multivalued fact into its own relation |

**Practical guidance.** Normalize to BCNF where you can do so without losing dependency preservation; settle for 3NF where you cannot, and document the constraint that application code or a trigger must then enforce. Denormalize only afterwards, deliberately, to optimize a measured performance problem — and record the redundancy you have reintroduced so that a future maintainer can reason about the update behavior of the design.
