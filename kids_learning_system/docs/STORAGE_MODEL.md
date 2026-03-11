# Storage Model

## Object Stores
- quizzes
- attempts (indexed by quizId, childId, completedAt)
- profiles (indexed by childId)
- analyses (indexed by childId)
- instructions (indexed by childId)
- mediaCatalog
- settings

## Rules
- UI never accesses IndexedDB directly
- Raw attempt data is immutable
- Analysis artifacts are stored separately from attempts
- Instruction sets reference the analysis that generated them
