# Codebase Analysis Prompts

## 1. Initial Architecture Overview

```
Analyze this codebase and provide:
1. The primary entry point(s)
2. High-level architecture diagram of major components
3. Core dependencies and their versions
4. Key configuration files and their purposes
5. Main directories/modules and their responsibilities

Save as 1-architecture-overview.md.
```

## 2. Functional Flow Analysis

```
For each major component identified:
1. What are the main data flows?
2. What are the key interfaces between components?
3. What is the sequence of operations for core functionalities?
4. What are the primary business logic implementations?
5. What are the error handling patterns?

Save as 2-functional-flow.md.
```

## 3. Configuration and Environment Setup

```
Review the configuration management:
1. What environment variables are required?
2. What are the critical configuration parameters?
3. Are there different configurations for development/staging/production?
4. How are secrets managed?
5. What external services are required?

Save as 3-config-env.md.
```

## 4. Production Readiness Assessment

```
Evaluate production readiness:
1. What logging and monitoring is implemented?
2. What security measures are in place?
3. How is error handling implemented across the application?
4. What performance optimizations exist?
5. How is the application deployed and scaled?

Save as 4-production-readiness.md.
```

## 5. Modern Best Practices Gap Analysis

```
Compare against current best practices:
1. Which dependencies are outdated and what are their latest stable versions?
2. What current security vulnerabilities exist?
3. Which patterns are obsolete and what are their modern equivalents?
4. What test coverage exists and where are the gaps?
5. Which performance patterns could be improved with modern approaches?

Save as 5-best-practice-gaps.md.
```

## 6. Technical Debt Assessment

```
Identify areas needing improvement:
1. What code smells or anti-patterns exist?
2. Where is code duplicated or overly complex?
3. Which parts lack proper documentation?
4. What technical debt exists in the architecture?
5. Which parts would benefit most from refactoring?

Save as 6-technical-debts.md.
```

## 7. Documentation Gaps

```
Analyze documentation needs:
1. What critical functionality lacks documentation?
2. Where are the API documentation gaps?
3. What setup/deployment steps need better documentation?
4. Which configuration options need better explanation?
5. What examples would be most helpful to add?

Save as 7-documentation-gaps.md.
```

## 8. Testing Strategy

```
Evaluate testing approach:
1. What is the current test coverage?
2. Which critical paths lack testing?
3. What types of tests are missing (unit, integration, e2e)?
4. How can the test suite be modernized?
5. What test automation improvements are needed?

Save as 8-testing-strategy.md.
```

## 9. Performance Analysis

```
Assess performance considerations:
1. What are the main performance bottlenecks?
2. Where could caching be implemented or improved?
3. What database queries need optimization?
4. Where could async operations be beneficial?
5. What resource usage patterns need improvement?

Save as 9-performance-analysis.md.
```

## 10. Modernization Roadmap

```
Create an improvement plan:
1. What are the highest priority improvements needed?
2. Which updates would provide the most immediate value?
3. What is the recommended sequence of updates?
4. What potential risks exist in the modernization process?
5. What dependencies need to be updated first?

Save as 10-modernization.md.
```

## 11. File Structure Analysis
```
Analyze the codebase structure and create a detailed map:
1. Generate a tree structure of all directories and files
2. For each directory, explain its purpose and responsibility
3. For each file, provide:
   - Primary purpose
   - Key functions/classes
   - Dependencies and relationships
   - Configuration or environment requirements
   - Notable patterns or algorithms used
   - Public interfaces exposed
   - Integration points with other files

Example desired output format:

📁 src/
├── 📁 api/
│   ├── 📄 users.js
│   │   - Purpose: User management API endpoints
│   │   - Key functions: createUser(), getUserProfile()
│   │   - Dependencies: auth.js, database.js
│   │   - Interfaces: REST endpoints for /users/*
│   │   - Notable: Implements rate limiting
│   ├── 📄 auth.js
│   │   - Purpose: Authentication middleware
│   │   - Key functions: validateToken(), generateToken()
│   │   - Dependencies: jwt, crypto
│   │   - Notable: Uses JWT with RSA signing
├── 📁 models/
│   ├── 📄 user.js
│   │   - Purpose: User data model
│   │   - Key classes: UserSchema
│   │   - Dependencies: mongoose
│   │   - Notable: Includes password hashing hooks
...

4. Identify cross-cutting concerns and shared utilities
5. Map data flow between files
6. Document build/compilation order dependencies
7. Note any circular dependencies
8. Identify files that may need splitting or consolidation

Save as 11-file-structure.md.
```

## 12. File Health Metrics
```
For each file, evaluate and document:
1. Lines of code
2. Cyclomatic complexity
3. Test coverage percentage
4. Number of imports/dependencies
5. Last modified date
6. Number of contributors
7. Comment-to-code ratio
8. Number of TODOs/FIXMEs
9. Lint warnings/errors
10. Security scan results

Example desired output format:

📄 api/users.js
- Size: 458 lines
- Complexity: 15
- Coverage: 78%
- Dependencies: 8
- Last modified: 2024-01-15
- Contributors: 3
- Comment ratio: 0.15
- TODOs: 2
- Lint issues: 3 warnings
- Security: 1 medium risk

Save as 12-file-health-metrics.md.
```

## 13. File Relationship Map
```
Create a dependency graph showing:
1. Import/export relationships between files
2. Shared resource usage
3. Event flow between files
4. Database access patterns
5. External API interactions

Example desired output format:

users.js → auth.js → database.js
         ↘ email.js
         ↘ logging.js

Save as 13-file-relationship-map.md.
```